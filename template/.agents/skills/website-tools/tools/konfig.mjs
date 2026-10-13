// Einstellungen der Webtools (Profil Website): Standardwerte des Profils, überschrieben von `website.config.mjs` im Projektordner.
// Das Projekt nennt dort nur, was bei ihm anders ist (Pfade, Build-Befehl, Port, interne Routen, ruhende CSS-Dateien).
// Die Webtools laufen aus dem Projektordner (process.cwd()), z. B. über npm-Skripte.
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const standard = {
  name: 'website',            // Kurzname, z. B. für den Dauer-Dienst der Vorschau
  quelle: 'src',              // wird beobachtet; bei Änderungen baut die Vorschau neu
  ausgabe: 'dist',            // gebaute Website
  styles: 'src/styles',       // CSS-Quellen für das Audit ungenutzter Selektoren
  stylesOhne: [],             // CSS-Dateien, die gerade bewusst nicht eingebunden sind
  build: ['node', 'scripts/build.mjs'], // Befehl, der `ausgabe` erzeugt
  port: 4173,                 // lokale Vorschau
  interneOrdner: ['konzepte'],// gebaut, aber nicht Teil der Website (Konzeptseiten): von Prüfungen ausgenommen
  breiten: [1440, 390, 320],  // Projekt-Prüfgrößen; nur Overrides in website.config.mjs
  routen: null,              // erwartete statische Routen; null = entdecken, Soll-Abgleich separat
  bereit: null,             // optionaler JS-Ausdruck für projektspezifische Layoutbereitschaft
  warteMs: 15000,            // begrenztes Browser-/CDP-/Zustandswarten
};

const datei = join(process.cwd(), 'website.config.mjs');
const projekt = existsSync(datei) ? (await import(pathToFileURL(datei).href)).default : {};

// Statischer Ordner ohne Build (z. B. Entwürfe beim Erkunden, init.md Abschnitt 0): ORDNER=entwuerfe liefert und prüft
// diesen Ordner direkt, ohne website.config.mjs und ohne Build; interne Ordner gibt es dann nicht.
const ordner = process.env.ORDNER;
const statisch = ordner ? { quelle: ordner, ausgabe: ordner, styles: ordner, build: null, interneOrdner: [] } : {};

export const konfig = { ...standard, ...projekt, ...statisch };
if (!Number.isInteger(konfig.warteMs) || konfig.warteMs < 100) throw new Error('warteMs muss ein positiver Integer >= 100 sein');
if (konfig.bereit !== null && typeof konfig.bereit !== 'string') throw new Error('bereit muss ein JS-Ausdruck oder null sein');

// Dateitypen für Vorschau und Prüfserver (eine Tabelle für beide).
export const dateitypen = {
  '.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8',
  '.js':'text/javascript; charset=utf-8', '.mjs':'text/javascript; charset=utf-8', '.json':'application/json; charset=utf-8',
  '.txt':'text/plain; charset=utf-8', '.xml':'application/xml; charset=utf-8', '.webmanifest':'application/manifest+json',
  '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.png':'image/png', '.gif':'image/gif', '.webp':'image/webp', '.avif':'image/avif',
  '.svg':'image/svg+xml', '.ico':'image/x-icon', '.woff':'font/woff', '.woff2':'font/woff2', '.ttf':'font/ttf', '.pdf':'application/pdf',
  '.mp4':'video/mp4', '.webm':'video/webm',
};
export const projektOrdner = process.cwd();
