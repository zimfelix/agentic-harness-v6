// Misst die Pflichtregeln aus Teil A des Website-Profils auf allen gebauten Seiten und Prüfbreiten (konfig.breiten):
// horizontaler Überlauf, geladene Schriften, Skriptfehler, fehlende Dateien, Formularfelder unter 16 px,
// zu kleine Bedienelemente (unter 24 × 24 px) und Textkontrast (WCAG: 4,5 bzw. 3 bei großer Schrift).
// Aufruf aus dem Projektordner, vorher bauen:  node <webtools>/pruefen.mjs [build-ordner]
// Ergebnis: eine Zeile je Seite und Breite; Exit-Code 1 bei harten Fehlern (Überlauf, Skriptfehler, 404, Feldgröße, Schrift nicht geladen).
// Hinweise (Kontrast, kleine Bedienelemente) brechen nicht ab, sondern werden zur Beurteilung aufgelistet.
import { launch, open, routesIn, serve } from './browser.mjs';
import { konfig } from './konfig.mjs';

const root = process.argv[2] || konfig.ausgabe;

const FEHLERFANG = `window.__fehler = [];
addEventListener('error', e => __fehler.push((e.message || 'Fehler') + ' @' + String(e.filename || '').split('/').pop() + ':' + e.lineno));
addEventListener('unhandledrejection', e => __fehler.push('Promise: ' + e.reason));`;

const MESSUNG = `(() => {
  const r = {};
  const sichtbar = el => { const b = el.getBoundingClientRect(); return b.width > 0 && b.height > 0 && el.checkVisibility({ opacityProperty: true, visibilityProperty: true }); };
  // clientWidth statt innerWidth: Mit Handy-Emulation zieht der Browser das Fenster bei zu breitem Inhalt mit, innerWidth verdeckt den Überlauf.
  const breite = document.documentElement.clientWidth;
  r.ueberlauf = document.documentElement.scrollWidth - breite;
  r.zuBreit = r.ueberlauf > 0 ? [...document.querySelectorAll('body *')].filter(el => el.getBoundingClientRect().right > breite + 1 && getComputedStyle(el).position !== 'fixed')
    .slice(0, 3).map(el => el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\\s+/).join('.') : '')) : [];
  const genutzt = new Set([...document.querySelectorAll('body *')].map(el => getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g, '').trim()));
  const geladen = new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/["']/g, '')));
  const eigene = new Set([...document.fonts].map(f => f.family.replace(/["']/g, '')));
  r.schriftFehlt = [...genutzt].filter(f => eigene.has(f) && !geladen.has(f));
  r.fehler = window.__fehler || [];
  r.dateien404 = performance.getEntriesByType('resource').filter(e => e.responseStatus >= 400).map(e => e.name.split('/').slice(-2).join('/') + ' ' + e.responseStatus);
  r.felder = [...document.querySelectorAll('input:not([type=radio]):not([type=checkbox]):not([type=hidden]), select, textarea')].filter(sichtbar)
    .filter(el => parseFloat(getComputedStyle(el).fontSize) < 16).map(el => (el.id || el.name || el.tagName.toLowerCase()) + ' ' + getComputedStyle(el).fontSize);
  const inText = el => el.tagName === 'A' && el.closest('p, li, td, dd') && el.parentElement.textContent.trim().length > el.textContent.trim().length + 20;
  r.klein = [...document.querySelectorAll('a, button, input, select, textarea, summary, [role=button]')]
    .filter(el => sichtbar(el) && !inText(el) && !(el.tagName === 'INPUT' && ['radio', 'checkbox'].includes(el.type) && getComputedStyle(el).opacity === '0'))
    .filter(el => { const b = el.getBoundingClientRect(); return b.width < 24 || b.height < 24; })
    .slice(0, 6).map(el => { const b = el.getBoundingClientRect(); return (el.textContent.trim() || el.getAttribute('aria-label') || el.tagName).slice(0, 28) + ' ' + Math.round(b.width) + '×' + Math.round(b.height); });
  const farbe = s => { const m = s.match(/rgba?\\(([^)]+)\\)/); if (!m) return null; const t = m[1].split(/[ ,\\/]+/).filter(Boolean).map(Number); return { r: t[0], g: t[1], b: t[2], a: t[3] ?? 1 }; };
  const lum = c => { const k = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * k(c.r) + 0.7152 * k(c.g) + 0.0722 * k(c.b); };
  const misch = (o, u) => ({ r: o.r * o.a + u.r * (1 - o.a), g: o.g * o.a + u.g * (1 - o.a), b: o.b * o.a + u.b * (1 - o.a), a: 1 });
  const hinten = el => { const lagen = []; for (let e = el; e; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.backgroundImage !== 'none') return null; const c = farbe(cs.backgroundColor); if (c && c.a > 0) { lagen.push(c); if (c.a >= 0.99) break; } } let erg = { r: 255, g: 255, b: 255, a: 1 }; for (const l of lagen.reverse()) erg = misch(l, erg); return erg; };
  r.kontrast = [];
  for (const el of document.querySelectorAll('body *')) {
    if (!sichtbar(el) || el.closest('svg')) continue;
    const text = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join(' ').trim();
    if (!text) continue;
    const cs = getComputedStyle(el); const vorne = farbe(cs.color); const h = hinten(el); if (!vorne || !h) continue;
    const v = misch(vorne, h); const k = (Math.max(lum(v), lum(h)) + 0.05) / (Math.min(lum(v), lum(h)) + 0.05);
    const gross = parseFloat(cs.fontSize) >= 24 || (parseFloat(cs.fontSize) >= 18.66 && parseInt(cs.fontWeight) >= 700);
    if (k < (gross ? 3 : 4.5)) r.kontrast.push(k.toFixed(2) + ' „' + text.slice(0, 32) + '“');
  }
  r.kontrast = [...new Set(r.kontrast)].slice(0, 6);
  return r;
})()`;

