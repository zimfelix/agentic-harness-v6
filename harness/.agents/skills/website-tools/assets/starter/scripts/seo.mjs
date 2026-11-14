// Generatoren für SEO by Design (Regeln und Begründungen: references/seo.md des website-tools-Skills): head, JSON-LD,
// Brotkrumen, sitemap.xml, robots.txt und ein Ersatz-Favicon. Reine Funktionen: Projektdaten rein, Text raus;
// build.mjs schreibt die Dateien. Vorschau und Produktion unterscheiden sich nur in noindex.
import { crc32, deflateSync } from 'node:zlib';
import { esc } from './html.mjs';

export const ursprung = site => new URL(site.siteUrl).origin;
export const absolut = (site, pfad) => new URL(pfad, ursprung(site) + '/').href;
export const istSonder = seite => seite.art === 'sonder';
export const istSuche = seite => !seite.art || seite.art === 'suche';

// Sonderseiten (404, Danke) tragen immer noindex, in der Vorschau jede Seite. Sonst ist alles gleich.
export const indexierbar = (seite, umgebung) => umgebung === 'produktion' && !istSonder(seite);

// ---------- head ----------
export function kopf({ site, seite, umgebung, icons = [], daten = [] }) {
  const z = [
    '<meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width, initial-scale=1">',
    `<title>${esc(seite.title)}</title>`,
  ];
  if (seite.description) z.push(`<meta name="description" content="${esc(seite.description)}">`);
  if (!indexierbar(seite, umgebung)) z.push('<meta name="robots" content="noindex">');
  if (!istSonder(seite)) {
    const url = absolut(site, seite.route), ogBild = seite.ogBild || site.ogBild;
    z.push(`<link rel="canonical" href="${esc(url)}">`,
      '<meta property="og:type" content="website">',
      `<meta property="og:url" content="${esc(url)}">`,
      `<meta property="og:title" content="${esc(seite.title)}">`);
    if (seite.description) z.push(`<meta property="og:description" content="${esc(seite.description)}">`);
    if (ogBild) z.push(`<meta property="og:image" content="${esc(absolut(site, ogBild))}">`);
    z.push(`<meta property="og:site_name" content="${esc(site.firma.name)}">`, `<meta property="og:locale" content="${esc(site.locale)}">`);
  }
  for (const i of icons) z.push(`<link rel="${i.rel}" href="${esc(i.href)}"${i.type ? ` type="${i.type}"` : ''}${i.sizes ? ` sizes="${i.sizes}"` : ''}>`);
  if (site.farbe) z.push(`<meta name="theme-color" content="${esc(site.farbe)}">`);
  if (daten.length) z.push(jsonLd(daten.length === 1 ? daten[0] : { '@graph': daten }));
  return z.join('\n');
}

// JSON-LD als <script>; „<“ maskiert, damit Texte wie „</script>“ den Block nicht beenden.
export const jsonLd = objekt => `<script type="application/ld+json">${JSON.stringify({ '@context': 'https://schema.org', ...objekt }).replace(/</g, '\\u003c')}</script>`;

const ohneLeere = wert => {
  if (Array.isArray(wert)) { const a = wert.map(ohneLeere).filter(x => x !== undefined); return a.length ? a : undefined; }
  if (wert && typeof wert === 'object') {
    const o = Object.fromEntries(Object.entries(wert).map(([k, v]) => [k, ohneLeere(v)]).filter(([, v]) => v !== undefined));
    return Object.keys(o).some(k => !k.startsWith('@')) ? o : undefined;
  }
  return wert === '' || wert === null ? undefined : wert;
};

// ---------- strukturierte Daten (nur, was die Seiten sichtbar sagen; gleiche Quelle wie Fußzeile und Impressum) ----------
export function firmaDaten(site) {
  const f = site.firma, a = f.adresse || {}, u = ursprung(site);
  return ohneLeere({
    '@type': f.typ || 'LocalBusiness',
    '@id': `${u}/#firma`,
    name: f.name,
    description: f.beschreibung,
    url: `${u}/`,
    telephone: f.telefon,
    email: f.email,
    image: f.logo || site.ogBild ? absolut(site, f.logo || site.ogBild) : undefined,
    logo: f.logo ? absolut(site, f.logo) : undefined,
    address: a.strasse || a.ort // nur mit echter Anschrift; ein Land allein ist keine
      ? { '@type': 'PostalAddress', streetAddress: a.strasse, postalCode: a.plz, addressLocality: a.ort, addressRegion: a.region, addressCountry: a.land }
      : undefined,
    openingHoursSpecification: (f.oeffnungszeiten || []).map(o => ({ '@type': 'OpeningHoursSpecification', dayOfWeek: o.tage, opens: o.von, closes: o.bis })),
    areaServed: f.einsatzgebiet,
    sameAs: f.sameAs,
  });
}

