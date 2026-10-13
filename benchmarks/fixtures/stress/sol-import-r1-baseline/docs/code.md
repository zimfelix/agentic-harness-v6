# Codekonventionen

**Zuständigkeit:** Nicht bereits durch Code oder Werkzeuge ausgedrückte Konventionen und technische Schulden. Lesen bei Codeänderungen/Refactoring, Struktur aus `docs/architecture.md` beachten.

## Universeller Rahmen

Nur geltende Konventionen für den gewählten Stack festhalten. Ausführbare Regeln in Formatter/Linter/Typprüfung statt Prosa. Gemeinsame Werte einmal definieren; Regeln ersetzen, nicht mit Sonderfällen übersteuern. Refactorings folgen Core und Projekt-Regression, nicht einer ungeprüften Behauptung „sauberer“.

## Projektspezifische Befüllung

Nur Python-3-Standardbibliothek. Fachfehler sind explizite typisierte Exceptions, werden an der CLI-Grenze als JSON ausgegeben. Bezeichner werden nicht getrimmt oder als Anweisungen interpretiert; strip dient nur der Blankprüfung. Mengen sind ASCII-Dezimalziffern, keine Vorzeichen/Whitespace. Fachregeln in parsing/service, SQLite-Constraints als zweite Integritätsgrenze. Keine abstrahierten Provider oder ungenutzten Erweiterungspunkte.
