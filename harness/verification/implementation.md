# Implementierung – Änderung und Verhalten nachweisen

> **Zuständigkeit:** Für jedes betroffene AK beobachtbare Evidenz einholen; kein zweites `docs/testing.md`.

- Prüfe den Diff gegen die betroffene Spec: notwendiger Code, Tests, Konfiguration und Projektgrenzen; keine unerwarteten Änderungen.
- Lies bei Bedarf `docs/code.md` und `docs/testing.md`. Führe relevante Tests und den eingerichteten Gate-Befehl aus `harness/project.md` tatsächlich aus; prüfe auch aussagekräftige Fehlerfälle.
- Ein grüner Build belegt nicht automatisch funktionierendes Nutzerverhalten. Verifiziere den wichtigen Ablauf über die passende Grenze (z. B. API, Datenbank oder UI), wenn die Spec das verlangt; nutze sichere Testdaten.
- Erfasse pro AK: Test beziehungsweise manuelle Prüfung, Ergebnis und Grenze des Nachweises. Nicht ausführbare oder nicht vorhandene Checks als **nicht verifiziert** melden.

Ausführbare Anwendungstests stehen in `tests/`. Dieser Leitfaden beschreibt ihre Anwendung, nicht ihre Implementierung.
