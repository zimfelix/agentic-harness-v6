# Agentic Harness V3

![Harness overview](assets/images/img.png)

Schablone für Entwicklungsagenten in mittelgroßen Projekten. **Dieses Repository ist noch kein initialisiertes Produktprojekt:** Projektprofil, Architektur und Produktprüfungen sind nicht eingerichtet. Die kurzen Dateien markieren offene Punkte, statt Produktfakten vorzugeben.

| Pfad | Verantwortung |
| --- | --- |
| `AGENTS.md` | Einstieg und bedarfsgeladene Verweise; keine zweite Ablaufanleitung. |
| `harness/core.md` | Wiederverwendbarer Ablauf von Auftrag bis Übergabe. |
| `harness/init.md` | Neues Produktprojekt klären und initialisieren. |
| `harness/project.md` | Nach Init aktive Projektgrenzen und Prüf-Einstieg. |
| `harness/verification/` | Anforderungen prüfen, Implementierung belegen, Fehler behandeln. |
| `harness/templates/` | Formate für Ideas und Specs; keine ausgefüllten Aufträge. |
| `docs/` | Geltendes Produktwissen; weitere Themen nach `docs/README.md`. |
| `ideas/` | Noch ungeklärte Vorhaben; kein Implementierungsauftrag. |
| `specs/` | Beauftragtes Soll-Verhalten mit Akzeptanzkriterien. |
| `src/` | Anwendungscode des späteren Produkts. |
| `tests/` | Ausführbare Tests des späteren Produkts. |

**Ablauf:** `AGENTS.md` → `harness/core.md` → bei neuem Projekt `harness/init.md` → aktives `harness/project.md` → passende `docs/` und `specs/` → `harness/verification/gate.md`. Details nur lesen, wenn sie für die Aufgabe gelten. `docs/testing.md` erklärt die Testpraxis; `tests/` enthält Tests; das Gate entscheidet anhand tatsächlich ausgeführter Nachweise über den Abschluss. `docs/` ersetzt weder `specs/` noch die Arbeitsregeln in `harness/`.

Beim Einsatz als Vorlage: eigene Projektfakten ermitteln, Platzhalter im Profil gezielt ersetzen und einen echten Gate-Einstieg einrichten. Keine Regeln, Tools, Skills oder Dokumente für ungenutzte Technologien auf Vorrat erfinden. Das Weiterentwickeln **dieser Schablone** ist nicht die Project Init einer fiktiven Anwendung.
