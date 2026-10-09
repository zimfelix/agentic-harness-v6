"""Repository-only regression tests. Not exported into product projects."""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[2] / 'agentic-harness'
spec = importlib.util.spec_from_file_location('checker', SOURCE / 'tools/check-harness.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'
        shutil.copytree(SOURCE, self.project)

    def run_tool(self, tool, *args, env=None):
        return subprocess.run(['node', str(SOURCE / 'profiles/website/tools' / tool), *map(str, args)],
                              cwd=self.project, env={**os.environ, **(env or {})}, capture_output=True,
                              text=True, timeout=20)

    def fill(self, profiles='website'):
        path = self.project / 'harness/project.md'
        text = path.read_text()
        for name in checker.FIELDS:
            import re
            text = re.sub(r'^- \*\*' + re.escape(name) + r':\*\* .+$', f'- **{name}:** bestätigt: Testwert', text, flags=re.M)
        text = text.replace(checker.field(text, 'Profile'), profiles)
        path.write_text(text)
        for name in checker.DOCS:
            p = self.project / f'docs/{name}.md'
            p.write_text(p.read_text().replace('Noch offen (Project Init).', 'Konkreter Testaufbau.'))
        return path

    def test_structure_and_copy(self):
        self.assertEqual(checker.check(), [])
        self.assertEqual(checker.check(self.project), [])

    def test_export_reset_and_new_references(self):
        dst = self.root / 'export'
        p = subprocess.run(['sh', str(SOURCE / 'tools/export-harness.sh'), str(dst)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(checker.check(dst), [])
        self.assertTrue(checker.check(dst, ready=True))
        source_rules = (SOURCE / 'harness-learnings.md').read_text().partition('## Aktive Learnings')[0]
        exported_rules, marker, entries = (dst / 'harness-learnings.md').read_text().partition('## Aktive Learnings')
        self.assertTrue(marker)
        self.assertEqual(exported_rules, source_rules)  # context/weekly-review rules survive
        self.assertEqual(entries.strip(), '### Offen\n\nKeine.\n\n### Lokal übernommen\n\nKeine.')
        self.assertNotEqual((dst / 'README.md').read_text(), (SOURCE.parent / 'README.md').read_text())
        self.assertTrue((dst / 'README.md').read_text().startswith('# Agentic Harness'))
        self.assertTrue((dst / 'profiles/business-software/references/importe-und-jobs.md').exists())
        self.assertFalse((dst / 'tests').exists())

    def test_export_rejects_nonempty_product_without_changes(self):
        dst = self.root / 'product'
        dst.mkdir()
        (dst / 'keep.txt').write_text('preserve')
        p = subprocess.run(['sh', str(SOURCE / 'tools/export-harness.sh'), str(dst)], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(list(dst.iterdir()), [dst / 'keep.txt'])
        self.assertEqual((dst / 'keep.txt').read_text(), 'preserve')

    def test_pending_fields_rejected(self):
        self.assertTrue(checker.check(self.project, ready=True))
        self.assertTrue(checker.check(self.project, go=True))

    def test_ready_before_go_then_recorded_go(self):
        path = self.fill()
        self.assertEqual(checker.check(self.project, ready=True), [])
        self.assertTrue(checker.check(self.project, go=True))
        text = path.read_text().replace('**Status:** Pending Project Init', '**Status:** Init abgeschlossen')
        import re
        text = re.sub(r'^- \*\*Init-Go:\*\* .+$', '- **Init-Go:** bestätigt: Bauvoraussetzungen geprüft, keine blockierenden Lücken', text, flags=re.M)
        path.write_text(text)
        self.assertEqual(checker.check(self.project, go=True), [])

    def test_go_rejects_missing_or_ambiguous_authorization(self):
        path = self.fill()
        text = path.read_text().replace('**Status:** Pending Project Init', '**Status:** Init abgeschlossen')
        import re
        for value in ['offen', 'noch nicht erteilt', 'keine Freigabe', 'ausstehend']:
            path.write_text(re.sub(r'^- \*\*Init-Go:\*\* .+$', '- **Init-Go:** ' + value, text, flags=re.M))
            self.assertTrue(checker.check(self.project, go=True), value)
        path.write_text(text + '\n**Status:** Init abgeschlossen\n')
        self.assertTrue(checker.check(self.project, go=True))

    def test_unknown_profile_rejected(self):
        self.fill('imaginary-profile')
        self.assertTrue(checker.check(self.project, ready=True))

    def test_business_areas_from_single_source(self):
        areas = ['Fachmodell', 'Daten und Migrationen', 'Importe und Jobs', 'Geld', 'Zeit',
                 'Rechte und Mandanten', 'Personendaten', 'Seiteneffekte', 'Buchhaltung']
        valid = 'business-software: Fachmodell; abgewählt: ' + ', '.join(a + ' (Testgrund)' for a in areas[1:])
        self.assertEqual(checker.profile_errors(self.project, valid), [])
        self.assertEqual(checker.profile_errors(self.project, valid + ' | website'), [])
        for invalid in ['business-software: Idempotenz', 'business-software: Fachmodell',
                        valid.replace('Geld (Testgrund)', 'Geld'), valid + ', Fachmodell (doch nicht)',
                        'website | website', 'keine', 'keine (offen)']:
            self.assertTrue(checker.profile_errors(self.project, invalid), invalid)
        self.assertEqual(checker.profile_errors(self.project, 'keine (reine Bibliothek ohne passendes Profil)'), [])

    def test_vendor_markdown_not_scanned(self):
        p = self.project / 'node_modules/fake/README.md'
        p.parent.mkdir(parents=True)
        p.write_text('[broken](missing.md)')
        self.assertEqual(checker.check(self.project), [])

    def test_broken_reference_detected(self):
        (self.project / 'profiles/business-software/references/importe-und-jobs.md').unlink()
        self.assertTrue(checker.check(self.project))

    def test_empty_and_symmetric_screens(self):
        a, b = self.root / 'a', self.root / 'b'
        a.mkdir(); b.mkdir()
        self.assertNotEqual(self.run_tool('screens.mjs', '--compare', a, b).returncode, 0)
        (a / 'a.png').write_bytes(b'fixture')
        (b / 'a.png').write_bytes(b'fixture')
        self.assertEqual(self.run_tool('screens.mjs', '--compare', a, b).returncode, 0)
        (b / 'extra.png').write_bytes(b'new')
        for x, y in [(a, b), (b, a)]:
            self.assertNotEqual(self.run_tool('screens.mjs', '--compare', x, y).returncode, 0)
        (b / 'extra.png').unlink()
        (b / 'a.png').write_bytes(b'changed')
        self.assertNotEqual(self.run_tool('screens.mjs', '--compare', a, b).returncode, 0)
        (b / 'a.png').write_bytes(b'')
        self.assertNotEqual(self.run_tool('screens.mjs', '--compare', a, b).returncode, 0)

    def test_style_empty_invalid_added_and_changed(self):
        a, b = self.root / 'a.json', self.root / 'b.json'
        for left, right, success in [('{}', '{}', False), ('[]', '{}', False),
                                      ('{"x":[]}', '{"x":[]}', False),
                                      ('{"x":["a"]}', '{"x":["a"]}', True),
                                      ('{"x":["a"]}', '{"x":["b"]}', False),
                                      ('{"x":["a"]}', '{"x":["a"],"y":["b"]}', False),
                                      ('{"x":["a"],"y":["b"]}', '{"x":["a"]}', False)]:
            a.write_text(left); b.write_text(right)
            self.assertEqual(self.run_tool('style-snapshot.mjs', '--compare', a, b).returncode == 0, success)

    def test_empty_route_tools_fail_before_browser(self):
        empty = self.root / 'empty'
        empty.mkdir()
        for tool, args in [('pruefen.mjs', [empty]), ('screens.mjs', [self.root / 'shots', empty]),
                           ('style-snapshot.mjs', [self.root / 'styles.json', empty])]:
            p = self.run_tool(tool, *args, env={'BRAVE_PATH': '/missing'})
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('Keine statischen Prüfrouten', p.stderr)
            self.assertNotIn('Browser: Brave', p.stdout)

    def test_route_discovery_normalizes_root_and_internal_dirs(self):
        dist = self.project / 'dist'
        (dist / 'about').mkdir(parents=True)
        (dist / '_geraete').mkdir()
        for folder in [dist, dist / 'about', dist / '_geraete']:
            (folder / 'index.html').write_text('<h1>Fixture</h1>')
        (self.project / 'website.config.mjs').write_text("export default {interneOrdner:['_geraete']};")
        script = f'import {{routesIn}} from {str((SOURCE / "profiles/website/tools/browser.mjs").as_uri())!r}; console.log(JSON.stringify(await routesIn(process.argv[1])));'
        for root in [str(dist), str(dist) + '/', 'dist/']:
            p = subprocess.run(['node', '--input-type=module', '-e', script, root], cwd=self.project, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(p.stdout.strip(), '["/","/about/"]')

    def test_declared_routes_and_widths(self):
        dist = self.project / 'dist'
        dist.mkdir(); (dist / 'index.html').write_text('<h1>Probe</h1>')
        for config in ["export default {routen:['/missing/']};", "export default {breiten:[]};"]:
            (self.project / 'website.config.mjs').write_text(config)
            p = self.run_tool('pruefen.mjs')
            self.assertNotEqual(p.returncode, 0)
            self.assertNotIn('Browser: Brave', p.stdout)

    def test_no_chrome_fallback(self):
        # Need a real route to reach browser validation.
        (self.project / 'index.html').write_text('<h1>Probe</h1>')
        p = self.run_tool('pruefen.mjs', self.project, env={'BRAVE_PATH': sys.executable})
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('Nicht als Brave verifizierter Browserpfad', p.stderr)


if __name__ == '__main__':
    unittest.main()
