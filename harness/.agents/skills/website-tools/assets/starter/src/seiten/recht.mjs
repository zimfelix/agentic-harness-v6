// Vorlage Rechtsseiten (Impressum, Datenschutz): Text vom Kunden oder seinem Rechtstext-Generator als HTML-Datei
// (seite.datei, relativ zu src/), nie erfunden. Klartext im HTML, nicht erst per Klick sichtbar (references/seo.md).
import { esc, platzhalter } from '../../scripts/html.mjs';

export default function recht({ seite, datei }) {
  return `<h1>${esc(seite.h1)}</h1>
${datei || `<p>${platzhalter(`${seite.h1}: Text vom Kunden als HTML-Datei, in src/site.config.mjs als datei eintragen`)}</p>`}`;
}
