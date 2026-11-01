import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('updater', ROOT / 'tools/update.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)
exporter = updater.exporter


class UpdateTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.repo = self.root / 'repo'
        self.source = self.repo / 'harness'
        shutil.copytree(ROOT / 'harness', self.source)
        self.git('init', '-q')
        self.commit('v1')
        self.project = exporter.export(self.root / 'project', self.source)
        agents = self.project / 'AGENTS.md'
        agents.write_text(agents.read_text().replace('None yet.', '- Dictation: "Futter" means footer.'))
        (self.project / 'PROJECT.md').write_text('# Project\n\nGoal: real product facts.\n')
        (self.project / 'specs/S001-area.md').write_text('project spec\n')

    def git(self, *args):
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
                       check=True, capture_output=True)

    def commit(self, message):
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message)

    def change(self, rel, extra):
        path = self.source / rel
        path.write_text(path.read_text() + extra)

    def test_updates_universal_parts_and_keeps_project_content(self):
        self.change('AGENTS.md', '\nNew core rule.\n')
        self.change('specs/README.md', '\nNew spec guidance.\n')
        self.commit('v2')
        result = updater.plan(self.project, self.source)
        self.assertEqual(result['status'], 'update')
        updater.apply(self.project, result)
        agents = (self.project / 'AGENTS.md').read_text()
        self.assertIn('New core rule.', agents)
        self.assertIn('"Futter" means footer.', agents)
        self.assertIn('New spec guidance.', (self.project / 'specs/README.md').read_text())
        self.assertEqual((self.project / 'PROJECT.md').read_text(), '# Project\n\nGoal: real product facts.\n')
        self.assertEqual((self.project / 'specs/S001-area.md').read_text(), 'project spec\n')
        self.assertFalse((self.project / updater.NOTE).exists())
        self.assertEqual(updater.plan(self.project, self.source)['status'], 'current')

    def test_project_template_change_becomes_review_note(self):
        self.change('PROJECT.md', '\nNew template section.\n')
        self.commit('v2')
        result = updater.plan(self.project, self.source)
        updater.apply(self.project, result)
        self.assertEqual((self.project / 'PROJECT.md').read_text(), '# Project\n\nGoal: real product facts.\n')
        note = (self.project / updater.NOTE).read_text()
        self.assertIn('PROJECT.md: the template changed', note)
        self.assertIn('+New template section.', note)

    def test_locally_edited_core_or_readme_is_not_overwritten(self):
        (self.project / 'ideas/README.md').write_text('own ideas guidance\n')
        self.change('ideas/README.md', '\nNew ideas guidance.\n')
        self.commit('v2')
        result = updater.plan(self.project, self.source)
        updater.apply(self.project, result)
        self.assertEqual((self.project / 'ideas/README.md').read_text(), 'own ideas guidance\n')
        self.assertIn('ideas/README.md: changed locally', (self.project / updater.NOTE).read_text())

        agents = self.project / 'AGENTS.md'
        agents.write_text('Project rule above the marker.\n' + agents.read_text())
        before = agents.read_text()
        result = updater.plan(self.project, self.source)
        self.assertEqual(result['status'], 'conflict')
        self.assertEqual(result['writes'], {})
        self.assertEqual(agents.read_text(), before)

    def test_learnings_header_updates_and_entries_stay(self):
        learnings = self.project / 'learnings.md'
        entry = '## 2026-11-03 · SEO title breaks hero · offen\n- **Ziel:** skill:website-tools\n'
        learnings.write_text(learnings.read_text() + '\n' + entry)
        self.change('learnings.md', '')
        path = self.source / 'learnings.md'
        path.write_text(path.read_text().replace('# Learnings', '# Learnings\n\nNew header line.', 1))
        self.commit('v2')
        updater.apply(self.project, updater.plan(self.project, self.source))
        text = learnings.read_text()
        self.assertIn('New header line.', text)
        self.assertTrue(text.rstrip().endswith(entry.rstrip()))

        spec = importlib.util.spec_from_file_location('collector', ROOT / 'tools/learnings.py')
        collector = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(collector)
        learnings.write_text(text.replace('offen', 'verworfen').replace(
            entry.replace('offen', 'verworfen'), entry.replace('offen', 'verworfen') + '\n' + entry))
        self.assertEqual(len(collector.entries(learnings)), 1)
        self.assertEqual(len(collector.entries(learnings, include_all=True)), 2)
        self.assertEqual([p.resolve() for p in collector.projects([self.root])], [self.project.resolve()])

    def test_project_without_marker_is_left_alone(self):
        old = self.root / 'old'
        old.mkdir()
        (old / 'AGENTS.md').write_text('# Agentic Harness – Einstieg\n')
        self.assertEqual(updater.plan(old, self.source)['status'], 'no-marker')


if __name__ == '__main__':
    unittest.main()
