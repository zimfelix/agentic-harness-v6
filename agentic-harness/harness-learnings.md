# Harness-Learnings

**Zuständigkeit:** Harness-Schwächen, wiederkehrende Agentenfehler und Gründe beauftragter Harness-/Profil-/Tooländerungen. Bei Beobachtungen, vor Harness-Änderungen und beim Release lesen.

## Zweck und Regeln

Produktfakten gehören in Projektprofil/Docs/Specs. Harness-Beobachtungen zunächst in der `harness-learnings.md` des jeweiligen Produktprojekts sammeln, nicht unmittelbar in allgemeine Regeln übersetzen. Universelle Harness-Regeln, Profile und Werkzeuge werden grundsätzlich nur im zentralen Vorlagen-Repository `agentic-harness-v6` angepasst; außerhalb davon ausschließlich auf einen konkreten Auftrag, der diese Harness-Änderung ausdrücklich erlaubt. Projektbefüllung und projektspezifische Ergänzungen sind keine Änderung der universellen Vorlage.

## Kontext je Learning

Kurz, aber später ohne die ursprüngliche Sitzung auswertbar festhalten:

- **Herkunft:** Projekt/Repository und auffindbarer Ort, Datum, verwendeter Harness-Stand (Version/Commit, soweit bekannt).
- **Arbeitskontext:** Projektart, relevanter Stack/Profilbereich, Reifegrad und konkreter Auftrag samt delegiertem Rahmen.
- **Beobachtung:** Auslöser, erwartetes und tatsächliches Verhalten, betroffene Regel; menschlicher Eingriff, falls erfolgt.
- **Nachweis:** Konkrete Dateien/AK, ausgeführter Check und Ergebnis/Grenzen. Flüchtige Logs nur ergänzend; nötigen Kontext hier zusammenfassen. Keine Secrets oder vertraulichen Produktdaten.
- **Einordnung:** Beobachtung von vermuteter Ursache trennen; lokalen Workaround und Regelvorschlag unterscheiden. Fehlende Angaben als unbekannt markieren, nicht rekonstruieren/erfinden.
- **Offen / nächster Schritt:** Welche Frage ist ungeklärt, was würde sie prüfen, und erscheint die Erkenntnis lokal, profilbezogen oder universell?

## Wöchentliche Auswertung und Übernahme

Zum Wochenreview auf Auftrag ausgewählte Projekt-Learnings mit Herkunft und Nachweisen im zentralen v6-Repository auswerten. Kein automatischer Transfer, keine Hintergrundsynchronisierung und keine selbstständige Regeländerung in Produktprojekten. Erst Ursache/Übertragbarkeit prüfen und entscheiden: nur lokal belassen, weiter erproben oder eine beauftragte Vorlagenänderung ableiten. Beim Übertragen Quellprojekt und relevante Randbedingungen erhalten; bloße Kurzthesen ohne Kontext reichen nicht.

Vor Änderungen aktive Einträge prüfen, bewusste Entscheidungen nicht still zurückdrehen. Neue Regeländerungen im selben Schritt mit Grund und Prüfstand dokumentieren. **Offen** = Beobachtung/Hypothese. **Lokal übernommen** = im angegebenen Kontext ausdrücklich beauftragte Änderung, Wirksamkeit ggf. noch ungeprüft; keine allgemeine Freigabe zum Ändern des Harness. Nach beauftragtem Release gegen Zieldateien prüfen und erledigte Einträge verdichten; Herkunft, Aussagegrenzen und offene Fragen erhalten. Übernommene Punkte aus aktiven Einträgen entfernen, verbleibende Unsicherheiten unter „Offen“ erhalten. Ältere Details bleiben in Git bzw. im vorhandenen Prüfbericht, kein separater Archivordner. Export übernimmt diese Regeln, keine Einträge/Archive; neue Projekte sammeln eigene Learnings. Statische Checks belegen keine konstante Agentenleistung.

