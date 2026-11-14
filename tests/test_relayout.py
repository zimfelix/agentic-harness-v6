import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('relayout', ROOT / 'tools/relayout.py')
relayout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(relayout)
updater = relayout.updater
exporter = updater.exporter


class RelayoutTests(unittest.TestCase):
    """A flat v6 project (memory in the root) moves into harness/ with every reference intact."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.repo = self.root / 'repo'
        self.source = self.repo / 'harness'
        shutil.copytree(ROOT / 'harness', self.source)
        self.git(self.repo, 'init', '-q')
        self.git(self.repo, 'add', '-A')
        self.git(self.repo, 'commit', '-q', '-m', 'v1')
        project = exporter.export(self.root / 'project', self.source)
        for entry in (project / 'harness').iterdir():  # flatten: the layout before this change
            entry.rename(project / entry.name)
        (project / 'harness').rmdir()
        self.project = project
        self.write('AGENTS.md', self.read('AGENTS.md').replace('None yet.', '- Design: read `docs/design.md`.'))
        self.core = self.read('AGENTS.md').split('## Project rules')[0]
        self.write('PROJECT.md', '# Project\n\nSpec: [S1](specs/S1.md). Details in `docs/design.md`.\n')
        self.write('specs/S1.md', 'Code: [app](../src/app.py). Brief: `PROJECT.md`.\n')
        self.write('docs/design.md', 'Back to ../PROJECT.md; see https://example.org/docs/a and [x](https://a.test/specs/).\n')
        self.head = self.read('learnings.md')
        self.write('learnings.md', self.head + '\n## 2026-11-15 · Doc path · offen\n- **Beleg:** `docs/design.md`\n')
        self.write('src/app.py', '# Rules: docs/design.md; unrelated: mydocs/x and src/docs/\nVALUE = 1\n')
        self.write('README.md', 'Start with [the brief](PROJECT.md).\n')
        self.git(project, 'init', '-q')
        self.git(project, 'add', '-A')
        self.git(project, 'commit', '-q', '-m', 'flat')
        self.write('harness-update.md', 'untracked note\n')

    def git(self, where, *args):
        return subprocess.run(['git', '-C', str(where), '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
                              check=True, capture_output=True, text=True).stdout

    def read(self, rel):
        return (self.project / rel).read_text()

    def write(self, rel, text):
        (self.project / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.project / rel).write_text(text)

    def test_dry_run_writes_nothing(self):
        before = {p: p.read_bytes() for p in self.project.rglob('*') if p.is_file() and '.git' not in p.parts}
        result = relayout.plan(self.project)
        self.assertIn(('docs', 'harness/docs'), result['moves'])
        self.assertIn('outside Markdown (review): src/app.py', result['notes'])
        self.assertEqual({p: p.read_bytes() for p in self.project.rglob('*') if p.is_file() and '.git' not in p.parts},
                         before)

    def test_apply_moves_memory_and_keeps_references_valid(self):
        relayout.apply(self.project, relayout.plan(self.project))
        self.assertEqual(sorted(p.name for p in (self.project / 'harness').iterdir()),
                         ['PROJECT.md', 'docs', 'harness-update.md', 'ideas', 'learnings.md', 'specs'])
        for name in ('PROJECT.md', 'specs', 'docs', 'learnings.md'):
            self.assertFalse((self.project / name).exists(), name)
        agents = self.read('AGENTS.md')
        self.assertTrue(agents.startswith(self.core), 'harness part above the marker is left to update.py')
        self.assertIn('- Design: read `harness/docs/design.md`.', agents)
        self.assertEqual(self.read('harness/PROJECT.md'),
                         '# Project\n\nSpec: [S1](specs/S1.md). Details in `harness/docs/design.md`.\n')
        self.assertEqual(self.read('harness/specs/S1.md'),
                         'Code: [app](../../src/app.py). Brief: `harness/PROJECT.md`.\n')
        self.assertEqual(self.read('harness/docs/design.md'), 'Back to harness/PROJECT.md; see '
                         'https://example.org/docs/a and [x](https://a.test/specs/).\n')
        learnings = self.read('harness/learnings.md')
        self.assertTrue(learnings.startswith(self.head))
        self.assertIn('`harness/docs/design.md`', learnings)
        self.assertEqual(self.read('src/app.py'),
                         '# Rules: harness/docs/design.md; unrelated: mydocs/x and src/docs/\nVALUE = 1\n')
        self.assertEqual(self.read('README.md'), 'Start with [the brief](harness/PROJECT.md).\n')
        self.assertEqual(self.read('harness/harness-update.md'), 'untracked note\n')
        status = self.git(self.project, 'status', '--porcelain')
        self.assertIn('PROJECT.md -> harness/PROJECT.md', status)  # staged rename, rewrite unstaged
        self.assertEqual(updater.plan(self.project, self.source)['status'], 'current')

    def test_a_rewrite_that_would_break_links_stops_before_writing(self):
        before = {p: p.read_bytes() for p in self.project.rglob('*') if p.is_file() and '.git' not in p.parts}
        original = relayout._link
        relayout._link = lambda target, old_rel, new_rel: target  # simulated bug: links are not recomputed
        self.addCleanup(setattr, relayout, '_link', original)
        with self.assertRaisesRegex(ValueError, r'break links.*harness/specs/S1.md -> \.\./src/app.py'):
            relayout.plan(self.project)
        self.assertEqual({p: p.read_bytes() for p in self.project.rglob('*') if p.is_file() and '.git' not in p.parts},
                         before)

    def test_refuses_unsafe_starts(self):
        self.write('PROJECT.md', self.read('PROJECT.md') + 'uncommitted\n')
        with self.assertRaisesRegex(ValueError, 'uncommitted'):
            relayout.plan(self.project)
        self.git(self.project, 'checkout', '--', 'PROJECT.md')
        (self.project / 'harness').mkdir()
        with self.assertRaisesRegex(ValueError, 'already exists'):
            relayout.plan(self.project)
        (self.project / 'harness').rmdir()
        self.write('AGENTS.md', '# Old harness\n')
        self.git(self.project, 'commit', '-qam', 'old')
        with self.assertRaisesRegex(ValueError, 'marker'):
            relayout.plan(self.project)


if __name__ == '__main__':
    unittest.main()
