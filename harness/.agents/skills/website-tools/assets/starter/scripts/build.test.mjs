// Tests des Starters (npm test). Sie laufen auch in der CI, wo der website-tools-Skill fehlt:
//  1. Generatoren mit erfundenen Daten und Mini-Vorlagen in einem Temp-Ordner, unabhängig von der Gestaltung.
//  2. Das echte Projekt (src/site.config.mjs, eigene Vorlagen) als Vorschau: Regeln, die jede Gestaltung einhalten muss.
// Livegang-Tor ist `npm run build:prod`; die volle Prüfung bleibt seo-pruefen.mjs des Skills.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { bauen, dateiVon } from './build.mjs';
import projekt from '../src/site.config.mjs';

const MINI_LAYOUT = 'export default ({ site, kopf, main }) => `<!doctype html><html lang="${site.sprache}"><head>${kopf}</head>'
  + '<body><main>${main}</main><footer>${site.firma.telefonAnzeige}</footer></body></html>`;';
const MINI_SEITE = 'export default ({ seite, seiten }) => `<h1>${seite.h1}</h1>${seiten.map(s => `<a href="${s.route}">${s.h1}</a>`).join(" ")}'
  + '<p>${seite.inhalt?.text ?? ""}</p>`;';

const beispiel = () => ({
  siteUrl: 'https://www.beispiel.de', sprache: 'de', locale: 'de_DE', farbe: '#336699', ogBild: '/og.jpg', kiCrawler: 'alle',
  firma: {
    name: 'Muster Elektro', typ: 'Electrician', beschreibung: 'Elektrobetrieb in Musterstadt seit 1990.',
    telefon: '+49 30 1234567', telefonAnzeige: '030 123 45 67',
    adresse: { strasse: 'Musterweg 1', plz: '12345', ort: 'Musterstadt', land: 'DE' },
    oeffnungszeiten: [{ tage: ['Monday', 'Tuesday', 'Wednesday'], von: '08:00', bis: '17:00' }], einsatzgebiet: ['Musterstadt'],
  },
  navigation: [{ text: 'E-Check', href: '/leistungen/e-check/' }],
  seiten: [
    { route: '/', vorlage: 'seite', title: 'Elektriker in Musterstadt – Muster Elektro', h1: 'Elektriker in Musterstadt',
      description: 'Elektroinstallation, E-Check und Reparaturen in Musterstadt, mit Meisterbetrieb und festen Terminen.',
      absicht: 'Elektriker Musterstadt', beleg: 'Meisterbrief, 40 Referenzen 2025', geaendert: '2026-10-01' },
    { route: '/leistungen/e-check/', vorlage: 'seite', kurz: 'E-Check', title: 'E-Check in Musterstadt – Muster Elektro', h1: 'E-Check',
      description: 'E-Check für Wohnungen und Betriebe in Musterstadt: Ablauf, Dauer, Preise und Prüfprotokoll.',
      absicht: 'E-Check Musterstadt', beleg: 'Prüfprotokolle, Preisliste' },
    { route: '/impressum/', art: 'recht', vorlage: 'seite', title: 'Impressum – Muster Elektro', h1: 'Impressum',
      description: 'Impressum von Muster Elektro: Anbieter, Anschrift, Kontakt und Kammer.' },
    { route: '/404.html', art: 'sonder', vorlage: 'seite', title: 'Seite nicht gefunden – Muster Elektro', h1: 'Seite nicht gefunden' },
  ],
});

