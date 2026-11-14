// Vorlage Landingpage: ein Hauptthema plus Region (Home-Skelett aus references/sections.md des website-tools-Skills).
// Struktur ohne Gestaltung; Reihenfolge, Abschnitte und Markup frei ändern. Texte kommen aus seite.inhalt in
// src/site.config.mjs oder direkt hierher. Was der Kunde noch liefern muss, bleibt ein sichtbarer Platzhalter.
// Leistungsseiten (vorlage 'leistung') verlinkt der Abschnitt Leistungen automatisch; inhalt.leistungen ergänzt Leistungen ohne eigene Seite.
import { anschrift, bild, esc, nachweise, oder, platzhalter, telHref, zeiten } from '../../scripts/html.mjs';

export default function start({ site, seite, seiten }) {
  const f = site.firma, i = seite.inhalt || {};
  const leistungsseiten = seiten.filter(s => s.vorlage === 'leistung');
  const tel = f.telefon ? `<a class="knopf" href="${telHref(f.telefon)}">${esc(f.telefonAnzeige || f.telefon)}</a>` : '';
  // Erst Leistungen mit eigener Seite (Kartentext: inhalt.karte, sonst description), dann die ohne (inhalt.leistungen).
  const karten = [
    ...leistungsseiten.map(s => `<li><h3><a href="${s.route}">${esc(s.kurz || s.h1)}</a></h3><p>${esc(s.inhalt?.karte || s.description)}</p></li>`),
    ...(i.leistungen || []).map(l => `<li><h3>${esc(l.titel)}</h3><p>${oder(l.text, `ein Satz zu ${l.titel}`)}</p></li>`),
  ];
  return `<section class="held" aria-labelledby="titel">
  <h1 id="titel">${esc(seite.h1)}</h1>
  <p>${oder(i.einleitung, 'ein Satz: was, für wen, wo – in den Worten der Kunden')}</p>
  <p><a class="knopf" href="#kontakt">${esc(i.aktion || 'Anfrage stellen')}</a> ${tel}</p>
  ${i.bild ? bild(i.bild, { zuerst: true }) : ''}
</section>

<section id="leistungen" aria-labelledby="leistungen-titel">
  <h2 id="leistungen-titel">Leistungen</h2>
  ${karten.length ? `<ul class="karten">${karten.join('')}</ul>` : `<p>${platzhalter('die wichtigsten Leistungen mit je einem Satz')}</p>`}
</section>

<section id="referenzen" aria-labelledby="referenzen-titel">
  <h2 id="referenzen-titel">Referenzen</h2>
  ${i.nachweise?.length ? nachweise(i.nachweise)
    : `<p>${platzhalter('echte Referenzen oder Bewertungen mit Ort, Datum und Quelle; Bewertungen mit Hinweis, ob und wie sie geprüft sind')}</p>`}
</section>

<section id="gebiet" aria-labelledby="gebiet-titel">
  <h2 id="gebiet-titel">Einsatzgebiet</h2>
  ${f.einsatzgebiet?.length ? `<ul>${f.einsatzgebiet.map(o => `<li>${esc(o)}</li>`).join('')}</ul>` : `<p>${platzhalter('die echten Orte und Regionen')}</p>`}
</section>

<section id="kontakt" aria-labelledby="kontakt-titel">
  <h2 id="kontakt-titel">Kontakt</h2>
  <p>${oder(i.kontakt, 'ein Satz, was nach der Anfrage passiert')}</p>
  <p>${tel || platzhalter('Telefon oder anderer Kontaktweg')}${f.email ? ` <a href="mailto:${esc(f.email)}">${esc(f.email)}</a>` : ''}</p>
  ${f.oeffnungszeiten?.length ? `<p>${zeiten(f.oeffnungszeiten).map(esc).join('<br>')}</p>` : ''}
  ${anschrift(f.adresse).length ? `<p>${anschrift(f.adresse).map(esc).join('<br>')}</p>` : ''}
</section>`;
}
