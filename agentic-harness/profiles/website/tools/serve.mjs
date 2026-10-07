// Lokale Vorschau einer gebauten Website (Profil Website): liefert konfig.ausgabe aus, baut bei Änderungen in
// konfig.quelle selbst neu (Browser-Refresh genügt), zeigt unbekannte Adressen mit der eigenen 404-Seite
// und bietet die Geräte-Vorschau unter /_geraete/. Aufruf aus dem Projektordner: node <webtools>/serve.mjs
import { createServer } from 'node:http';
import { readFile, readdir, stat } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { networkInterfaces } from 'node:os';
import { join, normalize, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { routesIn } from './browser.mjs';
import { konfig, dateitypen } from './konfig.mjs';
const root = join(process.cwd(), konfig.ausgabe);
// Geräte-Vorschau: Vorlage aus dem Website-Profil, unverändert ausgeliefert (eine Quelle für Projekt und Harness-Vorlage).
const devicePreview = fileURLToPath(new URL('../assets/device-preview.html', import.meta.url));
const types = dateitypen;
// Baut vor jeder Anfrage neu, sobald sich Dateien in konfig.quelle geändert haben – Browser-Refresh genügt.
let builtAt = Date.now();
const newestSource = async (dir = join(process.cwd(), konfig.quelle)) => {
  let newest = 0;
  for (const entry of await readdir(dir, { withFileTypes:true })) {
    const path = join(dir, entry.name);
    newest = Math.max(newest, entry.isDirectory() ? await newestSource(path) : (await stat(path)).mtimeMs);
  }
  return newest;
};
const rebuildIfChanged = async () => {
  if (!konfig.build) return; // statischer Ordner (ORDNER=…): nichts zu bauen
  if (await newestSource() <= builtAt) return;
  builtAt = Date.now();
  const [befehl, ...argumente] = konfig.build;
  try { execFileSync(befehl === 'node' ? process.execPath : befehl, argumente, { stdio:'inherit' }); }
  catch { console.error('Build fehlgeschlagen – zuletzt gebauter Stand bleibt sichtbar.'); }
};
const port = Number(process.env.PORT || konfig.port);
// Standard: nur auf diesem Rechner. HOST=0.0.0.0 (z. B. npm run dev:lan) gibt die Vorschau im lokalen Netz frei, z. B. fürs Handy.
const host = process.env.HOST || '127.0.0.1';
const lanAddresses = () => Object.values(networkInterfaces()).flat().filter(a => a.family === 'IPv4' && !a.internal).map(a => a.address);
createServer(async (req,res) => {
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
      res.writeHead(200, { 'Content-Type':'application/json; charset=utf-8', 'Cache-Control':'no-store' });
      res.end(JSON.stringify({ stand:builtAt, seiten:await routesIn(root) }));
      return;
    }
    const path = normalize(decodeURIComponent(url.pathname)).replace(/^[/\\]+/,'');
    if (path.startsWith('..') || path.includes('..\\') || path.includes('../')) { res.writeHead(403); res.end(); return; }
    const file = join(root, path, extname(path) ? '' : 'index.html');
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
