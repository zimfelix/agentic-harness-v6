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

Pflichtregression: `python3 -m unittest discover -s tests -v`; Init-/Dokumentenprüfung: `python3 tools/check-harness.py --go`. Nur Python-Standardbibliothek, lokale Loopback-HTTP-Verbindungen und projektinterne temporäre SQLite-Dateien; keine echten Daten oder Provider. CLI-Tests starten echte Subprozesse und prüfen Portmeldung und Restart.

Regeltests: Ganzzahl-Typgrenzen, HALF_UP-Steuer, Zustandsgraph (testgetrieben für klare Regeln). HTTP-/SQLite-Integration nach Implementierung: Rollenmatrix, fehlende Identität, tenant isolation einschließlich Referenzen, strikte Formen/JSON, stale/ungültige Übergänge, parallele Versions- und Issuance-Konflikte, persisted Replay/Payload-Konflikt, Void-Einmaligkeit/Audit, v1-ID-Erhalt und wiederholter Restart. Audit und DB-Zähler prüfen fehlende Teilmutationen. SQL-Abbruchtest prüft rollback von Mutation plus Audit.

Neue Prüflogik durch absichtliche Änderung der Steuerregel gegenprüfen und danach unveränderten Stand vollständig erneut testen. Nicht im Nachweis: Last-/DoS-Tests, reale Auth, Deployment, rechtliche Belegkonformität oder zugesagtes Backup/Restore. Kein UI, daher keine Screenshots/Browserchecks; kein CI autorisiert. Produktionsgates siehe `docs/architecture.md`.
