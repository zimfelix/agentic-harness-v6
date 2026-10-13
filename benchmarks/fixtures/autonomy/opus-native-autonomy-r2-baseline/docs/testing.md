# Prüfstrategie

**Zuständigkeit:** Risikobezogene Testauswahl, Regression, Werkzeuge, Umgebung und Nachweisgrenzen. Lesen bei Testplanung/-änderung/-ausführung. Befehle/letzte Ergebnisse stehen in `harness/project.md`, AK in Specs.

## Universeller Rahmen

Aus Nutzerablauf, Risiken, Architektur und gewählten Profilen die kleinste aussagekräftige Auswahl begründen; keine Pflicht zu allen Testarten oder separaten Ordnern je Ebene.

- **Unit:** isolierte Regeln/Grenzfälle; beweist kein Zusammenspiel.
- **Integration:** echte Persistenz und relevante Schnittstellen; externe Dienste ggf. mit Vertragstest plus separat ausgewiesenem Live-Check.
- **API/CLI/UI/System:** beauftragtes Verhalten an der Nutzergrenze einschließlich relevanter Fehlerfälle.
- **Risikoprüfungen:** Rechte/Mandanten, Datenintegrität/Wiederholung, Ausfall/Parallelität, Leistung, Barrierefreiheit/Kompatibilität nur nach relevantem Risiko und vereinbartem Ziel.

TDD bewusst je Bereich wählen. Neue Checks mit einem absichtlichen Fehler gegenprüfen. Tests reproduzierbar isolieren; keine echten Personendaten/Secrets in Fixtures. Refactorings sichern unverändertes Verhalten ab; unklare Reichweite → gesamte vorhandene Verhaltenstestsuite.

UI im Zielmedium messen und per Screenshot beurteilen, nicht per HTML-/CSS-Strings. Prüfgrößen und Zustände festlegen; wiederverwendbare Werkzeuge einmal einrichten. Coverage/Build/Lint allein belegen keine AK.

Pflichtchecks, Regressionumfang, lokal/CI, Umgebungen, Abgewähltes mit Grund und offene Checks samt Auslöser/Zuständigkeit festhalten. Fehlende Umgebung nie als bestanden werten. Umfang nach Reifegrad im Init; konkrete Nachweise nach `harness/verification.md`.

## Projektspezifische Befüllung

- **Mandatory / regression:** `python3 -m unittest discover -s tests` (whole suite, ~seconds; always run fully).
- **Unit (`tests/test_rules.py`):** pure rules on `Plan`: cycle detection, completion guard, delete integrity, estimate parsing, next-work ordering (transfer validation is covered in the CLI tests).
- **CLI behavior (`tests/test_cli.py`):** real `./planner` entrypoint as subprocess on a temp SQLite file under `.test-tmp/` (in-project, removed afterwards): persistence across invocations, error exits, malformed import/restore leave state byte-identical (compare export), backup→mutate→restore equality, fixture import, concurrency (parallel writers lose nothing), schema version newer than code is refused.
- **End-to-end demo:** `scripts/demo.sh` against `.demo/` data; output is checked by eye plus its `CHECK OK` state comparisons.
- **Clock:** commands depending on "today" accept `--today YYYY-MM-DD`; tests always pass it.
- **Deselected:** performance (small personal data), UI/accessibility (no UI), external service contracts (none), CI (no remote; local only).
- New checks were cross-checked with a deliberate fault (see spec Nachweise).