const wurzel = () => {
  const w = mkdtempSync(join(tmpdir(), 'starter-test-'));
  mkdirSync(join(w, 'src/seiten'), { recursive: true });
  mkdirSync(join(w, 'src/static'));
  writeFileSync(join(w, 'src/static/og.jpg'), 'bild');
  writeFileSync(join(w, 'src/layout.mjs'), MINI_LAYOUT);
  writeFileSync(join(w, 'src/seiten/seite.mjs'), MINI_SEITE);
  return w;
};
const bau = async (site, produktion = false) => {
  const w = wurzel();
  const r = await bauen({ site, wurzel: w, produktion });
  const lies = route => readFileSync(join(r.ziel, dateiVon(route)), 'utf8');
  return { ...r, lies, datei: n => readFileSync(join(r.ziel, n), 'utf8') };
};
const noindex = html => /<meta name="robots" content="noindex">/.test(html);
const canonical = html => [...html.matchAll(/<link rel="canonical" href="([^"]+)">/g)].map(m => m[1]);
const jsonld = html => [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map(m => JSON.parse(m[1]));

test('Vorschau ist Produktion plus noindex: gleiche canonicals, Sitemap und robots.txt', async () => {
  const site = beispiel(), vorschau = await bau(site), prod = await bau(site, true);
  for (const s of site.seiten) {
    assert.ok(noindex(vorschau.lies(s.route)), `Vorschau ohne noindex: ${s.route}`);
    assert.equal(noindex(prod.lies(s.route)), s.art === 'sonder', `Produktion: noindex nur auf Sonderseiten (${s.route})`);
    assert.deepEqual(canonical(vorschau.lies(s.route)), canonical(prod.lies(s.route)));
  }
  assert.equal(vorschau.datei('sitemap.xml'), prod.datei('sitemap.xml'));
  assert.equal(vorschau.datei('robots.txt'), prod.datei('robots.txt'));
});

test('canonical, og:url und Sitemap nennen je Suchseite dieselbe URL; Sonderseiten fehlen', async () => {
  const site = beispiel(), r = await bau(site, true);
  const locs = [...r.datei('sitemap.xml').matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1]);
  const erwartet = site.seiten.filter(s => s.art !== 'sonder').map(s => `https://www.beispiel.de${s.route}`);
  assert.deepEqual(locs, erwartet);
  for (const s of site.seiten.filter(s => s.art !== 'sonder')) {
    const html = r.lies(s.route), url = `https://www.beispiel.de${s.route}`;
    assert.deepEqual(canonical(html), [url]);
    assert.match(html, new RegExp(`<meta property="og:url" content="${url}">`));
    assert.equal((html.match(/<title>/g) || []).length, 1);
  }
  assert.deepEqual(canonical(r.lies('/404.html')), []);
  assert.match(r.datei('sitemap.xml'), /<lastmod>2026-10-01<\/lastmod>/);
  assert.equal((r.datei('sitemap.xml').match(/<lastmod>/g) || []).length, 1, 'lastmod nur mit echtem Inhaltsdatum');
  assert.match(r.datei('robots.txt'), /^Sitemap: https:\/\/www\.beispiel\.de\/sitemap\.xml$/m);
});

test('JSON-LD: Firma und WebSite auf der Startseite, Brotkrumen ab Tiefe 2, Daten wie sichtbar', async () => {
  const r = await bau(beispiel(), true);
  const [start] = jsonld(r.lies('/'));
  const firma = start['@graph'].find(x => x['@type'] === 'Electrician');
  assert.equal(firma.telephone, '+49 30 1234567');
  assert.deepEqual(firma.openingHoursSpecification[0].dayOfWeek, ['Monday', 'Tuesday', 'Wednesday']);
  assert.equal(firma.address.streetAddress, 'Musterweg 1');
  assert.ok(!('aggregateRating' in firma) && !('review' in firma));
  assert.ok(start['@graph'].some(x => x['@type'] === 'WebSite'));
  const [krumen] = jsonld(r.lies('/leistungen/e-check/'));
  assert.equal(krumen['@type'], 'BreadcrumbList');
  assert.deepEqual(krumen.itemListElement.map(i => i.item), ['https://www.beispiel.de/', 'https://www.beispiel.de/leistungen/e-check/']);
  assert.deepEqual(jsonld(r.lies('/impressum/')), [], 'Tiefe 1: keine Brotkrumen');
});

test('robots.txt: Voreinstellung B sperrt Training und erlaubt Suche; nie Disallow für alle', async () => {
  const r = await bau({ ...beispiel(), kiCrawler: 'nurSuche' }, true), txt = r.datei('robots.txt');
  const gruppe = agent => txt.split(/\n\n/).find(g => g.includes(`User-agent: ${agent}\n`));
  for (const a of ['GPTBot', 'ClaudeBot', 'Google-Extended', 'CCBot']) assert.match(gruppe(a), /Disallow: \/$/m, a);
  for (const a of ['OAI-SearchBot', 'Claude-SearchBot', 'PerplexityBot']) assert.match(gruppe(a), /Allow: \/$/m, a);
  assert.match(gruppe('*'), /^Allow: \/$/m);
});

test('Produktions-Build sperrt Platzhalter, fehlenden Beleg, Beispiel-URL und fehlende Bilder, ohne etwas zu schreiben', async () => {
  const faelle = [
    [s => { s.seiten[1].inhalt = { text: 'Platzhalter: Preise vom Kunden' }; }, /\/leistungen\/e-check\/: Platzhalter/],
    [s => { s.seiten[1].description = 'Platzhalter: Description'; }, /Platzhalter in einem Attribut/],
    [s => { s.seiten[0].beleg = ''; }, /\/: beleg fehlt/],
    [s => { s.siteUrl = 'https://www.example.com'; }, /Beispieladresse/],
    [s => { s.firma.adresse.strasse = ''; }, /adresse unvollständig/],
    [s => { s.ogBild = '/fehlt.jpg'; }, /ogBild: Datei fehlt/],
  ];
  for (const [aendern, meldung] of faelle) {
    const site = beispiel(); aendern(site);
    const w = wurzel();
    await assert.rejects(bauen({ site, wurzel: w, produktion: true }), meldung);
    assert.ok(!existsSync(join(w, 'dist')), 'gesperrter Build schreibt nichts');
    const vorschau = await bauen({ site, wurzel: w });
    assert.ok(vorschau.offen.some(o => meldung.test(o)), 'die Vorschau baut und meldet es');
  }
});

