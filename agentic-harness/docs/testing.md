# Testing – Risiken und Testpraxis

> - **Typ:** Projektdoku
> - **Status:** Pending Project Init; noch keine Testpraxis oder Anwendungstests bestätigt.
> - **Zuständigkeit:** Geeignete Tests für den ersten Nutzerablauf auswählen und ihre Organisation beschreiben.
> - **Gilt bei:** Project Init sowie Testplanung, Teständerung und Testausführung.
> - **Ladebeziehungen:** Vorher `agentic-harness/harness/project.md` für Ziel und Befehle lesen. Bei Testcode zusätzlich `agentic-harness/docs/code.md` beachten; Abschlussregel: `agentic-harness/harness/verification/gate.md`.
> - **Nicht zuständig:** Akzeptanzkriterien oder Gate-Ergebnisse als erfüllt erklären.

## Verhalten und Risiken – im Init festzulegen

Welcher erste Ablauf und welche relevanten Fehlerfälle müssen nachweisbar sein? Testebenen nach Verhalten und Risiko wählen; nicht für jedes Projekt pauschal alle Ebenen verlangen.

## Testorganisation – im Init festzulegen

Wenn Tests entstehen: Ablage, Werkzeuge, Testdaten und Isolation beschreiben. Tests sollen unabhängig laufen und eine beobachtbare Erwartung prüfen. Eine leere Suite ist kein Nachweis.

## Ausführung und Grenzen

Die tatsächlich eingerichteten Befehle, ihren Geltungsbereich und den letzten beobachteten Status in `agentic-harness/harness/project.md` festhalten. Nicht eingerichtete Prüfungen als offen markieren; ein bestandener Build beweist kein Nutzerverhalten.
