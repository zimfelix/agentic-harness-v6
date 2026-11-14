"""seo-pruefen.mjs at its public boundary: a built fixture site, the CLI exit code and its findings."""
import http.server
import json
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / 'harness/.agents/skills/website-tools/tools/seo-pruefen.mjs'
SITE = 'https://www.beispiel.de'
NAV = '<nav><a href="/">Start</a> <a href="/leistung/">Baumfällung</a> <a href="/kontakt/">Kontakt</a> <a href="/impressum/">Impressum</a></nav>'
FOOTER = '<footer>Musterweg 1, 12345 Musterstadt · Telefon 0123 456789</footer>'
BUSINESS = {'@context': 'https://schema.org', '@type': 'LocalBusiness', 'name': 'Muster Gartenbau',
            'telephone': '+49 123 456789',
            'address': {'@type': 'PostalAddress', 'streetAddress': 'Musterweg 1', 'postalCode': '12345', 'addressLocality': 'Musterstadt'},
            'openingHoursSpecification': [{'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Monday', 'Friday'], 'opens': '08:00', 'closes': '17:00'}]}


def page(route, title, body, head='', noindex=False, canonical=True):
    url = SITE + route
    desc = f'{title}: Ablauf, Kosten und Einsatzgebiet rund um Musterstadt, mit echten Beispielen aus der Region.'
    meta = '<meta name="robots" content="noindex">' if noindex else ''
    if canonical:
        meta += (f'<link rel="canonical" href="{url}"><meta property="og:url" content="{url}">'
                 f'<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">'
                 f'<meta property="og:image" content="{SITE}/og.png">')
    return (f'<!doctype html><html lang="de"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">{meta}<title>{title}</title>'
            f'<meta name="description" content="{desc}"><link rel="icon" href="/favicon.png">{head}</head>'
            f'<body>{NAV}<main><h1>{title}</h1>{body}</main>{FOOTER}</body></html>')


class SeoCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dist = self.root / 'dist'
        (self.root / 'website.config.mjs').write_text(
            f"export default {{ seo: {{ siteUrl: '{SITE}', pflichtLinks: ['/impressum/'] }} }};")
        jsonld = f'<script type="application/ld+json">{json.dumps(BUSINESS)}</script>'
        self.pages = {
            '/': page('/', 'Muster Gartenbau – Garten- und Baumarbeiten in Musterstadt', '<p>Gärten, Bäume und Pflege.</p>', jsonld),
            '/leistung/': page('/leistung/', 'Baumfällung in Musterstadt', '<p id="ablauf">Fällung mit Genehmigung und Entsorgung.</p>'),
            '/kontakt/': page('/kontakt/', 'Kontakt zu Muster Gartenbau', '<p>Ruf an oder schreib uns. <a href="/leistung/#ablauf">Ablauf der Baumfällung</a></p>'),
            '/impressum/': page('/impressum/', 'Impressum von Muster Gartenbau', '<p>Angaben nach § 5 DDG.</p>'),
            '/404.html': page('/404.html', 'Seite nicht gefunden', '<p>Zurück zur Startseite.</p>', noindex=True, canonical=False),
        }
        self.sitemap = ['/', '/leistung/', '/kontakt/', '/impressum/']
        self.robots = f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n'

    def write(self):
        for route, html in self.pages.items():
            name = 'index.html' if route == '/' else route.strip('/') if route.endswith('.html') else route.strip('/') + '/index.html'
            path = self.dist / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html)
        locs = ''.join(f'<url><loc>{SITE}{r}</loc></url>' for r in self.sitemap)
        (self.dist / 'sitemap.xml').write_text(f'<?xml version="1.0"?><urlset>{locs}</urlset>')
        (self.dist / 'robots.txt').write_text(self.robots)
        png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR' + (48).to_bytes(4, 'big') * 2 + b'\x08\x06\x00\x00\x00\x00\x00\x00\x00'
        (self.dist / 'favicon.png').write_bytes(png)

    def run_tool(self, *args):
        self.write()
        return subprocess.run(['node', str(TOOL), *args], cwd=self.root, capture_output=True, text=True, timeout=60)

    def assertFails(self, needle, *args):
        result = self.run_tool(*args)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(needle, result.stdout)

    def test_clean_site_passes(self):
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('❌', result.stdout)
        self.assertIn('4 indexierbar', result.stdout)

    def test_duplicate_title(self):
        self.pages['/kontakt/'] = self.pages['/kontakt/'].replace('Kontakt zu Muster Gartenbau', 'Baumfällung in Musterstadt')
        self.assertFails('gleicher Title')

    def test_canonical_must_be_self_referencing(self):
        self.pages['/leistung/'] = self.pages['/leistung/'].replace(f'rel="canonical" href="{SITE}/leistung/"', 'rel="canonical" href="https://beispiel.de/leistung/"')
        self.assertFails('canonical nicht selbstreferenzierend')

    def test_noindex_behind_disallow_is_never_seen(self):
        self.robots += 'Disallow: /404.html\n'
        self.assertFails('sieht das noindex nie')

    def test_sitemap_must_match_indexable_pages(self):
        self.sitemap.remove('/kontakt/')
        self.assertFails('fehlt in sitemap.xml')
        self.sitemap += ['/kontakt/', '/404.html']
        self.assertFails('noindex-Seite in sitemap.xml')

    def test_structured_data_rules(self):
        german = json.dumps(BUSINESS).replace('"Monday"', '"Montag"')
        self.pages['/'] = self.pages['/'].replace(json.dumps(BUSINESS), german)
        self.assertFails('dayOfWeek muss englisch sein')
        rated = dict(BUSINESS, aggregateRating={'@type': 'AggregateRating', 'ratingValue': '5', 'reviewCount': '12'})
        self.pages['/'] = self.pages['/'].replace(german, json.dumps(rated))
        self.assertFails('Bewertungen/Sterne')
        hidden = dict(BUSINESS, telephone='+49 999 888777')
        self.pages['/'] = self.pages['/'].replace(json.dumps(rated), json.dumps(hidden))
        self.assertFails('auf keiner Seite sichtbar')

    def test_business_subtypes_and_offered_services(self):
        offer = {'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': 'Baumfällung'}}
        electrician = dict(BUSINESS, **{'@type': 'Electrician', 'makesOffer': [offer]})
        self.pages['/'] = self.pages['/'].replace(json.dumps(BUSINESS), json.dumps(electrician))
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout)  # a Service offer needs no address
        rated = dict(electrician, aggregateRating={'@type': 'AggregateRating', 'ratingValue': '5', 'reviewCount': '3'})
        self.pages['/'] = self.pages['/'].replace(json.dumps(electrician), json.dumps(rated))
        self.assertFails('Bewertungen/Sterne')
        nameless = {k: v for k, v in electrician.items() if k != 'address'}
        self.pages['/'] = self.pages['/'].replace(json.dumps(rated), json.dumps(nameless))
        self.assertFails('Electrician-Markup ohne name oder address')

    def test_trailing_slash_never(self):
        (self.root / 'website.config.mjs').write_text(
            f"export default {{ seo: {{ siteUrl: '{SITE}', schraegstrich: 'nie', pflichtLinks: ['/impressum'] }} }};")
        self.pages = {(r.rstrip('/') or '/'): page(r.rstrip('/') or '/', t, '<p id="ablauf">Text zur Seite.</p>')
                      for r, t in [('/', 'Muster Gartenbau in Musterstadt'), ('/leistung/', 'Baumfällung in Musterstadt'),
                                   ('/kontakt/', 'Kontakt zu Muster Gartenbau'), ('/impressum/', 'Impressum von Muster Gartenbau')]}
        self.sitemap = ['/', '/leistung', '/kontakt', '/impressum']
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('nicht in kanonischer Form', result.stdout)  # the fixture nav still links with slashes

    def test_links_orphans_and_required_links(self):
        self.pages['/versteckt/'] = page('/versteckt/', 'Versteckte Seite ohne Link', '<p>Niemand verlinkt hierher.</p>')
        self.sitemap.append('/versteckt/')
        self.assertFails('verwaiste Seite')
        self.pages['/kontakt/'] = self.pages['/kontakt/'].replace('/leistung/#ablauf', '/leistung/#gibt-es-nicht')
        self.assertFails('Anker fehlt im Ziel')
        self.pages['/kontakt/'] = self.pages['/kontakt/'].replace('/leistung/#gibt-es-nicht', '/weg/')
        self.assertFails('toter interner Link')
        self.pages['/versteckt/'] = self.pages['/versteckt/'].replace('<a href="/impressum/">Impressum</a>', '')
        self.assertFails('Pflichtlink fehlt: /impressum/')

    def test_privacy_and_placeholders(self):
        fonts = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">'
        self.pages['/leistung/'] = self.pages['/leistung/'].replace('</head>', fonts + '</head>')
        self.assertFails('Google Fonts')
        mention = '<p>Wir laden keine Schriften von fonts.googleapis.com.</p>'
        self.pages['/leistung/'] = self.pages['/leistung/'].replace(fonts, '').replace('</main>', mention + '</main>')
        self.assertEqual(self.run_tool().returncode, 0)  # a privacy text may name the domain
        inline = "<style>@import url('https://fonts.googleapis.com/css2?family=Inter');</style>"
        self.pages['/leistung/'] = self.pages['/leistung/'].replace('</head>', inline + '</head>')
        self.assertFails('Google Fonts')
        self.pages['/leistung/'] = self.pages['/leistung/'].replace(inline, '').replace('Entsorgung.', 'Entsorgung. Lorem ipsum.')
        self.assertFails('Platzhalter im Text')

    def test_prototype_rests_until_go_live(self):
        for route in self.pages:
            self.pages[route] = page(route, route.strip('/') or 'Start', '<p>Entwurf.</p>', noindex=True, canonical=False)
        self.sitemap = []
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('Index-Regeln ruhen', result.stdout)
        self.assertFails('genau ein canonical im <head> nötig', '--livegang')
        self.assertIn('Seiten tragen noch noindex', self.run_tool('--livegang').stdout)  # info, not one error per page

    def serve(self, routes):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                status, headers, body = routes(self.path)
                self.send_response(status)
                for k, v in headers.items(): self.send_header(k, v)
                self.end_headers(); self.wfile.write(body.encode())
            def log_message(self, *args): pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        return f'http://127.0.0.1:{server.server_address[1]}/'

    def test_live_detects_soft_404_and_duplicate_index_url(self):
        base = self.serve(lambda path: (200, {}, '<html><body>immer da</body></html>'))
        result = self.run_tool('--live', base)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('Soft 404', result.stdout)
        self.assertIn('index.html liefert 200 ohne Weiterleitung', result.stdout)

    def test_live_accepts_permanent_redirects_and_flags_temporary(self):
        def routes(path, temporary=False):
            if path == '/sitemap.xml': return 200, {}, f'<urlset><url><loc>{base}</loc></url></urlset>'
            if path == '/': return 200, {}, 'ok'
            if path == '/index.html': return (307 if temporary else 301), {'Location': '/'}, ''
            if path.startswith('/seo-pruefen-'): return 404, {}, 'nicht gefunden'
            if not path.endswith('/') and '.' not in path: return 308, {'Location': path + '/'}, ''
            return 404, {}, 'nicht gefunden'
        base = self.serve(routes)
        result = self.run_tool('--live', base)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        base = self.serve(lambda path: routes(path, temporary=True))
        self.assertFails('vorübergehende Weiterleitung', '--live', base)

    def test_live_catches_production_noindex_and_blocking_robots(self):
        def routes(path):
            if path == '/': return 200, {}, '<html><head><meta name="robots" content="noindex"></head></html>'
            if path == '/robots.txt': return 200, {}, 'User-agent: *\nDisallow: /\n'
            return 404, {}, 'nicht gefunden'
        base = self.serve(routes)
        result = self.run_tool('--live', base)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('Startseite ist live noindex', result.stdout)
        self.assertIn('robots.txt sperrt die Startseite', result.stdout)


if __name__ == '__main__':
    unittest.main()
