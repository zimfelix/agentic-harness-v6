# Agentic Harness V2 – Starter-Kit

**Status: Prototyp.** Die Runner-Tests und kurze Wegwerf-Piloten sind bestanden, aber der Harness wurde noch nicht durch vollständige Project-Init-Abläufe in realen Projekten validiert. Zur Nutzung werden die Harness-Dateien in ein bestehendes oder neues Projekt kopiert, dort per Project Init angepasst und mit projektspezifischen Checks vervollständigt.

Kopiere `AGENTS.md`, `learning-state.md`, `harness/rules/`, `harness/templates/` und, sofern Python verfügbar ist, `scripts/verify.py` in das Root eines neuen Projekts. Die Entwicklungsartefakte unter `ideas/`, `specs/` und `tests/` gehören **nicht** in das Zielprojekt. Überschreibe vorhandene Projektdateien nicht blind: Führe bestehende `AGENTS.md`-Regeln zusammen und übernimm diese README-Zuständigkeitskarte in eine vorhandene Projekt-README. Bei Project Init wird `learning-state.md` zur knappen, manuellen Sammlung bestätigter Erkenntnisse aus diesem Projekt. Sie wird nur auf ausdrücklichen Sammelauftrag am Ende eines Chats/Tages aktualisiert; Projektstatus bleibt in README, Specs und Git nachvollziehbar. Allgemeine, übertragbare Learnings werden später separat kuratiert und nur auf ausdrücklichen Auftrag in globale Agent-Dateien übernommen. Diese Einleitung wird in der Projekt-README durch Projektziel, Start und Testeinstieg ersetzt. `project-specific/*.md` bleiben sichtbar auf `Pending Project Init`, solange sie nicht benötigt und definiert sind.

## Zuständigkeiten – eine Quelle pro Regel

| Ort | Einzige Aufgabe |
|---|---|
| `AGENTS.md` | Einstieg und Verweise auf relevante Dateien; kein zweiter Core. |
| `harness/rules/universal/core.md` | Universeller Ablauf und Entscheidung, *wann* Idea, Spec und Gate nötig sind. |
| `harness/rules/universal/ideas.md` | *Wie* ein unklares Vorhaben im Dialog geklärt und bestätigt wird. |
| `harness/rules/universal/quality.md` | Prinzipien zur Auswahl passender Nachweise, keine Projektbefehle. |
| `harness/templates/idea.md`, `story.md` | Form der jeweiligen Artefakte, keine parallelen Prozessregeln. |
| `harness/templates/project-init.md` | Fragen und Schritte zur einmaligen projektspezifischen Initialisierung. |
| `harness/rules/project-specific/project.md` | Tatsächliche Ziele, Grenzen, Architektur und Gate-Einstieg des neuen Projekts. |
| `harness/rules/project-specific/code.md`, `python.md`, `web.md`, `testing.md` | Nur benötigte Code-, Sprach-, Plattform- oder Testkonventionen; keine Kopie der universellen Regeln. |
| `harness/rules/project-specific/quality-matrix.md` | Bei Bedarf Zuordnung von Checks zu Projektbereichen; keine zweite Befehlsquelle. |
| Gate-Konfiguration und -Einstieg (z. B. `quality-gate.json` und `scripts/verify.py`) | Konkrete Checks beziehungsweise deren Ausführung; keine Produkt- oder Testpolitik. |
| `ideas/`, `specs/`, `learning-state.md` | Unklare Vorhaben, konkrete Anforderungen und manuell gesammelte Erkenntnisse – keine Harness-Regeln oder laufenden Chatprotokolle. |

## Quality Gate

`scripts/verify.py` ist als neutraler Python-Runner fertig: Er startet konfigurierte Befehle und scheitert ohne gültige Checks. **Ein wirksames Projekt-Gate ist damit noch nicht eingerichtet.** Bei Project Init wählt das Projekt passende Prüfungen und konfiguriert sie in `harness/rules/project-specific/quality-gate.json`; Format und Grenzen stehen in `harness/templates/project-init.md`. Ohne Python braucht das Zielprojekt einen eigenen Gate-Einstieg. Markdown-Dateien erweitern den Runner nicht automatisch. Dieser Abschnitt wird bei Project Init auf das tatsächliche Projekt-Gate angepasst.

`tests/test_verify.py` testet nur den Runner des Starter-Kits. Diese Entwicklungstests werden nicht ins Zielprojekt kopiert; dort entstehen Anwendungstests passend zu den Specs.

Universelle Regeln beschreiben das *Wie* der Zusammenarbeit; das Projektprofil beschreibt konkrete Fakten und Grenzen, die Gate-Konfiguration ausführbare Befehle. Keine Dokumentation ersetzt eine tatsächlich durchgeführte Prüfung.
