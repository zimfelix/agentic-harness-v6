#!/bin/sh
# Exportiert die explizite universelle Dateiliste, nie Produktdaten. Kein Commit/Push.
# ZIEL: leer oder sauberer, unbefüllter Export-Klon mit .harness-template.
set -eu
QUELLE=$(cd "$(dirname "$0")/.." && pwd)
[ -n "${1:-}" ] || { echo 'Aufruf: sh tools/export-harness.sh ZIEL' >&2; exit 1; }
export QUELLE
ZIEL=$(python3 - "$1" <<'PY'
import os, sys
from pathlib import Path
src=Path(os.environ['QUELLE']).resolve(); dst=Path(sys.argv[1]).resolve()
if src == dst or src in dst.parents or dst in src.parents:
    sys.exit('Quelle/Ziel dürfen nicht ineinander liegen')
print(dst)
PY
)
if [ ! -e "$ZIEL" ]; then
  MODUS=neu
elif [ -d "$ZIEL" ] && [ -z "$(ls -A "$ZIEL")" ]; then
  MODUS=neu
elif [ -d "$ZIEL" ] && [ -e "$ZIEL/.git" ] && [ -f "$ZIEL/.harness-template" ] \
  && [ -f "$ZIEL/harness/project.md" ] && grep -q '^\*\*Status:\*\* Pending Project Init$' "$ZIEL/harness/project.md" \
  && grep -q '^# Agentic Harness' "$ZIEL/README.md"; then
  [ -z "$(git -C "$ZIEL" status --porcelain)" ] || { echo 'Ziel hat offene Änderungen' >&2; exit 1; }
  # A stale template marker must not turn a pending product project into an update target.
  python3 - "$ZIEL" <<'PY'
import sys
from pathlib import Path
root=Path(sys.argv[1])
allowed={'.git','.idea','.DS_Store','.gitignore','.harness-template','AGENTS.md','README.md',
         'document-contract.md','harness-learnings.md','harness','profiles','tools','docs','project','ideas','specs'}
if any(p.name not in allowed for p in root.iterdir()):
    sys.exit('Ziel enthält Produkt-/Fremddateien; Aktualisierung abgelehnt')
for directory, allowed_names in [('docs',{'architecture.md','code.md','testing.md','design.md'}),
                                 ('project',{'README.md'}),('ideas',{'I000-readme.md'}),('specs',{'S000-readme.md'})]:
    if any(p.name not in allowed_names for p in (root/directory).iterdir()):
        sys.exit('Ziel enthält konkrete Projektartefakte; Aktualisierung abgelehnt')
PY
  MODUS=aktualisieren
else
  echo 'Ziel ist weder leer noch ein sauberer unbefüllter Export-Klon' >&2
  exit 1
fi
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/harness/templates" "$TMP/docs" "$TMP/ideas" "$TMP/specs" "$TMP/project"
cd "$QUELLE"
cp AGENTS.md document-contract.md harness-learnings.md "$TMP/"
cp harness/core.md harness/init.md harness/project.md harness/verification.md harness/README.md "$TMP/harness/"
cp harness/templates/idea.md harness/templates/spec.md harness/templates/project.md "$TMP/harness/templates/"
for name in architecture code testing design; do cp "docs/$name.md" "$TMP/docs/"; done
cp -R profiles tools "$TMP/"
cp ideas/I000-readme.md "$TMP/ideas/"
cp specs/S000-readme.md "$TMP/specs/"
cp project/README.md "$TMP/project/"
printf '.DS_Store\n.idea/\n__pycache__/\n' > "$TMP/.gitignore"
printf 'Agentic Harness export template\n' > "$TMP/.harness-template"
cat > "$TMP/README.md" <<EOF
# Agentic Harness${VERSION:+ $VERSION}

Vorlage für Softwareprojekte mit KI-Coding-Agenten. Ordner öffnen und das Vorhaben beschreiben; optional zuerst \`project/brief.md\` schreiben. Init klärt Brief, Technik, Struktur und Prüfungen vor Produktcode.

Anleitung: [harness/README.md](harness/README.md). Nach Init hier Produktzweck, Einrichtung und geprüfte Startschritte eintragen.
EOF
# Produktteile zurücksetzen; der Reset verwendet die unbefüllte Vorlage nicht als Produktquelle.
python3 - "$QUELLE" "$TMP" <<'PY'
import sys
from pathlib import Path
src, dst=map(Path,sys.argv[1:])
for name in ('harness/project.md','docs/architecture.md','docs/code.md','docs/testing.md','docs/design.md'):
    p=dst/name; before, marker, _=p.read_text().partition('## Projektspezifische Befüllung')
    if not marker: sys.exit('Export-Trennung fehlt: '+name)
    if name == 'harness/project.md':
        # Required field defaults have one source: the unfilled project template.
        template=(src/'harness/templates/project.md').read_text()
        _, found, body=template.partition('## Projektspezifische Befüllung')
        if not found: sys.exit('Projekt-Template fehlt')
        body=body.lstrip()
    else: body='Noch offen (Project Init).\n'
    p.write_text(before+marker+'\n\n'+body)
for name,marker,body in [('AGENTS.md','## Projektspezifische Ergänzungen',''),
                         ('harness-learnings.md','## Aktive Learnings','\n### Offen\n\nKeine.\n\n### Lokal übernommen\n\nKeine.\n')]:
    p=dst/name; before, found, _=p.read_text().partition(marker)
    if not found: sys.exit('Export-Trennung fehlt: '+name)
    p.write_text(before+marker+'\n'+body)
# No IDE artifacts or caches from the source belong in exports.
import shutil
for p in list(dst.rglob('__pycache__'))+list(dst.rglob('.DS_Store')):
    if p.is_dir(): shutil.rmtree(p)
    else: p.unlink()
PY
python3 "$TMP/tools/check-harness.py"
python3 - "$TMP" <<'PY'
import re, sys
from pathlib import Path
pattern=re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}')
for path in Path(sys.argv[1]).rglob('*'):
    if not path.is_file(): continue
    try: text=path.read_text()
    except UnicodeError: continue
    found=[s for s in pattern.findall(text) if s not in ('git@github.com','git@gitlab.com')]
    if found: sys.exit('Mögliche Produktadresse in '+str(path.relative_to(sys.argv[1]))+'; Ziel unverändert')
PY
if [ -n "${PRODUKTBEGRIFFE:-}" ] && grep -rniE "$PRODUKTBEGRIFFE" "$TMP"; then
  echo 'Abbruch: mögliche Produktreste; Ziel unverändert' >&2; exit 1
fi
if [ "$MODUS" = neu ]; then
  mkdir -p "$ZIEL"
  cp -R "$TMP"/. "$ZIEL"/
else
  rsync -a --checksum --delete --exclude '.git' --exclude '.idea' --exclude '.DS_Store' "$TMP"/ "$ZIEL"/
fi
echo "Harness nach $ZIEL exportiert. Diff prüfen; kein Commit/Push ausgeführt."
