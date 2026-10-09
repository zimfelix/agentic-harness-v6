// Lokale Vorschau einer gebauten Website (Profil Website): liefert konfig.ausgabe aus, baut bei Änderungen in
// konfig.quelle selbst neu (Browser-Refresh genügt), zeigt unbekannte Adressen mit der eigenen 404-Seite
// und bietet die Geräte-Vorschau unter /_geraete/. Aufruf aus dem Projektordner: node <webtools>/serve.mjs
import { createServer } from 'node:http';
import { readFile, readdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { networkInterfaces } from 'node:os';
import { join, extname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { routesIn } from './browser.mjs';
import { konfig, dateitypen } from './konfig.mjs';
const root = join(process.cwd(), konfig.ausgabe);
// Geräte-Vorschau: Vorlage aus dem Website-Profil, unverändert ausgeliefert (eine Quelle für Projekt und Harness-Vorlage).
const devicePreview = fileURLToPath(new URL('../assets/device-preview.html', import.meta.url));
const types = dateitypen;
// Inhalts-/Dateimengenabgleich erkennt auch Löschen und Änderungen bei alten mtimes.
let builtAt = null, attemptedSource = null, builtSource = null, buildError = null;
const sourceStamp = async (dir = join(process.cwd(), konfig.quelle), hash = createHash('sha256')) => {
  for (const entry of (await readdir(dir, { withFileTypes:true })).sort((a, b) => a.name.localeCompare(b.name))) {
    const path = join(dir, entry.name);
    hash.update(JSON.stringify([path, entry.isDirectory()]));
    if (entry.isDirectory()) await sourceStamp(path, hash);
    else if (entry.isFile()) hash.update(await readFile(path));
  }
  return hash;
};
const rebuildIfChanged = async () => {
  let stamp;
  try { stamp = (await sourceStamp()).digest('hex'); }
  catch { buildError = 'Buildquelle nicht lesbar; kein aktueller Nachweis'; return; }
  if (stamp === attemptedSource && !buildError) return;
  if (stamp === attemptedSource && buildError?.startsWith('Build fehlgeschlagen')) return;
  attemptedSource = stamp;
  try {
    if (konfig.build) {
      const [befehl, ...argumente] = konfig.build;
      execFileSync(befehl === 'node' ? process.execPath : befehl, argumente, { stdio:'inherit', timeout:60000 });
    }
    builtSource = stamp;
    builtAt = Date.now(); // nur nach erfolgreichem Build/aktuellem statischen Stand
    buildError = null;
  } catch {
    buildError = 'Build fehlgeschlagen; alter Stand ist kein aktueller Nachweis';
    console.error(buildError);
  }
};
const port = Number(process.env.PORT || konfig.port);
// Standard: nur auf diesem Rechner. HOST=0.0.0.0 (z. B. npm run dev:lan) gibt die Vorschau im lokalen Netz frei, z. B. fürs Handy.
const host = process.env.HOST || '127.0.0.1';
const lanAddresses = () => Object.values(networkInterfaces()).flat().filter(a => a.family === 'IPv4' && !a.internal).map(a => a.address);
createServer(async (req,res) => {
  res.setHeader('Cache-Control', 'no-store');
  try {
    await rebuildIfChanged();
    const url = new URL(req.url, `http://${req.headers.host}`);
    // Geräte-Vorschau (npm run geraete): nur hier ausgeliefert, nicht Teil der Website in dist/.
    if (url.pathname === '/_geraete' || url.pathname === '/_geraete/') {
      res.writeHead(200, { 'Content-Type':'text/html; charset=utf-8', 'X-Robots-Tag':'noindex, nofollow' });
      res.end(await readFile(devicePreview));
      return;
    }
    if (url.pathname === '/_geraete/stand') {
      res.writeHead(buildError ? 503 : 200, { 'Content-Type':'application/json; charset=utf-8', 'Cache-Control':'no-store' });
      res.end(JSON.stringify({ stand:builtAt, aktuell:!buildError, quelle:builtSource, fehler:buildError, seiten:buildError ? [] : await routesIn(root) }));
      return;
    }
    if (buildError) {
      res.writeHead(503, { 'Content-Type':'text/plain; charset=utf-8', 'Cache-Control':'no-store' });
      res.end(buildError);
      return;
    }
    const path = decodeURIComponent(url.pathname).replace(/^[/\\]+/,'');
    const base = resolve(root);
    const file = resolve(base, path, extname(path) ? '' : 'index.html');
    if (!file.startsWith(base + sep)) { res.writeHead(403); res.end(); return; }
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type':types[extname(file)] || 'application/octet-stream', 'X-Robots-Tag':'noindex, nofollow' });
    res.end(body);
  } catch {
    // Unbekannte Adresse: eigene Fehlerseite (/404/) mit Status 404, wie auf dem Server.
    const page = await readFile(join(root, '404', 'index.html')).catch(() => 'Nicht gefunden');
    res.writeHead(404, { 'Content-Type':'text/html; charset=utf-8', 'X-Robots-Tag':'noindex, nofollow' });
    res.end(page);
  }
}).listen(port, host, () => {
  console.log(`Preview: http://127.0.0.1:${port}/`);
  if (host === '0.0.0.0') for (const address of lanAddresses()) console.log(`Im lokalen Netz: http://${address}:${port}/`);
});
