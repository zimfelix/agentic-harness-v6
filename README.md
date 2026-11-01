# Agentic Harness V6 — schlank, mit überprüfbarem Vergleich

**Ergebnis:** Für Intermediate-Projekte empfehle ich den schlankeren Ansatz. Kein universeller Codequalitätssieger; beide lösen die meisten Aufgaben, der Kandidat braucht weniger Prozess-/Tokenaufwand. Ein echter Dispatch-Fehler im ersten schlanken Lauf bleibt dokumentiert. [Auswertung und Grenzen](reports/RESULTS.md)

```text
Freier Brief → PROJECT: Ziel, Grenzen, Stack und Entscheidungen
             → relevante Spec → autonome Umsetzung → gezielte Verification
                                    ↓
                         Skills nur bei tatsächlichem Bedarf
```

## Neue Projekte

```sh
# Ziel muss neu oder leer sein; keine überschreibenden Updates:
python3 tools/export.py /absolute/path/to/project

# Nur wenn das Projekt ohne globale Skill-Links laufen muss (Cloud, anderer Rechner):
python3 tools/export.py /absolute/path/to/project --with-skills

python3 tools/launch.py --project /absolute/path/to/project --client pi
python3 tools/launch.py --project /absolute/path/to/project --client claude
```

**Skills werden nicht ins Projekt kopiert.** Einzige Quelle ist `harness/.agents/skills/` in diesem Repo; Claude Code und Pi sehen sie über globale Links (`~/.claude/skills/<name>`, `~/.pi/agent/skills/<name>` → dieser Ordner). Eine Skill-Verbesserung aus einem beliebigen Projekt landet damit direkt hier und wird hier committet; kein Rückkopieren. `--with-skills` legt eine Kopie samt `.claude/skills`-Links ins Projekt, die nicht zurückfließt. Der Claude-Launcher lädt die aktuelle projektbezogene `AGENTS.md` ausdrücklich. Keine Projekt-`CLAUDE.md`. Ohne diese Integration nicht behaupten, ein normaler Claude-Start erkenne AGENTS/`.agents` automatisch. [Client-Kompatibilität](reports/CLIENT-COMPATIBILITY.md)

## Bestehende Projekte aktualisieren

```sh
python3 tools/update.py ~/Code/projekt-a ~/Code/projekt-b          # nur anzeigen
python3 tools/update.py ~/Code/projekt-a ~/Code/projekt-b --apply  # schreiben (v6 vorher committen)
```

Universell sind nur drei Dateien: `AGENTS.md` **oberhalb** der Markierungszeile `<!-- harness-v6@<version> … -->`, `specs/README.md` und `ideas/README.md`. Projektregeln stehen unterhalb der Markierung; `PROJECT.md`, übrige Specs/Ideas, `README.md`, `learning-state.md` und Code schreibt das Update nie. Was sich nicht sicher automatisch ersetzen lässt (lokal geänderte Dateien, geänderte `PROJECT.md`-Vorlage), landet als Hinweis in `harness-update.md` im Projekt; der Agent bespricht ihn bei der nächsten Aufgabe und löscht die Datei danach. Projekte ohne Markierung (alter Harness) bleiben unberührt und brauchen einmal einen Umzug.

## Aufbau

```text
harness/          exportierbarer Harness; kein separater profiles-Katalog
  AGENTS.md        Arbeitsweise + Verification
  PROJECT.md       konkreter Brief, Architektur/Stack, aktueller Stand
  specs/           relevantes Verhalten und Nachweise
  ideas/           optional für offene/größere Vorhaben
  .agents/skills/  einzige Skill-Quelle, global verlinkt, standardmäßig nicht exportiert
                  business-software: bedarfsgeladene Risiken
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
python3 benchmarks/run.py --workspace /tmp/new-comparison prepare --baseline /path/to/original-v6   # Checkout von Commit dc1af55 (v6.1)
python3 benchmarks/run.py --workspace /tmp/new-comparison pair crm --run-agents
```

[Versuchsplan](reports/PLAN.md) · [QA-Szenarien](benchmarks/QA-NOTES.md) · [Messwerte](reports/metrics.json) · [Produktextrakte](benchmarks/fixtures/README.md)

Die Hauptresultate gelten für den eingefrorenen Kandidaten vor der anschließenden Profile→Skills-Konsolidierung. Parität/Export/Client-Start und die ergänzende Init-Gegenprobe prüfen den finalen Aufbau; kein erfundener zusätzlicher Effizienzbeweis. Die frühe Kandidatenfassung liegt als Commit `f06f60b` im Vorgänger-Repo `zimfelix/agentic-harness-v6-next`; die Ergänzungen aus dem Lexware-Pilot danach sind nicht mitgemessen ([Einordnung](reports/LEXWARE-LEARNINGS.md)).

Keine Rohsessions, Zugangsdaten oder fremden Produktdaten veröffentlicht. Bestehende Projekte werden nicht automatisch umgeschrieben.
