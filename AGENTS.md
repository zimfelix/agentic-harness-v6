# Agentic Harness – Einstieg

> - **Typ:** Einstieg
> - **Zuständigkeit:** Aufgaben den zuständigen Harness-Dateien zuordnen.
> - **Gilt bei:** Arbeit in diesem Repository und später in Projekten mit diesem Harness.
> - **Ladebeziehungen:** Immer `agentic-harness/harness/core.md` und `agentic-harness/harness/project.md` lesen; weitere Dateien nur nach den Auslösern unten.
> - **Nicht zuständig:** Den Arbeitsablauf, Produktfakten oder Qualitätsregeln hier erneut erklären.

## Wohin mit der Aufgabe?

| Auslöser | Zusätzlich lesen | Zweck |
|---|---|---|
| Erste Produktumsetzung bei `Pending Project Init` | `agentic-harness/harness/init.md` | Projektziel und Grenzen klären; nicht allein wegen Harness-Engineering ausführen. |
| Architektur, Zuständigkeiten oder Dateistruktur | `agentic-harness/docs/architecture.md` | Produktaufbau und Abhängigkeiten prüfen. |
| Codeänderung oder Refactor | `agentic-harness/docs/code.md` | Projektbezogene Codekonventionen prüfen. |
| Testplanung, Teständerung oder Testlauf | `agentic-harness/docs/testing.md` | Testkonventionen prüfen; Befehle stehen im Projektprofil. |
| Größere offene Idee | `agentic-harness/ideas/README.md` | Idee klären; bei Neuanlage `agentic-harness/harness/templates/idea.md` verwenden. |
| Neues oder geändertes Nutzerverhalten | `agentic-harness/specs/README.md` und betroffene Spec | Beauftragtes Soll prüfen; bei Neuanlage `agentic-harness/harness/templates/spec.md` verwenden. |
| Abschluss einer Änderung | `agentic-harness/harness/verification/gate.md` | Auftrag und Nachweise prüfen; bei Fehlschlag `agentic-harness/harness/verification/fail.md`. |
| Harness erstmals einordnen oder Project Init durchführen | `agentic-harness/harness-map.md` | Dateirollen und geplante Ladewege verstehen; tatsächliche Pfade prüfen. |
| Markdown-Datei neu anlegen, befüllen oder Pfade ändern | `agentic-harness/document-contract.md`; bei neuer Rolle/Pfad auch `agentic-harness/harness-map.md` | Dokumentkopf und Verweise vor und nach Änderungen prüfen. |

Treffen mehrere Auslöser zu, lies die betreffenden Dateien. Lade nicht alle Docs auf Vorrat. Neue thematische Projekt-Docs brauchen einen klaren Auslöser im Einstieg; verweise auf Regeln statt sie hier zu kopieren.

Vor dem Umbenennen, Verschieben oder Löschen einer Harness-Datei suche repo-weit nach Verweisen auf Pfad und Dateinamen. Aktualisiere betroffene Verweise und Ladewege im selben Schritt. Prüfe danach alle verbliebenen Pfade gegen den tatsächlichen Baum. Nach manuellen Änderungen zuerst den Ist-Stand prüfen; ein Markdown-Verweis aktualisiert sich nicht automatisch.

## Aktiver Stand und Pfade

`agentic-harness/harness/core.md` ist derzeit der aktive Ablauf; `agentic-harness/harness/corev2.md` bleibt ein Entwurf. Landkarte und Dokumentenvertrag sind Referenzen für Orientierung und Markdown-Pflege. Die Landkarte zeigt geplante Root-Pfade; bis zur Migration sind die tatsächlichen `agentic-harness/`-Pfade in dieser Datei maßgeblich.

Produktcode und Produkttests liegen außerhalb der Harness-Dokumente. Bei Widersprüchen zwischen Auftrag, bestehenden Projektanweisungen und Harness kläre die Zuständigkeit vor riskanten Änderungen. Ändere nicht stillschweigend weitere Dateien, nur weil sie verlinkt sind.

Bei Commits beschreibt der Betreff in einem kurzen, konkreten Satz die tatsächliche Änderung. Vermeide ungenaue Betreffe wie „Update files“.

Bei Project Init nur nötige zusätzliche Projektverweise unter der folgenden Überschrift eintragen. Universelle Regeln oben nicht kopieren.

## Projektspezifische Ergänzungen
