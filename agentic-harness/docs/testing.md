# Testing – Risiken und Testpraxis

> - **Typ:** Projektdoku
> - **Status:** Pending Project Init; noch keine Testpraxis oder Anwendungstests bestätigt.
> - **Zuständigkeit:** Geeignete Tests für den aktuellen Nutzerablauf auswählen und ihre Organisation beschreiben.
> - **Gilt bei:** Project Init sowie Testplanung, Teständerung und Testausführung.
> - **Ladebeziehungen:** Vorher `agentic-harness/harness/project.md` für Ziel und Befehle lesen. Bei Testcode `agentic-harness/docs/code.md` beachten; Abschlussregel: `agentic-harness/harness/verification/gate.md`.
> - **Nicht zuständig:** Akzeptanzkriterien oder Gate-Ergebnisse als erfüllt erklären.

## Universeller Rahmen

Testebenen nach Verhalten und Risiko auswählen, nicht pauschal alle verlangen. Eine leere Suite ist kein Nachweis; ausgeführte Befehle und Ergebnisse stehen im Projektprofil.

## Projektspezifische Befüllung

### Verhalten und Testebenen

Noch offen (Project Init): Welcher erste Ablauf und welche relevanten Fehlerfälle brauchen Nachweise? Welche Testebenen eignen sich dafür?

### Teststruktur und Isolation

Noch offen (Project Init): Ablage, Werkzeuge, Testdaten, Fixtures und Unabhängigkeit der Tests – soweit für den ersten Ablauf benötigt.

### Ausführung und Nachweisgrenzen

Noch offen (Project Init): welche Prüfungen tatsächlich eingerichtet sind und was sie nicht belegen. Befehle und beobachteten Status nur in `agentic-harness/harness/project.md` führen.
