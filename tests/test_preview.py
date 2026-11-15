"""HTTP/build regressions plus opt-in real Brave integration tests."""
import concurrent.futures
import json
import os
import socket
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / 'harness/.agents/skills/website-tools/tools'


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'public').mkdir()
        (self.root / 'public/index.html').write_text('<h1>Alpha</h1>')
        (self.root / 'build.mjs').write_text('''import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
const content=readFileSync('public/index.html','utf8');
if(content.includes('FAIL')) throw new Error('intentional build failure');
mkdirSync('dist',{recursive:true}); writeFileSync('dist/index.html',content);
const count=existsSync('count.txt')?Number(readFileSync('count.txt','utf8')):0;
writeFileSync('count.txt',String(count+1));''')
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0)); self.port = s.getsockname()[1]
        (self.root / 'website.config.mjs').write_text(f"export default {{port:{self.port},quelle:'public',build:['node','build.mjs']}};")

    def start_server(self):
        log = (self.root / 'server.log').open('w')
        self.addCleanup(log.close)
        p = subprocess.Popen(['node', str(TOOLS / 'serve.mjs')], cwd=self.root, stdout=log, stderr=log)
        def stop():
            p.terminate()
            try: p.wait(timeout=5)
            except subprocess.TimeoutExpired: p.kill(); p.wait()
        self.addCleanup(stop)
        for _ in range(50):
            try:
                self.fetch('/_geraete/stand'); return
            except (OSError, urllib.error.URLError): time.sleep(.1)
        self.fail('preview did not start: ' + (self.root / 'server.log').read_text())

    def fetch(self, path):
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{self.port}{path}', timeout=5) as res:
                return res.status, res.read().decode()
        except urllib.error.HTTPError as res:
            with res: return res.code, res.read().decode()

    def test_stale_build_is_not_current_and_recovery(self):
        self.start_server()
        status, body = self.fetch('/')
        self.assertEqual(status, 200); self.assertIn('Alpha', body)
        with urllib.request.urlopen(f'http://127.0.0.1:{self.port}/', timeout=5) as response:
            self.assertEqual(response.headers.get('Cache-Control'), 'no-store')
        first = json.loads(self.fetch('/_geraete/stand')[1])
        self.assertTrue(first['aktuell'])
        (self.root / 'public/index.html').write_text('FAIL')
        status, body = self.fetch('/')
        self.assertEqual(status, 503); self.assertNotIn('Alpha', body)
        status, raw = self.fetch('/_geraete/stand')
        failed = json.loads(raw)
        self.assertEqual(status, 503); self.assertFalse(failed['aktuell'])
        self.assertEqual(failed['stand'], first['stand']); self.assertEqual(failed['seiten'], [])
        (self.root / 'public/index.html').write_text('<h1>Bravo</h1>')
        # An old mtime must not hide changed content.
        os.utime(self.root / 'public/index.html', (1, 1))
        status, body = self.fetch('/')
        self.assertEqual(status, 200); self.assertIn('Bravo', body)
        fixed = json.loads(self.fetch('/_geraete/stand')[1])
        self.assertTrue(fixed['aktuell']); self.assertGreater(fixed['stand'], first['stand'])
        self.assertNotEqual(fixed['quelle'], first['quelle'])

    def test_source_deletion_triggers_rebuild_and_missing_source_fails(self):
        extra = self.root / 'public/extra.txt'; extra.write_text('extra')
        self.start_server()
        first = int((self.root / 'count.txt').read_text())
        extra.unlink(); self.fetch('/')
        self.assertEqual(int((self.root / 'count.txt').read_text()), first + 1)
        (self.root / 'public').rename(self.root / 'missing-source')
        self.assertEqual(self.fetch('/')[0], 503)
        self.assertFalse(json.loads(self.fetch('/_geraete/stand')[1])['aktuell'])
        (self.root / 'missing-source').rename(self.root / 'public')
        self.assertEqual(self.fetch('/')[0], 200)

    def test_path_boundary(self):
        (self.root / 'outside.txt').write_text('not served')
        self.start_server()
        status, body = self.fetch('/..%2foutside.txt')
        self.assertEqual(status, 403); self.assertNotIn('not served', body)


