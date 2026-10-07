# Core

**Zuständigkeit:** Auftrag → Soll → Umsetzung → Nachweis → Übergabe. Immer über `AGENTS.md` mit `harness/project.md` lesen.

## 1. Start und Auftrag

- Vor dem Schreiben `git status` prüfen. Pro Arbeitsverzeichnis nur eine schreibende Sitzung; parallele Sitzungen nutzen Worktrees/Klone. Fremde Änderungen weder überschreiben noch mitcommitten. Unerwartete Dateiänderungen zuerst neu lesen und klären. Commits nur auf Auftrag.
- Fortsetzung: zugehörige Idea/Spec samt Arbeitsstand und Docs nach `AGENTS.md` lesen; Angaben gegen Code und Git prüfen. Keine offenen Vorhaben ohne konkreten Auftrag weiterbauen.
- Diktat sinngemäß deuten; bei verschiedenen folgenreichen Lesarten die Deutung nennen oder fragen. Nur entscheidungsrelevante Fragen bündeln. Reversible Annahmen nennen; neue Produktentscheidungen und spürbare Risiken klären.
- Fehlende Fakten nicht erfinden. Vorschläge und Annahmen sind keine bestätigten Projektfakten.
- Vor Massenaktionen oder irreversiblen Schritten (Löschen, Versand, Veröffentlichung, Kosten) Umfang und Probelauf zeigen: Anzahl, Beispiele, Rückweg. Erst danach konkret bestätigen lassen.

## 2. Vor Produktcode: Voraussetzungen prüfen

**Lesen ist nicht Ausführen.** Bei `Pending Project Init` zuerst `harness/init.md` abschließen. Vor Produktcode müssen Brief/Projektgrenzen, Stack und Dateistruktur, gewählte Profile, Prüfstrategie und nötige Docs tatsächlich eingetragen sein. `python3 tools/check-harness.py --ready` prüft fehlende Pflichtfelder und Platzhalter; das ersetzt nicht die fachliche Go-Entscheidung im Init.

- Neues/geändertes Nutzerverhalten: betroffene Bereichs-Spec vor Umsetzung auf `Modified` setzen, Soll und Prüfplan festlegen (`specs/S000-readme.md`). Das gilt auch für Produkt-Prototypen. Nur ein ausdrücklich abgegrenzter Erkundungs-Spike folgt der Ausnahme im Init.
- Größere/unklare Vorhaben: Idea als Änderungsakte (`ideas/I000-readme.md`). Klarer direkter Auftrag genügt für „Beauftragt“; keine zusätzliche Freigabeschleife erfinden.
- Verhaltensgleicher Refactor, Struktur- oder Dokuauftrag: Auftrag und Prüfplan reichen, keine künstliche Produktspec.
- Neuer Projektteil anderer Art: passende Profile/Bereiche, Risiken und offene Technikfragen kurz einordnen; Auswahl mit Auftraggeber klären und im Projektprofil festhalten.
- Vor Umsetzung Pflichtchecks und betroffene Regression aus der Projekt-Prüfstrategie bestimmen; in der Spec, bei Arbeit ohne Spec im Fortsetzungsstand festhalten.

## 3. Umsetzen

Setze den ganzen beauftragten Umfang um, aber keine Nebenaufgaben. Bei „wie vorher, nur …“ zuerst den vorherigen Stand herstellen, dann nur das Genannte ändern. Weitere Funde berichten.

- Neuen Code sofort in der beschlossenen Struktur anlegen, nicht später einsortieren. Fehlt die Struktur, zurück zum Init bzw. zur Architekturentscheidung.
- Eine Quelle je Wert/Regel. Geänderte Regeln ersetzen die alten, nicht durch Sonderfälle übersteuern.
- Gemeinsame Bausteine bilden, sobald die Gemeinsamkeit klar ist, spätestens beim dritten Vorkommen. Keine Abstraktionen auf Vorrat; eine Datei hat eine nachvollziehbare Verantwortung. Bewusst identische Website-Rahmen folgen dem Website-Profil.
- Refactoring bleibt verhaltensgleich und wird durch die betroffene Regression abgesichert. Bei unklarer Auswirkung gesamte vorhandene Verhaltenstestsuite ausführen. Unbeteiligte Teile nicht ungefragt umbauen; notwendige größere Umbauten/technische Schulden benennen.
- Neues Soll oder neue Entscheidung nötig? Erst klären und zuständige Spec/Doc aktualisieren, dann weiterarbeiten.
- Geltenden Stand in Projektdateien ersetzen, nicht als Verlauf anhängen (`document-contract.md`). Konfiguration/Code sind Quelle ausführbarer Werte; Docs wiederholen sie nicht.

## 4. Abschluss und Fortsetzung

`harness/verification.md` ausführen. Bei Lücken nicht „fertig“ melden. Vor Übergabe oder Aufgabenwechsel Arbeitsstand in Idea/Spec aktualisieren, sonst in `harness/project.md`: erledigt, ausstehend, Blocker, nächster Schritt und erforderliche Checks.

Übergabe: Ergebnis, geänderte Pfade, tatsächlich ausgeführte Prüfungen samt Grenzen, Annahmen und Offenes. Beim Harness-Test auf Wunsch zusätzlich den gewählten Entscheidungszweig und tatsächlich gelesene Dateien nennen. Harness-Regeln nur auf ausdrücklichen Auftrag ändern; Beobachtungen in `harness-learnings.md` festhalten. Bei Harness-Änderungen den Abhängigkeitsabgleich aus `document-contract.md` im selben Schritt ausführen.
