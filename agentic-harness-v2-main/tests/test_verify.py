"""Contract tests for the project-configured quality gate."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "verify.py"


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.script = self.root / "scripts" / "verify.py"
        self.script.parent.mkdir()
        self.script.write_bytes(SOURCE.read_bytes())
        self.config = self.root / "harness" / "rules" / "project-specific" / "quality-gate.json"
        self.config.parent.mkdir(parents=True)

    def run_gate(self):
        return subprocess.run(
            [sys.executable, str(self.script)],
            capture_output=True,
            text=True,
            check=False,
        )

    def configure(self, checks):
        self.config.write_text(json.dumps({"checks": checks}), encoding="utf-8")

    def test_missing_configuration_fails(self):
        # S001-AK1
        result = self.run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Project Init required", result.stderr)

    def test_empty_configuration_fails(self):
        # S001-AK2
        self.configure([])
        result = self.run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No checks configured", result.stderr)

    def test_all_configured_checks_run_and_pass(self):
        # S001-AK3
        self.configure([
            {"name": "First", "command": [sys.executable, "-c", "print('first ran')"]},
            {"name": "Second", "command": [sys.executable, "-c", "print('second ran')"]},
        ])
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("first ran", result.stdout)
        self.assertIn("second ran", result.stdout)
        self.assertIn("[PASS] Quality Gate", result.stdout)

    def test_failed_check_fails_even_if_later_check_passes(self):
        # S001-AK4
        self.configure([
            {"name": "Fail", "command": [sys.executable, "-c", "raise SystemExit(1)"]},
            {"name": "Pass", "command": [sys.executable, "-c", "print('continued')"]},
        ])
        result = self.run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("continued", result.stdout)
        self.assertIn("[FAIL] Fail", result.stderr)

    def test_invalid_configuration_and_missing_command_fail(self):
        # S001-AK5
        self.configure([{"name": "Bad", "command": "echo success"}])
        self.assertIn("command array", self.run_gate().stderr)
        self.configure([{"name": "Missing", "command": ["missing-test-tool-xyz"]}])
        result = self.run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[FAIL] Missing", result.stderr)
        self.configure([
            {"name": "Outside", "command": [sys.executable, "-c", "print('ran')"], "cwd": ".."}
        ])
        result = self.run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cwd must be an existing project directory", result.stderr)
        self.assertNotIn("ran", result.stdout)


if __name__ == "__main__":
    unittest.main()
