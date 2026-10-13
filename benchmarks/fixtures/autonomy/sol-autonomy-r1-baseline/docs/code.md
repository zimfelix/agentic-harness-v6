# Codekonventionen

**Zuständigkeit:** Nicht bereits durch Code oder Werkzeuge ausgedrückte Konventionen und technische Schulden. Lesen bei Codeänderungen/Refactoring, Struktur aus `docs/architecture.md` beachten.

## Universeller Rahmen

Nur geltende Konventionen für den gewählten Stack festhalten. Ausführbare Regeln in Formatter/Linter/Typprüfung statt Prosa. Gemeinsame Werte einmal definieren; Regeln ersetzen, nicht mit Sonderfällen übersteuern. Refactorings folgen Core und Projekt-Regression, nicht einer ungeprüften Behauptung „sauberer“.

## Projektspezifische Befüllung

Standardbibliothek, kleine Module nach Verantwortung, keine Framework-/Plugin-Abstraktionen. Domain wirft ValueError für erwartete Regelverletzungen; CLI berichtet erwartete IO-/Validierungsfehler ohne Traceback. Keine stillen Fallbacks bei beschädigtem Speicher. Strikte Schlüssel-/Typprüfung auch für Import und gespeicherten Zustand; bool ist kein Integer. Tests sind die ausführbare Quelle der Invarianten. Keine ungeprüften Drittwerkzeuge oder behaupteten Lint-/Coverage-Ergebnisse.