## Aktive Learnings

### Offen

- **Mail-Prototyp / Vor-Code-Grenze:** Im ursprünglichen Mail-Projekt schrieb der Agent trotz gelesener Init-/Business-Regeln Produktcode bei `Pending Project Init`, ohne Projektbefüllung, Architektur, Soll oder Tests; Auftraggeber stoppte. Quellpfad, ursprünglicher Zeitpunkt/Stack und damaliger Harness-Stand sind hier nicht dokumentiert. Nachprüfung im Vorlagenprojekt am 2026-10-09: alle drei neuen CSV-/CRM-/Job-Proben nutzten Readiness/Go vor Produktcode, aber mit engen bestätigten Briefen; kein Wiederholungstest des ursprünglichen Mail-Auftrags. Offen: Verhalten bei normalem freien Brief und echte Wirkung der globalen Pi-Extension `~/.pi/agent/extensions/harness-init-guard.ts`. Bekannt: nur `write`/`edit`, `bash` umgeht sie; sechs Loader-Tests beweisen keine Laufzeit-/Sicherheitsgrenze. Nächster Schritt auf Auftrag: ursprünglichen Kontext ergänzen und isoliert nachstellen. Extension-Änderung außerhalb dieses Repositories braucht einen konkreten Ausnahmeauftrag; kein Blocker für den Vorlagenrelease.
- **Stoppregel / Completion-Vergleich:** Herkunft: Vergleich mit `mitsuhiko/agent-stuff`, `extensions/goal.ts`/`extensions/review.ts`, im v6-Vorlagenprojekt. Anforderungsabdeckung, keine Ersatzlösung, menschliche Übergabehinweise und sichtbare Fallbacks sind jetzt in Core/Verification übernommen; keine offene Umsetzung mehr. Ungeprüft bleibt, ob eine andere Stoppregel hilft: unsere zwei erfolglosen Korrekturen derselben Ursache sind nicht identisch mit drei gleichen Blocker-Runden dort. Hooks/P0–P3-Raster sind nicht beauftragt. Vor Änderung konkrete Vergleichsfälle und Auftrag nötig; bestehende Regel bleibt erhalten.
- **Übertragbarkeit / Aufwand:** Herkunft: drei isolierte Python-/SQLite-Projektarten im Vorlagenprojekt, Baseline `47065ef` gegen präzisierten Stand, 2026-10-09; Bericht im Repository unter `tests/harness/RESULTS.md`. Spec-Status bei fehlendem Provider, Fortsetzung aus Dateien und Nichtumsetzung einer zurückgestellten Idea sind in diesen Fällen praktisch nachgewiesen, nicht mehr vollständig unerprobt. Offen: normale weniger präzise Briefe, größere Projekte, angemessene Check-/TDD-Auswahl und Dokumentwachstum; kein belegter Effizienzgewinn. Auch die nach den Agentenproben ergänzte zentrale Lern-/Pflegegrenze ist bisher nur dokument-/exportgeprüft. Nächster Schritt: relevante Beobachtungen aus echten Projekten sammeln und gezielte frische Proben statt pauschal mehr Regeln.
- **Globale Lernpräferenzen (nicht exportiert):** Im früheren Auftrag wurden Shipping/Learning, Architektur-/Stack-/Dependencyerklärung und Fachsprachkorrektur global für Pi (`~/.pi/agent/AGENTS.md`) und Claude Code (`~/.claude/CLAUDE.md`) präzisiert. Quellprojekt/Datum dieses Auftrags sind hier nicht dokumentiert; bekannte Evidenz ist der damalige textliche Abgleich, keine gezielte frische Verhaltensprobe. Offen bleibt deren Wirkung in normalen Shipping-/Learning-Sitzungen. Keine globale Datei im v6.1-Release geändert; nächste Prüfung nur auf passenden Auftrag, nicht automatisch mit Harness-Regeln gleichsetzen.

### Lokal übernommen

Keine.
