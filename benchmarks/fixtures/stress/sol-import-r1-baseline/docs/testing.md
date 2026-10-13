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

Pflichtregression: python3 -m unittest discover -s tests -v. Synthetische Daten und temporäre Verzeichnisse innerhalb tests/; kein Netzwerk oder außerhalb des Projekts geschriebener Testzustand. Regeltests plus echte SQLite/CLI-Tests: Seed-All-or-nothing, Tenant-Scoping, Gruppenreihenfolge und Rollback, globale Transfer-ID-Dubletten, exakte Byteidentität, New-ID, Persistenz/Replay, Failpoints auch letzte Gruppe, Nullaccounts und Conservation. Parallelität durch gleichzeitig gestartete Subprozesse auf derselben DB, identische und konkurrierende Runs. Locktimeout, Migration leer/befüllt, backup/restore und JSON/Exitcodes prüfen. Prüfmechanismus mit absichtlich falscher Erwartung gegenprüfen. Vollständige Suite nach jeder fachlichen Änderung; keine Packages/Linter nötig. Nicht geprüft: Produktionshardware-Powerloss, Netzwerk-Dateisysteme, enorme Dateien oder Auth (nicht zugesagt).
