// Fingerabdruck der berechneten Styles aller Elemente – für CSS-Umbauten ohne sichtbare Änderung,
// auch in Zuständen, die Screenshots nicht zeigen (Hover, Fokus, aufgeklappte Menüs/FAQ, Radio-Auswahl).
//   node <webtools>/style-snapshot.mjs <ausgabe.json> [build-ordner]
//   node <webtools>/style-snapshot.mjs --compare <a.json> <b.json>
// Elemente werden über ihre Position im Dokument verglichen, nicht über Klassen: Umbenennen bleibt erlaubt,
// solange die HTML-Struktur gleich bleibt. link-, script- und style-Elemente zählen nicht mit.
import { readFile, writeFile } from 'node:fs/promises';
import { launch, open, routesIn, serve, sleep } from './browser.mjs';
import { konfig } from './konfig.mjs';

const [first, second, third] = process.argv.slice(2);

if (first === '--compare') {
  const [a, b] = await Promise.all([second, third].map(async f => JSON.parse(await readFile(f, 'utf8'))));
  let bad = 0;
  for (const key of Object.keys(a)) {
    const x = a[key], y = b[key];
    if (!y) { console.log(`${key}: fehlt`); bad++; continue; }
    const i = x.findIndex((v, n) => v !== y[n]);
    if (i !== -1 || x.length !== y.length) { console.log(`${key}: Element ${i === -1 ? x.length : i} (${x[i] ?? '–'} → ${y[i] ?? '–'})`); bad++; }
  }
  console.log(bad ? `${bad} von ${Object.keys(a).length} Zuständen abweichend.` : `Alle ${Object.keys(a).length} Zustände gleich.`);
  process.exit(bad ? 1 : 0);
}

if (!first) { console.error('Aufruf: node style-snapshot.mjs <ausgabe.json> [build-ordner]'); process.exit(2); }
const root = second || konfig.ausgabe;

// Im Browser: je Element Tag + Prüfsumme aller berechneten Eigenschaften (auch ::before/::after/::marker/::placeholder).
const fingerprint = `(() => {
  const props = [...getComputedStyle(document.documentElement)].filter(p => !p.startsWith('--'));
  const hash = s => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0).toString(36); };
  const read = (el, pseudo) => { const cs = getComputedStyle(el, pseudo); return props.map(p => cs.getPropertyValue(p)).join('|'); };
  const skip = new Set(['LINK', 'SCRIPT', 'STYLE']);
  return [document.documentElement, document.body, ...document.body.querySelectorAll('*')].filter(el => !skip.has(el.tagName)).map(el => {
    let s = read(el);
    for (const pseudo of ['::before', '::after']) { const c = getComputedStyle(el, pseudo).content; if (c && c !== 'none' && c !== 'normal') s += pseudo + read(el, pseudo); }
    if (getComputedStyle(el).display === 'list-item' || el.tagName === 'SUMMARY') s += '::marker' + read(el, '::marker');
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') s += '::placeholder' + read(el, '::placeholder');
    return el.tagName.toLowerCase() + ':' + hash(s);
  });
})()`;

// Erzwungene Pseudoklassen auf allen Elementen (über das DevTools-Protokoll).
async function force(page, classes) {
  await page.send('DOM.enable'); await page.send('CSS.enable');
  const { result } = await page.send('DOM.getDocument', { depth:-1 });
  const { result:{ nodeIds } } = await page.send('DOM.querySelectorAll', { nodeId:result.root.nodeId, selector:'body *' });
  for (const nodeId of nodeIds) await page.send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses:classes });
}

const states = {
  default: async () => {},
  open: async page => page.evaluate(`document.querySelectorAll('details').forEach(d => d.open = true)`),
  radio1: async page => page.evaluate(`(() => { const groups = {}; document.querySelectorAll('input[type=radio]').forEach(r => (groups[r.name] ||= []).push(r)); Object.values(groups).forEach(g => { if (g[1]) g[1].checked = true; }); })()`),
  radio2: async page => page.evaluate(`(() => { const groups = {}; document.querySelectorAll('input[type=radio]').forEach(r => (groups[r.name] ||= []).push(r)); Object.values(groups).forEach(g => { if (g[2]) g[2].checked = true; }); })()`),
  hover: async page => force(page, ['hover']),
  focus: async page => force(page, ['focus', 'focus-visible', 'focus-within']),
};

const out = {};
const server = await serve(root);
const page = await launch();
try {
  for (const route of await routesIn(root)) {
    for (const width of konfig.breiten) {
      for (const [name, apply] of Object.entries(states)) {
        await open(page, server.base + route, width);
        if (name.startsWith('radio') && !(await page.evaluate(`document.querySelectorAll('input[type=radio]').length`))) continue;
        await apply(page);
        if (name !== 'default') await sleep(600); // laufende Übergänge (transition) abwarten
        out[`${route}@${width}@${name}`] = await page.evaluate(fingerprint);
      }
    }
  }
  await writeFile(first, JSON.stringify(out));
  console.log(`${Object.keys(out).length} Zustände in ${first}`);
} finally { await page.close(); server.close(); }
