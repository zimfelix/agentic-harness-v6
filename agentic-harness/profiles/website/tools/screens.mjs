// Ganzseitige Screenshots aller gebauten Seiten bei den Prüfbreiten (konfig.breiten) – für Umbauten ohne sichtbare Änderung.
//   node <webtools>/screens.mjs <ausgabe-ordner> [build-ordner]   Screenshots aufnehmen (Standard: konfig.ausgabe)
//   node <webtools>/screens.mjs --compare <ordner-a> <ordner-b>   Aufnahmen vergleichen (bytegleich = keine sichtbare Änderung)
import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { launch, open, checkedRoutes, serve } from './browser.mjs';
import { konfig } from './konfig.mjs';

const widths = konfig.breiten;
const [first, second, third] = process.argv.slice(2);

if (first === '--compare') {
  if (!second || !third) throw new Error('Zwei Vergleichsordner erforderlich');
  const [left, right] = await Promise.all([second, third].map(async dir => (await readdir(dir)).filter(n => n.endsWith('.png'))));
  if (!left.length || !right.length) throw new Error('Leere Screenshotmenge; kein Nachweis');
  const names = [...new Set([...left, ...right])].sort();
  const changed = [];
  for (const name of names) {
    if (!left.includes(name) || !right.includes(name)) { changed.push(`${name}: fehlt in ${left.includes(name) ? 'B' : 'A'}`); continue; }
    const [a, b] = await Promise.all([readFile(join(second, name)), readFile(join(third, name))]);
    if (!a.length || !b.length || !a.equals(b)) changed.push(name);
  }
  console.log(changed.length ? `Abweichend (${changed.length}/${names.length}):\n${changed.join('\n')}` : `Alle ${names.length} Aufnahmen identisch.`);
  process.exit(changed.length ? 1 : 0);
}

if (!first) { console.error('Aufruf: node screens.mjs <ausgabe-ordner> [build-ordner]'); process.exit(2); }
const root = second || konfig.ausgabe;
const routes = await checkedRoutes(root);
await mkdir(first, { recursive:true });
if ((await readdir(first)).some(n => n.endsWith('.png'))) throw new Error('Aufnahmeordner enthält alte Screenshots; neuen leeren Ordner wählen');
const server = await serve(root);
let page;
try {
  page = await launch();
  for (const route of routes) {
    const name = encodeURIComponent(route);
    for (const width of widths) {
      await open(page, server.base + route, width);
      const height = await page.evaluate('document.documentElement.scrollHeight');
      await open(page, server.base + route, width, height);
      const shot = await page.send('Page.captureScreenshot', { format:'png' });
      await writeFile(join(first, `${name}@${width}.png`), Buffer.from(shot.result.data, 'base64'));
    }
  }
  console.log(`Screenshots in ${first}/`);
} finally { await page?.close(); server.close(); }
