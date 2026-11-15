// Statische Website-Prüfungen über CDP, ausschließlich mit verifiziertem Brave-Pfad.
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { existsSync, realpathSync } from 'node:fs';
import { mkdtemp, readdir, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, extname, basename, resolve, relative, sep } from 'node:path';
import { konfig, dateitypen } from './konfig.mjs';

export const browserPath = process.env.BRAVE_PATH || process.env.CHROME_PATH || [
  // alter Variablenname bleibt unterstützt, kein Chrome-Fallback
  '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
  '/usr/bin/brave-browser', '/usr/bin/brave-browser-stable', '/usr/bin/brave',
].find(p => existsSync(p));
export const sleep = ms => new Promise(r => setTimeout(r, ms));

export async function routesIn(root, dir = root, found = []) {
  root = resolve(root); dir = resolve(dir);
  for (const entry of await readdir(dir, { withFileTypes:true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory() && !(dir === root && konfig.interneOrdner.includes(entry.name))) await routesIn(root, path, found);
    else if (entry.name === 'index.html') found.push('/' + relative(root, path).replaceAll('\\', '/').replace(/index\.html$/, ''));
  }
  return found.sort();
}

// Nichtleere Prüfmengen vor Server/Browserstart. Deklarierte Routen müssen den Build vollständig decken.
export async function checkedRoutes(root) {
  const routes = await routesIn(root);
  if (!routes.length) throw new Error(`Keine statischen Prüfrouten in ${root}; kein Nachweis`);
  if (!Array.isArray(konfig.breiten) || !konfig.breiten.length ||
      konfig.breiten.some(w => !Number.isInteger(w) || w <= 0) || new Set(konfig.breiten).size !== konfig.breiten.length) {
    throw new Error('Prüfbreiten müssen nichtleere, eindeutige positive Integer sein');
  }
  if (konfig.routen !== null) {
    if (!Array.isArray(konfig.routen) || !konfig.routen.length || konfig.routen.some(r => typeof r !== 'string') ||
        new Set(konfig.routen).size !== konfig.routen.length) throw new Error('Ungültige erwartete Routen');
    const expected = [...konfig.routen].sort();
    if (JSON.stringify(expected) !== JSON.stringify(routes)) {
      throw new Error(`Routenmenge abweichend: erwartet ${JSON.stringify(expected)}, gebaut ${JSON.stringify(routes)}`);
    }
  }
  console.log(`Prüfumfang: ${root}, ${routes.length} Routen (${konfig.routen === null ? 'automatisch entdeckt, Soll-Abgleich separat' : 'deklariert'}), Breiten ${konfig.breiten.join('/')}`);
  return routes;
}

export async function serve(root) {
  const base = resolve(root);
  const server = createServer(async (req, res) => {
    try {
      const path = decodeURIComponent(new URL(req.url, 'http://x').pathname).replace(/^\/+/, '');
      const file = resolve(base, path, extname(path) ? '' : 'index.html');
      if (!file.startsWith(base + sep)) { res.writeHead(403); res.end(); return; }
      const body = await readFile(file);
      res.writeHead(200, { 'Content-Type':dateitypen[extname(file)] || 'application/octet-stream' });
      res.end(body);
    } catch { res.writeHead(404); res.end(); }
  });
  await new Promise((accept, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', accept); });
  return { base:`http://127.0.0.1:${server.address().port}`, close:() => server.close() };
}

export async function launch() {
  if (!browserPath) throw new Error('Kein Brave gefunden (BRAVE_PATH setzen); kein Browser-Fallback');
  const executable = realpathSync(browserPath);
  if (!/^(Brave Browser|brave|brave-browser(?:-stable)?)$/i.test(basename(executable))) {
    throw new Error(`Nicht als Brave verifizierter Browserpfad: ${executable}`);
  }
  console.log(`Browser: Brave (${executable})`);
  const profile = await mkdtemp(join(tmpdir(), 'website-pruefung-'));
  const browser = spawn(executable, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
    '--no-first-run', '--hide-scrollbars', ...(process.env.CI ? ['--disable-dev-shm-usage'] : []), 'about:blank'], { stdio:'ignore' });
  let exited = false, spawnError, ws;
  browser.on('exit', () => { exited = true; });
  browser.on('error', error => { spawnError = error; exited = true; });
  const stop = async () => { ws?.close(); browser.kill(); await sleep(300); await rm(profile, { recursive:true, force:true }); };
  try {
    let page;
    for (const end = Date.now() + konfig.warteMs; Date.now() < end && !exited;) {
      try {
        const port = Number((await readFile(join(profile, 'DevToolsActivePort'), 'utf8')).split('\n')[0]);
        page = (await (await fetch(`http://127.0.0.1:${port}/json`, { signal:AbortSignal.timeout(1000) })).json()).find(t => t.type === 'page');
        if (page) break;
      } catch { /* Browserstart noch nicht bereit; begrenztes Warten. */ }
      await sleep(100);
    }
    if (!page) throw spawnError || new Error('Brave wurde beendet oder antwortet nicht im Zeitlimit');
    ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((accept, reject) => {
      const timer = setTimeout(() => reject(new Error('DevTools-Verbindung: Zeitlimit')), konfig.warteMs);
      ws.onopen = () => { clearTimeout(timer); accept(); };
      ws.onerror = () => { clearTimeout(timer); reject(new Error('DevTools-Verbindung fehlgeschlagen')); };
    });
    let id = 0;
    const pending = new Map(), listeners = new Set();
    const fail = error => { for (const p of pending.values()) p.reject(error); pending.clear(); for (const l of [...listeners]) l.reject(error); };
    ws.onclose = () => fail(new Error('DevTools-Verbindung geschlossen'));
    ws.onerror = () => fail(new Error('DevTools-Verbindungsfehler'));
    ws.onmessage = event => {
      const message = JSON.parse(event.data);
      const p = pending.get(message.id);
      if (p) { pending.delete(message.id); message.error ? p.reject(new Error(`${p.method}: ${message.error.message}`)) : p.accept(message); }
      for (const l of [...listeners]) if (l.method === message.method && l.when(message.params)) l.accept(message.params);
    };
    const send = (method, params = {}) => new Promise((accept, reject) => {
      const i = ++id;
      const timer = setTimeout(() => { pending.delete(i); reject(new Error(`${method}: Zeitlimit`)); }, konfig.warteMs);
      pending.set(i, { method, accept:m => { clearTimeout(timer); accept(m); }, reject:e => { clearTimeout(timer); reject(e); } });
      try { ws.send(JSON.stringify({ id:i, method, params })); }
      catch (error) { pending.get(i).reject(error); pending.delete(i); }
    });
    const waitFor = (method, when = () => true) => new Promise((accept, reject) => {
      const finish = (fn, value) => { clearTimeout(timer); listeners.delete(listener); fn(value); };
      const listener = { method, when, accept:v => finish(accept, v), reject:e => finish(reject, e) };
      const timer = setTimeout(() => listener.reject(new Error(`${method}: Zeitlimit`)), konfig.warteMs);
      listeners.add(listener);
    });
    const evaluate = async expression => {
      const { result:r } = await send('Runtime.evaluate', { expression, returnByValue:true, awaitPromise:true });
      if (r.exceptionDetails) throw new Error('Seitenfehler: ' + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
      return r.result.value;
    };
    await send('Page.enable');
    return { send, evaluate, waitFor, close:stop };
  } catch (error) { await stop(); throw error; }
}

// Load-Ereignis, Schriftladung, ggf. projektspezifischer Zustand und zwei Layoutframes statt festem Sleep.
export async function open(page, url, width, height = 900) {
  await page.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor:1, mobile:width < 800 });
  await page.send('Network.enable');
  const response = page.waitFor('Network.responseReceived', p => p.type === 'Document');
  response.catch(() => {});
  const loaded = page.waitFor('Page.loadEventFired');
  loaded.catch(() => {}); // Navigation kann vorher fehlschlagen; kein unhandled rejection.
  const navigation = await page.send('Page.navigate', { url });
  if (navigation.result.errorText) throw new Error(`Navigation fehlgeschlagen: ${navigation.result.errorText}`);
  const document = await response;
  if (document.response.status >= 400) throw new Error(`Navigation HTTP ${document.response.status}: ${url}`);
  await loaded;
  await page.evaluate('document.fonts.ready.then(() => true)');
  if (konfig.bereit) {
    await page.evaluate(`new Promise((accept, reject) => { const end = Date.now() + ${konfig.warteMs}; const check = () => { try { if (${konfig.bereit}) return accept(true); if (Date.now() >= end) return reject(new Error('Bereitschaftszustand: Zeitlimit')); requestAnimationFrame(check); } catch (e) { reject(e); } }; check(); })`);
  }
  await page.evaluate(ZWEI_FRAMES);
}

const ZWEI_FRAMES = 'new Promise(accept => requestAnimationFrame(() => requestAnimationFrame(() => accept(true))))';
// Fensterhöhe des ersten Bildschirms: Desktop 900 px, Handy 844 px (gängiges Smartphone).
export const bildschirm = breite => (breite < 800 ? 844 : 900);
const MAX_HOEHE = 16384; // Grenze einer Browser-Aufnahme; längere Seiten werden abgeschnitten und gemeldet
// Lazy-Bilder und Einblendungen auslösen: in echter Fensterhöhe einmal durchscrollen, begrenzt auf Bilder warten.
const NACHLADEN = `(async () => {
  for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight) {
    scrollTo(0, y); await new Promise(r => requestAnimationFrame(() => setTimeout(r, 60)));
  }
  scrollTo(0, 0);
  const offen = [...document.images].filter(i => !i.complete).map(i => new Promise(r => { i.addEventListener('load', r, { once:true }); i.addEventListener('error', r, { once:true }); }));
  await Promise.race([Promise.all(offen), new Promise(r => setTimeout(r, 3000))]);
  return true;
})()`;
// Animationen und Übergänge auf ihren Endstand setzen; endlose stehen auf dem Anfang. Sonst entsteht das Bild mitten im Ablauf.
const ANIMATIONEN_ENDEN = `(() => { for (const a of document.getAnimations()) { try { a.finish(); } catch { a.pause(); a.currentTime = 0; } } return true; })()`;
const HOEHEN_MERKEN = `(() => { window.__hoehen = [...document.querySelectorAll('html, body, body *')].map(el => [el, el.getBoundingClientRect().height]);
  return document.documentElement.scrollHeight; })()`;
// Nach dem Vergrößern des Fensters: was seine Höhe geändert hat (vh, svh, per JS aus innerHeight), auf die echte Höhe festsetzen.
const HOEHEN_HALTEN = `(() => { let n = 0;
  for (const [el, h] of window.__hoehen) if (Math.abs(el.getBoundingClientRect().height - h) > 0.5) {
    for (const p of ['height', 'min-height', 'max-height']) el.style.setProperty(p, h + 'px', 'important');
    n++;
  }
  return n; })()`;

// Aufnahme einer Seite wie auf dem Gerät: `start` = erster Bildschirm in echter Fensterhöhe, `ganz` = ganze Seite mit denselben
// Höhen wie im echten Fenster. Für die Ganzseite wird das Fenster auf Seitenhöhe gestreckt; damit vh-Bereiche dabei nicht
// mitwachsen, werden geänderte Höhen vorher auf den gemessenen Stand festgesetzt. Optionen: format ('png'|'jpeg'), qualitaet, skala (ganz).
export async function aufnehmen(page, url, breite, { format = 'png', qualitaet, skala = 1 } = {}) {
  const mobile = breite < 800;
  await open(page, url, breite, bildschirm(breite));
  await page.evaluate(NACHLADEN);
  await page.evaluate(ANIMATIONEN_ENDEN);
  await page.evaluate(ZWEI_FRAMES);
  const bild = async clip => Buffer.from((await page.send('Page.captureScreenshot',
    { format, ...(qualitaet ? { quality:qualitaet } : {}), ...(clip ? { clip } : {}) })).result.data, 'base64');
  const start = await bild();
  const gesamt = await page.evaluate(HOEHEN_MERKEN);
  const hoehe = Math.min(gesamt, MAX_HOEHE);
  await page.send('Emulation.setDeviceMetricsOverride', { width:breite, height:hoehe, deviceScaleFactor:1, mobile });
  await page.evaluate(ZWEI_FRAMES);
  const gehalten = await page.evaluate(HOEHEN_HALTEN);
  await page.evaluate(ANIMATIONEN_ENDEN); // das Vergrößern kann Einblendungen auslösen
  await page.evaluate(ZWEI_FRAMES);
  const ganz = await bild(skala === 1 ? undefined : { x:0, y:0, width:breite, height:hoehe, scale:skala });
  return { start, ganz, gehalten, abgeschnitten: gesamt > MAX_HOEHE };
}
