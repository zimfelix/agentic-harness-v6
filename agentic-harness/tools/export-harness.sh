#!/bin/sh
# Harness-Export: kopiert den universellen Harness, setzt die Projektteile zurück und prüft auf Reste.
# Committet und pusht nichts.
#
# Aufruf aus einem Projekt mit diesem Harness:
#   sh agentic-harness/tools/export-harness.sh ZIEL
#     ZIEL leer oder nicht vorhanden  → neues Projekt bzw. neue Vorlage anlegen
#     ZIEL sauberer Git-Klon der Vorlage → Inhalt außer .git und .idea ersetzen
#   Zusätzliche Suchbegriffe für Produktreste (Groß-/Kleinschreibung egal):
#   PRODUKTBEGRIFFE='produktname|domain|ort' sh agentic-harness/tools/export-harness.sh ZIEL
set -eu

H=agentic-harness
QUELLE=$(cd "$(dirname "$0")/../.." && pwd)
ZIEL=${1:-}
[ -n "$ZIEL" ] || { echo "Aufruf: sh $H/tools/export-harness.sh ZIEL" >&2; exit 1; }
[ -f "$QUELLE/AGENTS.md" ] || { echo "Quelle ohne AGENTS.md: $QUELLE" >&2; exit 1; }

pruefe_lage() {
  case "$1/" in "$QUELLE/"*) echo "Ziel liegt in der Quelle: $1" >&2; exit 1;; esac
  case "$QUELLE/" in "$1/"*) echo "Quelle liegt im Ziel: $1" >&2; exit 1;; esac
}
case "$ZIEL" in /*) ;; *) ZIEL="$PWD/$ZIEL";; esac
pruefe_lage "$ZIEL"
mkdir -p "$ZIEL"
ZIEL=$(cd "$ZIEL" && pwd)
pruefe_lage "$ZIEL"

if [ -z "$(ls -A "$ZIEL")" ]; then
  MODUS=neu
elif [ -d "$ZIEL/.git" ] && [ -f "$ZIEL/AGENTS.md" ] && [ -d "$ZIEL/$H" ]; then
  [ -z "$(git -C "$ZIEL" status --porcelain)" ] || { echo "Ziel hat offene Änderungen: $ZIEL" >&2; exit 1; }
  MODUS=aktualisieren
else
  echo "Ziel ist weder leer noch ein Git-Klon einer Harness-Vorlage: $ZIEL" >&2; exit 1
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# 1. Universelle Dateien und Profile kopieren
mkdir -p "$TMP/$H/ideas" "$TMP/$H/specs"
cd "$QUELLE"
cp AGENTS.md "$TMP/"
cp -R "$H/harness" "$H/docs" "$H/profiles" "$H/tools" "$TMP/$H/"
cp "$H/README.md" "$H/document-contract.md" "$H/harness-map.md" "$H/harness-learnings.md" "$TMP/$H/"
cp "$H/ideas/I000-readme.md" "$TMP/$H/ideas/"
cp "$H/specs/S000-readme.md" "$TMP/$H/specs/"
printf '.DS_Store\n.idea/\n' > "$TMP/.gitignore"
printf '# Neues Produktprojekt\n\nVorlage: Die Anleitung zum Harness steht in [agentic-harness/README.md](agentic-harness/README.md). Diese Datei wird beim Project Init durch die Produkt-README ersetzt.\n' > "$TMP/README.md"

# 2. Projektteile zurücksetzen
cd "$TMP"
braucht() { grep -q "$2" "$1" || { echo "Abschnitt „$2“ fehlt in $1" >&2; exit 1; }; }

befuellung_leeren() { # Datei, neue Status-Zeile
  braucht "$1" '^## Projektspezifische Befüllung'
  awk -v st="$2" '
    /^> - \*\*Status:\*\*/ { print "> - **Status:** " st; next }
    /^## Projektspezifische Befüllung/ { print; print ""; print "Noch offen (Project Init)."; exit }
    { print }' "$1" > "$1.neu" && mv "$1.neu" "$1"
}
befuellung_leeren "$H/harness/project.md" 'Pending Project Init'
for f in "$H"/docs/*.md; do befuellung_leeren "$f" 'Noch offen (Project Init).'; done

braucht AGENTS.md '^## Projektspezifische Ergänzungen'
awk '/^## Projektspezifische Ergänzungen/ { print; exit } { print }' AGENTS.md > AGENTS.md.neu && mv AGENTS.md.neu AGENTS.md

L="$H/harness-learnings.md"
braucht "$L" '^## Abgrenzung'
awk '
  /^> - \*\*Status:\*\*/ { print "> - **Status:** Noch keine Beobachtungen."; next }
  /^## / { if (gesehen) exit; if ($0 == "## Abgrenzung") gesehen = 1 }
  { print }' "$L" > "$L.neu" && mv "$L.neu" "$L"
printf '## Beobachtungen\n\nNoch keine Beobachtungen.\n' >> "$L"

# 3. Auf Reste und fehlende Verweise prüfen
FUND=$(grep -rnE '[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}' . || true)
if [ -n "${PRODUKTBEGRIFFE:-}" ]; then
  FUND="$FUND$(grep -rniE "$PRODUKTBEGRIFFE" . || true)"
fi
FEHLT=$(grep -rhoE "$H/[A-Za-z0-9_./-]+\.(md|sh)" . | sort -u | while read -r p; do
  [ -e "$p" ] || [ "$p" = "$H/project-brief.md" ] || echo "$p"
done)
if [ -n "$FUND" ] || [ -n "$FEHLT" ]; then
  [ -z "$FUND" ] || { echo "Mögliche Produktreste:" >&2; echo "$FUND" >&2; }
  [ -z "$FEHLT" ] || { echo "Verweise auf fehlende Dateien:" >&2; echo "$FEHLT" >&2; }
  echo "Abbruch: Ziel wurde nicht verändert." >&2
  exit 1
fi

# 4. Ins Ziel übertragen
if [ "$MODUS" = neu ]; then
  cp -R "$TMP"/. "$ZIEL"/
  echo "Harness nach $ZIEL exportiert. Nächster Schritt: Ordner mit dem Agenten öffnen und den Auftrag geben."
else
  rsync -a --delete --exclude '.git' --exclude '.idea' --exclude '.DS_Store' "$TMP"/ "$ZIEL"/
  echo "Vorlage in $ZIEL aktualisiert. Änderungen:"
  git -C "$ZIEL" status --short
  echo "Diff prüfen, committen und erst nach Freigabe pushen."
fi
