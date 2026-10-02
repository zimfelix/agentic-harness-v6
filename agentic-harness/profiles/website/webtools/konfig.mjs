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
  breiten: [1440, 390, 320],  // Prüfgrößen (docs/testing.md im Projekt)
};

const datei = join(process.cwd(), 'website.config.mjs');
const projekt = existsSync(datei) ? (await import(pathToFileURL(datei).href)).default : {};

export const konfig = { ...standard, ...projekt };
export const projektOrdner = process.cwd();
