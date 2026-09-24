# S001 – Starter-Kit-Initialisierung und Quality Gate

> **Verantwortung:** Diese Spec hält das konkrete Verhalten fest, das beim Starter-Kit bereits umgesetzt und geprüft wurde. Sie zeigt, welche Akzeptanzkriterien das Project Init und das neutrale Quality Gate erfüllen müssen.

## Meta

- **State:** Implemented

## User Story

Als **Nutzer eines neuen Projekts** möchte ich **nur passende Projektregeln initialisieren und ein echtes Quality Gate ausführen**, damit **ein unkonfigurierter Prototyp nicht als geprüft gilt**.

## Beschreibung

Das Starter-Kit enthält universelle Regeln und sichtbare, noch nicht initialisierte projektspezifische Kategorien. Project Init befüllt für ein konkretes Projekt nur benötigte Regeln und richtet dessen Prüfungen ein. Das Gate führt konfigurierte Befehle ohne Shell aus und meldet Fehler zuverlässig.

## Akzeptanzkriterien

- **AK1:** Ohne projektbezogene Gate-Konfiguration endet `scripts/verify.py` mit Fehlerstatus.
- **AK2:** Eine Gate-Konfiguration ohne Checks endet mit Fehlerstatus.
- **AK3:** Für eine gültige Konfiguration werden die Checks aus deren Liste ausgeführt.
- **AK4:** Ein fehlgeschlagener Check führt zu einem Fehlerstatus des Gates.
- **AK5:** Ungültige Konfigurationen und nicht ausführbare Befehle führen zu einem Fehlerstatus mit verständlicher Meldung.
- **AK6:** Im kopierbaren Starter-Kit sind die vorgesehenen projektspezifischen Markdown-Dateien als künftige Projektrichtlinien sichtbar und bis Project Init eindeutig als noch nicht definiert gekennzeichnet.

## Nicht im Umfang

- Prüfungen für eine konkrete Anwendung oder automatische Erzeugung der Projektkonfiguration.

## Nachweise

- **AK6 [Statisch]:** `PASS` — alle sechs `project-specific/*.md` sind mit `Pending Project Init` als vorgesehene Projektrichtlinien markiert; `AGENTS.md` und `project-init.md` berücksichtigen den Marker; keine widersprechenden alten Statusformulierungen.
- **Quality Gate:** `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s harness-v2/tests -v` — 5 Tests bestanden; `.venv/bin/python -m ruff check harness-v2/scripts/verify.py harness-v2/tests/test_verify.py` — bestanden. Das Gate eines noch nicht initialisierten Zielprojekts bleibt absichtlich rot.
