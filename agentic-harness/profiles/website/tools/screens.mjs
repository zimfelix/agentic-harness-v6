// Ganzseitige Screenshots aller gebauten Seiten bei den Prüfbreiten (konfig.breiten) – für Umbauten ohne sichtbare Änderung.
//   node <webtools>/screens.mjs <ausgabe-ordner> [build-ordner]   Screenshots aufnehmen (Standard: konfig.ausgabe)
//   node <webtools>/screens.mjs --compare <ordner-a> <ordner-b>   Aufnahmen vergleichen (bytegleich = keine sichtbare Änderung)
import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { launch, open, routesIn, serve } from './browser.mjs';
import { konfig } from './konfig.mjs';

const widths = konfig.breiten;
const [first, second, third] = process.argv.slice(2);

if (first === '--compare') {
  const names = (await readdir(second)).filter(n => n.endsWith('.png'));
  const changed = [];
  for (const name of names) {
    const [a, b] = await Promise.all([readFile(join(second, name)), readFile(join(third, name)).catch(() => null)]);
    if (!b || !a.equals(b)) changed.push(name);
  }
  console.log(changed.length ? `Abweichend (${changed.length}/${names.length}):\n${changed.join('\n')}` : `Alle ${names.length} Aufnahmen identisch.`);
  process.exit(changed.length ? 1 : 0);
}

if (!first) { console.error('Aufruf: node screens.mjs <ausgabe-ordner> [build-ordner]'); process.exit(2); }
const root = second || konfig.ausgabe;
await mkdir(first, { recursive:true });
const server = await serve(root);
const page = await launch();
try {
  for (const route of await routesIn(root)) {
    const name = route === '/' ? 'start' : route.slice(1, -1).replaceAll('/', '_');
    for (const width of widths) {
      await open(page, server.base + route, width);
      const height = await page.evaluate('document.documentElement.scrollHeight');
      await open(page, server.base + route, width, height);
      const shot = await page.send('Page.captureScreenshot', { format:'png' });
      await writeFile(join(first, `${name}@${width}.png`), Buffer.from(shot.result.data, 'base64'));
    }
  }
  console.log(`Screenshots in ${first}/`);
} finally { await page.close(); server.close(); }
