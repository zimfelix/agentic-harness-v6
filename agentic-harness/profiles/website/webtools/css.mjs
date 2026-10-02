// Kleiner CSS-Leser für die Quelldateien: findet Regeln, Kommentare und @media-Blöcke samt Textposition,
// damit Werkzeuge gezielt einzelne Selektoren entfernen können, ohne die übrige Formatierung anzufassen.

// Überspringt Zeichenketten und Kommentare; liefert die Position nach dem gesuchten Zeichen auf oberster Ebene.
function scanTo(text, i, stops) {
  let depth = 0;
  while (i < text.length) {
    const ch = text[i];
    if (text.startsWith('/*', i)) { i = text.indexOf('*/', i + 2) + 2; continue; }
    if (ch === '"' || ch === "'") { i++; while (i < text.length && text[i] !== ch) i += text[i] === '\\' ? 2 : 1; i++; continue; }
    if (ch === '(' || ch === '[') depth++;
    else if (ch === ')' || ch === ']') depth--;
    else if (depth === 0 && stops.includes(ch)) return i;
    i++;
  }
  return i;
}

// Position direkt hinter der schließenden Klammer eines Blocks, der bei `open` beginnt.
function blockEnd(text, open) {
  let depth = 0, i = open;
  while (i < text.length) {
    if (text.startsWith('/*', i)) { i = text.indexOf('*/', i + 2) + 2; continue; }
    const ch = text[i];
    if (ch === '"' || ch === "'") { i++; while (i < text.length && text[i] !== ch) i += text[i] === '\\' ? 2 : 1; i++; continue; }
    if (ch === '{') depth++;
    else if (ch === '}' && --depth === 0) return i + 1;
    i++;
  }
  return i;
}

// Liest eine Ebene: Kommentare, Regeln und @-Blöcke. @media/@supports werden rekursiv gelesen.
export function parseCss(text, i = 0, end = text.length) {
  const items = [];
  while (i < end) {
    while (i < end && /\s/.test(text[i])) i++;
    if (i >= end) break;
    if (text.startsWith('/*', i)) { const close = text.indexOf('*/', i + 2) + 2; items.push({ type:'comment', start:i, end:close }); i = close; continue; }
    if (text[i] === '@') {
      const stop = scanTo(text, i, '{;');
      const prelude = text.slice(i, stop).trim();
      if (text[stop] === ';') { items.push({ type:'statement', start:i, end:stop + 1, prelude }); i = stop + 1; continue; }
      const close = blockEnd(text, stop);
      const nested = /^@(media|supports)\b/.test(prelude);
      items.push({ type:'at', start:i, end:close, prelude, children: nested ? parseCss(text, stop + 1, close - 1) : null });
      i = close; continue;
    }
    const open = scanTo(text, i, '{');
    const close = blockEnd(text, open);
    const selector = text.slice(i, open);
    items.push({ type:'rule', start:i, end:close, selStart:i, selEnd:open, selector:selector.trim(), selectors:splitSelectors(selector) });
    i = close;
  }
  return items;
}

// Teilt eine Selektorliste an Kommas auf oberster Ebene.
export function splitSelectors(list) {
  const parts = []; let depth = 0, from = 0;
  for (let i = 0; i < list.length; i++) {
    const ch = list[i];
    if (ch === '(' || ch === '[') depth++;
    else if (ch === ')' || ch === ']') depth--;
    else if (ch === ',' && depth === 0) { parts.push(list.slice(from, i).trim()); from = i + 1; }
  }
  parts.push(list.slice(from).trim());
  return parts.filter(Boolean);
}

// Alle Regeln (auch in @media) als flache Liste.
export const allRules = items => items.flatMap(item => item.type === 'rule' ? [item] : item.children ? allRules(item.children) : []);
