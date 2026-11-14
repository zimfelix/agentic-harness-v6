"""The website starter at its public boundary: copied like at project start, built, audited by seo-pruefen.mjs."""
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / 'harness/.agents/skills/website-tools'
STARTER = SKILL / 'assets/starter'
SEO = SKILL / 'tools/seo-pruefen.mjs'

SAMPLE = """
const firma = {
  name: 'Muster Dachbau', typ: 'RoofingContractor', beschreibung: 'Dachdecker-Meisterbetrieb in Musterstadt seit 1998.',
  telefon: '+49 351 123456', telefonAnzeige: '0351 123456', email: 'info@beispiel.de',
  adresse: { strasse: 'Musterweg 1', plz: '01234', ort: 'Musterstadt', land: 'DE' },
  oeffnungszeiten: [{ tage: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], von: '07:00', bis: '16:00' }],
  einsatzgebiet: ['Musterstadt', 'Nachbarort'], sameAs: [],
};
const leistung = (name, kurz, einleitung) => ({
  route: `/leistungen/${name}/`, vorlage: 'leistung', kurz, title: `${kurz} in Musterstadt – ${firma.name}`, h1: `${kurz} in Musterstadt`,
  description: `${kurz} vom Meisterbetrieb in Musterstadt: Ablauf, Dauer, Preise und Referenzen aus der Region.`,
  absicht: `${kurz} Musterstadt`, beleg: 'Fotos und Daten echter Aufträge 2025', geaendert: '2026-10-01',
  inhalt: { einleitung, punkte: ['Begehung vor Ort', 'Festpreisangebot'], ablauf: ['Termin', 'Angebot', 'Ausführung'], preis: 'ab 90 € je m² inkl. MwSt.' },
});
export default {
  siteUrl: 'https://www.beispiel.de', sprache: 'de', locale: 'de_DE', farbe: '#7a3e2b', ogBild: '/og.jpg', kiCrawler: 'nurSuche',
  firma,
  navigation: [{ text: 'Leistungen', href: '/#leistungen' }, { text: 'Kontakt', href: '/#kontakt' }],
  seiten: [
    { route: '/', vorlage: 'start', kurz: 'Start', title: `Dachdecker in Musterstadt – ${firma.name}`, h1: 'Dachdecker in Musterstadt',
      description: 'Dachsanierung, Reparatur und Dachfenster vom Meisterbetrieb in Musterstadt, mit Festpreis und eigenem Team.',
      absicht: 'Dachdecker Musterstadt', beleg: 'Meisterbrief, 30 Referenzen', geaendert: '2026-10-02',
      inhalt: { einleitung: 'Wir sanieren und reparieren Dächer in Musterstadt.', kontakt: 'Wir melden uns innerhalb eines Werktags.',
                nachweise: [{ text: 'Neues Dach in Nachbarort', quelle: 'eigenes Projekt', datum: '2025-09' }] } },
    leistung('dachsanierung', 'Dachsanierung', 'Komplette Sanierung von Steil- und Flachdächern.'),
    leistung('dachreparatur', 'Dachreparatur', 'Schnelle Reparatur nach Sturm und bei Undichtigkeit.'),
    { route: '/impressum/', art: 'recht', vorlage: 'recht', kurz: 'Impressum', title: `Impressum – ${firma.name}`, h1: 'Impressum',
      description: `Impressum von ${firma.name}: Anbieter, Anschrift, Kontakt und Handwerkskammer.`, datei: 'recht/impressum.html' },
    { route: '/datenschutz/', art: 'recht', vorlage: 'recht', kurz: 'Datenschutz', title: `Datenschutzerklärung – ${firma.name}`,
      h1: 'Datenschutzerklärung', description: `Datenschutzerklärung von ${firma.name}: welche Daten diese Website verarbeitet.`,
      datei: 'recht/datenschutz.html' },
    { route: '/404.html', art: 'sonder', vorlage: 'fehler', title: `Seite nicht gefunden – ${firma.name}`, h1: 'Seite nicht gefunden' },
  ],
};
"""


class StarterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name) / 'site'
        self.site.mkdir()
        # the documented copy command at project start (portable: BSD and GNU cp)
        subprocess.run(['cp', '-Rn', f'{STARTER}/.', str(self.site)], check=True)

    def sample(self, config=SAMPLE):
        (self.site / 'src/site.config.mjs').write_text(config)
        (self.site / 'src/static').mkdir(exist_ok=True)
        (self.site / 'src/static/og.jpg').write_bytes(b'\xff\xd8\xff')  # stands in for the share image
        legal = self.site / 'src/recht'
        legal.mkdir(exist_ok=True)
        (legal / 'impressum.html').write_text('<p>Muster Dachbau, Musterweg 1, 01234 Musterstadt. Angaben nach § 5 DDG.</p>')
        (legal / 'datenschutz.html').write_text('<p>Diese Website setzt keine Cookies und lädt nichts von Dritten.</p>')

    def node(self, *args):
        return subprocess.run(['node', *map(str, args)], cwd=self.site, capture_output=True, text=True, timeout=60)

    def build(self, *args):
        return self.node('scripts/build.mjs', *args)

    def check(self, *args):
        return self.node(SEO, *args)

    def pages(self):
        return {p.relative_to(self.site / 'dist').as_posix(): p.read_text() for p in (self.site / 'dist').rglob('*.html')}

    def assertOk(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('❌', result.stdout)

    def test_shipped_starter_is_a_marked_draft(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Vor dem Livegang offen', result.stdout)
        self.assertOk(self.check())
        self.assertIn('Index-Regeln ruhen', self.check().stdout)
        livegang = self.check('--livegang')
        self.assertEqual(livegang.returncode, 1, livegang.stdout)
        self.assertIn('Platzhalter im Text', livegang.stdout)
        production = self.build('--produktion')
        self.assertEqual(production.returncode, 1, production.stdout)
        self.assertIn('Produktions-Build gesperrt', production.stderr)
        self.assertIn('Beispieladresse', production.stderr)

    def test_sample_site_passes_in_both_environments(self):
        self.sample()
        self.assertEqual(self.build().returncode, 0)
        for name, html in self.pages().items():
            self.assertIn('<meta name="robots" content="noindex">', html, name)
        self.assertOk(self.check())
        self.assertOk(self.check('--livegang'))
        self.assertIn('Seiten tragen noch noindex', self.check('--livegang').stdout)

        production = self.build('--produktion')
        self.assertEqual(production.returncode, 0, production.stderr)
        for name, html in self.pages().items():
            self.assertEqual('content="noindex"' in html, name == '404.html', name)
        result = self.check()
        self.assertOk(result)
        self.assertIn('5 indexierbar', result.stdout)
        robots = (self.site / 'dist/robots.txt').read_text()
        self.assertRegex(robots, r'User-agent: GPTBot\n(User-agent: .+\n)*Disallow: /\n')

    def test_placeholder_blocks_go_live(self):
        self.sample(SAMPLE.replace("'Schnelle Reparatur nach Sturm und bei Undichtigkeit.'", "''"))
        self.assertEqual(self.build().returncode, 0)
        self.assertOk(self.check())  # drafts may carry marked placeholders
        livegang = self.check('--livegang')
        self.assertEqual(livegang.returncode, 1, livegang.stdout)
        self.assertRegex(livegang.stdout, r'/leistungen/dachreparatur/: Platzhalter im Text')
        production = self.build('--produktion')
        self.assertEqual(production.returncode, 1, production.stdout)
        self.assertIn('/leistungen/dachreparatur/: Platzhalter', production.stderr)

    def test_starter_own_tests_and_imports(self):
        for config in (None, SAMPLE):
            if config:
                self.sample(config)
            result = self.node('--test', 'scripts/build.test.mjs')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for path in STARTER.rglob('*.mjs'):
            for target in re.findall(r"from ['\"](\.[^'\"]+)['\"]", path.read_text()):
                self.assertTrue((path.parent / target).exists(), (path, target))
            self.assertEqual(subprocess.run(['node', '--check', str(path)], capture_output=True).returncode, 0, path)


if __name__ == '__main__':
    unittest.main()
