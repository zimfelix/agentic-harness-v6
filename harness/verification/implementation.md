# Implementierung – Änderung und Verhalten nachweisen

> **Zuständigkeit:** Für jedes betroffene AK beobachtbare Evidenz einholen; kein zweites `docs/testing.md`.

- Prüfe den Diff gegen die betroffene Spec und die tatsächliche Änderung: Code, Tests, Konfiguration, Dokumentation und unerwartete Nebenwirkungen.
- Beachte geltende Konventionen in `docs/code.md` und `docs/testing.md`. Führe relevante Tests aus `tests/` und die eingerichteten Befehle aus `harness/project.md` tatsächlich aus; prüfe passende Fehlerfälle.
- Ein grüner Build belegt nicht automatisch funktionierendes Nutzerverhalten. Verifiziere den wichtigsten Ablauf über die passende Grenze (z. B. API, Datenbank oder UI), wenn die Spec das verlangt; schütze echte Daten.
- Halte für jedes AK Test oder begründete manuelle Prüfung, beobachtetes Ergebnis und Grenzen des Nachweises fest. Fehlende, leere oder nicht ausführbare Checks sind **nicht verifiziert**, nicht `PASS`.

Hier wird Evidenz für die Änderung beurteilt. Teststrategie steht in `docs/testing.md`, ausführbare Tests in `tests/`, Abschlussentscheidung in `gate.md`.
