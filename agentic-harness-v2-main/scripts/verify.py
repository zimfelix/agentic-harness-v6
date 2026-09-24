"""Run the checks configured during project initialization (no shell)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "harness" / "rules" / "project-specific" / "quality-gate.json"


def load_checks() -> list[tuple[str, list[str], Path]]:
    """Read and validate the project's explicitly chosen checks."""
    if not CONFIG.is_file():
        raise ValueError(f"Project Init required: configure checks in {CONFIG}")
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read quality-gate.json: {error}") from error

    if not isinstance(config, dict) or not isinstance(config.get("checks"), list):
        raise TypeError('quality-gate.json must contain a "checks" list')
    if not config["checks"]:
        raise ValueError("No checks configured; Project Init must select real checks")

    checks = []
    for index, entry in enumerate(config["checks"], start=1):
        if not isinstance(entry, dict):
            raise TypeError(f"Check {index} must be an object")
        name, command, working_dir = (
            entry.get("name"), entry.get("command"), entry.get("cwd", ".")
        )
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Check {index} needs a name")
        if (
            not isinstance(command, list)
            or not command
            or any(not isinstance(arg, str) or not arg for arg in command)
        ):
            raise ValueError(f"Check {index} needs a non-empty command array")
        if not isinstance(working_dir, str) or not working_dir.strip():
            raise ValueError(f"Check {index} needs a valid cwd")
        directory = (ROOT / working_dir).resolve()
        if not directory.is_relative_to(ROOT) or not directory.is_dir():
            raise ValueError(f"Check {index} cwd must be an existing project directory")
        checks.append((name, command, directory))
    return checks


def main() -> int:
    """Return success only when every configured check succeeds."""
    try:
        checks = load_checks()
    except (TypeError, ValueError) as error:
        print(f"[FAIL] Quality Gate: {error}", file=sys.stderr)
        return 1

    failed = False
    for name, command, directory in checks:
        print(f"== {name} ==", flush=True)
        try:
            result = subprocess.run(command, cwd=directory, check=False)
        except OSError as error:
            print(f"[FAIL] {name}: {error}", file=sys.stderr)
            failed = True
            continue
        if result.returncode != 0:
            print(f"[FAIL] {name}: exit {result.returncode}", file=sys.stderr)
            failed = True
        else:
            print(f"[PASS] {name}", flush=True)
    print(f"[{'FAIL' if failed else 'PASS'}] Quality Gate")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
