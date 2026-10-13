"""Behavior tests. Most drive the real CLI in a separate process (the public
boundary); ranking edge cases call the suggestion function directly."""
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "examples" / "sample-project.json"
sys.path.insert(0, str(ROOT))
from planner import model, suggest  # noqa: E402

SCRATCH = ROOT / ".scratch" / "tests"


class CliCase(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.dir = Path(tempfile.mkdtemp(dir=SCRATCH))
        self.data = self.dir / "planner.json"

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def run_cli(self, *args, ok=True):
        r = subprocess.run([sys.executable, str(ROOT / "planner.py"), "--data", str(self.data),
                            "--today", "2026-10-10", *map(str, args)], capture_output=True, text=True)
        if ok is not None:
            self.assertEqual(r.returncode == 0, ok, f"{args}: {r.stdout}{r.stderr}")
        return r.stdout + r.stderr

    def state(self):
        return json.loads(self.data.read_text())

    def task(self, tid):
        return next(t for t in self.state()["tasks"] if t["id"] == tid)

    def load_fixture(self):
        self.run_cli("import", FIXTURE, "--replace")


class TestBasics(CliCase):
    def test_create_edit_persist_across_invocations(self):
        self.run_cli("project", "add", "Alpha", "--description", "synthetic")
        self.run_cli("task", "add", "alpha", "Draft", "--estimate", "1h30m", "--due", "2026-10-12", "--priority", "high")
        self.run_cli("task", "edit", "t1", "--title", "Draft v2", "--no-due")
        out = self.run_cli("task", "show", "t1")  # new process reads saved file
        self.assertIn("Draft v2", out)
        self.assertIn("1h30m", out)
        self.assertIn("due:       -", out)
        self.assertEqual(self.task("t1")["estimate_minutes"], 90)

    def test_input_validation(self):
        self.run_cli("project", "add", "Alpha")
        self.assertIn("already used", self.run_cli("project", "add", "ALPHA", ok=False))
        self.assertIn("calendar date", self.run_cli("task", "add", "p1", "x", "--due", "2026-02-30", ok=False))
        self.assertIn("estimate", self.run_cli("task", "add", "p1", "x", "--estimate", "soon", ok=False))
        self.assertIn("priority", self.run_cli("task", "add", "p1", "x", "--priority", "urgent", ok=False))
        self.assertIn("no project", self.run_cli("task", "add", "nope", "x", ok=False))
        self.assertEqual(self.state()["tasks"], [])

    def test_ids_are_not_reused(self):
        self.run_cli("project", "add", "Alpha")
        self.run_cli("task", "add", "p1", "a")
        self.run_cli("task", "delete", "t1")
        self.assertIn("created task t2", self.run_cli("task", "add", "p1", "b"))

    def test_overview(self):
        self.load_fixture()
        out = self.run_cli("overview")
        self.assertIn("tasks 5: 1 done, 2 ready, 2 blocked | remaining estimate 18h", out)
        self.assertIn("tasks 3: 0 done, 2 ready, 1 blocked | remaining estimate 3h30m (+1 unestimated)", out)
        out = self.run_cli("--today", "2026-10-12", "overview", "Admin", ok=True)
        self.assertIn("OVERDUE: t6 (due 2026-10-11)", out)
        self.assertIn("File quarterly figures", out)


class TestDependencies(CliCase):
    def setUp(self):
        super().setUp()
        self.load_fixture()

    def test_blocked_task_cannot_be_completed(self):
        before = self.data.read_bytes()
        self.assertIn("blocked by unfinished prerequisite(s): t2, t3", self.run_cli("task", "done", "t4", ok=False))
        self.assertEqual(self.data.read_bytes(), before)
        self.run_cli("task", "done", "t2")
        self.assertIn("t3", self.run_cli("task", "done", "t4", ok=False))
        self.assertIn("now ready: t4", self.run_cli("task", "done", "t3"))
        self.run_cli("task", "done", "t4")
        self.assertEqual(self.task("t4")["status"], "done")

    def test_blocked_listing(self):
        out = self.run_cli("blocked")
        self.assertIn("t4 [p1] Build pages -- waiting for: t2 (Wireframes), t3 (Write page copy)", out)
        self.assertIn("t5 [p1] Launch -- waiting for: t4", out)
        self.assertIn("t7 [p2]", out)
        self.assertNotIn("t2 [p1]", out)

    def test_cycles_rejected(self):
        before = self.data.read_bytes()
        self.assertIn("cycle: t2 -> t5 -> t4 -> t2", self.run_cli("task", "depend", "t2", "t5", ok=False))
        self.assertIn("itself", self.run_cli("task", "depend", "t3", "t3", ok=False))
        self.assertEqual(self.data.read_bytes(), before)
        # cycle across projects via task edits
        self.run_cli("task", "depend", "t6", "t8")
        self.assertIn("cycle: t8 -> t7 -> t6 -> t8", self.run_cli("task", "depend", "t8", "t7", ok=False))

    def test_done_invariant_on_reopen_and_depend(self):
        self.run_cli("task", "done", "t6")
        self.run_cli("task", "done", "t7")
        self.assertIn("t7 depend on it", self.run_cli("task", "reopen", "t6", ok=False))
        self.assertIn("is done", self.run_cli("task", "depend", "t7", "t8", ok=False))
        self.run_cli("task", "reopen", "t7")
        self.run_cli("task", "reopen", "t6")
        self.assertEqual(self.task("t6")["status"], "open")

    def test_delete_task_refused_or_detached(self):
        self.assertIn("t4 depends on t2", self.run_cli("task", "delete", "t2", ok=False))
        self.assertIn("t2", [t["id"] for t in self.state()["tasks"]])
        out = self.run_cli("task", "delete", "t2", "--detach")
        self.assertIn("removed dependency: t4 no longer depends on t2", out)
        self.assertEqual(self.task("t4")["depends_on"], ["t3"])

    def test_delete_project_cross_project_refs(self):
        self.run_cli("task", "depend", "t8", "t5")  # p2 task depends on p1 task
        self.assertIn("--yes", self.run_cli("project", "delete", "p1", ok=False))
        self.assertIn("t8 depends on t5", self.run_cli("project", "delete", "p1", "--yes", ok=False))
        self.assertEqual(len(self.state()["projects"]), 2)
        out = self.run_cli("project", "delete", "p1", "--yes", "--detach")
        self.assertIn("t8 no longer depends on t5", out)
        s = self.state()
        self.assertEqual([p["id"] for p in s["projects"]], ["p2"])
        self.assertEqual(sorted(t["id"] for t in s["tasks"]), ["t6", "t7", "t8"])
        self.assertEqual(self.task("t8")["depends_on"], [])
        self.assertEqual(len(list((self.dir / "backups").glob("*pre-delete*"))), 1)


class TestImportExportRestore(CliCase):
    def setUp(self):
        super().setUp()
        self.load_fixture()
        self.before = self.data.read_bytes()

    def write(self, name, content):
        p = self.dir / name
        p.write_text(content if isinstance(content, str) else json.dumps(content))
        return p

    def fixture_with(self, change):
        d = json.loads(FIXTURE.read_text())
        change(d)
        return d

    def test_malformed_imports_leave_state_intact(self):
        cases = {
            "truncated": '{"format": "local-planner", "projects": [',
            "not object": "[]",
            "wrong version": self.fixture_with(lambda d: d.update(schema_version=2)),
            "dangling": self.fixture_with(lambda d: d["tasks"][2]["depends_on"].append("t42")),
            "cycle": self.fixture_with(lambda d: d["tasks"][1]["depends_on"].append("t5")),
            "done with open prereq": self.fixture_with(lambda d: d["tasks"][4].update(status="done")),
            "bad project": self.fixture_with(lambda d: d["tasks"][0].update(project="p9")),
            "duplicate id": self.fixture_with(lambda d: d["tasks"].append(dict(d["tasks"][0]))),
            "bad date": self.fixture_with(lambda d: d["tasks"][0].update(due="10/12/2026")),
            "bad counter": self.fixture_with(lambda d: d.update(next_task=3)),
        }
        for name, content in cases.items():
            for mode in ("--replace", "--merge"):
                with self.subTest(name, mode=mode):
                    self.run_cli("import", self.write("bad.json", content), mode, ok=False)
                    self.assertEqual(self.data.read_bytes(), self.before)
        self.assertIn("t2 -> t5 -> t4 -> t2", self.run_cli("import", self.write("c.json", cases["cycle"]),
                                                          "--replace", ok=False))

    def test_dry_run_and_merge(self):
        other = self.fixture_with(lambda d: [p.update(name=p["name"] + " B") for p in d["projects"]])
        f = self.write("other.json", other)
        self.assertIn("result would have 4 project(s), 16 task(s)", self.run_cli("import", f, "--merge", "--dry-run"))
        self.assertEqual(self.data.read_bytes(), self.before)
        self.assertIn("t4->t12", self.run_cli("import", f, "--merge"))
        self.assertEqual(self.task("t12")["depends_on"], ["t10", "t11"])
        self.assertIn("already used", self.run_cli("import", FIXTURE, "--merge", ok=False))

    def test_export_backup_restore_roundtrip(self):
        exported = self.dir / "export.json"
        self.run_cli("export", "--out", exported)
        self.assertIn("already exists", self.run_cli("export", "--out", exported, ok=False))
        self.run_cli("backup")
        self.run_cli("task", "done", "t6")
        self.run_cli("project", "add", "Later")
        self.run_cli("restore", exported)
        self.assertEqual(self.data.read_bytes(), exported.read_bytes())
        self.assertEqual(json.loads(self.run_cli("export")), json.loads(FIXTURE.read_text()))
        self.assertTrue(list((self.dir / "backups").glob("*pre-restore*")))

    def test_corrupt_state_reported_and_recoverable(self):
        self.run_cli("backup")
        self.data.write_text("{oops")
        out = self.run_cli("project", "add", "X", ok=False)
        self.assertIn("unreadable", out)
        self.assertEqual(self.data.read_text(), "{oops")  # not overwritten
        self.run_cli("restore", "--latest")
        self.assertEqual(self.data.read_bytes(), self.before)
        raw = list((self.dir / "backups").glob("*corrupt*"))
        self.assertEqual(raw[0].read_text(), "{oops")
        self.assertIn("is not valid JSON", self.run_cli("restore", self.write("x.json", "nope"), ok=False))
        self.assertEqual(self.data.read_bytes(), self.before)

    def test_concurrent_writers_do_not_lose_updates(self):
        threads = [threading.Thread(target=self.run_cli, args=("task", "add", "p2", f"parallel {i}"))
                   for i in range(8)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        s = self.state()
        self.assertEqual(len(s["tasks"]), 16)
        self.assertEqual(len({t["id"] for t in s["tasks"]}), 16)


class TestNextWork(CliCase):
    def test_cli_excludes_blocked_and_done(self):
        self.load_fixture()
        out = self.run_cli("next", "--limit", "20")
        ids = [line.split()[1] for line in out.splitlines() if line[:1].isdigit()]
        self.assertEqual(ids, ["t6", "t3", "t2", "t8"])  # t1 done; t4, t5, t7 blocked
        self.assertIn("priority high via t7", out)
        self.assertEqual(out, self.run_cli("next", "--limit", "20"))  # deterministic

    def test_nothing_ready(self):
        self.run_cli("project", "add", "Empty")
        self.assertIn("nothing is ready", self.run_cli("next"))


class TestRanking(unittest.TestCase):
    TODAY = dt.date(2026, 10, 10)

    def state(self, *tasks):
        s = model.empty_state()
        model.add_project(s, "P")
        for kw in tasks:
            t = model.add_task(s, "p1", kw.pop("title"), **{k: v for k, v in kw.items() if k != "done"})
            if kw.get("done"):
                model.complete_task(s, t["id"])
        return model.validate_state(s)

    def ranked(self, s):
        return [t["id"] for t, _ in suggest.next_work(s, self.TODAY, limit=50)]

    def test_urgent_beats_priority_and_overdue_first(self):
        s = self.state(dict(title="crit", priority="critical"),
                       dict(title="soon", priority="low", due="2026-10-12"),
                       dict(title="late", priority="low", due="2026-10-01"),
                       dict(title="far", priority="high", due="2026-12-01"))
        self.assertEqual(self.ranked(s), ["t3", "t2", "t1", "t4"])

    def test_tie_breaks(self):
        s = self.state(dict(title="big", estimate="5h"), dict(title="none"), dict(title="small", estimate="1h"),
                       dict(title="dep", depends_on=["t2"]))
        # t2 unblocks t4 -> first; then smaller estimate; unestimated last among equals
        self.assertEqual(self.ranked(s), ["t2", "t3", "t1"])

    def test_inherits_from_blocked_dependents_only_while_open(self):
        s = self.state(dict(title="pre", priority="low"), dict(title="other", priority="high"),
                       dict(title="goal", priority="critical", due="2026-10-11", depends_on=["t1"]))
        self.assertEqual(self.ranked(s), ["t1", "t2"])
        s = self.state(dict(title="a", done=True), dict(title="b", priority="low"))
        self.assertEqual(self.ranked(s), ["t2"])


if __name__ == "__main__":
    unittest.main()
