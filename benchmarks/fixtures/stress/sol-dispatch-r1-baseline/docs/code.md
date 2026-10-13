# Codekonventionen

**Zuständigkeit:** Nicht bereits durch Code oder Werkzeuge ausgedrückte Konventionen und technische Schulden. Lesen bei Codeänderungen/Refactoring, Struktur aus `docs/architecture.md` beachten.

## Universeller Rahmen

Nur geltende Konventionen für den gewählten Stack festhalten. Ausführbare Regeln in Formatter/Linter/Typprüfung statt Prosa. Gemeinsame Werte einmal definieren; Regeln ersetzen, nicht mit Sonderfällen übersteuern. Refactorings folgen Core und Projekt-Regression, nicht einer ungeprüften Behauptung „sauberer“.

## Projektspezifische Befüllung

Node ESM, ausschließlich Standardbibliothek. Eingaben an der CLI-Grenze und Snapshots beim Laden prüfen. Erwartete Fehler ergeben einen JSON-Fehler und Exit != 0. Keine Fallbacks bei kaputtem Bestand. Fachregeln in dispatch.mjs, Speicher/Locks in store.mjs; Test-Checkpoints sind interne Funktionsparameter, keine zusätzlichen CLI-Kommandos.
