"""Repeatable synthetic demonstration; uses only temporary files inside project."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = []
    with tempfile.TemporaryDirectory(dir=ROOT, prefix=".demo-planner-") as directory:
        folder = Path(directory)
        state = folder / "state.json"

        def run(*args, expected=0):
            command = [sys.executable, str(ROOT / "planner.py"), "--state", str(state), *map(str, args)]
            process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            if process.returncode != expected:
                raise RuntimeError(process.stdout + process.stderr)
            output = json.loads(process.stdout) if expected == 0 else process.stderr.strip()
            records.append({"command": " ".join(map(str, args)).replace(str(folder), "<demo>"),
                            "exit": process.returncode, "output": output})
            return output

        run("import", "fixtures/demo.json", "--yes")
        original = state.read_bytes()
        original_view = run("overview")  # independent fresh process
        suggestion = run("next")["next"]
        assert suggestion["id"] == "a2" and suggestion["status"] == "ready"
        tasks = [task for p in original_view["projects"] for task in p["tasks"]]
        assert len(tasks) == 6 and len(original_view["projects"]) == 2
        assert any(t["status"] == "blocked" for t in tasks)
        assert any(t["status"] == "done" for t in tasks)
        malformed = folder / "malformed.json"
        malformed.write_text('{"version":', encoding="utf-8")
        run("import", malformed, "--yes", expected=2)
        assert state.read_bytes() == original
        run("task", "update", "a2", "--depends-on", "a3", expected=2)
        assert state.read_bytes() == original
        run("task", "done", "a3", expected=2)
        assert state.read_bytes() == original
        backup = folder / "backup.json"
        run("backup", backup)
        run("task", "done", "a2")
        assert run("next")["next"]["id"] == "a3"
        run("restore", backup, "--dry-run")
        run("restore", backup, "--yes")
        assert state.read_bytes() == original
        assert run("overview") == original_view
        records.append({"checks": "restart, blocked completion, malformed import, cycle rejection, next eligibility and restore equality passed",
                        "state_sha256_before_and_after_restore": hashlib.sha256(original).hexdigest()})
    # Only this synthetic report is intentionally replaced on repeat runs.
    output_path = ROOT / "examples/demo-results.json"
    output_path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"Synthetic demonstration passed; report: {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
