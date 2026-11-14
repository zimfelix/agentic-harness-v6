// Vorlage 404-Seite: noindex, kein canonical, nicht in der Sitemap; in der Sprache der Website und mit Wegen weiter.
// Der Host muss sie mit Status 404 ausliefern (prüft `seo-pruefen.mjs --live`).
import { esc } from '../../scripts/html.mjs';

export default function fehler({ seite, seiten }) {
  const wege = seiten.filter(s => !s.art || s.art === 'suche');
  return `<h1>${esc(seite.h1)}</h1>
<p>Diese Adresse gibt es nicht (mehr). Weiter geht es hier:</p>
<ul>${wege.map(s => `<li><a href="${s.route}">${esc(s.kurz || s.h1)}</a></li>`).join('')}</ul>`;
}
