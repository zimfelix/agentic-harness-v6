# Project Init – leeres Projekt beginnen

> - **Typ:** Prozess
> - **Zuständigkeit:** Ein neues, leeres Produktprojekt für den ersten beauftragten Arbeitsschritt vorbereiten.
> - **Gilt bei:** Vor der ersten Produktumsetzung, wenn `agentic-harness/harness/project.md` noch `Pending Project Init` enthält. Nicht bei Harness-Engineering.
> - **Ladebeziehungen:**
>   - Vorher: `AGENTS.md` → `agentic-harness/harness/core.md` → `agentic-harness/harness/project.md`.
>   - Für Dateirollen und Format: `agentic-harness/harness-map.md` und `agentic-harness/document-contract.md`.
>   - Danach: betroffene Projektdateien befüllen; Abschluss nach Abschnitt 4.
> - **Nicht zuständig:** Bestehende Anwendungen analysieren, spätere Features planen oder eine Produktspec als umgesetzt erklären.

## 1. Ersten Schritt klären

Kläre Nutzer, Problem und den ersten sichtbaren Ablauf. Halte Umfang und Nicht-Ziele des ersten Meilensteins fest.

Frage nur nach Daten, Betrieb, Integrationen und Freigaben, die diesen Schritt beeinflussen. Erfinde keine Antworten.

Leite für den ersten Ablauf passende Bausteine, Stack- und Testkandidaten ab. Prüfe entscheidungsrelevante Versionen und Voraussetzungen anhand verfügbarer Quellen oder Werkzeuge. Vergleiche echte Alternativen kurz mit Nutzen und Kosten.

Technische Möglichkeiten bleiben **Vorschläge**, bis sie entschieden sind. Vertage nicht benötigte Technik.

Fasse den ersten Schritt und offene Entscheidungen zusammen. Hole die nötige fachliche Bestätigung ein, bevor du Vorschläge als Projektfakten festhältst.

## 2. Bestätigtes an die richtige Stelle schreiben

Lies die Inhaltsvorgaben der Projektdateien. Behalte Dokumentkopf und „Universeller Rahmen“, aber prüfe den Kopf beim Befüllen: Stimmen Zuständigkeit, Auslöser, Ladebeziehungen und Abgrenzung zum bestätigten Projekt und zu den tatsächlichen Pfaden?

Ersetze „Noch offen (Project Init)“ unter „Projektspezifische Befüllung“ durch bestätigte Inhalte. Ist ein Bereich nicht entscheidbar oder nicht relevant, kennzeichne ihn ausdrücklich. Entferne den Platzhalterstatus erst nach tatsächlicher Befüllung.

- `agentic-harness/harness/project.md`: bestätigtes Nutzerziel, Umfang, Grenzen und Freigaben; Start- und Prüfbefehle mit tatsächlichem Status.
- `agentic-harness/docs/architecture.md`: bestätigte erste Bausteine, Zuständigkeiten und Datenfluss; Geplantes und Offenes gesondert kennzeichnen.
- `agentic-harness/docs/code.md`: nur geltende Konventionen für den gewählten Stack.
- `agentic-harness/docs/testing.md`: passende Testebenen und Testpraxis für den ersten Ablauf.
- `agentic-harness/docs/README.md`: weitere Projekt-Docs nur bei konkretem Bedarf unter „Weitere Projektdokumente“ verlinken.
- Root-`AGENTS.md`: nur nötige zusätzliche Ladeverweise unter „Projektspezifische Ergänzungen“ eintragen; keine Detailregeln kopieren.

Fülle die Produkt-`README.md` mit bestätigtem Zweck und geprüften Startschritten. Ersetze ihren Platzhalter-Titel durch den Produktnamen. Überschreibe keine bereits vorhandenen Produktinformationen; erfinde keine Fakten.

## 3. Prüf-Einstieg und Verweise prüfen

Richte passende Checks ein, sobald sie ausführbar sind. Führe sie tatsächlich aus. Prüfe bei Bedarf, ob sie einen absichtlichen Fehler erkennen.

Eine leere Testsuite oder ein geplanter Befehl gilt nicht als bestanden. Halte nicht eingerichtete Checks im Projektprofil offen.

Prüfe auch die Ladebeziehungen in den befüllten Dokumentköpfen. Ergänzte Verweise müssen vom Repo-Root aus auf vorhandene Dateien zeigen. Wenn sich Rollen oder Ladeauslöser geändert haben, passe `AGENTS.md` und `agentic-harness/harness-map.md` gezielt an.

## 4. Übergabe

Entferne `Pending Project Init` erst, wenn Ziel, Grenzen und erster Schritt ausreichend geklärt sind. Das bedeutet **nicht**: Produkt-Gate bestanden oder Spec `Implemented`.

Für beauftragtes Nutzerverhalten nutze `agentic-harness/specs/README.md` und `agentic-harness/harness/templates/spec.md`.

Eine Idea nach `agentic-harness/ideas/README.md` ist nur bei offenem Klärungsbedarf nötig. Danach gilt wieder `agentic-harness/harness/core.md`.
