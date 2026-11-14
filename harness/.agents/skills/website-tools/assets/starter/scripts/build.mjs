// Baut die Website aus src/site.config.mjs und den Vorlagen in src/seiten/ nach dist/
// (website-tools-Starter; gehört nach dem Kopieren dem Projekt, Anpassungen hier sind erwünscht).
//   node scripts/build.mjs                Vorschau: jede Seite noindex; offene Punkte werden gemeldet
//   node scripts/build.mjs --produktion   Livegang: indexierbar; bricht ab bei Platzhaltern, fehlendem Beleg, Beispiel-URL
//   --ausgabe <ordner>                    anderer Zielordner (Standard dist)
// canonical, Open Graph, JSON-LD, sitemap.xml und robots.txt sind in beiden Umgebungen gleich; nur noindex unterscheidet sie.
// Danach prüfen (Skill): node <skill>/tools/seo-pruefen.mjs [--livegang]
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import * as seo from './seo.mjs';

const WURZEL = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const TAGE = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'PublicHolidays'];
const PLATZHALTER = /platzhalter|placeholder|lorem ipsum|\bTODO\b/i;
const BEISPIEL_HOST = /(^|\.)example\.(com|net|org)$|\.(example|invalid|test|localhost)$/i;
const NUR_ORGANISATION = /^(Organization|Corporation|OnlineBusiness|OnlineStore|NGO)$/;

export const dateiVon = route => (route.endsWith('.html') ? route.slice(1) : `${route.slice(1)}index.html`);

