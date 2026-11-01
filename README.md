# Agentic Harness V6 — schlank, mit überprüfbarem Vergleich

**Ergebnis:** Für Intermediate-Projekte empfehle ich den schlankeren Ansatz. Kein universeller Codequalitätssieger; beide lösen die meisten Aufgaben, der Kandidat braucht weniger Prozess-/Tokenaufwand. Ein echter Dispatch-Fehler im ersten schlanken Lauf bleibt dokumentiert. [Auswertung und Grenzen](reports/RESULTS.md)

```text
Freier Brief → PROJECT: Ziel, Grenzen, Stack und Entscheidungen
             → relevante Spec → autonome Umsetzung → gezielte Verification
                                    ↓
                         Skills nur bei tatsächlichem Bedarf
```

## Skills

Eigene Skills liegen nur hier unter `harness/.agents/skills/` und sind global verlinkt (`~/.claude/skills/`, `~/.pi/agent/skills/`); der Core in `harness/AGENTS.md` löst sie aus.

| Eigener Skill | Wofür | Auslöser im Core |
|---|---|---|
| `website-tools` | Websites: Inhalte, Responsive, Rechte, Veröffentlichung; optionale Screenshot-/Prüf-Tools | Arbeit an einer Website |
| `business-software` | Geschäftslogik: Datenintegrität, Migration, Rechte, Geld/Zeit, externe Wirkungen | Geschäftslogik, Persistenz, Rechte, Integrationen |
| `testing` | Tests, die Verhalten an echten Grenzen prüfen; Mocks nur an fremden Grenzen; wann TDD; wann stoppen | Tests planen, schreiben oder prüfen |
| `handoff` | Knapper Übergabe-Prompt (4–5 Sätze) für einen neuen Chat: Ziel, nächste Schritte, Belege statt Erklärungen | Wechsel in einen neuen Chat, langer Kontext (über die Skill-Beschreibung, kein Core-Auslöser) |

Wie oft die Skills tatsächlich geladen wurden (eigene zuerst, dann importierte):

<!-- skills:start -->
Stand 2026-11-01, aus lokalen Claude-Code- und Pi-Protokollen (`python3 tools/skill_usage.py --readme`).

| Skill | Herkunft | Ladungen Claude | Ladungen Pi | Sitzungen | zuletzt |
|---|---|---:|---:|---:|---|
| `business-software` | eigen (v6) | 8 | 8 | 9 | 2026-11-01 |
| `website-tools` | eigen (v6) | 8 | 4 | 6 | 2026-11-01 |
| `testing` | eigen (v6) | 2 | 0 | 1 | 2026-11-01 |
| `handoff` | eigen (v6) | 0 | 0 | 0 | – |
| `commit` | importiert: ~/.local/share/agent-skills/mitsuhiko-agent-stuff | 30 | 8 | 32 | 2026-11-01 |
| `sitegeist` | importiert: ~/.local/share/agent-skills | 18 | 0 | 18 | 2026-10-31 |
| `librarian` | importiert: ~/.local/share/agent-skills/mitsuhiko-agent-stuff | 2 | 7 | 6 | 2026-10-10 |
| `summarize` | importiert: ~/.local/share/agent-skills/mitsuhiko-agent-stuff | 4 | 0 | 1 | 2026-10-09 |
| `discuss` | importiert: ~/.local/share/agent-skills/mitsuhiko-agent-stuff | 3 | 0 | 2 | 2026-10-21 |
| `obsidian-cli` | importiert: ~/.local/share/agent-skills/obsidian-skills | 0 | 3 | 2 | 2026-10-05 |
| `obsidian-markdown` | importiert: ~/.local/share/agent-skills/obsidian-skills | 0 | 2 | 2 | 2026-10-05 |
| `json-canvas` | importiert: ~/.local/share/agent-skills/obsidian-skills | 0 | 0 | 0 | – |
<!-- skills:end -->

Gezählt werden Ladungen, nicht Nützlichkeit; Sitzungen, in denen ein Skill nur bearbeitet wurde, zählen mit. Ein Skill, der über Wochen bei 0 bleibt, ist ein Kandidat zum Entfernen oder für eine bessere Beschreibung.

## Learnings

Jedes Projekt hat eine `learnings.md`: oben ein fester Kopf, der den Ablauf erklärt (bleibt per `tools/update.py` aktuell), darunter Einträge zu Stellen, an denen Core oder Skill nicht funktioniert haben. Der Agent prüft offene Einträge zu Beginn jeder Aufgabe. Gesichtet wird gebündelt hier, etwa wöchentlich:

```sh
python3 tools/learnings.py        # offene Einträge aller Projekte (automatisch gefunden) + eigene
python3 tools/learnings.py --all  # alle Status
```

Übernommen wird nach „Reviewing and adopting learnings“ in [`AGENTS.md`](AGENTS.md): einordnen (die meisten Learnings gehören in einen Skill oder bleiben lokal), knapp formulieren, dann eine Prüfschleife, bis alles passt – sinnvoll als allgemeine Regel, keine Wiederholung, präzise, richtig eingeordnet, ufert nicht aus, wo möglich durch einen Test abgesichert. Ersetzen ist eine Möglichkeit, kein Zwang. Danach Eintrag im Projekt schließen.

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

Universell sind: `AGENTS.md` **oberhalb** der Markierungszeile `<!-- harness-v6@<version> … -->`, der Kopf von `learnings.md` oberhalb von `<!-- learnings:entries … -->`, `specs/README.md` und `ideas/README.md`. Projektregeln stehen unterhalb der Markierung; `PROJECT.md`, übrige Specs/Ideas, Learnings-Einträge, `README.md` und Code schreibt das Update nie. Was sich nicht sicher automatisch ersetzen lässt (lokal geänderte Dateien, geänderte `PROJECT.md`-Vorlage), landet als Hinweis in `harness-update.md` im Projekt; der Agent bespricht ihn bei der nächsten Aufgabe und löscht die Datei danach. Projekte ohne Markierung (alter Harness) bleiben unberührt und brauchen einmal einen Umzug.

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
