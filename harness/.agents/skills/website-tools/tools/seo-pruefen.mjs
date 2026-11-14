// SEO-Prüfer für gebaute statische Websites (Regeln und Begründungen: references/seo.md dieses Skills).
// Liest nur Dateien des Build-Ordners (eigenes, generiertes HTML; kein Browser, keine Pakete) und prüft strukturelle Regeln:
// Title/Description, canonical = Sitemap = og:url, noindex/robots.txt/Sitemap passen zusammen, interne Links und Anker,
// erreichbare Seiten, JSON-LD, Bilder, Favicon, hreflang, Platzhalter und Google Fonts. Werte stehen im Projekt:
// website.config.mjs → seo: { siteUrl, schraegstrich, sonderseiten, platzhalter, pflichtLinks }.
// Aufruf aus dem Projektordner, vorher bauen:
//   node <webtools>/seo-pruefen.mjs [build-ordner] [--livegang] [--live [https://www.example.de]]
//   --livegang  prüft, als wäre noindex schon entfernt: jede Seite außer seo.sonderseiten muss als Suchseite vollständig sein.
//   --live      zusätzlich HTTP-Prüfungen am veröffentlichten Stand (nur GET): noindex, robots.txt, 404, Weiterleitungen, Sitemap-URLs.
// Ergebnis: ❌ harte Fehler (Exit-Code 1), ⚠️ Hinweise, ❓ Fragen zur Beurteilung. Bestanden heißt nicht „rankt“.
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join, relative, resolve, extname } from 'node:path';
import { konfig } from './konfig.mjs';

const args = process.argv.slice(2);
const livegang = args.includes('--livegang');
const liveIndex = args.indexOf('--live');
const liveWert = liveIndex >= 0 && /^https?:\/\//.test(args[liveIndex + 1] || '') ? args[liveIndex + 1] : null;
const ordnerArg = args.find((a, i) => !a.startsWith('--') && !(liveWert && i === liveIndex + 1));
const root = resolve(ordnerArg ?? konfig.ausgabe);

const seo = {
  siteUrl: null,                                // Produktions-URL, eine Quelle für canonical, Sitemap und og:url
  schraegstrich: 'immer',                       // URL-Form: 'immer' (/leistung/) oder 'nie' (/leistung)
  sonderseiten: ['/404/', '/404.html', '/404'], // Fehler-/Danke-Seiten: dürfen noindex tragen, keine Suchseiten
  platzhalter: ['lorem ipsum', '\\bTODO\\b', '\\bTBD\\b', 'example\\.(com|org|net)', 'platzhalter', 'placeholder'],
  pflichtLinks: [],                             // Routen, die jede Seite verlinken muss, z. B. Impressum und Datenschutz
  ...(konfig.seo || {}),
};
if (!['immer', 'nie'].includes(seo.schraegstrich)) throw new Error("seo.schraegstrich muss 'immer' oder 'nie' sein");
const site = seo.siteUrl ? new URL(seo.siteUrl) : null;
const liveUrl = liveIndex >= 0 ? (liveWert ?? site?.href) : null;
if (liveIndex >= 0 && !liveUrl) throw new Error('--live braucht eine URL oder seo.siteUrl in website.config.mjs');
if (!existsSync(root)) throw new Error(`Build-Ordner fehlt: ${root} (vorher bauen)`);

// ---------- Einlesen ----------
const dateienIn = (dir, endung, gefunden = []) => {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const pfad = join(dir, e.name);
    if (e.isDirectory()) { if (!(dir === root && konfig.interneOrdner.includes(e.name))) dateienIn(pfad, endung, gefunden); }
    else if (e.name.endsWith(endung)) gefunden.push(pfad);
  }
  return gefunden;
};
const htmlDateien = dateienIn(root, '.html');
if (!htmlDateien.length) throw new Error(`Keine HTML-Seiten in ${root}; kein Nachweis`);

