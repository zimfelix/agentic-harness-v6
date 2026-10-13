"""Run a repeatable synthetic demonstration, without touching your default state."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(dir=ROOT, prefix=".demo-") as directory:
        directory = Path(directory)
        db = directory / "planner.sqlite3"

        def run(*args, success=True):
            result = subprocess.run([sys.executable, str(ROOT / "planner.py"), "--db", str(db), *map(str, args)], cwd=ROOT, capture_output=True, text=True)
            if success:
                if result.returncode:
                    raise RuntimeError(result.stderr)
                return json.loads(result.stdout)
            if result.returncode == 0:
                raise RuntimeError("expected rejection")
            print(result.stderr.strip())

        def snapshot():
            path = directory / "snapshot.json"
            run("export", path, "--overwrite")
            return json.loads(path.read_text())

        print("Import:", run("import", ROOT / "examples/synthetic.json", "--replace"))
        original = snapshot()
        view = run("overview")  # Always a new invocation/process.
        for project in view["projects"]:
            print(project["id"], project["counts"], "remaining minutes:", project["remaining_minutes"])
            for task in project["tasks"]:
                print(" ", task["id"], task["status"], "blockers:", task["blockers"])
        print("Fresh invocation read exact saved state:", snapshot() == original)
        next_task = run("next")["task"]
        if next_task["id"] != "a2" or next_task["status"] != "ready":
            raise RuntimeError("invalid suggestion")
        print("Next:", next_task["id"], next_task["title"], "(blocked/done excluded)")
        malformed = directory / "malformed.json"
        malformed.write_text('{"version":')
        run("import", malformed, "--replace", success=False)
        if snapshot() != original:
            raise RuntimeError("malformed import altered state")
        print("Malformed import preserved exact state: True")
        run("depend", "a2", "a4", success=False)
        run("done", "a3", success=False)
        if snapshot() != original:
            raise RuntimeError("rejected mutation altered state")
        print("Cycle and blocked completion rejected without mutation: True")
        backup = directory / "backup.json"
        run("backup", backup)
        run("done", "a2")
        if snapshot() == original:
            raise RuntimeError("completion did not persist")
        run("restore", backup, "--replace")
        if snapshot() != original:
            raise RuntimeError("restore differs")
        print("Backup restored exact original state: True")


if __name__ == "__main__":
    main()