const server = await serve(root);
const page = await launch();
const harte = [];
let hinweise = 0;
try {
  await page.send('Page.addScriptToEvaluateOnNewDocument', { source: FEHLERFANG });
  for (const route of await routesIn(root)) {
    for (const breite of konfig.breiten) {
      await open(page, server.base + route, breite);
      const m = await page.evaluate(MESSUNG);
      const zeile = [];
      if (m.ueberlauf > 0) { zeile.push(`❌ Überlauf ${m.ueberlauf}px (${m.zuBreit.join(', ')})`); harte.push(`${route}@${breite} Überlauf`); }
      if (m.schriftFehlt.length) { zeile.push(`❌ Schrift nicht geladen: ${m.schriftFehlt.join(', ')}`); harte.push(`${route}@${breite} Schrift`); }
      if (m.fehler.length) { zeile.push(`❌ Skriptfehler: ${m.fehler.join(' | ')}`); harte.push(`${route}@${breite} Skript`); }
      if (m.dateien404.length) { zeile.push(`❌ fehlt: ${m.dateien404.join(', ')}`); harte.push(`${route}@${breite} Datei`); }
      if (m.felder.length) { zeile.push(`❌ Feld unter 16 px: ${m.felder.join(', ')}`); harte.push(`${route}@${breite} Feld`); }
      if (m.klein.length) { zeile.push(`⚠️ klein: ${m.klein.join(' | ')}`); hinweise++; }
      if (m.kontrast.length) { zeile.push(`⚠️ Kontrast: ${m.kontrast.join(' | ')}`); hinweise++; }
      console.log(`${route} @${breite}: ${zeile.length ? zeile.join(' · ') : '✅'}`);
    }
  }
} finally {
  await page.close();
  server.close();
}
console.log(harte.length ? `\n❌ ${harte.length} harte Fehler: ${harte.join(', ')}` : `\n✅ Keine harten Fehler${hinweise ? ` · ${hinweise} Hinweise zur Beurteilung` : ''}.`);
process.exitCode = harte.length ? 1 : 0;
