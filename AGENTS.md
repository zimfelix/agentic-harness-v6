# Agentic Harness V3 – Entwicklungsanweisungen

Der wiederverwendbare Harness liegt gebündelt unter `agentic-harness/`. Lies `agentic-harness/AGENTS.md` als Einstieg und `agentic-harness/harness/core.md` für den Arbeitsablauf. Bestätigte Fakten über dieses Repository stehen in `agentic-harness/harness/project.md`; seine Installation und Wartung beschreiben `README.md` und `scripts/`.

Installer-Änderungen müssen in `tests/test_install.py` geprüft werden. `agentic-harness/` ist die kopierbare Einheit; `scripts/` und die Tests des Installers gehören nur zum Starter-Kit. Bestehende Zielprojektanweisungen nie überschreiben: der Installer fügt einen markierten Verweis hinzu. Projekt-Code und Projekttests bleiben außerhalb des Harness-Bundles.
