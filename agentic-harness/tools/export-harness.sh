#!/bin/sh
# Exportiert nur die vollständige Variante, setzt Projektteile zurück und prüft Verweise.
# Quelle wird am Skript lokalisiert, unabhängig von Arbeitsverzeichnis und Varianten-Repository.
# Aufruf: sh tools/export-harness.sh ZIEL
# ZIEL: leer/nicht vorhanden oder sauberer Git-Klon dieser flachen vollständigen Vorlage.
# Optional: PRODUKTBEGRIFFE='produktname|domain|ort', VERSION=v5.17
# Committet und pusht nichts. Nie auf ein Produktprojekt oder das Varianten-Repository richten.
set -eu

QUELLE=$(cd "$(dirname "$0")/.." && pwd)
ZIEL=${1:-}
[ -n "$ZIEL" ] || { echo 'Aufruf: sh tools/export-harness.sh ZIEL' >&2; exit 1; }
[ -f "$QUELLE/AGENTS.md" ] && [ -f "$QUELLE/harness/core.md" ] || {
  echo "Quelle ist keine vollständige Harness-Variante: $QUELLE" >&2; exit 1;
}

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
elif [ -e "$ZIEL/.git" ] && [ -f "$ZIEL/AGENTS.md" ] && [ -f "$ZIEL/harness/core.md" ] \
  && [ ! -d "$ZIEL/agentic-harness" ] && [ ! -d "$ZIEL/agentic-harness-lite" ]; then
  [ -z "$(git -C "$ZIEL" status --porcelain)" ] || { echo "Ziel hat offene Änderungen: $ZIEL" >&2; exit 1; }
  MODUS=aktualisieren
else
  echo "Ziel ist weder leer noch ein Git-Klon dieser vollständigen Harness-Vorlage: $ZIEL" >&2
  exit 1
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Universelle Dateien kopieren; konkrete Projektartefakte werden nicht übernommen.
mkdir -p "$TMP/ideas" "$TMP/specs" "$TMP/project"
cd "$QUELLE"
cp AGENTS.md "$TMP/"
cp -R harness docs profiles tools "$TMP/"
cp document-contract.md harness-map.md harness-learnings.md "$TMP/"
cp ideas/I000-readme.md "$TMP/ideas/"
cp specs/S000-readme.md "$TMP/specs/"
cp project/README.md "$TMP/project/"
printf '.DS_Store\n.idea/\n' > "$TMP/.gitignore"
cat > "$TMP/README.md" <<EOF
# Agentic Harness${VERSION:+ $VERSION}

Vollständige Vorlage für Softwareprojekte mit KI-Coding-Agenten. \`AGENTS.md\` führt von Klärung und Init über Umsetzung bis zur Verifikation. Projektart, Stack und Prüfungen werden beim Init geklärt; danach ersetzt der Agent diesen Kopf durch die Produktbeschreibung.

**Start:** Idee optional in \`project/brief.md\` erzählen oder den Projektordner mit dem Agenten öffnen und den Auftrag geben. Anleitung: [harness/README.md](harness/README.md).

EOF
grep -q '^## Projektstart mit dem Agentic Harness' README.md || {
  echo 'Abschnitt „Projektstart mit dem Agentic Harness“ fehlt in README.md' >&2; exit 1;
}
awk 'f && !c && /^## / { exit } /^## Projektstart mit dem Agentic Harness/ { f = 1 } /^```/ { c = !c } f' README.md >> "$TMP/README.md"

# Projektteile zurücksetzen.
cd "$TMP"
braucht() { grep -q "$2" "$1" || { echo "Abschnitt „$2“ fehlt in $1" >&2; exit 1; }; }
befuellung_leeren() {
  braucht "$1" '^## Projektspezifische Befüllung'
  awk -v st="$2" '
    /^> - \*\*Status:\*\*/ { print "> - **Status:** " st; next }
    /^## Projektspezifische Befüllung/ { print; print ""; print "Noch offen (Project Init)."; exit }
    { print }' "$1" > "$1.neu" && mv "$1.neu" "$1"
}
befuellung_leeren harness/project.md 'Pending Project Init'
for f in docs/*.md; do befuellung_leeren "$f" 'Noch offen (Project Init).'; done
braucht AGENTS.md '^## Projektspezifische Ergänzungen'
awk '/^## Projektspezifische Ergänzungen/ { print; exit } { print }' AGENTS.md > AGENTS.md.neu && mv AGENTS.md.neu AGENTS.md
braucht harness-learnings.md '^## Zweck und Regeln'
awk '
  /^> - \*\*Status:\*\*/ { print "> - **Status:** Noch keine Einträge."; next }
  /^## / { if (gesehen) exit; if ($0 == "## Zweck und Regeln") gesehen = 1 }
  { print }' harness-learnings.md > harness-learnings.md.neu && mv harness-learnings.md.neu harness-learnings.md
printf '## Aktive Learnings\n\n### Offen\n\nKeine.\n\n### Lokal übernommen\n\nKeine.\n' >> harness-learnings.md

# Erst bei vollständig validiertem Export wird das Ziel befüllt/geändert.
FUND=$(grep -rnoE '[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}' . | grep -vE ':git@(github|gitlab)\.com$' || true)
if [ -n "${PRODUKTBEGRIFFE:-}" ]; then
  FUND="$FUND$(grep -rniE "$PRODUKTBEGRIFFE" . || true)"
fi
FEHLT=$(grep -rhoE '(^|[^A-Za-z0-9_./-])(harness|docs|profiles|tools|ideas|specs|project)/[A-Za-z0-9_./-]+\.(md|sh)' . | sed 's/^[^A-Za-z]//' | sort -u | while read -r p; do
  # Projektdateien und ausdrücklich als xxx benannte Vorlagenbeispiele sind keine realen Ziele.
  case "$p" in (project/README.md) ;; (project/*|ideas/Ixxx-*|specs/Sxxx-*) continue ;; esac
  [ -e "$p" ] || echo "$p"
done)
if [ -n "$FUND" ] || [ -n "$FEHLT" ]; then
  [ -z "$FUND" ] || { echo 'Mögliche Produktreste:' >&2; echo "$FUND" >&2; }
  [ -z "$FEHLT" ] || { echo 'Verweise auf fehlende Dateien:' >&2; echo "$FEHLT" >&2; }
  echo 'Abbruch: Ziel wurde nicht verändert.' >&2
  exit 1
fi

if [ "$MODUS" = neu ]; then
  cp -R "$TMP"/. "$ZIEL"/
  echo "Vollständigen Harness nach $ZIEL exportiert. Ordner mit dem Agenten öffnen und Auftrag geben."
else
  rsync -a --checksum --delete --exclude '.git' --exclude '.idea' --exclude '.DS_Store' "$TMP"/ "$ZIEL"/
  echo "Vollständige Vorlage in $ZIEL aktualisiert. Diff prüfen und erst nach Freigabe pushen."
  git -C "$ZIEL" status --short
fi
