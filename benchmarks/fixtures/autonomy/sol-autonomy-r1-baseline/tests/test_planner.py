import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from workplanner.domain import empty, mutate, next_task, overview, validate
from workplanner.storage import Store, read_json, write_new


def fixture():
    return read_json(ROOT / "fixtures/demo.json")


class DomainTests(unittest.TestCase):
    def test_fixture_overview_and_next(self):
        state = fixture()
        view = overview(state)
        self.assertEqual(len(view["projects"]), 2)
        self.assertEqual(view["projects"][0]["counts"], {"ready": 1, "blocked": 1, "done": 1})
        self.assertEqual(view["projects"][0]["estimate_minutes"], 150)
        self.assertEqual(view["projects"][0]["remaining_minutes"], 120)
        self.assertEqual(next_task(state)["id"], "a2")
        self.assertEqual(next_task(state, "beacon")["id"], "b1")
        self.assertEqual(view["projects"][0]["tasks"][2]["blockers"], ["a2"])

    def test_done_and_reopen_integrity(self):
        original = fixture()
        with self.assertRaisesRegex(ValueError, "unfinished"):
            mutate(original, "done", "a3")
        with self.assertRaisesRegex(ValueError, "unfinished"):
            mutate(mutate(original, "done", "a2"), "reopen", "a1")
        state = mutate(original, "done", "a2")
        state = mutate(state, "done", "a3")
        self.assertEqual(next_task(state)["id"], "b1")
        self.assertFalse(original["tasks"][1]["done"])
        for task in list(state["tasks"]):
            if not task["done"]:
                state = mutate(state, "done", task["id"])
        self.assertIsNone(next_task(state))
        state = mutate(state, "reopen", "a3")
        self.assertEqual(next_task(state)["id"], "a3")

    def test_cycles_missing_and_completed_prerequisites(self):
        for identity, deps, message in [("a2", ["a3"], "cycle"), ("b1", ["b1"], "cycle"),
                                        ("b1", ["missing"], "unknown"), ("a1", ["b1"], "unfinished")]:
            with self.subTest(identity=identity):
                with self.assertRaisesRegex(ValueError, message):
                    mutate(fixture(), "task-update", identity, depends_on=deps)

    def test_deletion_and_cross_project_dependencies(self):
        state = fixture()
        with self.assertRaisesRegex(ValueError, "referenced"):
            mutate(state, "task-delete", "a2")
        with self.assertRaisesRegex(ValueError, "cascade"):
            mutate(state, "project-delete", "atlas")
        linked = mutate(state, "task-update", "b3", depends_on=["a3"])
        with self.assertRaisesRegex(ValueError, "referenced"):
            mutate(linked, "project-delete", "atlas", cascade=True)
        removed = mutate(state, "project-delete", "atlas", cascade=True)
        self.assertEqual(len(removed["tasks"]), 3)
        removed = mutate(removed, "task-delete", "b3")
        self.assertEqual(len(removed["tasks"]), 2)

    def test_validation_types_and_dates(self):
        invalid = [("estimate", 0), ("estimate", True), ("estimate", 1.5), ("priority", 4),
                   ("priority", False), ("due", "2026-02-29"), ("due", "20260801"), ("due", "2026-13-01"),
                   ("title", " "), ("done", 1), ("depends_on", ["a1", "a1"]), ("project", "missing")]
        for field, value in invalid:
            state = fixture()
            state["tasks"][1][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                validate(state)
        state = mutate(fixture(), "task-update", "a2", due="2028-02-29")
        self.assertEqual(state["tasks"][1]["due"], "2028-02-29")
        for state in [dict(empty(), version=2), dict(empty(), version=True), dict(empty(), extra=1),
                      {"version": 1, "projects": {}, "tasks": []}]:
            with self.assertRaises(ValueError):
                validate(state)
        state = fixture()
        state["tasks"].append(copy.deepcopy(state["tasks"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate(state)

    def test_deterministic_tiebreakers_and_no_dates(self):
        state = empty()
        state = mutate(state, "project-add", "p", name="Synthetic")
        for tid, priority, estimate, due in [("z", 1, 5, None), ("b", 2, 10, "2026-08-01"),
                                             ("a", 2, 10, "2026-08-01"), ("c", 3, 1, "2026-08-01")]:
            state = mutate(state, "task-add", tid, project="p", title=tid, priority=priority,
                           estimate=estimate, due=due, depends_on=[])
        self.assertEqual(next_task(state)["id"], "a")
        state = mutate(state, "task-update", "b", estimate=9)
        self.assertEqual(next_task(state)["id"], "b")
        state = mutate(state, "task-update", "c", priority=1)
        self.assertEqual(next_task(state)["id"], "c")
        state["tasks"].reverse()
        self.assertEqual(next_task(state)["id"], "c")
        for tid in ("a", "b", "c"):
            state = mutate(state, "done", tid)
        self.assertEqual(next_task(state)["id"], "z")

    def test_long_dependency_chain(self):
        state = {"version": 1, "projects": [{"id": "p", "name": "Synthetic"}], "tasks": []}
        for i in range(1500):
            state["tasks"].append({"id": f"t{i}", "project": "p", "title": "Synthetic", "estimate": 1,
                                   "priority": 2, "due": None, "done": False,
                                   "depends_on": [f"t{i-1}"] if i else []})
        validate(state)
        state["tasks"][0]["depends_on"] = ["t1499"]
        with self.assertRaisesRegex(ValueError, "cycle"):
            validate(state)


class FileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT, prefix=".test-planner-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.store = Store(self.folder / "state.json")

    def test_restart_lock_and_failed_write(self):
        with self.store.session():
            self.assertEqual(self.store.load(), empty())
            self.store.save(fixture())
            with self.assertRaisesRegex(ValueError, "locked"):
                with Store(self.store.path).session():
                    pass
        original = self.store.path.read_bytes()
        with self.store.session():
            with patch("workplanner.storage.os.replace", side_effect=OSError("synthetic write failure")):
                with self.assertRaises(OSError):
                    self.store.save(empty())
        self.assertEqual(self.store.path.read_bytes(), original)
        self.assertFalse(self.store.lock.exists())
        self.assertEqual(list(self.folder.glob(".planner-*")), [])
        with Store(self.store.path).session() as restarted:
            self.assertEqual(restarted.load(), fixture())

    def test_strict_json_and_non_overwriting_backup(self):
        path = self.folder / "backup.json"
        write_new(path, fixture())
        with self.assertRaises(FileExistsError):
            write_new(path, empty())
        self.assertEqual(read_json(path), fixture())
        path.write_text('{"version":1,"version":1,"projects":[],"tasks":[]}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate JSON"):
            read_json(path)


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT, prefix=".test-cli-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.state = self.folder / "state.json"

    def run_cli(self, *arguments, ok=True):
        run = subprocess.run([sys.executable, str(ROOT / "planner.py"), "--state", str(self.state),
                              *map(str, arguments)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0 if ok else 2, run.stdout + run.stderr)
        if ok:
            return json.loads(run.stdout)
        self.assertIn("error:", run.stderr)
        self.assertNotIn("Traceback", run.stderr)
        return run.stderr

    def import_fixture(self):
        self.run_cli("import", ROOT / "fixtures/demo.json", "--yes")

    def assert_failure_unchanged(self, *args):
        before = self.state.read_bytes()
        error = self.run_cli(*args, ok=False)
        self.assertEqual(self.state.read_bytes(), before)
        return error

    def test_crud_estimates_due_dependencies(self):
        self.run_cli("project", "add", "p", "Synthetic project")
        self.run_cli("project", "update", "p", "Synthetic renamed")
        self.run_cli("task", "add", "t1", "--project", "p", "--title", "First", "--estimate", 30)
        self.run_cli("task", "add", "t2", "--project", "p", "--title", "Second", "--estimate", 60,
                     "--depends-on", "t1", "--due", "2028-02-29", "--priority", 1)
        self.assertEqual(self.run_cli("task", "show", "t2")["status"], "blocked")
        self.assert_failure_unchanged("task", "done", "t2")
        self.run_cli("task", "update", "t2", "--estimate", 45, "--due", "none", "--depends-on")
        task = self.run_cli("task", "show", "t2")
        self.assertEqual((task["estimate"], task["due"], task["depends_on"]), (45, None, []))
        self.run_cli("task", "done", "t2")
        self.run_cli("task", "reopen", "t2")
        self.assert_failure_unchanged("task", "update", "t2", "--priority", 0)
        self.assert_failure_unchanged("task", "update", "t2")
        self.assert_failure_unchanged("task", "delete", "t2")
        self.run_cli("task", "delete", "t2", "--yes")
        self.assert_failure_unchanged("project", "delete", "p", "--yes")
        self.run_cli("project", "delete", "p", "--yes", "--cascade")
        self.assertEqual(self.run_cli("overview")["projects"], [])
        self.assertIsNone(self.run_cli("next")["next"])

    def test_full_synthetic_restart_import_export_restore(self):
        report = self.run_cli("import", ROOT / "fixtures/demo.json", "--dry-run")
        self.assertFalse(report["saved"])
        self.assertFalse(self.state.exists())
        self.import_fixture()
        original = self.state.read_bytes()
        view = self.run_cli("overview")  # a new interpreter reads disk, not cached memory
        self.assertEqual(len(view["projects"]), 2)
        self.assertEqual(self.run_cli("next")["next"]["id"], "a2")
        self.assertEqual(self.run_cli("task", "show", "a3")["status"], "blocked")
        self.assertEqual(self.run_cli("task", "show", "a1")["status"], "done")
        self.assert_failure_unchanged("task", "update", "a2", "--depends-on", "a3")
        self.assert_failure_unchanged("task", "delete", "a2", "--yes")
        self.assert_failure_unchanged("import", ROOT / "fixtures/demo.json")
        bad = self.folder / "bad.json"
        bad.write_text('{"version":', encoding="utf-8")
        self.assert_failure_unchanged("import", bad, "--yes")
        self.assert_failure_unchanged("restore", bad, "--yes")
        cyclic = fixture()
        cyclic["tasks"][1]["depends_on"] = ["a3"]
        bad.write_text(json.dumps(cyclic), encoding="utf-8")
        self.assert_failure_unchanged("import", bad, "--yes")
        repeat = self.run_cli("import", ROOT / "fixtures/demo.json", "--yes")
        self.assertEqual(repeat["changes"]["tasks"]["new"], [])
        self.assertEqual(len(repeat["changes"]["tasks"]["unchanged"]), 6)
        self.assertEqual(self.state.read_bytes(), original)
        backup, export = self.folder / "backup.json", self.folder / "export.json"
        self.run_cli("backup", backup)
        self.run_cli("export", export)
        self.assertEqual(read_json(backup), read_json(export))
        self.assert_failure_unchanged("backup", backup)
        self.assert_failure_unchanged("export", self.state)
        self.assert_failure_unchanged("restore", self.state)
        self.run_cli("task", "done", "a2")
        self.assertEqual(self.run_cli("next")["next"]["id"], "a3")
        dry = self.run_cli("restore", backup, "--dry-run")
        self.assertIn("a2", dry["changes"]["tasks"]["changed"])
        self.run_cli("restore", backup, "--yes")
        self.assertEqual(self.state.read_bytes(), original)
        self.assertEqual(self.run_cli("overview"), view)

    def test_lock_corruption_and_recovery(self):
        self.import_fixture()
        lock = self.state.with_name("state.json.lock")
        lock.write_text("synthetic competing process", encoding="utf-8")
        self.assert_failure_unchanged("task", "done", "a2")
        lock.unlink()
        backup = self.folder / "backup.json"
        self.run_cli("backup", backup)
        self.state.write_text("broken JSON", encoding="utf-8")
        self.assert_failure_unchanged("overview")
        self.assert_failure_unchanged("import", ROOT / "fixtures/demo.json", "--yes")
        report = self.run_cli("restore", backup, "--dry-run")
        self.assertIn("unreadable_current_state", report["changes"])
        self.assertEqual(self.state.read_text(), "broken JSON")
        self.run_cli("restore", backup, "--yes")
        self.assertEqual(read_json(self.state), fixture())

    def test_missing_ids_duplicate_ids_and_path_boundary(self):
        self.import_fixture()
        self.assert_failure_unchanged("project", "add", "atlas", "Duplicate")
        self.assert_failure_unchanged("task", "show", "missing")
        self.assert_failure_unchanged("next", "--project", "missing")
        self.assert_failure_unchanged("export", ROOT.parent / "forbidden-output.json")
        self.assertFalse((ROOT.parent / "forbidden-output.json").exists())


if __name__ == "__main__":
    unittest.main()
