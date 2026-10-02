#!/bin/sh
# Hält die lokale Vorschau einer Website dauerhaft erreichbar (macOS, Profil Website), z. B. http://127.0.0.1:4173/
# Hintergrunddienst (launchd): baut beim Start, startet beim Anmelden und nach Abstürzen neu; serve.mjs baut bei Änderungen selbst neu.
# Name und Port kommen aus website.config.mjs des Projekts. Nur auf diesem Rechner erreichbar.
# Aufruf aus dem Projektordner:
#   sh <webtools>/vorschau-dauerhaft.sh            einrichten oder neu starten
#   sh <webtools>/vorschau-dauerhaft.sh status     prüfen, ob die Vorschau antwortet
#   sh <webtools>/vorschau-dauerhaft.sh entfernen  Dienst abschalten und löschen
set -eu

REPO=$(pwd)
WERKZEUGE=$(cd "$(dirname "$0")" && pwd)
NODE=$(command -v node) || { echo "node nicht gefunden."; exit 1; }
wert() { "$NODE" --input-type=module -e "import { konfig } from '$WERKZEUGE/konfig.mjs'; console.log($1)"; }
NAME=$(wert konfig.name)
PORT=$(wert konfig.port)
BUILD=$(wert "konfig.build.map(t => t === 'node' ? '\"$NODE\"' : JSON.stringify(t)).join(' ')")
LABEL="com.$(id -un).$NAME-vorschau"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG="$HOME/Library/Logs/$NAME-vorschau.log"
DOMAIN="gui/$(id -u)"
URL="http://127.0.0.1:$PORT/"

antwortet() { curl -fsS -o /dev/null --max-time 3 "$URL"; }

case "${1:-einrichten}" in
  entfernen)
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    rm -f "$PLIST"
    echo "Vorschau-Dienst entfernt."
    exit 0 ;;
  status)
    if antwortet; then echo "Vorschau läuft: $URL"; else echo "Vorschau antwortet nicht. Einrichten mit: sh $0"; exit 1; fi
    exit 0 ;;
  einrichten) ;;
  *) echo "Unbekannter Befehl: $1 (einrichten, status, entfernen)"; exit 2 ;;
esac

launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
sleep 1
if lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT ist von einem anderen Programm belegt (z. B. ein laufendes npm run dev):"
  lsof -nP -iTCP:$PORT -sTCP:LISTEN
  echo "Dieses Programm zuerst beenden, dann das Skript erneut ausführen."
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/sh</string><string>-c</string>
    <string>$BUILD; exec "$NODE" "$WERKZEUGE/serve.mjs"</string>
  </array>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>EnvironmentVariables</key>
  <dict><key>PORT</key><string>$PORT</string><key>HOST</key><string>127.0.0.1</string></dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>5</integer>
  <key>ProcessType</key><string>Background</string>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
EOF

launchctl bootstrap "$DOMAIN" "$PLIST"
for _ in $(seq 1 20); do
  if antwortet; then echo "Vorschau läuft dauerhaft: $URL (startet beim Anmelden und nach Abstürzen neu)"; exit 0; fi
  sleep 1
done
echo "Vorschau antwortet nicht. Protokoll: $LOG"
exit 1
