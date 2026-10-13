# Codekonventionen

**Zuständigkeit:** Nicht bereits durch Code oder Werkzeuge ausgedrückte Konventionen und technische Schulden. Lesen bei Codeänderungen/Refactoring, Struktur aus `docs/architecture.md` beachten.

## Universeller Rahmen

Nur geltende Konventionen für den gewählten Stack festhalten. Ausführbare Regeln in Formatter/Linter/Typprüfung statt Prosa. Gemeinsame Werte einmal definieren; Regeln ersetzen, nicht mit Sonderfällen übersteuern. Refactorings folgen Core und Projekt-Regression, nicht einer ungeprüften Behauptung „sauberer“.

## Projektspezifische Befüllung

Python-Standardbibliothek, kleine Module nach Verantwortung, parametrisierte SQL-Werte. Fachfehler explizit mit HTTP-Status; technische Fehler nicht verschlucken. Keine Geld-Floats, Client-Tenants, Token-/Payload-Logs oder zusätzlichen Abhängigkeiten. Schema und Domain-Regeln sind im Code die ausführbare Quelle; Tests prüfen öffentliche API und reine Regeln.