@unittest.skipUnless(os.environ.get('HARNESS_BRAVE_TESTS') == '1', 'set HARNESS_BRAVE_TESTS=1 for real Brave')
class BraveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'dist').mkdir()
        (self.root / 'dist/index.html').write_text('''<!doctype html><meta charset="utf-8"><link rel="icon" href="data:,"><title>Fixture</title>
<style>body{margin:0;padding:12px}nav{display:flex}p{color:#333}</style>
<nav><a href="/about/">About</a></nav><h1>Fixture</h1><p>Ready content</p>
<script>setTimeout(()=>{window.fixtureReady=true;document.querySelector('p').textContent='Ready now'},150)</script>''')
        (self.root / 'dist/about').mkdir()
        (self.root / 'dist/about/index.html').write_text('<meta charset="utf-8"><link rel="icon" href="data:,"><h1>About</h1><script>window.fixtureReady=true</script>')
        (self.root / 'website.config.mjs').write_text("export default {breiten:[390],routen:['/','/about/'],bereit:'window.fixtureReady === true',warteMs:5000};")

    def tool(self, name, *args):
        return subprocess.run(['node', str(TOOLS / name), *map(str, args)], cwd=self.root,
                              capture_output=True, text=True, timeout=30)

    def test_pruefen_screens_styles_real_brave(self):
        p = self.tool('pruefen.mjs')
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn('Browser: Brave', p.stdout)
        shots = self.root / 'shots'
        p = self.tool('screens.mjs', shots)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(len(list(shots.glob('*.png'))), 4)
        self.assertTrue((shots / '%2Fabout%2F@390-start.png').is_file())
        other = self.root / 'other-shots'
        p = self.tool('screens.mjs', other)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        p = self.tool('screens.mjs', '--compare', shots, other)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        p = self.tool('screens.mjs', shots)
        self.assertNotEqual(p.returncode, 0); self.assertIn('alte Screenshots', p.stderr)
        a = self.root / 'a.json'; b = self.root / 'b.json'
        for dest in [a, b]:
            p = self.tool('style-snapshot.mjs', dest)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        p = self.tool('style-snapshot.mjs', '--compare', a, b)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        states = json.loads(a.read_text())
        self.assertTrue(states); self.assertTrue(all(states.values()))

    def png_height(self, path):
        return int.from_bytes(path.read_bytes()[20:24], 'big')

    def png_pixel(self, path, x, y):
        """RGB of one pixel of an 8-bit RGB/RGBA PNG (decodes rows 0..y only)."""
        import zlib
        data, pos, idat = path.read_bytes(), 8, b''
        while pos < len(data):
            size, kind = int.from_bytes(data[pos:pos + 4], 'big'), data[pos + 4:pos + 8]
            if kind == b'IHDR': width, depth, colour = int.from_bytes(data[pos + 8:pos + 12], 'big'), data[pos + 16], data[pos + 17]
            if kind == b'IDAT': idat += data[pos + 8:pos + 8 + size]
            pos += 12 + size
        self.assertEqual((depth, colour in (2, 6)), (8, True))
        bpp = 3 if colour == 2 else 4
        raw, stride, prev = zlib.decompressobj().decompress(idat, (y + 1) * (width * bpp + 1)), width * bpp, bytearray(width * bpp)
        for row in range(y + 1):
            kind, line = raw[row * (stride + 1)], bytearray(raw[row * (stride + 1) + 1:(row + 1) * (stride + 1)])
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0; b = prev[i]; c = prev[i - bpp] if i >= bpp else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                line[i] = (line[i] + (0, a, b, (a + b) // 2, a if pa <= pb and pa <= pc else b if pb <= pc else c)[kind]) & 255
            prev = line
        return tuple(prev[x * bpp:x * bpp + 3])

    def test_full_page_keeps_real_viewport_heights(self):
        # 46vh at 844 px window = 388 px; a stretched capture window must not grow it (was > 1500 px).
        (self.root / 'dist/index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><link rel="icon" href="data:,">'
            '<style>body{margin:0}.hero{height:46vh;background:#f00}.rest{height:3000px;background:#00f}</style><div class="hero"></div><div class="rest"></div><script>window.fixtureReady=true</script>')
        (self.root / 'website.config.mjs').write_text("export default {breiten:[390],routen:['/','/about/'],bereit:'window.fixtureReady === true',warteMs:5000};")
        shots = self.root / 'shots'
        p = self.tool('screens.mjs', shots)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.png_height(shots / '%2F@390.png'), 388 + 3000)
        self.assertEqual(self.png_pixel(shots / '%2F@390.png', 10, 300), (255, 0, 0))
        self.assertEqual(self.png_pixel(shots / '%2F@390.png', 10, 600), (0, 0, 255))  # hero ends at 388, not ~1560
        self.assertEqual(self.png_height(shots / '%2F@390-start.png'), 844)

    def test_pruefen_reports_hover_outside_media_and_differing_footer(self):
        css = 'a:hover{color:red} @media (hover: hover){.ok:hover{color:blue}}'
        page = lambda foot: (f'<meta charset="utf-8"><link rel="icon" href="data:,"><style>{css}</style><header><a href="/">Start</a></header>'
                             f'<main><h1>X</h1><article><footer>Artikel</footer></article></main><footer>{foot}</footer><script>window.fixtureReady=true</script>')
        (self.root / 'dist/index.html').write_text(page('Fuß A'))
        (self.root / 'dist/about/index.html').write_text(page('Fuß A'))
        (self.root / 'dist/other').mkdir()
        (self.root / 'dist/other/index.html').write_text(page('Fuß B'))
        (self.root / 'website.config.mjs').write_text("export default {breiten:[390],bereit:'window.fixtureReady === true',warteMs:5000};")
        p = self.tool('pruefen.mjs')
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)  # hints, not hard failures
        hover = next(line for line in p.stdout.splitlines() if ':hover außerhalb' in line)
        self.assertIn('a:hover', hover); self.assertNotIn('.ok:hover', hover)
        self.assertIn('Fußzeile anders als auf den übrigen Seiten: /other/', p.stdout)
        self.assertNotIn('Kopfzeile anders', p.stdout)

    def test_vorbild_records_entry_and_section(self):
        handler = lambda *a: None
        import http.server, threading, functools
        site = self.root / 'dist'
        (site / 'index.html').write_text('<meta charset="utf-8"><link rel="icon" href="data:,"><style>body{margin:0}.hero{height:80vh;background:#246}</style>'
                                         '<div class="hero"></div><section id="leistungen" style="height:500px">Leistungen</section>')
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(site)))
        server.RequestHandlerClass.log_message = handler
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        url = f'http://127.0.0.1:{server.server_address[1]}/'
        (self.root / 'website.config.mjs').write_text('export default {warteMs:5000};')
        entry = self.root / 'harness/docs/inspiration/kunde-vorbild'
        p = self.tool('vorbild.mjs', url, 'kunde-vorbild')
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        for name in ('start.jpg', 'ganz.jpg'):
            self.assertEqual((entry / name).read_bytes()[:2], b'\xff\xd8', name)
        self.assertLess(sum(f.stat().st_size for f in entry.glob('*.jpg')), 1024 * 1024)
        brief = (entry / 'steckbrief.md').read_text()
        self.assertIn('lokale Adressen sind keine Quelle', brief); self.assertNotIn(url, brief)
        index = (self.root / 'harness/docs/inspiration/README.md').read_text()
        self.assertEqual(index.count('[kunde-vorbild](kunde-vorbild/steckbrief.md)'), 1)
        p = self.tool('vorbild.mjs', url, 'kunde-vorbild')
        self.assertNotEqual(p.returncode, 0); self.assertIn('gibt es schon', p.stderr)
        p = self.tool('vorbild.mjs', url, 'kunde-vorbild', '--abschnitt', 'leistungen=#leistungen')
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue((entry / 'abschnitt-leistungen.jpg').is_file())
        self.assertEqual((self.root / 'harness/docs/inspiration/README.md').read_text(), index)
        p = self.tool('vorbild.mjs', url, 'kunde-vorbild', '--abschnitt', 'x=.fehlt')
        self.assertNotEqual(p.returncode, 0); self.assertIn('Abschnitt nicht gefunden', p.stderr)

    def test_navigation_http_error_is_failure(self):
        script = f'''import {{launch,open}} from {str((TOOLS / 'browser.mjs').as_uri())!r};
import {{createServer}} from 'node:http';
const server=createServer((req,res)=>{{res.writeHead(404,{{'Content-Type':'text/html'}});res.end('<h1>Missing</h1>'+'.'.repeat(600));}});
await new Promise(done=>server.listen(0,'127.0.0.1',done)); let page;
try {{page=await launch(); await open(page,'http://127.0.0.1:'+server.address().port+'/missing/',390);}}
finally {{await page?.close(); server.close();}}'''
        p = subprocess.run(['node', '--input-type=module', '-e', script], cwd=self.root,
            capture_output=True, text=True, timeout=15)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('Navigation HTTP 404', p.stderr)

    def test_readiness_timeout_is_failure(self):
        (self.root / 'website.config.mjs').write_text("export default {breiten:[390],bereit:'false',warteMs:1000};")
        started = time.monotonic()
        p = self.tool('pruefen.mjs')
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('Zeitlimit', p.stderr)
        self.assertLess(time.monotonic() - started, 8)

    def test_browser_process_exit_is_failure(self):
        stub = self.root / 'brave'
        stub.write_text('#!/bin/sh\nexit 17\n'); stub.chmod(0o700)
        started = time.monotonic()
        p = subprocess.run(['node', str(TOOLS / 'pruefen.mjs')], cwd=self.root,
            env={**os.environ, 'BRAVE_PATH':str(stub)}, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('Brave wurde beendet', p.stderr)
        self.assertLess(time.monotonic() - started, 5)

    def test_runtime_error_is_failure(self):
        (self.root / 'dist/index.html').write_text('<h1>Failure fixture</h1><script>window.fixtureReady=true;throw new Error("intentional runtime failure")</script>')
        p = self.tool('pruefen.mjs')
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('runtime failure', p.stdout)


if __name__ == '__main__': unittest.main()
