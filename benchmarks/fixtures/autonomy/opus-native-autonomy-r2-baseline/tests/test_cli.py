"""Behavior tests through the real ./planner entrypoint on isolated temp databases."""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "synthetic-portfolio.json"
TMP_BASE = ROOT / ".test-tmp"


class CliTests(unittest.TestCase):
    def setUp(self):
        TMP_BASE.mkdir(exist_ok=True)
        self.dir = Path(tempfile.mkdtemp(dir=TMP_BASE))
        self.addCleanup(shutil.rmtree, self.dir)
        self.db = self.dir / "p.db"

    def run_cli(self, *args, ok=True):
        r = subprocess.run([sys.executable, str(ROOT / "planner"), "--db", str(self.db), *args],
                           capture_output=True, text=True)
        if ok is not None:
            self.assertEqual(r.returncode == 0, ok, f"{args}: {r.stdout}{r.stderr}")
        return r

    def state(self):
        doc = json.loads(self.run_cli("export", "-").stdout)
        doc.pop("exported_at")
        return doc

    def load_fixture(self):
        self.run_cli("import", str(FIXTURE))

    def test_fixture_import_and_restart_persistence(self):
        out = self.run_cli("import", str(FIXTURE)).stdout
        self.assertIn("2 project(s)", out)
        self.assertIn("7 task(s), 5 dependencies", out)
        self.run_cli("task", "add", "dash-tool", "Extra", "--estimate", "1h", "--after", "7")
        overview = self.run_cli("overview", "--today", "2026-10-10").stdout
        self.assertIn("4 tasks: 1 done (25%), 1 ready, 2 blocked; remaining estimate 13h00m", overview)
        self.assertIn("4 tasks: 0 done (0%), 2 ready, 2 blocked; remaining estimate 10h00m", overview)
        self.assertIn("#8    [blocked] Extra", overview)

    def test_blocked_task_cannot_be_completed(self):
        self.load_fixture()
        r = self.run_cli("task", "done", "3", ok=False)
        self.assertIn("blocked by unfinished #2", r.stderr)
        self.assertIn("#3    [blocked]", self.run_cli("blocked").stdout)
        self.run_cli("task", "done", "2")
        self.run_cli("task", "done", "3")
        self.assertIn("[done   ] Build pages", self.run_cli("list", "--state", "done").stdout)

    def test_cycle_rejected_without_change(self):
        self.load_fixture()
        before = self.state()
        r = self.run_cli("dep", "add", "2", "4", ok=False)
        self.assertIn("cycle", r.stderr)
        self.run_cli("dep", "add", "5", "5", ok=False)
        self.assertEqual(self.state(), before)

    def test_delete_integrity(self):
        self.load_fixture()
        self.assertIn("still required by #3", self.run_cli("task", "delete", "2", ok=False).stderr)
        out = self.run_cli("task", "delete", "2", "--detach").stdout
        self.assertIn("#3 no longer waits for #2", out)
        self.run_cli("dep", "add", "7", "4")  # cross-project link
        self.assertIn("would delete", self.run_cli("project", "delete", "bakery-site").stdout)
        self.run_cli("project", "delete", "bakery-site", "--yes", ok=False)
        self.run_cli("project", "delete", "bakery-site", "--yes", "--detach")
        doc = self.state()
        self.assertEqual([p["key"] for p in doc["projects"]], ["dash-tool"])
        ids = {t["id"] for t in doc["tasks"]}
        self.assertTrue(all(set(t["depends_on"]) <= ids for t in doc["tasks"]))

    def test_invalid_inputs_change_nothing(self):
        self.load_fixture()
        before = self.state()
        for args in (["task", "add", "nope", "x"], ["task", "add", "dash-tool", "x", "--priority", "top"],
                     ["task", "add", "dash-tool", "x", "--due", "2026-02-30"],
                     ["task", "add", "dash-tool", "x", "--estimate", "soon"],
                     ["project", "add", "dash-tool", "dup"], ["project", "add", "Bad Key", "x"],
                     ["task", "done", "99"], ["task", "reopen", "5"]):
            self.assertTrue(self.run_cli(*args, ok=False).stderr.startswith("error:"), args)
        self.assertEqual(self.state(), before)

    def test_reopen_guard_and_done_task_gets_no_open_prereq(self):
        self.load_fixture()
        self.run_cli("task", "done", "2")
        self.assertIn("reopen them first", self.run_cli("task", "reopen", "1", ok=False).stderr)
        self.assertIn("reopen it", self.run_cli("dep", "add", "2", "5", ok=False).stderr)
        self.run_cli("task", "reopen", "2")

    def test_next_excludes_blocked_done_and_is_deterministic(self):
        self.load_fixture()
        runs = {self.run_cli("next", "--today", "2026-10-10", "--limit", "20").stdout for _ in range(3)}
        self.assertEqual(len(runs), 1)
        ids = [line.split()[1] for line in runs.pop().splitlines()]
        self.assertEqual(ids, ["#2", "#5", "#6"])
        for t in ("1", "2", "5", "6"):
            if t != "1":
                self.run_cli("task", "done", t)
        self.run_cli("task", "done", "3")
        self.run_cli("task", "done", "4")
        self.run_cli("task", "done", "7")
        self.assertIn("nothing ready", self.run_cli("next").stdout)

    def test_malformed_imports_leave_state_intact(self):
        self.load_fixture()
        before = self.state()
        good = json.loads(FIXTURE.read_text())
        good["projects"] = [{"key": "new-one", "name": "N"}]
        cases = {
            "notjson": "{oops",
            "wrongformat": json.dumps({**good, "format": "x"}),
            "unknownfield": json.dumps({**good, "extra": 1}),
            "dangling": json.dumps({**good, "tasks": [{"id": 1, "project": "new-one", "title": "a",
                                                       "depends_on": [9]}]}),
            "cycle": json.dumps({**good, "tasks": [
                {"id": 1, "project": "new-one", "title": "a", "depends_on": [2]},
                {"id": 2, "project": "new-one", "title": "b", "depends_on": [1]}]}),
            "badpriority": json.dumps({**good, "tasks": [{"id": 1, "project": "new-one", "title": "a",
                                                          "priority": "asap"}]}),
            "existing": FIXTURE.read_text(),
        }
        for name, text in cases.items():
            path = self.dir / f"{name}.json"
            path.write_text(text)
            r = self.run_cli("import", str(path), ok=False)
            self.assertTrue(r.stderr.startswith("error:"), name)
            self.assertEqual(self.state(), before, name)

    def test_dry_run_import_changes_nothing(self):
        self.assertIn("dry run", self.run_cli("import", str(FIXTURE), "--dry-run").stdout)
        self.assertEqual(self.state()["tasks"], [])

    def test_backup_restore_roundtrip(self):
        self.load_fixture()
        self.run_cli("task", "done", "2")
        before = self.state()
        backup = self.dir / "b.json"
        self.run_cli("backup", str(backup))
        self.run_cli("task", "delete", "4")
        self.run_cli("task", "add", "bakery-site", "Later")
        self.run_cli("project", "delete", "dash-tool", "--yes")
        self.assertIn("re-run with --yes", self.run_cli("restore", str(backup)).stdout)
        self.assertNotEqual(self.state(), before)
        out = self.run_cli("restore", str(backup), "--yes").stdout
        self.assertEqual(self.state(), before)
        safety = Path(out.split("previous state: ")[1].split()[0])
        self.assertEqual(len(json.loads(safety.read_text())["tasks"]), 4)
        # the id counter is part of the restored state
        self.assertIn("#8", self.run_cli("task", "add", "dash-tool", "New").stdout)

    def test_malformed_restore_changes_nothing(self):
        self.load_fixture()
        before = self.state()
        bad = self.dir / "bad.json"
        doc = json.loads(self.run_cli("export", "-").stdout)
        doc["tasks"][1]["depends_on"] = [3]  # 2 -> 3 -> 2 cycle
        bad.write_text(json.dumps(doc))
        self.assertIn("cycle", self.run_cli("restore", str(bad), "--yes", ok=False).stderr)
        bad.write_text("")
        self.run_cli("restore", str(bad), "--yes", ok=False)
        self.assertEqual(self.state(), before)

    def test_export_import_roundtrip_and_subset_guard(self):
        self.load_fixture()
        self.run_cli("task", "done", "5")
        exported = self.dir / "e.json"
        self.run_cli("export", str(exported))
        original = self.state()
        self.db = self.dir / "other.db"
        self.run_cli("import", str(exported))
        copy = self.state()
        strip = lambda d: [{k: v for k, v in t.items() if k != "id"} for t in d["tasks"]]  # noqa: E731
        self.assertEqual((copy["projects"], strip(copy)), (original["projects"], strip(original)))
        self.run_cli("dep", "add", "7", "4")
        self.assertIn("leave it", self.run_cli("export", "-", "--project", "dash-tool", ok=False).stderr)

    def test_concurrent_writers_lose_nothing(self):
        self.run_cli("project", "add", "p", "P")
        with ThreadPoolExecutor(8) as pool:
            results = list(pool.map(lambda i: self.run_cli("task", "add", "p", f"t{i}", ok=None),
                                    range(16)))
        self.assertTrue(all(r.returncode == 0 for r in results), [r.stderr for r in results])
        self.assertEqual(len(self.state()["tasks"]), 16)

    def test_newer_schema_refused(self):
        self.run_cli("project", "list")
        with sqlite3.connect(self.db) as conn:
            conn.execute("PRAGMA user_version = 99")
        self.assertIn("newer", self.run_cli("project", "list", ok=False).stderr)


if __name__ == "__main__":
    os.chdir(ROOT)
    unittest.main()
