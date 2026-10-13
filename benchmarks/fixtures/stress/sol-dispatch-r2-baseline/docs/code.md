# Codekonventionen

**Zuständigkeit:** Nicht bereits durch Code oder Werkzeuge ausgedrückte Konventionen und technische Schulden. Lesen bei Codeänderungen/Refactoring, Struktur aus `docs/architecture.md` beachten.

## Universeller Rahmen

Nur geltende Konventionen für den gewählten Stack festhalten. Ausführbare Regeln in Formatter/Linter/Typprüfung statt Prosa. Gemeinsame Werte einmal definieren; Regeln ersetzen, nicht mit Sonderfällen übersteuern. Refactorings folgen Core und Projekt-Regression, nicht einer ungeprüften Behauptung „sauberer“.

## Projektspezifische Befüllung

ES-Module und Node-Standardbibliothek, keine Pakete. CLI-Fehler geben ein JSON-Fehlerobjekt und Exitcode 1; bewusstes Crash-Injection nutzt SIGKILL. Payloads/Secrets nicht loggen. SQL-Parameter statt Stringinterpolation für Nutzereingaben. Fachregeln in Dispatch, Transaktions-/Schemaregeln in Storage. Keine zusätzlichen Hintergrundprozesse.
