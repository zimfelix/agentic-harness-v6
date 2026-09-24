# Agentic Harness V3

## Einmal klonen, dann pro Projekt mit einem Befehl installieren

```bash
git clone https://github.com/FelixZimmermannDev/agentic-harness-v3.git ~/agentic-harness-starter
python3 ~/agentic-harness-starter/scripts/install.py /pfad/zum/projekt
```

Optional vorher nur die Vorschau: `python3 ~/agentic-harness-starter/scripts/install.py --dry-run /pfad/zum/projekt`. Der Installer kopiert **einen Ordner**, `agentic-harness/`, und ergänzt einen markierten Verweis in der Projekt-Root-`AGENTS.md`. Bestehende Anweisungen und README bleiben erhalten. Bei einem abweichenden vorhandenen `agentic-harness/` bricht er ab. Danach Project Init mit `agentic-harness/harness/init.md` ausführen.

Das Zielprojekt braucht weder das Starter-Repository noch `scripts/` oder `tests/test_install.py`. Diese beiden gehören zur **Quelle**: Das Skript kopiert das Harness-Paket, seine eigenen Tests prüfen den Installer. Anwendungscode und Produkttests bleiben im Zielprojekt außerhalb des Pakets.

## Was wird übernommen und was danach angepasst?

| Im einzelnen Bundle `agentic-harness/` | Behandlung im Zielprojekt |
| --- | --- |
| `AGENTS.md`, `README.md`, `harness/core.md`, `harness/init.md`, `harness/verification/`, `harness/templates/`, `ideas/README.md`, `specs/README.md` | Allgemeine Einstieg-, Ablauf-, Prüf- und Vorlagenregeln: grundsätzlich unverändert. |
| `harness/project.md` | Project Init: bestätigte Grenzen, Werkzeuge, Befehle und Gate-Status eintragen. |
| `docs/architecture.md`, `docs/code.md`, `docs/testing.md` | Mit relevanten Fakten/Konventionen aus dem tatsächlichen Projekt befüllen; irrelevante Dateien können entfallen. |
| `docs/README.md` | Ergänzen, wenn neue thematisch getrennte Docs entstehen. |
| `ideas/`, `specs/` | Konkrete Ideas und beauftragte Specs erst bei Bedarf anlegen. |

Die produktbezogene Root-`README.md` wird **nicht** vom Installer angelegt oder überschrieben. Ein vorhandenes Root-`AGENTS.md` behält seinen Inhalt; der Installer fügt einen eindeutig markierten Harness-Einstieg hinzu. Widersprüche zu bestehenden Regeln müssen beim Project Init fachlich geklärt werden.

## Abhängigkeiten

- Jede Aufgabe: Root-`AGENTS.md` → `agentic-harness/AGENTS.md` → Core und Projektprofil.
- Neues Projektprofil (`Pending Project Init`): Project Init → bestätigtes Profil → relevante Projektdokumentation und ausführbarer Prüf-Einstieg.
- Idea/Feature: jeweilige Ablageregel → passende Vorlage → konkrete Datei.
- Abschluss: Gate → Anforderungs- und Implementierungsprüfung → echte Projektchecks; bei Fehlschlag `fail.md`.

Der Installer richtet **keine** Produktchecks ein und macht eine Spec nicht automatisch `Implemented`. Er selbst lässt sich mit `python3 -m unittest discover -s tests -p 'test_install.py'` testen.