const ENT = { amp: '&', quot: '"', apos: "'", lt: '<', gt: '>', nbsp: ' ' };
const ent = s => s.replace(/&(?:#(\d+)|#x([0-9a-f]+)|(amp|quot|apos|lt|gt|nbsp));/gi,
  (_, d, h, n) => d ? String.fromCodePoint(+d) : h ? String.fromCodePoint(parseInt(h, 16)) : ENT[n.toLowerCase()]);
const attrs = s => {
  const a = {};
  for (const m of s.matchAll(/([^\s=\/>"']+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)) a[m[1].toLowerCase()] = ent(m[2] ?? m[3] ?? m[4] ?? '');
  return a;
};
const tags = (html, name) => [...html.matchAll(new RegExp(`<${name}(?=[\\s>/])([^>]*)>`, 'gi'))].map(m => attrs(m[1]));
const text = html => ent(html.replace(/<(svg|template)\b[\s\S]*?<\/\1>/gi, ' ').replace(/<!--[\s\S]*?-->/g, ' ')
  .replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();
const hatRel = (l, ...r) => (l.rel || '').toLowerCase().split(/\s+/).some(x => r.includes(x));
const NOINDEX = /noindex|\bnone\b/i;
const metaNoindex = html => tags(html, 'meta').some(m => /^(robots|googlebot)$/i.test(m.name || '') && NOINDEX.test(m.content || ''));
const nie = seo.schraegstrich === 'nie';
const routeVon = datei => {
  const r = '/' + relative(root, datei).replaceAll('\\', '/').replace(/(^|\/)index\.html$/, '$1');
  return nie && r !== '/' ? r.replace(/\/$/, '').replace(/\.html$/, '') : r;
};
const FREMDFONTS = /^(https?:)?\/\/fonts\.(googleapis|gstatic)\.com/i;

const seiten = htmlDateien.map(datei => {
  const roh = readFileSync(datei, 'utf8');
  const jsonld = [...roh.matchAll(/<script\b[^>]*type\s*=\s*["']?application\/ld\+json["']?[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
  const styleUrls = [...roh.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)]
    .flatMap(m => [...m[1].matchAll(/(?:@import\s+(?:url\()?|url\()\s*['"]?([^'")\s;]+)/gi)].map(x => x[1]));
  const html = roh.replace(/<(script|style|template)\b([^>]*)>[\s\S]*?<\/\1>/gi, '<$1$2></$1>'); // Inhalte von Skripten zählen nicht
  const kopf = (html.match(/<head\b[^>]*>([\s\S]*?)<\/head>/i) || [, html.split(/<body\b/i)[0]])[1];
  const main = html.match(/<main\b[^>]*>([\s\S]*?)<\/main>/i)?.[1] ?? html.match(/<body\b[^>]*>([\s\S]*)<\/body>/i)?.[1] ?? html;
  const metas = tags(html, 'meta');
  const meta = name => metas.filter(m => (m.name || '').toLowerCase() === name).map(m => (m.content || '').trim());
  const alleLinks = tags(html, 'link'), kopfLinks = tags(kopf, 'link');
  return {
    route: routeVon(datei), html, jsonld,
    noindex: metaNoindex(html), // Google beachtet robots-meta auch im body
    titel: [...kopf.matchAll(/<title\b[^>]*>([\s\S]*?)<\/title>/gi)].map(m => ent(m[1]).replace(/\s+/g, ' ').trim()),
    description: meta('description')[0] || '',
    viewport: meta('viewport').length > 0,
    lang: attrs((html.match(/<html\b([^>]*)>/i) || [, ''])[1]).lang,
    og: Object.fromEntries(metas.filter(m => (m.property || '').startsWith('og:')).map(m => [m.property, m.content])),
    canonicals: kopfLinks.filter(l => hatRel(l, 'canonical')).map(l => l.href),
    canonicalsGesamt: alleLinks.filter(l => hatRel(l, 'canonical')).length,
    hreflang: kopfLinks.filter(l => hatRel(l, 'alternate') && l.hreflang).map(l => ({ lang: l.hreflang, href: l.href })),
    icons: kopfLinks.filter(l => hatRel(l, 'icon', 'apple-touch-icon', 'apple-touch-icon-precomposed')).map(l => l.href),
    h1: (html.match(/<h1\b/gi) || []).length,
    anker: [...html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/gi)].map(m => ({ ...attrs(m[1]), text: text(m[2]) })),
    bilder: tags(html, 'img'), mainBilder: tags(main, 'img'),
    ids: new Set([...html.matchAll(/\s(?:id|name)\s*=\s*(?:"([^"]+)"|'([^']+)'|([^\s>"']+))/gi)].map(m => m[1] ?? m[2] ?? m[3])),
    text: text(main), ganzText: text(html),
    googleFonts: [...alleLinks.map(l => l.href), ...tags(roh, 'script').map(s => s.src), ...styleUrls].some(u => FREMDFONTS.test(u || '')),
    eingebunden: [...tags(html, 'script'), ...tags(html, 'img'), ...tags(html, 'iframe'), ...tags(html, 'source')].map(t => t.src)
      .concat(alleLinks.filter(l => hatRel(l, 'stylesheet')).map(l => l.href)).filter(Boolean),
  };
});

// robots.txt lesen: Google folgt der Gruppe „googlebot“, sonst „*“; längste passende Regel gewinnt, bei Gleichstand Allow.
const robotsLesen = txt => {
  const gruppen = []; let g = null, regeln = false;
  for (const zeile of txt.split(/\r?\n/)) {
    const ohne = zeile.replace(/#.*/, ''), i = ohne.indexOf(':'); if (i < 0) continue;
    const feld = ohne.slice(0, i).trim().toLowerCase(), wert = ohne.slice(i + 1).trim();
    if (feld === 'user-agent') { if (!g || regeln) { g = { agents: [], allow: [], disallow: [] }; gruppen.push(g); regeln = false; } g.agents.push(wert.toLowerCase()); }
    else if (g && (feld === 'allow' || feld === 'disallow')) { regeln = true; if (wert) g[feld].push(wert); }
  }
  const google = gruppen.filter(x => x.agents.includes('googlebot'));
  const gilt = google.length ? google : gruppen.filter(x => x.agents.includes('*'));
  const disallow = gilt.flatMap(x => x.disallow), allow = gilt.flatMap(x => x.allow);
  const muster = m => new RegExp('^' + m.replace(/[.+?^{}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*'));
  const laengster = (liste, pfad) => Math.max(-1, ...liste.filter(m => muster(m).test(pfad)).map(m => m.length));
  return { disallow, gesperrt: pfad => laengster(disallow, pfad) > laengster(allow, pfad) };
};

// ---------- Befunde ----------
const befunde = [], infos = [], fragen = [];
const melde = art => (wo, text) => { if (!befunde.some(b => b.art === art && b.wo === wo && b.text === text)) befunde.push({ art, wo, text }); };
const hart = melde('hart'), hinweis = melde('hinweis');

const nachRoute = new Map(seiten.map(s => [s.route, s]));
const sonder = s => seo.sonderseiten.includes(s.route);
const ziel = seiten.filter(s => !sonder(s) && (livegang || !s.noindex)); // Seiten, die (nach dem Livegang) gefunden werden sollen
const istZiel = new Set(ziel);
const absolut = route => site ? new URL(route, site).href : null;
const INTERN = 'https://intern.invalid';
const pfadVon = href => { try { return decodeURIComponent(new URL(href, INTERN).pathname); } catch { return null; } };
const soll = s => absolut(s.route) ?? s.route;
const vergleich = url => { try { const u = new URL(url, INTERN); return site ? u.href : decodeURIComponent(u.pathname); } catch { return url; } };
const formen = p => [p + '/', p.replace(/\/$/, ''), p.replace(/index\.html$/, ''), p.replace(/\/index\.html$/, ''), p.replace(/\.html$/, '')];
const platzhalter = new RegExp(seo.platzhalter.join('|'), 'i');
const kanten = new Map(seiten.map(s => [s.route, new Set()]));
const telefone = new Set(), strassen = new Set(), fremdeHosts = new Set();
const TAGE = /^(https?:\/\/schema\.org\/)?(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|PublicHolidays)$/;
// Firmen-Typen einschließlich üblicher LocalBusiness-Untertypen (Electrician, Bakery, ProfessionalService …); „Service“ allein ist ein Angebot.
const FIRMA = /(Organization|LocalBusiness|Business|Store|Shop|Contractor|Establishment|Restaurant|Bakery|Electrician|Plumber|Locksmith|Painter|Salon|Spa|Florist|Winery|Brewery|Distillery|Dentist|Physician|Agent|Agency|Office|Repair|Dealer|Hotel|.Service)$/;
const NUR_ORG = /^(Organization|Corporation|NGO|OnlineBusiness|OnlineStore|NewsMediaOrganization|EducationalOrganization|GovernmentOrganization|SportsOrganization|PerformingGroup)$/;
const knoten = (x, alle = []) => {
  if (Array.isArray(x)) x.forEach(y => knoten(y, alle));
  else if (x && typeof x === 'object') { alle.push(x); Object.values(x).forEach(y => knoten(y, alle)); }
  return alle;
};
const GENERISCH = new Set(['hier', 'mehr', 'mehr erfahren', 'weiterlesen', 'hier klicken', 'klicken sie hier', 'link', 'click here', 'read more', 'more', 'here']);

if (livegang && !site) hart('Website', 'seo.siteUrl fehlt in website.config.mjs (eine Quelle für canonical, Sitemap und og:url)');
else if (ziel.length && !site) hinweis('Website', 'seo.siteUrl fehlt: canonical und Sitemap werden nur nach Pfad geprüft');
if (site && site.protocol !== 'https:') hart('Website', `seo.siteUrl ohne https: ${site.href}`);
if (livegang) {
  const noch = seiten.filter(s => s.noindex && !sonder(s)).length;
  if (noch) infos.push(`${noch} Seiten tragen noch noindex: im Produktions-Build entfernen; \`--live\` prüft das nach dem Deploy.`);
}

for (const s of seiten) {
  const r = s.route, imZiel = istZiel.has(s);

  // Interne Links und Anker (alle Seiten)
  for (const a of s.anker) {
    const href = (a.href || '').trim();
    if (!href || /^(mailto:|tel:|javascript:|data:|sms:)/i.test(href)) continue;
    let u; try { u = new URL(href, INTERN + r); } catch { hart(r, `ungültiger Link: ${href}`); continue; }
    if (u.origin !== INTERN && !(site && u.hostname === site.hostname)) continue;
    const pfad = decodeURIComponent(u.pathname);
    let t = nachRoute.get(pfad);
    if (!t) {
      const alt = formen(pfad).find(f => f && nachRoute.has(f));
      if (alt) { t = nachRoute.get(alt); hinweis(r, `Link nicht in kanonischer Form (kostet eine Weiterleitung): ${href} → ${alt}`); }
    }
    if (!t) { if (!existsSync(join(root, pfad))) hart(r, `toter interner Link: ${href}`); continue; }
    kanten.get(r).add(t.route);
    const anker = decodeURIComponent(u.hash.slice(1));
    if (anker && anker !== 'top' && !t.ids.has(anker)) hart(r, `Anker fehlt im Ziel: ${href}`);
    if (imZiel && GENERISCH.has(a.text.toLowerCase())) hinweis(r, `nichtssagender Linktext „${a.text}“ (Ziel benennen)`);
  }

  // JSON-LD (alle Seiten)
  for (const block of s.jsonld) {
    let daten; try { daten = JSON.parse(block); } catch (e) { hart(r, `JSON-LD nicht lesbar: ${e.message}`); continue; }
    for (const k of knoten(daten)) {
      const typen = [].concat(k['@type'] || []).map(String);
      if (typen.some(t => /^(FAQPage|HowTo)$/.test(t))) hinweis(r, `${typen.join('/')}-Markup erzeugt kein Rich Result mehr (Inhalt darf bleiben)`);
      const firma = typen.some(t => FIRMA.test(t));
      const lokal = typen.some(t => FIRMA.test(t) && !NUR_ORG.test(t)) || ['openingHoursSpecification', 'openingHours', 'priceRange'].some(f => f in k);
      if (firma && (k.aggregateRating || k.review)) hart(r, 'eigene Bewertungen/Sterne im Firmen-Markup sind nicht zulässig (self-serving)');
      if (lokal && (!k.name || !k.address)) hart(r, `${typen.join('/') || 'LocalBusiness'}-Markup ohne name oder address`);
      for (const o of [].concat(k.openingHoursSpecification || [])) for (const t of [].concat(o?.dayOfWeek || [])) if (!TAGE.test(String(t))) hart(r, `dayOfWeek muss englisch sein (schema.org): ${t}`);
      for (const o of [].concat(k.openingHours || [])) if (/\b(Di|Mi|Do|So)\b|montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag/i.test(String(o))) hart(r, `openingHours mit deutschen Tagen: ${o}`);
      if (typeof k.telephone === 'string') { telefone.add(k.telephone); if (!k.telephone.trim().startsWith('+')) hinweis(r, `Telefon im JSON-LD nicht international (+49 …): ${k.telephone}`); }
      if (k.address && typeof k.address === 'object' && typeof k.address.streetAddress === 'string') strassen.add(k.address.streetAddress);
    }
  }

  // Einbindungen, Bilder, Platzhalter (alle Seiten)
  if (s.googleFonts) hart(r, 'Google Fonts vom Google-Server eingebunden (selbst hosten; DSGVO)');
  for (const src of s.eingebunden) {
    if (/^http:\/\//i.test(src)) hart(r, `unsicher per http eingebunden: ${src}`);
    try { const u = new URL(src, INTERN); if (u.origin !== INTERN && !(site && u.hostname === site.hostname)) fremdeHosts.add(u.hostname); } catch {}
  }
  if (s.bilder.some(b => !('alt' in b))) hart(r, `${s.bilder.filter(b => !('alt' in b)).length} Bild(er) ohne alt (leer bei Dekoration)`);
  const p = (s.titel.join(' ') + ' ' + s.ganzText).match(platzhalter);
  if (p) (imZiel ? hart : hinweis)(r, `Platzhalter im Text: „${p[0]}“${imZiel ? '' : ' (vor dem Livegang füllen oder entfernen)'}`);

  if (!imZiel) continue;
  // ---- nur Seiten, die gefunden werden sollen ----
  if (s.titel.length !== 1 || !s.titel[0]) hart(r, `genau ein nicht leerer <title> nötig (gefunden: ${s.titel.length})`);
  else if (/^(startseite|home|homepage|untitled|unbenannt)$/i.test(s.titel[0])) hart(r, `Title ohne Inhalt: „${s.titel[0]}“`);
  else if (s.titel[0].length > 60) hinweis(r, `Title hat ${s.titel[0].length} Zeichen (Faustregel ≈ 60, kein Google-Limit)`);
  if (!s.description) hart(r, 'Meta-Description fehlt (Hausregel)');
  else if (s.description.length < 50 || s.description.length > 160) hinweis(r, `Description hat ${s.description.length} Zeichen (Faustregel 50–160)`);
  if (!s.lang) hart(r, '<html lang> fehlt');
  if (!s.viewport) hart(r, 'meta viewport fehlt');
  if (s.h1 !== 1) hinweis(r, `${s.h1} H1 (Hausregel: genau eine, passend zur Hauptabsicht)`);
  if (/[A-Z_]/.test(r)) hinweis(r, 'URL mit Großbuchstaben oder Unterstrich (klein, mit Bindestrichen)');

  if (s.canonicals.length !== 1) hart(r, `genau ein canonical im <head> nötig (gefunden: ${s.canonicals.length})`);
  else {
    let u; try { u = new URL(s.canonicals[0]); } catch { hart(r, `canonical nicht absolut: ${s.canonicals[0]}`); }
    if (u && u.protocol !== 'https:') hart(r, `canonical ohne https: ${u.href}`);
    if (u && vergleich(u.href) !== vergleich(soll(s))) hart(r, `canonical nicht selbstreferenzierend: ${u.href} (erwartet ${soll(s)})`);
  }
  if (s.canonicalsGesamt > s.canonicals.length) hart(r, 'canonical außerhalb des <head> wird ignoriert');
  if (s.og['og:url'] && s.canonicals[0] && s.og['og:url'] !== s.canonicals[0]) hart(r, `og:url weicht vom canonical ab: ${s.og['og:url']}`);
  const ogFehlt = ['og:title', 'og:description', 'og:image', 'og:url'].filter(k => !s.og[k]);
  if (ogFehlt.length) hinweis(r, `Open Graph fehlt: ${ogFehlt.join(', ')}`);

  const ohneMass = s.bilder.filter(b => !b.width || !b.height).length;
  if (ohneMass) hinweis(r, `${ohneMass} Bild(er) ohne width/height (Layoutsprünge, CLS)`);
  if (s.mainBilder[0]?.loading === 'lazy') hinweis(r, 'erstes Bild im Inhalt ist lazy: ist es das LCP-Bild, nicht lazy laden');
  if (s.bilder.filter(b => b.fetchpriority === 'high').length > 1) hinweis(r, 'mehrere Bilder mit fetchpriority=high');
  const fuehrtZu = (href, route) => { const p = pfadVon(href || ''); return !!p && (p === route || formen(p).includes(route)); };
  for (const pflicht of seo.pflichtLinks) if (!s.anker.some(a => fuehrtZu(a.href, pflicht))) hart(r, `Pflichtlink fehlt: ${pflicht}`);

  for (const h of s.hreflang) {
    if (!/^(x-default|[a-z]{2,3}(-[A-Za-z]{4})?(-([A-Za-z]{2}|\d{3}))?)$/.test(h.lang)) hart(r, `ungültiger hreflang-Code: ${h.lang}`);
    const t = nachRoute.get(pfadVon(h.href));
    if (!t) { hart(r, `hreflang-Ziel nicht im Build: ${h.href}`); continue; }
    if (t !== s && !t.hreflang.some(x => pfadVon(x.href) === r)) hart(r, `hreflang nicht gegenseitig: ${t.route} verweist nicht zurück`);
  }
  if (s.hreflang.length && !s.hreflang.some(h => pfadVon(h.href) === r)) hart(r, 'hreflang ohne Verweis auf sich selbst');
}
if (fremdeHosts.size) hinweis('Website', `fremde Einbindungen (${[...fremdeHosts].join(', ')}): nur nach Einwilligung laden, wenn sie Daten übertragen (DE § 25 TDDDG, AT § 165 TKG)`);

// Gleiche Titles und Descriptions, Fast-Duplikate
const gruppiere = feld => {
  const m = new Map();
  for (const s of ziel) { const w = feld(s); if (w) m.set(w, [...(m.get(w) || []), s.route]); }
  return [...m].filter(([, routen]) => routen.length > 1);
};
for (const [w, routen] of gruppiere(s => s.titel[0])) hart('Website', `gleicher Title auf ${routen.join(', ')}: „${w}“`);
for (const [, routen] of gruppiere(s => s.description)) hinweis('Website', `gleiche Description auf ${routen.join(', ')}`);
const schindeln = t => { const w = t.toLowerCase().split(/[^\p{L}\p{N}]+/u).filter(Boolean); return new Set(w.slice(0, -2).map((_, i) => w.slice(i, i + 3).join(' '))); };
const sch = ziel.slice(0, 300).map(s => ({ s, m: schindeln(s.text) })).filter(x => x.m.size >= 30);
for (let i = 0; i < sch.length; i++) for (let j = i + 1; j < sch.length; j++) {
  const a = sch[i].m, b = sch[j].m; let gemeinsam = 0; for (const x of a) if (b.has(x)) gemeinsam++;
  const jaccard = gemeinsam / (a.size + b.size - gemeinsam);
  if (jaccard > 0.8) hinweis('Website', `${sch[i].s.route} und ${sch[j].s.route} sind fast gleich (${Math.round(jaccard * 100)} %): Doorway-Verdacht, references/page-plan.md`);
}

// Erreichbarkeit von der Startseite aus
if (ziel.length) {
  if (!nachRoute.has('/')) hart('Website', 'Startseite / fehlt im Build');
  else {
    const tiefe = new Map([['/', 0]]), warteschlange = ['/'];
    while (warteschlange.length) { const r = warteschlange.shift(); for (const t of kanten.get(r)) if (!tiefe.has(t)) { tiefe.set(t, tiefe.get(r) + 1); warteschlange.push(t); } }
    for (const s of ziel) {
      if (!tiefe.has(s.route)) hart(s.route, 'von / aus nicht verlinkt (verwaiste Seite)');
      else if (tiefe.get(s.route) > 3) hinweis(s.route, `${tiefe.get(s.route)} Klicks von der Startseite (Faustregel ≤ 3)`);
    }
  }
}

// Sitemap (Hausregel: immer eine, genau mit den Suchseiten)
const lesen = name => existsSync(join(root, name)) ? readFileSync(join(root, name), 'utf8') : null;
const sitemap = lesen('sitemap.xml');
if (ziel.length && !sitemap) hart('Website', 'sitemap.xml fehlt (Hausregel)');
if (sitemap && /<sitemapindex\b/i.test(sitemap)) hinweis('Website', 'Sitemap-Index: Unter-Sitemaps prüft dieses Skript nicht');
else if (sitemap) {
  const locs = [...sitemap.matchAll(/<loc>\s*([^<]+?)\s*<\/loc>/gi)].map(m => ent(m[1]));
  const drin = new Set(locs.map(vergleich));
  for (const s of ziel) if (!drin.has(vergleich(soll(s)))) hart(s.route, 'fehlt in sitemap.xml');
  const erwartet = new Set(ziel.map(s => vergleich(soll(s))));
  let ruhend = 0; // ganzer Build noindex (Vorschau = Produktion + noindex): der Abgleich ruht wie die übrigen Index-Regeln
  for (const loc of locs) if (!erwartet.has(vergleich(loc))) {
    const t = nachRoute.get(pfadVon(loc));
    if (t?.noindex && !ziel.length) { ruhend++; continue; }
    hart('Website', t?.noindex ? `noindex-Seite in sitemap.xml: ${loc}` : `sitemap.xml nennt eine URL ohne passende indexierbare Seite: ${loc}`);
  }
  if (ruhend) hinweis('Website', `sitemap.xml nennt ${ruhend} noindex-Seiten: ruht, solange keine Seite indexierbar ist (Vorschau); der Produktions-Build ohne noindex muss passen`);
  const lastmod = [...sitemap.matchAll(/<lastmod>\s*([^<]+?)\s*<\/lastmod>/gi)].map(m => m[1]);
  if (lastmod.length > 3 && new Set(lastmod).size === 1) hinweis('Website', 'alle lastmod gleich: Datum der Inhaltsänderung verwenden oder weglassen');
  if (/<(priority|changefreq)>/i.test(sitemap)) hinweis('Website', 'priority/changefreq ignoriert Google');
}

// robots.txt (Hausregel: immer eine, mit Sitemap-Zeile)
const robots = lesen('robots.txt');
if (ziel.length && !robots) hart('Website', 'robots.txt fehlt (Hausregel)');
if (robots) {
  const rb = robotsLesen(robots);
  if (ziel.length && !/^\s*sitemap\s*:/im.test(robots)) hart('Website', 'robots.txt ohne Sitemap:-Zeile (Hausregel)');
  for (const s of ziel) if (rb.gesperrt(s.route)) hart(s.route, 'per robots.txt gesperrt, soll aber gefunden werden');
  for (const s of seiten) if (s.noindex && rb.gesperrt(s.route)) hart(s.route, 'per robots.txt gesperrt: Google sieht das noindex nie (nur noindex verwenden)');
  if (/^\s*(noindex|crawl-delay)\s*:/im.test(robots)) hinweis('Website', 'robots.txt: noindex und crawl-delay unterstützt Google nicht');
  if (ziel.length && rb.disallow.some(m => /\.(css|js)\b|\/(assets?|css|js|img|images)\//i.test(m))) hinweis('Website', 'robots.txt sperrt vermutlich CSS, JS oder Bilder (Google braucht sie zum Rendern)');
}

// Favicon der Startseite
const start = nachRoute.get('/');
if (ziel.length && start) {
  if (!start.icons.length) hart('/', 'kein Favicon im <head> der Startseite');
  const dateien = start.icons.map(h => pfadVon(h)).filter(Boolean);
  for (const d of dateien) if (!existsSync(join(root, d))) hart('/', `Favicon-Datei fehlt: ${d}`);
  if (dateien.length && !dateien.some(d => /\.(ico|png|gif|jpe?g|bmp)$/i.test(d))) hinweis('/', 'kein Favicon in einem Google-Format (ICO, PNG, GIF, JPEG, BMP; nicht SVG/WebP): zusätzlich ICO oder PNG anbieten');
  const groesse = d => { // Kantenlänge aus dem Dateikopf (PNG, ICO), sonst null
    try {
      const b = readFileSync(join(root, d));
      if (b.subarray(1, 4).toString() === 'PNG') return b.readUInt32BE(16);
      if (b.readUInt16LE(0) === 0 && b.readUInt16LE(2) === 1) return Math.max(...Array.from({ length: b.readUInt16LE(4) }, (_, i) => b[6 + 16 * i] || 256));
    } catch {}
    return null;
  };
  const masse = dateien.map(groesse).filter(Boolean);
  if (masse.length && Math.max(...masse) < 48) hinweis('/', `Favicon höchstens ${Math.max(...masse)} px: mindestens 48 × 48 anbieten`);
}

// Telefon und Straße aus dem JSON-LD müssen sichtbar sein
const ziffern = seiten.map(s => s.ganzText.replace(/\D/g, '')).join(' ');
for (const tel of telefone) {
  const kern = tel.replace(/\D/g, '').replace(/^(00)?(49|43|41)/, '').replace(/^0/, '');
  if (kern.length >= 6 && !ziffern.includes(kern)) hart('Website', `Telefon aus dem JSON-LD ist auf keiner Seite sichtbar: ${tel}`);
}
const norm = x => x.toLowerCase().replace(/straße|strasse|str\./g, 'str').replace(/[^\p{L}\p{N}]/gu, '');
const sichtbar = seiten.map(s => norm(s.ganzText)).join(' ');
for (const strasse of strassen) if (!sichtbar.includes(norm(strasse))) hinweis('Website', `Straße aus dem JSON-LD nicht sichtbar gefunden: ${strasse}`);

// CSS-Dateien: Google Fonts per @import oder url()
for (const css of dateienIn(root, '.css')) {
  if (/(@import\s+(url\()?|url\()\s*['"]?(https?:)?\/\/fonts\.(googleapis|gstatic)\.com/i.test(readFileSync(css, 'utf8'))) hart(relative(root, css), 'Google Fonts vom Google-Server eingebunden (selbst hosten; DSGVO)');
}

// ---------- Live-Prüfung (nur GET) ----------
if (liveUrl) {
  const basis = new URL(liveUrl);
  if (site && basis.origin !== site.origin) hinweis('Live', `geprüft wird ${basis.origin}, seo.siteUrl ist ${site.origin}`);
  const holen = url => fetch(url, { redirect: 'manual', signal: AbortSignal.timeout(konfig.warteMs), headers: { 'user-agent': 'website-tools seo-pruefen' } });
  const istNoindex = async res => NOINDEX.test(res.headers.get('x-robots-tag') || '') || metaNoindex(await res.text());
  const kette = async (start, erwartet) => { // folgt bis zu 5 dauerhaften Weiterleitungen
    let url = start, schritte = 0;
    for (; schritte < 6; schritte++) {
      const res = await holen(url);
      if (![301, 302, 303, 307, 308].includes(res.status)) return { url, status: res.status, schritte };
      if (![301, 308].includes(res.status)) return { url, status: res.status, schritte, voruebergehend: true };
      url = new URL(res.headers.get('location'), url).href;
      if (url === erwartet) return { url, status: 200, schritte: schritte + 1 };
    }
    return { url, status: 0, schritte };
  };
  try {
    const res = await holen(basis.href);
    if (res.status !== 200) hart('Live', `${basis.href} liefert ${res.status} statt 200`);
    else if (await istNoindex(res)) hart('Live', 'Startseite ist live noindex (meta robots oder X-Robots-Tag)');

    const rt = await holen(new URL('/robots.txt', basis).href);
    if (rt.status >= 500 || rt.status === 429) hart('Live', `/robots.txt liefert ${rt.status}: Google behandelt die Website dann vorübergehend als gesperrt`);
    else if (rt.status === 200) { if (robotsLesen(await rt.text()).gesperrt('/')) hart('Live', 'robots.txt sperrt die Startseite für Google'); }
    else hinweis('Live', `/robots.txt liefert ${rt.status} (Google nimmt dann „alles erlaubt“ an, die Sitemap-Zeile fehlt)`);

    const unbekannt = new URL(`/seo-pruefen-gibt-es-nicht-${Date.now()}/`, basis).href;
    const fehler = await holen(unbekannt);
    if (![404, 410].includes(fehler.status)) hart('Live', `unbekannte URL liefert ${fehler.status} statt 404 (Soft 404)`);

    const tausch = new URL(basis.href); tausch.hostname = basis.hostname.startsWith('www.') ? basis.hostname.slice(4) : 'www.' + basis.hostname;
    const http = new URL(basis.href); http.protocol = 'http:';
    const unter = ziel.find(s => s.route !== '/' && (nie ? !extname(s.route) : s.route.endsWith('/')));
    const varianten = [[http.href, basis.href, true], [tausch.href, basis.href, true], [new URL('/index.html', basis).href, basis.href, false]];
    if (unter) varianten.push([new URL(nie ? unter.route + '/' : unter.route.slice(0, -1), basis).href, new URL(unter.route, basis).href, true]);
    for (const [variante, erwartet, wichtig] of varianten) {
      if (variante === basis.href) continue;
      try {
        const k = await kette(variante, erwartet);
        if (k.voruebergehend) hart('Live', `${variante}: vorübergehende Weiterleitung (${k.status}), dauerhaft 301/308 verwenden`);
        else if (k.url === erwartet && k.schritte > 1) hinweis('Live', `${variante}: ${k.schritte} Weiterleitungen bis ${erwartet} (besser ein Sprung)`);
        else if (k.url !== erwartet && k.status === 200) (wichtig ? hart : hinweis)('Live', k.schritte ? `${variante} endet auf ${k.url} statt ${erwartet}` : `${variante} liefert 200 ohne Weiterleitung (doppelte Adresse${wichtig ? '' : '; canonical fängt es ab'})`);
        else if (k.url !== erwartet) hinweis('Live', `${variante} liefert ${k.status}`);
      } catch (e) { hinweis('Live', `${variante} nicht erreichbar (${e.cause?.code || e.message})`); }
    }

    const liveSitemap = await holen(new URL('/sitemap.xml', basis).href);
    if (liveSitemap.status !== 200) hart('Live', `/sitemap.xml liefert ${liveSitemap.status}`);
    else for (const loc of [...(await liveSitemap.text()).matchAll(/<loc>\s*([^<]+?)\s*<\/loc>/gi)].map(m => ent(m[1])).slice(0, 100)) {
      const r = await holen(loc);
      if (r.status !== 200) hart('Live', `Sitemap-URL liefert ${r.status}: ${loc}`);
      else if (await istNoindex(r)) hart('Live', `Sitemap-URL ist live noindex: ${loc}`);
    }
  } catch (e) { hart('Live', `${basis.href} nicht erreichbar: ${e.cause?.code || e.message}`); }
}

// ---------- Ausgabe ----------
fragen.push('Hat jede indexierbare Seite eine eigene Hauptabsicht mit Beleg vom Kunden? Orts- und Variantenseiten: Doorway-Test (references/page-plan.md).');
fragen.push('Lesen sich Titles, Descriptions, Linktexte und Alt-Texte für Menschen gut? Suchbegriffe stehen sichtbar im Text, nichts versteckt.');
fragen.push('KI-Crawler-Politik in robots.txt vom Kunden entschieden (alles erlauben oder Suche ja, Training nein)?');
if (!liveUrl) fragen.push('Nach dem Deploy: --live, Rich Results Test von Hand, Search Console und Bing Webmaster Tools (references/seo.md, Livegang).');

console.log(`SEO-Prüfung: ${relative(process.cwd(), root) || '.'}, ${seiten.length} Seiten, ${ziel.length} ${livegang ? 'nach dem Livegang indexierbar' : 'indexierbar'}, ${seiten.length - ziel.length} ruhend (noindex oder Sonderseite)`);
if (!ziel.length && !livegang) infos.push('Keine indexierbare Seite (Prototyp?): Index-Regeln ruhen. `--livegang` zeigt, was vor dem Entfernen von noindex fehlt.');
for (const i of infos) console.log(`ℹ️  ${i}`);
// Gleiche Meldung auf vielen Seiten als eine Zeile
const gruppen = new Map();
for (const b of befunde) { const key = b.art + '\u0000' + b.text; gruppen.set(key, [...(gruppen.get(key) || []), b.wo]); }
const zeilen = [...gruppen].map(([key, wo]) => {
  const [art, text] = key.split('\u0000');
  return { art, zeile: wo.length > 3 ? `${text} (${wo.length} Seiten: ${wo.slice(0, 4).join(', ')} …)` : `${wo.join(', ')}: ${text}` };
});
for (const z of zeilen.sort((a, b) => (a.art === b.art ? 0 : a.art === 'hart' ? -1 : 1))) console.log(`${z.art === 'hart' ? '❌' : '⚠️ '} ${z.zeile}`);
console.log('\n❓ Zu beurteilen:\n' + fragen.map(f => `  - ${f}`).join('\n'));
const anzahl = art => befunde.filter(b => b.art === art).length;
console.log(anzahl('hart') ? `\n❌ ${anzahl('hart')} harte Fehler, ${anzahl('hinweis')} Hinweise.` : `\n✅ Keine harten Fehler${anzahl('hinweis') ? ` · ${anzahl('hinweis')} Hinweise` : ''}.`);
process.exitCode = anzahl('hart') ? 1 : 0;
