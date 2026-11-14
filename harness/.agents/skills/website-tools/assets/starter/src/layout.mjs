// Seitenrahmen aller Seiten: generierter <head>, Kopf- und Fußzeile aus einer Quelle (src/site.config.mjs).
// Markup, Klassen und Gestaltung gehören dem Projekt. Bleiben müssen: ${kopf} im <head>, Sprunglink auf #inhalt,
// Telefon und Anschrift sichtbar (das JSON-LD nennt sie), Rechtsseiten auf jeder Seite verlinkt, Brotkrumen, wenn `pfad` sie liefert.
import { anschrift, esc, telHref, zeiten } from '../scripts/html.mjs';

export default function layout({ site, kopf, pfad, main }) {
  const f = site.firma;
  const tel = f.telefon ? `<a href="${telHref(f.telefon)}">${esc(f.telefonAnzeige || f.telefon)}</a>` : '';
  const kontakt = [...anschrift(f.adresse).map(esc), tel && `Telefon ${tel}`, f.email && `<a href="mailto:${esc(f.email)}">${esc(f.email)}</a>`].filter(Boolean);
  const brotkrumen = pfad.length ? `
<nav class="brotkrumen" aria-label="Seitenpfad"><ol>${pfad.map((s, i) => i < pfad.length - 1
    ? `<li><a href="${esc(s.route)}">${esc(s.name)}</a></li>` : `<li aria-current="page">${esc(s.name)}</li>`).join('')}</ol></nav>` : '';
  return `<!doctype html>
<html lang="${esc(site.sprache)}">
<head>
${kopf}
<link rel="stylesheet" href="/styles/basis.css">
</head>
<body>
<a class="sprunglink" href="#inhalt">Zum Inhalt</a>
<header class="kopfzeile">
  <a class="marke" href="/">${esc(f.name)}</a>
  <nav aria-label="Hauptmenü"><ul>${(site.navigation || []).map(n => `<li><a href="${esc(n.href)}">${esc(n.text)}</a></li>`).join('')}</ul></nav>
  ${tel ? `<p class="kopfzeile-telefon">${tel}</p>` : ''}
</header>${brotkrumen}
<main id="inhalt">
${main}
</main>
<footer class="fusszeile">
  <p><strong>${esc(f.name)}</strong></p>
  ${kontakt.length ? `<address>${kontakt.join('<br>')}</address>` : ''}
  ${f.oeffnungszeiten?.length ? `<p>${zeiten(f.oeffnungszeiten).map(esc).join('<br>')}</p>` : ''}
  <nav aria-label="Rechtliches"><ul>${site.seiten.filter(s => s.art === 'recht').map(s => `<li><a href="${s.route}">${esc(s.kurz || s.h1)}</a></li>`).join('')}</ul></nav>
</footer>
</body>
</html>
`;
}
