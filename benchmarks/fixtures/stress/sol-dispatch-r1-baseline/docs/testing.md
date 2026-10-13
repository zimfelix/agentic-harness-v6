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

Pflichtregression: `node --test tests/*.test.mjs`; Syntax: `node --check app.mjs`, entsprechende Source-Dateien. Testdaten in temporären Unterverzeichnissen von tests, Cleanup nach Test. CLI-Grenze, semantische Gleichheit, Mandantentrennung, alle Modi, Retry-Fälligkeit/Budget, unabhängige Provider-Wahrheit, malformed Persistenz, Parallelität und echte SIGKILL-Recovery. Interne Checkpoints erlauben deterministischen externen Kill mit gehaltenem OS-Lock. Backup/Restore mit Fake-Bestand. Regeltests zusätzlich direkt an exportierten Funktionen. Prüflogik mit absichtlichem falschem Erwartungswert gegenprüfen.

TDD/risikoorientiert: Regeln und Grenzfälle isoliert, anschließend volle CLI/Prozessintegration. Keine UI-Tests. Externer Sandbox-Vertragscheck ist zusätzliches Abnahme-Gate nach specs/S001-dispatch.md AK10; aktuell nicht ausgeführt, da Endpunkt/Zugangsdaten fehlen und Netzwerk-/Live-Aktionen nicht autorisiert sind. Lokaler Fake ist kein Ersatz. Menschliche Zuständigkeit, Freigabevoraussetzungen, Nachweisumfang und nächster Schritt stehen in der Spec. Node-22-Kompatibilität auf API-Nutzung geprüft, tatsächliche Ausführung nur auf verfügbarer Laufzeit; exakte Zielversion und Power-Loss-/Network-FS-Verhalten bleiben unbelegt.
