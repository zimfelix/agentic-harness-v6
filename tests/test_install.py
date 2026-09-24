"""Installer tests for bundling and integrating the harness without clobbering projects."""

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

    def test_new_project_gets_single_bundle_and_root_agent_entry(self):
        actions = installer.install(self.target)
        self.assertEqual(actions, ["ADD  agentic-harness/", "ADD  AGENTS.md"])
        bundle = self.target / "agentic-harness"
        source_bundle = installer.SOURCE
        source_files = {p.relative_to(source_bundle) for p in source_bundle.rglob("*") if p.is_file()}
        installed_files = {p.relative_to(bundle) for p in bundle.rglob("*") if p.is_file()}
        self.assertEqual(installed_files, source_files)
        for relative in source_files:
            self.assertEqual((bundle / relative).read_bytes(), (source_bundle / relative).read_bytes())
        self.assertTrue((bundle / "harness/core.md").is_file())
        self.assertTrue((bundle / "docs/README.md").is_file())
        self.assertTrue((bundle / "ideas/README.md").is_file())
        self.assertTrue((bundle / "specs/README.md").is_file())
        self.assertIn("Pending Project Init", (bundle / "harness/project.md").read_text())
        agents = (self.target / "AGENTS.md").read_text()
        self.assertIn(installer.BLOCK, agents)
        self.assertFalse((self.target / "README.md").exists())
        for excluded in ("scripts/install.py", "tests/test_install.py", ".git", "main.py"):
            self.assertFalse((self.target / excluded).exists(), excluded)

    def test_existing_project_rules_and_readme_are_preserved_and_entry_appended(self):
        self.target.mkdir()
        original = "# Existing project rules\n\nKeep these rules.\n"
        (self.target / "AGENTS.md").write_text(original)
        (self.target / "README.md").write_text("Product README\n")
        actions = installer.install(self.target)
        self.assertEqual(actions, ["ADD  agentic-harness/", "UPDATE  AGENTS.md"])
        agents = (self.target / "AGENTS.md").read_text()
        self.assertTrue(agents.startswith(original))
        self.assertEqual(agents.count(installer.START), 1)
        self.assertEqual((self.target / "README.md").read_text(), "Product README\n")

    def test_repeat_install_is_idempotent(self):
        installer.install(self.target)
        self.assertEqual(installer.install(self.target), ["SAME  agentic-harness/", "SAME  AGENTS.md"])
        self.assertEqual((self.target / "AGENTS.md").read_text().count(installer.START), 1)

    def test_dry_run_does_not_create_target_or_write(self):
        actions = installer.install(self.target, dry_run=True)
        self.assertEqual(actions, ["ADD  agentic-harness/", "ADD  AGENTS.md"])
        self.assertFalse(self.target.exists())

    def test_conflicting_bundle_aborts_without_modifying_agents(self):
        self.target.mkdir()
        (self.target / "agentic-harness").mkdir()
        (self.target / "agentic-harness/own-file.md").write_text("local")
        (self.target / "AGENTS.md").write_text("Original\n")
        with self.assertRaisesRegex(ValueError, "already exists and differs"):
            installer.install(self.target)
        self.assertEqual((self.target / "AGENTS.md").read_text(), "Original\n")

    def test_different_managed_section_aborts(self):
        self.target.mkdir()
        bad_block = f"{installer.START}\nwrong instructions\n{installer.END}\n"
        (self.target / "AGENTS.md").write_text("Existing\n" + bad_block)
        with self.assertRaisesRegex(ValueError, "different managed Harness section"):
            installer.install(self.target)
        self.assertFalse((self.target / "agentic-harness").exists())

    def test_malformed_markers_abort_before_copy(self):
        self.target.mkdir()
        (self.target / "AGENTS.md").write_text(installer.START + "\nunfinished\n")
        with self.assertRaisesRegex(ValueError, "Malformed"):
            installer.install(self.target)
        self.assertFalse((self.target / "agentic-harness").exists())

    def test_symlink_agents_is_rejected(self):
        self.target.mkdir()
        other = Path(self.temporary.name) / "outside"
        other.write_text("safe")
        (self.target / "AGENTS.md").symlink_to(other)
        with self.assertRaisesRegex(ValueError, "symlink"):
            installer.install(self.target)
        self.assertEqual(other.read_text(), "safe")
        self.assertFalse((self.target / "agentic-harness").exists())

    def test_non_directory_target_is_rejected(self):
        self.target.parent.mkdir(exist_ok=True)
        self.target.write_text("not a directory")
        with self.assertRaisesRegex(ValueError, "not a normal directory"):
            installer.install(self.target)


if __name__ == "__main__":
    unittest.main()
