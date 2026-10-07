// Findet CSS-Selektoren, die auf keiner gebauten Seite etwas treffen (genutzt von css-audit.mjs und Browser-Tests der Projekte).
// Zustände (:hover, [open], :checked …) werden großzügig gewertet: Pseudoklassen und Attributbedingungen fallen beim Prüfen weg,
// damit nur wirklich tote Regeln gemeldet werden.
import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { launch, open, routesIn, serve } from './browser.mjs';
import { allRules, parseCss } from './css.mjs';
import { konfig } from './konfig.mjs';

// Alle .css-Dateien unter `stylesDir` samt gelesener Regeln; Dateien aus `stylesOhne` sind bewusst nicht eingebunden.
export async function readStyles(stylesDir = konfig.styles) {
  const files = [];
  for (const name of (await readdir(stylesDir, { recursive:true })).filter(n => n.endsWith('.css') && !konfig.stylesOhne.includes(n)).sort()) {
    const path = join(stylesDir, name);
    const text = await readFile(path, 'utf8');
    files.push({ path, text, items:parseCss(text) });
  }
  return files;
}

// Im Browser: Selektor verbreitern (Zustände entfernen) und auf der Seite suchen.
const matchScript = list => `(() => {
  const broaden = sel => {
    let s = sel, prev;
    do { prev = s; s = s.replace(/::?[\\w-]+\\([^()]*\\)/g, ''); } while (s !== prev);
    s = s.replace(/::?[\\w-]+/g, '').replace(/\\[[^\\]]*\\]/g, '');
    // Kombinatoren ohne Leerraum schreiben; wo danach ein Teil fehlt, steht * (z. B. ".a>:first-child" → ".a>*").
    s = s.replace(/\\s*([>+~])\\s*/g, '$1').trim().replace(/(^|[>+~])(?=[>+~]|$)/g, '$1*');
    return s || '*';
  };
  return ${JSON.stringify(list)}.filter(sel => { try { return document.querySelector(broaden(sel)) !== null; } catch { return true; } });
})()`;

// Liefert { files, used, unused } – `unused` je Datei als Liste von Selektoren.
export async function unusedSelectors({ stylesDir = konfig.styles, root = konfig.ausgabe } = {}) {
  const files = await readStyles(stylesDir);
  const selectors = [...new Set(files.flatMap(f => allRules(f.items).flatMap(r => r.selectors)))];
  const used = new Set();
  const server = await serve(root);
  const page = await launch();
  try {
    for (const route of await routesIn(root)) {
      await open(page, server.base + route, 1440);
      for (const sel of await page.evaluate(matchScript(selectors.filter(s => !used.has(s))))) used.add(sel);
    }
  } finally { await page.close(); server.close(); }
  const unused = Object.fromEntries(files.map(f => [f.path, [...new Set(allRules(f.items).flatMap(r => r.selectors).filter(s => !used.has(s)))]]));
  return { files, used, unused };
}
