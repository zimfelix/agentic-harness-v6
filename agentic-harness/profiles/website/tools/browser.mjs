// Gemeinsame Werkzeuge für Browser-Prüfungen von Websites (Profil Website): statischer Server für einen gebauten Ordner
// und ein headless Chrome/Brave, gesteuert über das Chrome DevTools Protocol (ohne npm-Pakete).
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdtemp, readdir, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, extname } from 'node:path';
import { konfig, dateitypen } from './konfig.mjs';

export const browserPath = [
  process.env.CHROME_PATH,
  '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
].find(p => p && existsSync(p));

export const sleep = ms => new Promise(r => setTimeout(r, ms));

const types = dateitypen;

// Alle gebauten Seiten eines Ordners als Routen, z. B. ['/', '/ablauf/', …].
// Ordner aus `interneOrdner` (z. B. Konzeptseiten unter /konzepte/) gehören nicht zur Website und fehlen hier.
export async function routesIn(root, dir = root, found = []) {
  for (const entry of await readdir(dir, { withFileTypes:true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory() && !(dir === root && konfig.interneOrdner.includes(entry.name))) await routesIn(root, path, found);
    else if (entry.name === 'index.html') found.push('/' + path.slice(root.length + 1).replace(/index\.html$/, ''));
  }
  return found.sort();
}

// Liefert den Ordner auf einem freien Port aus; gibt Basis-URL und close() zurück.
export async function serve(root) {
  const server = createServer(async (req, res) => {
    try {
      const path = decodeURIComponent(new URL(req.url, 'http://x').pathname);
      const file = join(root, path, extname(path) ? '' : 'index.html');
      const body = await readFile(file);
      res.writeHead(200, { 'Content-Type': types[extname(file)] || 'application/octet-stream' });
      res.end(body);
    } catch { res.writeHead(404); res.end(); }
  }).listen(0, '127.0.0.1');
  await new Promise(r => server.once('listening', r));
  return { base:`http://127.0.0.1:${server.address().port}`, close:() => server.close() };
}

// In CI (z. B. GitHub Actions) fehlt dem Browser oft die Sandbox und ein großes /dev/shm.
const ciFlags = process.env.CI ? ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'] : [];

// Startet den Browser einmal; liefert Prozess, Profil und Websocket-Adresse der Seite oder wirft nach `waitMs`.
async function start(waitMs) {
  const profile = await mkdtemp(join(tmpdir(), 'website-pruefung-'));
  const debugPort = 9400 + Math.floor(Math.random() * 400);
  const browser = spawn(browserPath, ['--headless=new', `--remote-debugging-port=${debugPort}`, `--user-data-dir=${profile}`, '--no-first-run', '--hide-scrollbars', ...ciFlags, 'about:blank'], { stdio:'ignore' });
  let exited = false;
  browser.on('exit', () => { exited = true; });
  const stop = async () => { browser.kill(); await sleep(300); await rm(profile, { recursive:true, force:true }); };
  for (const end = Date.now() + waitMs; Date.now() < end && !exited;) {
    try {
      const page = (await (await fetch(`http://127.0.0.1:${debugPort}/json`)).json()).find(t => t.type === 'page');
      if (page) return { profile, browser, stop, wsUrl: page.webSocketDebuggerUrl };
    } catch {}
    await sleep(250);
  }
  await stop();
  throw new Error(exited ? 'Browser hat sich beim Start beendet' : `Browser antwortet nach ${waitMs / 1000} s nicht`);
}

// Startet den Browser (ein zweiter Versuch, falls der erste hängt) und gibt send(), evaluate() und close() für eine Seite zurück.
export async function launch() {
  if (!browserPath) throw new Error('Kein Chrome/Brave gefunden (CHROME_PATH setzen)');
  let started;
  try { started = await start(20000); }
  catch (error) { console.error(`${error.message} (${browserPath}), zweiter Versuch …`); started = await start(30000); }
  const { browser, profile, wsUrl } = started;
  const ws = new WebSocket(wsUrl);
  try { await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = () => reject(new Error('Keine Verbindung zum Browser (DevTools-Websocket)')); }); }
  catch (error) { await started.stop(); throw error; }
  let id = 0; const pending = {};
  ws.onmessage = e => { const m = JSON.parse(e.data); if (pending[m.id]) { pending[m.id](m); delete pending[m.id]; } };
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pending[i] = r; ws.send(JSON.stringify({ id:i, method, params })); });
  const evaluate = async expression => {
    const r = (await send('Runtime.evaluate', { expression, returnByValue:true, awaitPromise:true })).result;
    if (r.exceptionDetails) throw new Error('Seitenfehler: ' + r.exceptionDetails.exception?.description);
    return r.result.value;
  };
  await send('Page.enable');
  const close = async () => { ws.close(); browser.kill(); await sleep(300); await rm(profile, { recursive:true, force:true }); };
  return { send, evaluate, close };
}

// Öffnet eine Route in gegebener Breite und wartet, bis Schrift und Layout stehen.
export async function open(page, url, width, height = 900) {
  await page.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor:1, mobile: width < 800 });
  await page.send('Page.navigate', { url });
  await sleep(400);
  await page.evaluate('document.fonts.ready.then(() => true)');
}
