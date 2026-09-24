# Code – Stack und Konventionen

> - **Typ:** Projektdoku
> - **Status:** Pending Project Init; noch keine projektspezifischen Codekonventionen bestätigt.
> - **Zuständigkeit:** Den gewählten Stack und die tatsächlich geltenden Regeln für Anwendungscode beschreiben.
> - **Gilt bei:** Project Init sowie Codeänderungen und Refactorings.
> - **Ladebeziehungen:** Vorher `agentic-harness/harness/project.md` lesen. Bei Modulgrenzen `agentic-harness/docs/architecture.md`; bei Testcode `agentic-harness/docs/testing.md` zusätzlich lesen.
> - **Nicht zuständig:** Produktarchitektur oder ausführbare Gate-Befehle duplizieren.

## Stack und Abhängigkeiten – im Init festzulegen

Welche Sprache, Laufzeit, Frameworks und Werkzeuge wurden für den ersten Ablauf gewählt? Nenne relevante Versionen oder Versionsgrenzen, Installationsquelle und Entwicklungsumgebung nur nach Prüfung oder Entscheidung. Begründe wesentliche Abhängigkeiten knapp.

## Codekonventionen – im Init festzulegen

Nur Regeln aufnehmen, die bei Änderungen handlungsrelevant sind: Struktur und Imports, Benennung, Typen, Fehlerbehandlung oder Formatierung – soweit sie zum gewählten Stack passen. Keine allgemeine Stil-Enzyklopädie.

## Qualitätswerkzeuge

Trenne **aktiv eingerichtet** von **vorgeschlagen**. Konfiguration hier verorten; konkrete Start- und Prüfbefehle mit Ergebnis stehen ausschließlich in `agentic-harness/harness/project.md`.
