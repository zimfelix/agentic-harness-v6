// Vorlage Leistungsseite: eine echte Suchabsicht mit Nachweis vom Kunden (references/page-plan.md des website-tools-Skills).
// Eine weitere Leistungsseite = ein weiterer Eintrag in src/site.config.mjs mit vorlage 'leistung' und eigenem seite.inhalt.
// Startseite und andere Leistungsseiten verlinken sie automatisch; ab Tiefe 2 (/leistungen/x/) entstehen Brotkrumen.
import { bild, esc, nachweise, oder, platzhalter, telHref } from '../../scripts/html.mjs';

export default function leistung({ site, seite, seiten }) {
  const f = site.firma, i = seite.inhalt || {};
  const tel = f.telefon ? `<a class="knopf" href="${telHref(f.telefon)}">${esc(f.telefonAnzeige || f.telefon)}</a>` : '';
  const andere = seiten.filter(s => s.vorlage === 'leistung' && s !== seite);
  const liste = (eintraege, tag, was) => (eintraege?.length ? `<${tag}>${eintraege.map(e => `<li>${esc(e)}</li>`).join('')}</${tag}>` : `<p>${platzhalter(was)}</p>`);
  return `<section class="held" aria-labelledby="titel">
  <h1 id="titel">${esc(seite.h1)}</h1>
  <p>${oder(i.einleitung, 'was, für wen und wo – ein bis zwei Sätze')}</p>
  <p><a class="knopf" href="#kontakt">${esc(i.aktion || 'Anfrage stellen')}</a> ${tel}</p>
  ${i.bild ? bild(i.bild, { zuerst: true }) : ''}
</section>

<section id="umfang" aria-labelledby="umfang-titel">
  <h2 id="umfang-titel">Was dazugehört</h2>
  ${liste(i.punkte, 'ul', 'was genau zur Leistung gehört')}
</section>

<section id="ablauf" aria-labelledby="ablauf-titel">
  <h2 id="ablauf-titel">Ablauf</h2>
  ${liste(i.ablauf, 'ol', 'drei bis fünf echte Schritte')}
</section>
${i.preis ? `
<section id="preise" aria-labelledby="preise-titel">
  <h2 id="preise-titel">Preise</h2>
  <p>${esc(i.preis)}</p>
</section>` : ''}${i.nachweise?.length ? `
<section id="referenzen" aria-labelledby="referenzen-titel">
  <h2 id="referenzen-titel">Referenzen</h2>
  ${nachweise(i.nachweise)}
</section>` : ''}${i.fragen?.length ? `
<section id="fragen" aria-labelledby="fragen-titel">
  <h2 id="fragen-titel">Häufige Fragen</h2>
  ${i.fragen.map(q => `<details><summary>${esc(q.frage)}</summary><p>${esc(q.antwort)}</p></details>`).join('\n  ')}
</section>` : ''}

<section id="kontakt" aria-labelledby="kontakt-titel">
  <h2 id="kontakt-titel">Kontakt</h2>
  <p>${f.einsatzgebiet?.length ? `Im Einsatz in ${esc(f.einsatzgebiet.join(', '))}.` : platzhalter('Einsatzgebiet')}</p>
  <p>${tel || platzhalter('Telefon oder anderer Kontaktweg')}${f.email ? ` <a href="mailto:${esc(f.email)}">${esc(f.email)}</a>` : ''}</p>
</section>${andere.length ? `

<nav class="weitere" aria-labelledby="weitere-titel">
  <h2 id="weitere-titel">Weitere Leistungen</h2>
  <ul>${andere.map(s => `<li><a href="${s.route}">${esc(s.kurz || s.h1)}</a></li>`).join('')}</ul>
</nav>` : ''}`;
}
