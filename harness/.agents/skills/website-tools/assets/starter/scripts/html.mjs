// Kleine HTML-Helfer für Layout und Vorlagen (website-tools-Starter; gehört nach dem Kopieren dem Projekt).
// Werte aus der Config immer mit esc() einsetzen: „Müller & Söhne“ bricht sonst das HTML.
const ZEICHEN = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
export const esc = wert => String(wert ?? '').replace(/[&<>"']/g, z => ZEICHEN[z]);

// Sichtbar markierter Platzhalter für Entwürfe. Der Produktions-Build und `seo-pruefen.mjs --livegang` brechen daran ab.
export const platzhalter = was => `<mark class="platzhalter">Platzhalter: ${esc(was)}</mark>`;

// Text vom Kunden oder, solange er fehlt, ein Platzhalter mit der Frage, was fehlt.
export const oder = (text, was) => (text ? esc(text) : platzhalter(was));

export const telHref = telefon => 'tel:' + String(telefon).replace(/[^\d+]/g, '');

// Bild mit festen Maßen (kein Layoutsprung). `zuerst` für das erste große Bild (LCP): nicht lazy, hohe Priorität.
export const bild = (b, { zuerst = false } = {}) => {
  if (!b?.src || b.alt === undefined || !b.width || !b.height) throw new Error(`Bild braucht src, alt (leer bei Dekoration), width und height: ${JSON.stringify(b)}`);
  const laden = zuerst ? ' fetchpriority="high"' : ' loading="lazy"';
  return `<img src="${esc(b.src)}" alt="${esc(b.alt)}" width="${b.width}" height="${b.height}" decoding="async"${laden}>`;
};

// Öffnungszeiten aus schema.org-Tagen (Monday …) als deutscher Text, z. B. „Mo–Fr: 08:00–17:00 Uhr“.
const TAG = { Monday: 'Mo', Tuesday: 'Di', Wednesday: 'Mi', Thursday: 'Do', Friday: 'Fr', Saturday: 'Sa', Sunday: 'So', PublicHolidays: 'Feiertage' };
const WOCHE = Object.keys(TAG);
const tageText = tage => {
  const nr = tage.map(t => WOCHE.indexOf(t));
  const folge = nr.length > 2 && nr.every((x, i) => i === 0 || x === nr[i - 1] + 1);
  return folge ? `${TAG[tage[0]]}–${TAG[tage.at(-1)]}` : tage.map(t => TAG[t]).join(', ');
};
export const zeiten = (oeffnungszeiten = []) => oeffnungszeiten.map(o => `${tageText(o.tage)}: ${o.von}–${o.bis} Uhr`);

// Nachweise (Referenzen, Bewertungen) als Liste: { text, quelle, datum }; nur echte, datierte Angaben vom Kunden.
export const nachweise = (liste = []) => `<ul>${liste.map(n => `<li>${esc(n.text)}${n.quelle || n.datum
  ? ` <small>(${[n.quelle, n.datum].filter(Boolean).map(esc).join(', ')})</small>` : ''}</li>`).join('')}</ul>`;

// Postanschrift als Zeilen (leere Teile entfallen).
export const anschrift = (a = {}) => [a.strasse, [a.plz, a.ort].filter(Boolean).join(' ')].filter(Boolean);
