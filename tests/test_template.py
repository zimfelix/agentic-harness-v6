import importlib.util
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'harness'
TOOLS = TEMPLATE / '.agents/skills/website-tools/tools'
spec = importlib.util.spec_from_file_location('exporter', ROOT / 'tools/export.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class TemplateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_export_is_pristine_and_scoped(self):
        target = exporter.export(self.root / 'product')
        self.assertEqual((target / 'PROJECT.md').read_bytes(), (TEMPLATE / 'PROJECT.md').read_bytes())
        for name in ('benchmarks', 'reports', 'tests', '.git', '.private', '.agents', '.claude'):
            self.assertFalse((target / name).exists())

    def test_brief_and_continuation_contract_is_exported(self):
        target = exporter.export(self.root / 'continuation')
        markers = {
            'AGENTS.md': (
                'briefly restate the intended outcome, main workflow and boundaries',
                'before binding specs or substantial code',
                "don't ask again for supplied/delegated decisions",
                'visible/background execution mode',
                'next authorized action or genuine blocker',
                'match it against actual git/code state',
            ),
            'PROJECT.md': (
                'main workflow',
                'input sources, provider-owned functions and project-owned actions',
                'ONE active work record',
            ),
            'specs/README.md': (
                'next authorized implementation action',
                'not only a regression command',
                'real decision/blocker',
            ),
        }
        for filename, required in markers.items():
            text = (target / filename).read_text()
            template = (TEMPLATE / filename).read_text()
            if filename == 'AGENTS.md':
                self.assertTrue(text.startswith(template.rstrip('\n')))
                self.assertRegex(text, r'<!-- harness-v6@([0-9a-f]+|local) ')
            else:
                self.assertEqual(text, template)
            for marker in required:
                self.assertIn(marker, text, (filename, marker))
        # These checks preserve instruction/export content, not prove that an LLM follows it.
        self.assertFalse((target / 'INIT.md').exists())
        self.assertFalse((target / 'profiles').exists())

    def test_claude_alias_has_single_source_and_no_rule_copy(self):
        target = exporter.export(self.root / 'both-clients', with_skills=True)
        skill = target / '.agents/skills/website-tools'
        alias = target / '.claude/skills/website-tools'
        self.assertTrue(alias.is_symlink())
        self.assertEqual(alias.resolve(), skill.resolve())
        self.assertTrue(alias.resolve().is_relative_to(target.resolve()))
        self.assertEqual((alias / 'SKILL.md').read_bytes(), (skill / 'SKILL.md').read_bytes())
        self.assertFalse((target / 'CLAUDE.md').exists())
        self.assertEqual(list((target / '.claude').iterdir()), [target / '.claude/skills'])
        self.assertEqual((target / '.claude/skills/business-software').resolve(),
                         (target / '.agents/skills/business-software').resolve())

    def test_launcher_loads_current_agents_without_copy(self):
        spec = importlib.util.spec_from_file_location('launcher', ROOT / 'tools/launch.py')
        launcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher)
        target = exporter.export(self.root / 'launch')
        self.assertEqual(launcher.command(target, 'pi', ['--model', 'gpt-6.1-sol']), ['pi', '--model', 'gpt-6.1-sol'])
        cmd = launcher.command(target, 'claude')
        self.assertEqual(cmd[:2], ['claude', '--append-system-prompt'])
        self.assertEqual(cmd[2], (target / 'AGENTS.md').read_text())
        (target / 'AGENTS.md').write_text('Updated instructions')
        self.assertEqual(launcher.command(target, 'claude')[2], 'Updated instructions')
        with self.assertRaises(ValueError):
            launcher.command(target, 'other-client')
        with self.assertRaises(ValueError):
            launcher.command(self.root / 'missing', 'pi')

    def test_existing_product_untouched(self):
        target = self.root / 'product'
        target.mkdir()
        (target / 'keep').write_text('unchanged')
        with self.assertRaises(ValueError):
            exporter.export(target)
        self.assertEqual([p.name for p in target.iterdir()], ['keep'])
        self.assertEqual((target / 'keep').read_text(), 'unchanged')

    def test_overlap_and_symlinks_rejected(self):
        for target in (TEMPLATE, TEMPLATE.parent, TEMPLATE / 'child'):
            with self.assertRaises(ValueError):
                exporter.export(target)
        source = self.root / 'source'
        shutil.copytree(TEMPLATE, source)
        (source / 'escape').symlink_to('/tmp')
        with self.assertRaises(ValueError):
            exporter.export(self.root / 'target', source)
        self.assertFalse((self.root / 'target').exists())

    def test_empty_target_and_missing_source(self):
        target = self.root / 'empty'
        target.mkdir()
        exporter.export(target)
        self.assertTrue((target / 'AGENTS.md').exists())
        with self.assertRaises(ValueError):
            exporter.export(self.root / 'bad', self.root / 'absent')
        self.assertFalse((self.root / 'bad').exists())

    def test_markdown_links_and_tool_imports(self):
        for path in TEMPLATE.rglob('*.md'):
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent / target.split('#')[0]).exists(), (path, target))
        for path in TOOLS.glob('*.mjs'):
            text = path.read_text()
            for target in re.findall(r"from ['\"](\.[^'\"]+)['\"]", text) + re.findall(r"new URL\(['\"](\.[^'\"]+)['\"], import.meta.url\)", text):
                self.assertTrue((path.parent / target).exists(), (path, target))
            result = subprocess.run(['node', '--check', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_native_skill_single_source(self):
        skills = list(TEMPLATE.rglob('SKILL.md'))
        self.assertEqual({s.parent.name for s in skills}, {'website-tools', 'business-software', 'testing'})
        for skill in skills:
            self.assertIn('name: ' + skill.parent.name, skill.read_text())
            self.assertIn('description:', skill.read_text())
        self.assertFalse((TEMPLATE / 'profiles').exists())
        images = [p for p in TEMPLATE.rglob('*') if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}]
        self.assertEqual(images, [], 'skills must stay project-neutral: no example designs or screenshots')
        self.assertLess(len((TEMPLATE / 'AGENTS.md').read_text()) + len((TEMPLATE / 'PROJECT.md').read_text()), 6000)

    def test_consolidation_preserves_risk_rules_and_website_requirements(self):
        business = (TEMPLATE / '.agents/skills/business-software/SKILL.md').read_text().split('---', 2)[2].strip()
        expected = (ROOT / 'tests/business-routing-expected.md').read_text().strip()
        self.assertEqual(business, expected)
        website = (TEMPLATE / '.agents/skills/website-tools/SKILL.md').read_text().split('---', 2)[2].strip()
        expected = (ROOT / 'tests/website-routing-expected.md').read_text().strip()
        website = website.replace('# Website work', '# Website profile').replace(
            'read `references/tooling.md` only when using or setting up those tools.',
            'load `../../.agents/skills/website-tools/SKILL.md`.')
        self.assertEqual(website, expected)
        for skill in (TEMPLATE / '.agents/skills').iterdir():
            for target in re.findall(r'`(references/[^`]+\\.md)`', (skill / 'SKILL.md').read_text()):
                self.assertTrue((skill / target).is_file(), target)
        agents = (TEMPLATE / 'AGENTS.md').read_text()
        self.assertNotIn('profiles/', agents)
        for name in ('business-software', 'website-tools', 'testing'):
            self.assertIn(f'`{name}` skill', agents)

    def tool(self, name, *args):
        return subprocess.run(['node', str(TOOLS / name), *map(str, args)], cwd=self.root,
                              capture_output=True, text=True, timeout=15)

    def test_screen_comparison_is_nonempty_symmetric(self):
        a, b = self.root / 'a', self.root / 'b'
        a.mkdir(); b.mkdir()
        self.assertNotEqual(self.tool('screens.mjs', '--compare', a, b).returncode, 0)
        for d in (a, b): (d / 'one.png').write_bytes(b'fixture')
        self.assertEqual(self.tool('screens.mjs', '--compare', a, b).returncode, 0)
        (a / 'two.png').write_bytes(b'new')
        for left, right in ((a, b), (b, a)):
            self.assertNotEqual(self.tool('screens.mjs', '--compare', left, right).returncode, 0)

    def test_style_comparison_and_empty_routes(self):
        a, b = self.root / 'a.json', self.root / 'b.json'
        for l, r, ok in [('{}', '{}', False), ('{"x":["a"]}', '{"x":["a"]}', True),
                          ('{"x":["a"]}', '{"x":["b"]}', False),
                          ('{"x":["a"]}', '{"x":["a"],"y":["b"]}', False)]:
            a.write_text(l); b.write_text(r)
            self.assertEqual(self.tool('style-snapshot.mjs', '--compare', a, b).returncode == 0, ok)
        empty = self.root / 'empty'; empty.mkdir()
        result = self.tool('pruefen.mjs', empty)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Keine statischen Prüfrouten', result.stderr)


if __name__ == '__main__':
    unittest.main()