// Eingaben prüfen, bevor etwas gebaut wird: Form und Eindeutigkeit, in beiden Umgebungen.
export function datenPruefen(site, wurzel = WURZEL) {
  const f = [], firma = site.firma || {}, seiten = Array.isArray(site.seiten) ? site.seiten : [];
  let url = null; try { url = new URL(site.siteUrl); } catch { f.push(`siteUrl ist keine URL: ${site.siteUrl}`); }
  if (url && (url.protocol !== 'https:' || url.pathname !== '/' || url.search || url.hash)) f.push(`siteUrl braucht https und keinen Pfad: ${site.siteUrl}`);
  if (!site.sprache) f.push('sprache fehlt (<html lang>)');
  if (!['alle', 'nurSuche'].includes(site.kiCrawler)) f.push("kiCrawler muss 'alle' oder 'nurSuche' sein (Kundenentscheidung, seo.md)");
  if (!/^#[0-9a-f]{6}$/i.test(site.farbe || '')) f.push('farbe muss #rrggbb sein');
  for (const pfad of [site.ogBild, firma.logo]) if (pfad && !pfad.startsWith('/')) f.push(`Bildpfad relativ zu src/static mit / am Anfang: ${pfad}`);
  if (!firma.name) f.push('firma.name fehlt');
  if (!/^[A-Z][A-Za-z]+$/.test(firma.typ || '')) f.push(`firma.typ ist kein schema.org-Typ: ${firma.typ}`);
  if (firma.telefon && !/^\+[1-9][\d ]{5,}$/.test(firma.telefon)) f.push(`firma.telefon international mit + und nur Ziffern/Leerzeichen: ${firma.telefon}`);
  for (const o of firma.oeffnungszeiten || []) {
    if (!o.tage?.length || o.tage.some(t => !TAGE.includes(t))) f.push(`oeffnungszeiten: Tage englisch wie schema.org (Monday …): ${o.tage}`);
    if (!/^\d\d:\d\d$/.test(o.von || '') || !/^\d\d:\d\d$/.test(o.bis || '')) f.push(`oeffnungszeiten: von/bis als HH:MM: ${o.von}–${o.bis}`);
  }
  if (!seiten.length) f.push('seiten ist leer');
  const routen = new Set(), titel = new Map();
  for (const s of seiten) {
    const wo = s.route || '(ohne route)';
    if (!['suche', 'recht', 'sonder', undefined].includes(s.art)) f.push(`${wo}: art muss 'suche', 'recht' oder 'sonder' sein`);
    if (seo.istSonder(s) ? !/^\/[a-z0-9-]+\.html$/.test(s.route || '') : !/^\/([a-z0-9-]+\/)*$/.test(s.route || ''))
      f.push(`${wo}: Route klein, mit Bindestrichen, mit / am Ende (Sonderseiten: /name.html)`);
    if (routen.has(s.route)) f.push(`${wo}: Route doppelt`);
    routen.add(s.route);
    if (!s.vorlage || !existsSync(join(wurzel, 'src/seiten', `${s.vorlage}.mjs`))) f.push(`${wo}: Vorlage fehlt: src/seiten/${s.vorlage}.mjs`);
    if (s.datei && !existsSync(join(wurzel, 'src', s.datei))) f.push(`${wo}: datei fehlt: src/${s.datei}`);
    if (!s.title || !s.h1) f.push(`${wo}: title und h1 nötig`);
    if (!seo.istSonder(s)) {
      if (!s.description) f.push(`${wo}: description fehlt`);
      if (s.title && titel.has(s.title)) f.push(`${wo}: gleicher Title wie ${titel.get(s.title)}`);
      titel.set(s.title, wo);
    }
    if (s.geaendert && !/^\d{4}-\d\d-\d\d$/.test(s.geaendert)) f.push(`${wo}: geaendert als JJJJ-MM-TT`);
  }
  if (seiten.length && !routen.has('/')) f.push('Startseite / fehlt');
  if (!seiten.some(s => s.route === '/404.html' && seo.istSonder(s))) f.push("Fehlerseite fehlt: { route: '/404.html', art: 'sonder', … }");
  for (const n of site.navigation || []) {
    const ziel = String(n.href || '').split('#')[0];
    if (!n.text || !String(n.href || '').startsWith('/') || !routen.has(ziel)) f.push(`navigation: Ziel muss eine Route sein: ${n.href}`);
  }
  return f;
}

// Was den Livegang sperrt: im Produktions-Build ein Abbruch, in der Vorschau eine Liste.
function sperren(site, gebaut, statisch) {
  const s = [], host = new URL(site.siteUrl).hostname, a = site.firma.adresse || {};
  if (BEISPIEL_HOST.test(host)) s.push(`siteUrl ist eine Beispieladresse: ${site.siteUrl}`);
  for (const [feld, pfad] of [['ogBild', site.ogBild], ['firma.logo', site.firma.logo], ...site.seiten.map(x => [`${x.route} ogBild`, x.ogBild])])
    if (pfad && !existsSync(join(statisch, pfad))) s.push(`${feld}: Datei fehlt in src/static${pfad}`);
  if (!NUR_ORGANISATION.test(site.firma.typ) && !(a.strasse && a.plz && a.ort)) s.push('firma.adresse unvollständig (LocalBusiness braucht Straße, PLZ und Ort)');
  for (const seite of site.seiten.filter(seo.istSuche)) {
    if (!String(seite.absicht || '').trim()) s.push(`${seite.route}: absicht fehlt (Hauptabsicht in Worten der Suchenden)`);
    if (!String(seite.beleg || '').trim()) s.push(`${seite.route}: beleg fehlt (echter Nachweis vom Kunden, page-plan.md)`);
  }
  for (const { seite, html } of gebaut) {
    const roh = html.replace(/<!--[\s\S]*?-->/g, ''); // Attribute zählen mit (description, og:*), Kommentare nicht
    const imText = roh.replace(/<[^>]+>/g, ' ').match(new RegExp(`(?:${PLATZHALTER.source}).{0,50}`, 'i'));
    if (imText) s.push(`${seite.route}: Platzhalter „${imText[0].replace(/\s+/g, ' ').trim()}“`);
    else if (PLATZHALTER.test(roh)) s.push(`${seite.route}: Platzhalter in einem Attribut (z. B. description)`);
  }
  return s;
}

function icons(statisch) {
  const hat = n => existsSync(join(statisch, n));
  const erzeugen = !hat('favicon.png') && !hat('favicon.ico');
  const liste = [];
  if (hat('favicon.ico')) liste.push({ rel: 'icon', href: '/favicon.ico', sizes: 'any' });
  if (hat('favicon.svg')) liste.push({ rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' });
  if (hat('favicon.png') || erzeugen) liste.push({ rel: 'icon', href: '/favicon.png', type: 'image/png' });
  const touch = hat('apple-touch-icon.png') ? '/apple-touch-icon.png' : hat('favicon.png') || erzeugen ? '/favicon.png' : null;
  if (touch) liste.push({ rel: 'apple-touch-icon', href: touch });
  return { liste, erzeugen };
}

export async function bauen({ site, wurzel = WURZEL, ausgabe = 'dist', produktion = false }) {
  const fehler = datenPruefen(site, wurzel);
  if (fehler.length) throw new Error(`site.config.mjs:\n  - ${fehler.join('\n  - ')}`);
  const umgebung = produktion ? 'produktion' : 'vorschau';
  const src = join(wurzel, 'src'), statisch = join(src, 'static');
  const ziel = resolve(wurzel, ausgabe);
  if (ziel === wurzel || wurzel.startsWith(ziel + sep) || ziel === src || ziel.startsWith(src + sep)) throw new Error(`Ausgabe darf weder Projekt noch src sein: ${ziel}`);
  const { liste, erzeugen } = icons(statisch);
  const layout = (await import(pathToFileURL(join(src, 'layout.mjs')).href)).default;

  const gebaut = [];
  for (const seite of site.seiten) {
    const vorlage = (await import(pathToFileURL(join(src, 'seiten', `${seite.vorlage}.mjs`)).href)).default;
    const schritte = seo.pfad(seite, site.seiten);
    const daten = [];
    if (seite.route === '/') daten.push(seo.firmaDaten(site), seo.websiteDaten(site));
    if (schritte.length) daten.push(seo.brotkrumenDaten(site, schritte));
    const ctx = { site, seite, seiten: site.seiten, pfad: schritte, datei: seite.datei ? readFileSync(join(src, seite.datei), 'utf8') : '' };
    const main = await vorlage(ctx);
    gebaut.push({ seite, html: layout({ ...ctx, main, kopf: seo.kopf({ site, seite, umgebung, icons: liste, daten }) }) });
  }

  const offen = sperren(site, gebaut, statisch);
  if (produktion && offen.length) throw new Error(`Produktions-Build gesperrt (erst echte Kundenangaben):\n  - ${offen.join('\n  - ')}`);

  rmSync(ziel, { recursive: true, force: true });
  mkdirSync(ziel, { recursive: true });
  if (existsSync(statisch)) cpSync(statisch, ziel, { recursive: true });
  if (existsSync(join(src, 'styles'))) cpSync(join(src, 'styles'), join(ziel, 'styles'), { recursive: true });
  for (const { seite, html } of gebaut) {
    const datei = join(ziel, dateiVon(seite.route));
    mkdirSync(dirname(datei), { recursive: true });
    writeFileSync(datei, html);
  }
  writeFileSync(join(ziel, 'sitemap.xml'), seo.sitemap(site, site.seiten));
  writeFileSync(join(ziel, 'robots.txt'), seo.robots(site));
  if (erzeugen) writeFileSync(join(ziel, 'favicon.png'), seo.favicon(site.farbe));
  return { ziel, umgebung, seiten: gebaut.length, offen, faviconErzeugt: erzeugen };
}

// ---------- Aufruf von der Kommandozeile ----------
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const i = args.indexOf('--ausgabe');
  const produktion = args.includes('--produktion') || process.env.UMGEBUNG === 'produktion';
  try {
    const site = (await import(pathToFileURL(join(WURZEL, 'src/site.config.mjs')).href)).default;
    const r = await bauen({ site, produktion, ausgabe: i >= 0 ? args[i + 1] : 'dist' });
    console.log(`${r.umgebung === 'produktion' ? 'Produktion (indexierbar)' : 'Vorschau (noindex)'}: ${r.seiten} Seiten → ${relative(process.cwd(), r.ziel) || '.'}`);
    if (r.offen.length) console.log(`Vor dem Livegang offen (der Produktions-Build bricht sonst ab):\n  - ${r.offen.join('\n  - ')}`);
    if (r.faviconErzeugt) console.log('Favicon einfarbig aus site.farbe erzeugt; eigenes Icon: src/static/favicon.png (quadratisch, ≥ 48 px).');
  } catch (e) {
    console.error(`❌ ${e.message}`);
    process.exitCode = 1;
  }
}
