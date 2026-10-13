"""Behavior checks use fresh processes and synthetic state in project-local temp dirs."""
import copy
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from planner import validate
from storage import Store


class CLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT, prefix=".test-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.db = self.directory / "state.sqlite3"
        self.fixture = json.loads((ROOT / "examples/synthetic.json").read_text())

    def command(self, *args):
        return [sys.executable, str(ROOT / "planner.py"), "--db", str(self.db), *map(str, args)]

    def cli(self, *args, ok=True):
        result = subprocess.run(self.command(*args), cwd=ROOT, capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("error:", result.stderr)
        return result.stderr

    def seed(self):
        return self.cli("import", ROOT / "examples/synthetic.json", "--replace")

    def snapshot(self):
        path = self.directory / "snapshot.json"
        self.cli("export", path, "--overwrite")
        return json.loads(path.read_text())

    def write(self, state):
        path = self.directory / "input.json"
        path.write_text(json.dumps(state))
        return path

    def test_demo_persistence_overview_and_next(self):
        self.assertEqual(self.seed()["tasks"], 7)
        view = self.cli("overview")
        self.assertEqual(len(view["projects"]), 2)
        atlas = view["projects"][0]
        self.assertEqual(atlas["counts"], {"blocked": 2, "done": 1, "ready": 1})
        self.assertEqual(atlas["remaining_minutes"], 155)
        self.assertEqual(atlas["tasks"][2]["blockers"], ["a2"])
        self.assertEqual(self.cli("next")["task"]["id"], "a2")
        self.assertEqual(self.snapshot(), self.fixture)

    def test_blocked_completion_cycle_and_deletion_are_atomic(self):
        self.seed()
        for args in (("done", "a3"), ("depend", "a2", "a4"), ("depend", "b1", "b1"), ("depend", "b1", "missing"), ("task-delete", "a2"), ("project-delete", "atlas")):
            self.cli(*args, ok=False)
            self.assertEqual(self.snapshot(), self.fixture)
        self.cli("done", "a2")
        self.cli("done", "a3")
        before = self.snapshot()
        self.cli("reopen", "a2", ok=False)
        self.assertEqual(self.snapshot(), before)
        self.cli("reopen", "a3")
        self.cli("reopen", "a2")

    def test_malformed_imports_leave_exact_state(self):
        self.seed()
        path = self.directory / "bad.json"
        for raw in ('{', '{"version":1,"version":1,"projects":[],"tasks":[]}', 'null'):
            path.write_text(raw)
            self.cli("import", path, "--replace", ok=False)
            self.assertEqual(self.snapshot(), self.fixture)
        cases = []
        for field, value in (("priority", True), ("estimate_minutes", -1), ("due", "2030-02-29"), ("done", "yes"), ("project_id", "absent"), ("dependencies", ["absent"]), ("dependencies", ["a1", "a1"])):
            state = copy.deepcopy(self.fixture)
            state["tasks"][1][field] = value
            cases.append(state)
        state = copy.deepcopy(self.fixture)
        state["tasks"][0]["dependencies"] = ["a4"]
        state["tasks"][0]["done"] = False
        cases.append(state)  # genuine cycle, not merely invalid completion
        state = copy.deepcopy(self.fixture)
        state["tasks"][2]["done"] = True
        cases.append(state)
        state = copy.deepcopy(self.fixture)
        state["tasks"].append(copy.deepcopy(state["tasks"][0]))
        cases.append(state)
        state = copy.deepcopy(self.fixture)
        state["version"] = 2
        cases.append(state)
        for state in cases:
            self.cli("import", self.write(state), "--replace", ok=False)
            self.assertEqual(self.snapshot(), self.fixture)

    def test_backup_exact_restore_and_replay(self):
        self.seed()
        backup = self.directory / "backup.json"
        self.cli("backup", backup)
        self.cli("done", "a2")
        self.assertNotEqual(self.snapshot(), self.fixture)
        self.cli("restore", backup, "--replace")
        self.assertEqual(self.snapshot(), self.fixture)
        self.cli("import", backup, "--replace")
        self.assertEqual(self.snapshot(), self.fixture)
        self.cli("restore", self.write({}), "--replace", ok=False)
        self.assertEqual(self.snapshot(), self.fixture)
        # Recover a malformed application document without loading it first.
        connection = sqlite3.connect(self.db)
        try:
            with connection:
                connection.execute("UPDATE state SET document='broken'")
        finally:
            connection.close()
        self.cli("overview", ok=False)
        self.cli("restore", backup, "--replace")
        self.assertEqual(self.snapshot(), self.fixture)
        # Recovery into a new database (loss of the original file).
        self.db = self.directory / "recovered.sqlite3"
        self.cli("restore", backup, "--replace")
        self.assertEqual(self.snapshot(), self.fixture)

    def test_crud_and_dependency_removal(self):
        self.cli("project-add", "Practice", "--id", "p")
        self.cli("project-edit", "p", "Renamed")
        self.cli("task-add", "p", "One", "--id", "one", "--estimate", "25", "--due", "2032-02-29")
        self.cli("task-add", "p", "Two", "--id", "two", "--depends", "one")
        self.cli("task-edit", "one", "--title", "Edited", "--estimate", "50", "--priority", "5", "--clear-due")
        item = self.cli("next")["task"]
        self.assertEqual((item["title"], item["estimate_minutes"], item["due"]), ("Edited", 50, None))
        self.cli("done", "one")
        self.cli("done", "two")
        self.assertIsNone(self.cli("next")["task"])
        self.cli("undepend", "two", "one")
        self.cli("task-delete", "one")
        self.cli("task-delete", "two")
        self.cli("project-delete", "p")
        self.assertEqual(self.snapshot(), {"version": 1, "projects": [], "tasks": []})

    def test_ranking_ties_and_cross_project_filter(self):
        state = copy.deepcopy(self.fixture)
        for t in state["tasks"]:
            t["done"] = False
            t["dependencies"] = []
            t["priority"] = 3
            t["due"] = None
            t["estimate_minutes"] = 60
        state["tasks"][4]["priority"] = 4
        self.cli("import", self.write(state), "--replace")
        self.assertEqual(self.cli("next")["task"]["id"], "b1")
        self.cli("task-edit", "b1", "--priority", "3")
        self.assertEqual(self.cli("next")["task"]["id"], "a1")
        self.cli("task-edit", "b2", "--due", "2031-01-01")
        self.assertEqual(self.cli("next")["task"]["id"], "b2")
        self.cli("task-edit", "a4", "--due", "2030-01-01")
        self.assertEqual(self.cli("next")["task"]["id"], "a4")
        self.cli("task-edit", "a3", "--due", "2030-01-01", "--estimate", "1")
        self.assertEqual(self.cli("next")["task"]["id"], "a3")
        self.assertEqual(self.cli("next", "--project", "beacon")["task"]["id"], "b2")
        self.cli("depend", "b2", "a3")
        self.assertEqual(self.cli("next", "--project", "beacon")["task"]["id"], "b1")
        self.cli("next", "--project", "absent", ok=False)

    def test_invalid_mutations_and_output_protection(self):
        self.seed()
        for args in (("task-add", "atlas", "X", "--id", "a1"), ("project-add", "X", "--id", "atlas"), ("task-edit", "a2", "--priority", "6"), ("task-edit", "a2", "--due", "2025-02-29"), ("task-add", "absent", "X"), ("task-add", "atlas", " "), ("done", "absent")):
            self.cli(*args, ok=False)
            self.assertEqual(self.snapshot(), self.fixture)
        for path in (self.db, Path(str(self.db) + "-journal")):
            self.cli("export", path, "--overwrite", ok=False)
        path = self.directory / "export.json"
        self.cli("export", path)
        self.cli("export", path, ok=False)
        self.assertEqual(json.loads(path.read_text()), self.fixture)
        self.assertEqual(self.snapshot(), self.fixture)
        self.cli("backup", self.directory / "missing" / "file.json", ok=False)

    def test_concurrent_writers_preserve_both_changes(self):
        self.seed()
        commands = [("task-add", "atlas", "Concurrent A", "--id", "c1"), ("task-add", "beacon", "Concurrent B", "--id", "c2")]
        processes = [subprocess.Popen(self.command(*args), cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for args in commands]
        for process in processes:
            stdout, stderr = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 0, stderr)
        self.assertEqual({t["id"] for t in self.snapshot()["tasks"]}, {t["id"] for t in self.fixture["tasks"]} | {"c1", "c2"})

    def test_transaction_exception_and_killed_writer_roll_back(self):
        self.seed()
        def fail(state):
            state["projects"].clear()
            raise RuntimeError("simulated interruption")
        with self.assertRaises(RuntimeError):
            Store(self.db).run(validate, action=fail)
        self.assertEqual(self.snapshot(), self.fixture)
        script = "import sqlite3,sys,time; c=sqlite3.connect(sys.argv[1]); c.execute('BEGIN IMMEDIATE'); c.execute(\"UPDATE state SET document='broken'\"); print('ready',flush=True); time.sleep(30)"
        process = subprocess.Popen([sys.executable, "-c", script, str(self.db)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(process.stdout.readline().strip(), "ready")
        finally:
            process.kill()
            process.communicate(timeout=5)
        self.assertEqual(self.snapshot(), self.fixture)

    def test_long_dependency_chain(self):
        state = {"version": 1, "projects": [{"id": "p", "name": "Long synthetic chain"}], "tasks": []}
        for i in range(1200):
            state["tasks"].append({"id": f"t{i}", "project_id": "p", "title": "Synthetic", "estimate_minutes": 1, "priority": 3, "due": None, "done": False, "dependencies": [f"t{i-1}"] if i else []})
        self.cli("import", self.write(state), "--replace")
        self.assertEqual(self.cli("next")["task"]["id"], "t0")
        self.assertIn("cycle", self.cli("depend", "t0", "t1199", ok=False))
        self.assertEqual(self.snapshot(), state)


if __name__ == "__main__":
    unittest.main()
