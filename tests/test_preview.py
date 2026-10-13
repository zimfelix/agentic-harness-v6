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

TOOLS = Path(__file__).resolve().parents[1] / 'template/.agents/skills/website-tools/tools'


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
        self.assertEqual(len(list(shots.glob('*.png'))), 2)
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
