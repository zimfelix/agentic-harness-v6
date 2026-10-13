# Agentic Harness V6 — schlank, mit überprüfbarem Vergleich

**Ergebnis:** Für Intermediate-Projekte empfehle ich den schlankeren Ansatz. Kein universeller Codequalitätssieger; beide lösen die meisten Aufgaben, der Kandidat braucht weniger Prozess-/Tokenaufwand. Ein echter Dispatch-Fehler im ersten schlanken Lauf bleibt dokumentiert. [Auswertung und Grenzen](reports/RESULTS.md)

```text
Freier Brief → PROJECT: Ziel, Grenzen, Stack und Entscheidungen
             → relevante Spec → autonome Umsetzung → gezielte Verification
                                    ↓
                         Skills nur bei tatsächlichem Bedarf
```

## Präzisierungen aus dem Lexware-Pilot

Der aktuelle Export macht drei Punkte konkreter: fachliches Verständnis vor größeren Aufgaben spiegeln, Projekt-/Ausführungswechsel ankündigen und eine nächste autorisierte Aktion statt bloß eines Testbefehls festhalten. Kein Pflichtfragebogen oder neues Freigaberitual. [Änderungen, Einordnung und Grenzen](reports/LEXWARE-LEARNINGS.md)

Diese Ergänzungen sind nach dem bisherigen Vergleich entstanden; dessen Messwerte beweisen ihre Wirksamkeit nicht. Bestehende Produkte werden nicht automatisch überschrieben.

## Neue Projekte

```sh
# Ziel muss neu oder leer sein; keine überschreibenden Updates:
python3 tools/export.py /absolute/path/to/project

# Zusätzlich Claude-Skill-Erkennung, ohne kopierte Regeln:
python3 tools/export.py /absolute/path/to/project --claude

python3 tools/launch.py --project /absolute/path/to/project --client pi
python3 tools/launch.py --project /absolute/path/to/project --client claude
```

Der Claude-Launcher lädt die aktuelle projektbezogene `AGENTS.md` ausdrücklich. `.claude/skills/<name>` ist nur ein relativer Link auf `.agents/skills/<name>`. Keine Projekt-`CLAUDE.md`, keine globalen Änderungen, keine zweite Skill-Quelle. Ohne diese Integration nicht behaupten, ein normaler Claude-Start erkenne AGENTS/`.agents` automatisch. [Client-Kompatibilität](reports/CLIENT-COMPATIBILITY.md)

## Aufbau

```text
harness/          exportierbarer Harness; kein separater profiles-Katalog
  AGENTS.md        Arbeitsweise + Verification
  PROJECT.md       konkreter Brief, Architektur/Stack, aktueller Stand
  specs/           relevantes Verhalten und Nachweise
  ideas/           optional für offene/größere Vorhaben
  .agents/skills/  business-software: bedarfsgeladene Risiken
                  website-tools: Grundlagen + optionale Tools/Referenzen
benchmarks/        Aufgaben, unabhängige Abnahme, isolierte Agentenläufe
  fixtures/       synthetische erzeugte Produkte für modellfreie Wiederholung
tests/             technische Regression und Fehler-Gegenfälle
reports/           Messwerte, Ergebnisse, Infrastrukturfehler und Grenzen
tools/             sicherer Export, Client-Start, Ergebnisaufbereitung
```

Im normalen Projekt werden nur `harness/`-Inhalte exportiert, nicht Benchmarks/Produktsamples/Reports. Regeln und Skripte haben jeweils eine Quelle. Kein Pflicht-Framework, kein Enterprise-Aufbau, keine Freigabe für jedes Implementierungsdetail. Projektentscheidungen bleiben verbindlich; kritische Skill-Leseauslöser stehen direkt in AGENTS.

## Tatsächliche Prüfungen

```sh
# Kein Modellverbrauch:
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
HARNESS_BRAVE_TESTS=1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -W error::ResourceWarning -m unittest discover -s benchmarks -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 benchmarks/verify_planners.py --output /tmp/planner-results.json
```

Die normale technische Suite überspringt fünf Brave-Fälle ausdrücklich; volle lokale Ausführung nutzt verifiziertes Brave. Oracle-Selbsttests belegen Fehlererkennung/Containment, nicht allein Produktqualität. 59 Stress-Prüfgruppen, getrennte Seeds, frische Fortsetzungen, Anforderungsänderung, externer Blocker, früher Brief und freiere Sol-/Opus-Projekte sind im Bericht einzeln ausgewiesen.

Abhängigkeiten: Python 3 für Export/Tests; Node.js 22.19+ und Brave nur für optionale Website-Werkzeuge. Keine npm-Pakete. Modellfreie Produktsamples haben ihre dokumentierten Python-/Node-Voraussetzungen. Tatsächlich geprüft: Python 3.14.7, Node 26.8.1, macOS; keine vollständige Runtime-/OS-Matrix.

## Vergleiche wiederholen

Modellaufrufe sind opt-in, kosten Quota und benötigen authentifiziertes Pi/CodexBar sowie macOS `sandbox-exec`:

```sh
python3 benchmarks/run.py --workspace /tmp/new-comparison prepare --baseline /path/to/original-v6
python3 benchmarks/run.py --workspace /tmp/new-comparison pair crm --run-agents
```

[Versuchsplan](reports/PLAN.md) · [QA-Szenarien](benchmarks/QA-NOTES.md) · [Messwerte](reports/metrics.json) · [Produktextrakte](benchmarks/fixtures/README.md)

Die Hauptresultate gelten für den eingefrorenen Kandidaten vor der anschließenden Profile→Skills-Konsolidierung. Parität/Export/Client-Start und die ergänzende Init-Gegenprobe prüfen den finalen Aufbau; kein erfundener zusätzlicher Effizienzbeweis. Die frühe Kandidatenfassung bleibt in Git erreichbar.

Keine Rohsessions, Zugangsdaten oder fremden Produktdaten veröffentlicht. Bestehende Projekte werden nicht automatisch umgeschrieben.
