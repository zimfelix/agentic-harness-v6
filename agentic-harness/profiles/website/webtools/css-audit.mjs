// Findet CSS-Selektoren in den Style-Quellen (konfig.styles), die auf keiner gebauten Seite etwas treffen
// (Profil Website, Konsistenz-Audit Punkt 7). Aufruf aus dem Projektordner, vorher bauen:
//   node <webtools>/css-audit.mjs         Liste der ungenutzten Selektoren je Datei
//   node <webtools>/css-audit.mjs --fix   ungenutzte Selektoren aus den Quelldateien entfernen
// Wie Zustände gewertet werden: unused-css.mjs.
import { writeFile } from 'node:fs/promises';
import { unusedSelectors } from './unused-css.mjs';

const fix = process.argv.includes('--fix');
const { files, used, unused } = await unusedSelectors();

let total = 0;
for (const file of files) {
  const list = unused[file.path];
  total += list.length;
  if (list.length) console.log(`${file.path}: ${list.length} ungenutzte Selektoren`);
  if (!fix) { for (const sel of list) console.log(`  ${sel}`); continue; }
  const edits = [];
  removeUnused(file.text, file.items, used, edits);
  let text = file.text;
  for (const { start, end, replacement } of edits.sort((x, y) => y.start - x.start)) text = text.slice(0, start) + replacement + text.slice(end);
  await writeFile(file.path, text);
}
console.log(total ? `${total} ungenutzte Selektoren${fix ? ' entfernt' : ''}.` : 'Keine ungenutzten Selektoren.');
process.exitCode = total && !fix ? 1 : 0;

// Entfernt tote Selektoren, leere Regeln, leere @media-Blöcke und Kommentare, deren ganze Gruppe entfällt.
// Gibt zurück, ob von der Ebene nichts übrig bleibt.
function removeUnused(text, items, used, edits) {
  // Zeile mitnehmen, wenn das Element allein auf ihr steht.
  const cut = (start, end) => {
    const lineStart = text.lastIndexOf('\n', start - 1) + 1;
    const lineEnd = text.indexOf('\n', end);
    const alone = !text.slice(lineStart, start).trim() && !text.slice(end, lineEnd === -1 ? text.length : lineEnd).trim();
    edits.push(alone ? { start:lineStart, end:lineEnd === -1 ? text.length : lineEnd + 1, replacement:'' } : { start, end, replacement:'' });
  };
  let group = { comments:[], members:[] }, allGone = true;
  const closeGroup = () => {
    if (group.members.length && group.members.every(m => m.gone)) group.comments.forEach(c => cut(c.start, c.end));
    group = { comments:[], members:[] };
  };
  for (const item of items) {
    if (item.type === 'comment') { if (group.members.length) closeGroup(); group.comments.push(item); continue; }
    let gone = false;
    if (item.type === 'rule') {
      const keep = item.selectors.filter(s => used.has(s));
      if (!keep.length) { gone = true; cut(item.start, item.end); }
      else if (keep.length < item.selectors.length) {
        const separator = /,\s+/.test(item.selector) ? ', ' : ',';
        edits.push({ start:item.selStart, end:item.selEnd, replacement:keep.join(separator) });
      }
    } else if (item.children) {
      const before = edits.length;
      if (removeUnused(text, item.children, used, edits)) { edits.splice(before); gone = true; cut(item.start, item.end); }
    }
    group.members.push({ gone });
    if (!gone) allGone = false;
  }
  closeGroup();
  return allGone && items.some(i => i.type !== 'comment');
}