export const websiteDaten = site => ({
  '@type': 'WebSite', '@id': `${ursprung(site)}/#website`, url: `${ursprung(site)}/`,
  name: site.firma.name, inLanguage: site.sprache, publisher: { '@id': `${ursprung(site)}/#firma` },
});

// Brotkrumen ab Tiefe 2 (/leistungen/x/): Start, vorhandene Elternseiten, aktuelle Seite. Sichtbar und als JSON-LD aus derselben Liste.
export function pfad(seite, seiten) {
  const teile = seite.route.split('/').filter(Boolean);
  if (istSonder(seite) || teile.length < 2) return [];
  const kette = [seiten.find(s => s.route === '/')];
  for (let i = 1; i < teile.length; i++) {
    const eltern = seiten.find(s => s.route === `/${teile.slice(0, i).join('/')}/`);
    if (eltern) kette.push(eltern);
  }
  kette.push(seite);
  return kette.map(s => ({ name: s.kurz || (s.route === '/' ? 'Start' : s.h1), route: s.route }));
}

export const brotkrumenDaten = (site, schritte) => ({
  '@type': 'BreadcrumbList',
  itemListElement: schritte.map((s, i) => ({ '@type': 'ListItem', position: i + 1, name: s.name, item: absolut(site, s.route) })),
});

// ---------- sitemap.xml und robots.txt (in beiden Umgebungen gleich) ----------
export function sitemap(site, seiten) {
  const urls = seiten.filter(s => !istSonder(s)).map(s =>
    `  <url>\n    <loc>${esc(absolut(site, s.route))}</loc>${s.geaendert ? `\n    <lastmod>${s.geaendert}</lastmod>` : ''}\n  </url>`);
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`;
}

// KI-Crawler-Politik ist eine Kundenentscheidung (seo.md, KI-Suche): 'alle' = Voreinstellung A, 'nurSuche' = B.
export const KI_SUCHE = ['OAI-SearchBot', 'Claude-SearchBot', 'PerplexityBot'];
export const KI_TRAINING = ['GPTBot', 'ClaudeBot', 'Applebot-Extended', 'CCBot', 'Google-Extended'];
export function robots(site) {
  const z = ['User-agent: *', 'Allow: /', ''];
  if (site.kiCrawler === 'nurSuche') z.push('# KI-Suche ja, KI-Training nein', ...KI_SUCHE.map(a => `User-agent: ${a}`), 'Allow: /', '',
    ...KI_TRAINING.map(a => `User-agent: ${a}`), 'Disallow: /', '');
  z.push(`Sitemap: ${absolut(site, '/sitemap.xml')}`);
  return z.join('\n') + '\n';
}

// ---------- Ersatz-Favicon: einfarbiges PNG, solange das Projekt kein eigenes Icon hat ----------
export function favicon(farbe, kante = 192) {
  const [r, g, b] = farbe.slice(1).match(/../g).map(x => parseInt(x, 16));
  const zeile = Buffer.alloc(1 + kante * 3); // Filterbyte 0, dann RGB
  for (let x = 0; x < kante; x++) zeile.set([r, g, b], 1 + x * 3);
  const block = (typ, daten) => {
    const kopfteil = Buffer.alloc(8); kopfteil.writeUInt32BE(daten.length); kopfteil.write(typ, 4, 'latin1');
    const pruef = Buffer.alloc(4); pruef.writeUInt32BE(crc32(Buffer.concat([kopfteil.subarray(4), daten])));
    return Buffer.concat([kopfteil, daten, pruef]);
  };
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(kante, 0); ihdr.writeUInt32BE(kante, 4); ihdr[8] = 8; ihdr[9] = 2;
  return Buffer.concat([Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]), block('IHDR', ihdr),
    block('IDAT', deflateSync(Buffer.concat(Array(kante).fill(zeile)))), block('IEND', Buffer.alloc(0))]);
}
