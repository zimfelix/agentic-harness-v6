// Nimmt ein Vorbild in die Inspirationssammlung des Projekts auf (Ablauf und Steckbrief: references/inspiration.md dieses Skills).
//   node <skill>/tools/vorbild.mjs <url> <ordnername>                         ganzer Entwurf: start.jpg, ganz.jpg, steckbrief.md, Indexzeile
//   node <skill>/tools/vorbild.mjs <url> <ordnername> --abschnitt <name>=<css>  ein gelobter Abschnitt: abschnitt-<name>.jpg
//   --ziel <ordner>   Sammlung (Standard harness/docs/inspiration)
// Ein Abschnitt zu einem bestehenden Eintrag ergänzt nur das Bild; Steckbrief und Index bleiben unberührt.
// Steckbrief und Index sind ein Gerüst: „Stark in“, Lob und Bewertung trägt der Agent nach dem Urteil des Auftraggebers ein.
// Aufnahme headless in Brave mit leerem Profil: Cookie-Banner und Anmeldungen erscheinen wie bei einem Erstbesuch; im Bild prüfen.
import { existsSync } from 'node:fs';
import { appendFile, mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { launch, aufnehmen, bildschirm, open } from './browser.mjs';

const ZIEL_MB = 1; // Bilder je Eintrag, damit die Sammlung im Repo klein bleibt
const args = process.argv.slice(2);
const wert = name => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : undefined; };
const ziel = wert('--ziel') || 'harness/docs/inspiration';
const abschnitt = wert('--abschnitt');
const [adresse, name] = args;

const abbruch = text => { console.error(`❌ ${text}`); process.exit(2); };
if (!adresse || !name) abbruch('Aufruf: node vorbild.mjs <url> <ordnername> [--abschnitt <name>=<css-selektor>] [--ziel <ordner>]');
let url; try { url = new URL(adresse); } catch { abbruch(`keine URL: ${adresse}`); }
if (!['http:', 'https:'].includes(url.protocol)) abbruch('nur http(s)-Adressen');
if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(name)) abbruch('Ordnername klein mit Bindestrichen, z. B. projekt-kurzname');
let teil;
if (abschnitt !== undefined) {
  const m = abschnitt.match(/^([a-z0-9-]+)=(.+)$/);
  if (!m) abbruch('--abschnitt <name>=<css-selektor>, z. B. hero=.hero');
  teil = { name: m[1], selektor: m[2] };
}
const ordner = join(ziel, name);
const neu = !existsSync(ordner);
if (!neu && !teil) abbruch(`${ordner} gibt es schon; Lob für einen Teil mit --abschnitt ergänzen, sonst anderen Namen wählen`);
if (teil && existsSync(join(ordner, `abschnitt-${teil.name}.jpg`))) abbruch(`abschnitt-${teil.name}.jpg gibt es schon`);

const page = await launch();
const dateien = {};
try {
  if (teil) {
    await open(page, url.href, 1440, bildschirm(1440));
    const box = await page.evaluate(`(() => { const el = document.querySelector(${JSON.stringify(teil.selektor)}); if (!el) return null;
      el.scrollIntoView({ block: 'start' }); const b = el.getBoundingClientRect();
      return { x: b.left + scrollX, y: b.top + scrollY, width: b.width, height: Math.min(b.height, 4000) }; })()`);
    if (!box || !box.width || !box.height) throw new Error(`Abschnitt nicht gefunden oder unsichtbar: ${teil.selektor}`);
    const bild = await page.send('Page.captureScreenshot', { format: 'jpeg', quality: 80, captureBeyondViewport: true, clip: { ...box, scale: 1 } });
    dateien[`abschnitt-${teil.name}.jpg`] = Buffer.from(bild.result.data, 'base64');
  } else {
    // Ganze Seite in halber Größe: reicht zum Lesen von Aufbau und Rhythmus; die Qualität sinkt, bis der Eintrag unter ZIEL_MB liegt.
    for (const qualitaet of [75, 60, 45]) {
      const { start, ganz, abgeschnitten } = await aufnehmen(page, url.href, 1440, { format: 'jpeg', qualitaet, skala: 0.5 });
      Object.assign(dateien, { 'start.jpg': start, 'ganz.jpg': ganz });
      if (abgeschnitten) console.log('⚠️ Seite länger als eine Aufnahme: ganz.jpg ist unten abgeschnitten');
      if (start.length + ganz.length <= ZIEL_MB * 1024 * 1024) break;
    }
  }
} catch (e) { console.error(`❌ ${e.message}`); process.exitCode = 1; } finally { await page.close(); }
if (process.exitCode) process.exit();

await mkdir(ordner, { recursive: true });
for (const [datei, inhalt] of Object.entries(dateien)) await writeFile(join(ordner, datei), inhalt);
const datum = new Date().toISOString().slice(0, 10);
const lokal = /^(127\.|localhost$|\[::1\]$|0\.0\.0\.0$)/.test(url.hostname);
if (neu) {
  const bilder = teil ? `- \`abschnitt-${teil.name}.jpg\` – offen: was das Bild zeigt und warum es hier ist`
    : '- `start.jpg` – erster Bildschirm, Desktop 1440 px\n- `ganz.jpg` – ganze Seite, halbe Größe';
  await writeFile(join(ordner, 'steckbrief.md'), `# ${name} – offen: Leitidee in wenigen Wörtern

- **Herkunft:** Website, aufgenommen ${datum}. Quelle: ${lokal ? 'offen: Repo und Datei (lokale Adressen sind keine Quelle)' : url.href}
- **Stark in:** offen
- **Auftraggeber:** offen: wörtliches Lob; fehlt es, das offen sagen

## Was gut ist

| Kategorie | Was es ausmacht |
|---|---|
| offen | konkret: welche Schrift, welche Farben (Hex), welche Anordnung, warum es wirkt |

## Übertragbar

- **Prinzip behalten:** offen
- **Frei austauschbar:** offen

## Bilder

${bilder}
`);
  const index = join(ziel, 'README.md');
  if (!existsSync(index)) await writeFile(index, '# Inspiration\n\n| Eintrag | Art | Stark in | Stichworte |\n|---|---|---|---|\n');
  const zeilen = (await readFile(index, 'utf8')).endsWith('\n') ? '' : '\n';
  await appendFile(index, `${zeilen}| [${name}](${name}/steckbrief.md) | ${teil ? 'Abschnitt' : 'ganzer Entwurf'} | offen | |\n`);
}
const groesse = Object.values(dateien).reduce((s, b) => s + b.length, 0);
console.log(`✅ ${ordner}/: ${Object.keys(dateien).join(', ')} (${(groesse / 1024).toFixed(0)} KB)${neu ? ', steckbrief.md, Zeile in README.md' : ''}`);
console.log('Weiter: Bilder ansehen (Cookie-Banner?), dann Steckbrief und „Stark in“ nach dem Lob des Auftraggebers füllen (inspiration.md).');
