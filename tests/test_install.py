"""Installer tests for the starter kit itself (not product application tests)."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

INSTALLER = Path(__file__).resolve().parents[1] / "scripts" / "install.py"
spec = importlib.util.spec_from_file_location("harness_installer", INSTALLER)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.target = Path(self.temporary.name) / "project"

    def test_new_project_copies_only_allowlisted_files_and_stays_pending(self):
        actions = installer.install(self.target)
        self.assertIn("ADD  harness/core.md", actions)
        self.assertTrue((self.target / "harness/verification/gate.md").is_file())
        self.assertTrue((self.target / "docs/README.md").is_file())
        self.assertTrue((self.target / "src/README.md").is_file())
        self.assertIn("Pending Project Init", (self.target / "harness/project.md").read_text())
        self.assertFalse((self.target / "README.md").exists())
        self.assertEqual((self.target / "AGENTS.md").read_bytes(),
                         (INSTALLER.parents[1] / "AGENTS.md").read_bytes())
        for excluded in ("main.py", "assets/images/img.png", "scripts/install.py", "tests/test_install.py", ".git"):
            self.assertFalse((self.target / excluded).exists(), excluded)
        self.assertTrue(all(action.startswith(("SAME", "KEEP")) for action in installer.install(self.target)))

    def test_existing_readme_is_preserved(self):
        self.target.mkdir()
        (self.target / "README.md").write_text("My project\n")
        installer.install(self.target)
        self.assertEqual((self.target / "README.md").read_text(), "My project\n")

    def test_conflict_aborts_before_writing_anything(self):
        self.target.mkdir()
        (self.target / "AGENTS.md").write_text("existing instructions\n")
        with self.assertRaisesRegex(ValueError, "AGENTS.md"):
            installer.install(self.target)
        self.assertFalse((self.target / "harness").exists())
        self.assertEqual((self.target / "AGENTS.md").read_text(), "existing instructions\n")

    def test_existing_agents_requires_opt_in_and_manual_integration(self):
        self.target.mkdir()
        (self.target / "AGENTS.md").write_text("existing instructions\n")
        actions = installer.install(self.target, keep_agents=True)
        self.assertIn("KEEP AGENTS.md (manual integration required)", actions)
        self.assertEqual((self.target / "AGENTS.md").read_text(), "existing instructions\n")
        self.assertTrue((self.target / "harness/core.md").exists())

    def test_dry_run_does_not_create_target(self):
        actions = installer.install(self.target, dry_run=True)
        self.assertIn("ADD  harness/core.md", actions)
        self.assertFalse(self.target.exists())

    def test_existing_different_harness_file_aborts_without_partial_copy(self):
        (self.target / "harness").mkdir(parents=True)
        (self.target / "harness/core.md").write_text("my workflow\n")
        with self.assertRaisesRegex(ValueError, "harness/core.md"):
            installer.install(self.target)
        self.assertFalse((self.target / "docs").exists())
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_directory_named_like_file_aborts_before_copy(self):
        (self.target / "docs/README.md").mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "docs/README.md"):
            installer.install(self.target)
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_symlink_destination_is_rejected(self):
        self.target.mkdir()
        other = Path(self.temporary.name) / "outside"
        other.write_text("safe")
        (self.target / "AGENTS.md").symlink_to(other)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            installer.install(self.target, keep_agents=True)
        self.assertEqual(other.read_text(), "safe")


if __name__ == "__main__":
    unittest.main()