test('Eingaben: doppelter Title, falsche Route, deutsche Tage und nationale Telefonnummer werden abgelehnt', async () => {
  const faelle = [
    [s => { s.seiten[2].title = s.seiten[0].title; }, /gleicher Title/],
    [s => { s.seiten[1].route = '/Leistungen/E_Check'; }, /Route klein/],
    [s => { s.firma.oeffnungszeiten[0].tage = ['Montag']; }, /Tage englisch/],
    [s => { s.firma.telefon = '030 1234567'; }, /international/],
    [s => { s.seiten.pop(); }, /Fehlerseite fehlt/],
    [s => { s.navigation[0].href = '/gibt-es-nicht/'; }, /navigation/],
  ];
  for (const [aendern, meldung] of faelle) {
    const site = beispiel(); aendern(site);
    await assert.rejects(bauen({ site, wurzel: wurzel() }), meldung);
  }
});

test('Sonderzeichen in Daten brechen weder HTML noch JSON-LD', async () => {
  const site = beispiel();
  site.firma.name = 'Müller & Söhne </script><b>';
  const html = (await bau(site, true)).lies('/');
  assert.match(html, /<meta property="og:site_name" content="Müller &amp; Söhne &lt;\/script&gt;&lt;b&gt;">/);
  assert.equal(jsonld(html)[0]['@graph'][0].name, 'Müller & Söhne </script><b>');
});

test('Ersatz-Favicon ist ein quadratisches PNG ab 48 px; ein eigenes Icon hat Vorrang', async () => {
  const r = await bau(beispiel());
  const png = readFileSync(join(r.ziel, 'favicon.png'));
  assert.equal(png.subarray(1, 4).toString(), 'PNG');
  assert.equal(png.readUInt32BE(16), png.readUInt32BE(20));
  assert.ok(png.readUInt32BE(16) >= 48);
  const w = wurzel();
  writeFileSync(join(w, 'src/static/favicon.ico'), 'eigenes');
  const eigen = await bauen({ site: beispiel(), wurzel: w });
  assert.ok(!eigen.faviconErzeugt && !existsSync(join(eigen.ziel, 'favicon.png')));
  assert.match(readFileSync(join(eigen.ziel, 'index.html'), 'utf8'), /<link rel="icon" href="\/favicon.ico" sizes="any">/);
});

test('Projekt (eigene Vorlagen und Daten) baut als Vorschau und hält die Grundregeln ein', async () => {
  const r = await bauen({ site: projekt, ausgabe: mkdtempSync(join(tmpdir(), 'starter-projekt-')) });
  const dateien = (d, alle = []) => { for (const e of readdirSync(d, { withFileTypes: true })) e.isDirectory() ? dateien(join(d, e.name), alle) : alle.push(join(d, e.name)); return alle; };
  const vorhanden = new Set(dateien(r.ziel).map(d => d.slice(r.ziel.length)));
  const text = [];
  for (const s of projekt.seiten) {
    const html = readFileSync(join(r.ziel, dateiVon(s.route)), 'utf8');
    assert.ok(noindex(html), `Vorschau ohne noindex: ${s.route}`);
    assert.equal((html.match(/<title>/g) || []).length, 1, `genau ein <title>: ${s.route}`);
    assert.equal((html.match(/<h1\b/g) || []).length, 1, `genau eine H1: ${s.route}`);
    assert.equal(canonical(html).length, s.art === 'sonder' ? 0 : 1, `canonical: ${s.route}`);
    for (const [, href] of html.matchAll(/<a\b[^>]*href="(\/[^"#?]*)/g)) {
      const ziel = href.endsWith('/') ? `${href}index.html` : href;
      assert.ok(vorhanden.has(ziel), `toter interner Link auf ${s.route}: ${href}`);
    }
    for (const recht of projekt.seiten.filter(x => x.art === 'recht')) assert.match(html, new RegExp(`href="${recht.route}"`), `Rechtsseite nicht verlinkt auf ${s.route}`);
    text.push(html.replace(/<script[\s\S]*?<\/script>|<[^>]+>/g, ' '));
  }
  const ziffern = text.join(' ').replace(/\D/g, '');
  const tel = (projekt.firma.telefon || '').replace(/\D/g, '').replace(/^(49|43|41)/, '');
  if (tel) assert.ok(ziffern.includes(tel), 'Telefon aus dem JSON-LD ist sichtbar');
});
