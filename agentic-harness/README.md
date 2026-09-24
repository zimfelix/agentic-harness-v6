# Agentic Harness – gebündelte Projektregeln

Dieser Ordner enthält den zusammenhängenden, kopierbaren Harness: Agenteneinstieg, Arbeitsablauf, Project Init, Projektprofil, Verification, Vorlagen, Projektdokumentation sowie Ideas- und Specs-Konventionen. Der Installer kopiert den Ordner als Einheit und ergänzt einen markierten Verweis in der Root-`AGENTS.md`.

| Pfad | Zuständigkeit |
| --- | --- |
| `AGENTS.md` | Einstieg und bedarfsgeladene Verweise. |
| `harness/core.md` | Universeller Ablauf von Auftrag bis Übergabe. |
| `harness/init.md` | Einmalige Klärung und Einrichtung des Zielprojekts. |
| `harness/project.md` | Bestätigte Projektgrenzen und konkrete Befehle; bei Init befüllen. |
| `harness/verification/` | Soll, Umsetzung, Gate und Fehlerbehandlung. |
| `harness/templates/` | Vorlagen für Ideas und Specs. |
| `docs/` | Projektfakten und thematische Konventionen; nach Bedarf befüllen/erweitern. |
| `ideas/`, `specs/` | Klärung offener Vorhaben und beauftragtes Soll-Verhalten. |

## Abhängigkeiten und Ladefolge

- Jede Aufgabe: Root-`AGENTS.md` → `agentic-harness/AGENTS.md` → `agentic-harness/harness/core.md` und Projektprofil.
- Neues Projekt mit `Pending Project Init`: `harness/init.md` → bestätigte Projektfakten in `harness/project.md` → relevante Doku und tatsächlicher Prüf-Einstieg.
- Offene größere Idee: `ideas/README.md` → `harness/templates/idea.md` → konkrete Idea.
- Beauftragtes Nutzerverhalten: `specs/README.md` → `harness/templates/spec.md` → konkrete Spec.
- Abschluss: `harness/verification/gate.md` lädt Requirements- und Implementation-Prüfung; bei Fehlschlag gilt `fail.md`.

Der Installer legt weder Produktfakten noch Tests oder ein grünes Quality Gate an. Anwendungscode und ausführbare Produkttests verbleiben außerhalb dieses Ordners. Siehe `harness/core.md` für das knappe Markdown-Format und `docs/README.md` für thematisch getrennte Projektdokumentation.
