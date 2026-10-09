# Harness verwenden und pflegen

## Aufbau

```text
AGENTS.md → core.md + project.md
                ├─ Pending → init.md → Brief, Struktur, Prüfplan → Go/No-Go
                ├─ beauftragtes Verhalten → Bereichs-Spec
                ├─ größeres/offenes Vorhaben → Idea
                └─ Docs/Profile nach Anlass → umsetzen → verification.md → Übergabe
```

`document-contract.md` regelt Dokumentpflege. `harness-learnings.md` hält Beobachtungen/Änderungsgründe. Eine separate Harness-Map entfällt; `AGENTS.md` und direkte Verweise sind die Orientierung.

## Start

Aus dem v6-Vorlagen-Repository nur `agentic-harness/` verwenden, nicht das gesamte Repository: `tests/` und die Root-README sind keine Produktvorlage. Für ein neues leeres Projekt den bereinigten Export bevorzugen; eine rohe Kopie kann lokale Befüllung/Learning-Einträge mitnehmen. Idee frei erzählen oder eine vorhandene Ausgangsbeschreibung angeben. Init nimmt bestehende Vorgaben auf, bestätigt den Brief und legt die Technik/Struktur fest. Ein vorhandener Bauauftrag läuft nach Init-Go weiter; Init allein beauftragt keinen Produktbau.

Projektarten liegen nur unter `profiles/<name>/`: `profile.md` routet Fachregeln/Referenzen, `tools/` und `assets/` bündeln das Zubehör. Auswahl/Bereiche stehen in `harness/project.md`; `AGENTS.md` schreibt das Lesen bei passenden Aufgaben vor. Keine native automatische Skill-Erkennung oder Adapter-Synchronisierung. Pflegevorgaben: `document-contract.md`.

Website-Werkzeuge und Setup: `profiles/website/README.md`. Bei Geschäfts-/Personendaten oder Seiteneffekten: `profiles/business-software/profile.md`.

## Prüfen

```sh
python3 tools/check-harness.py          # Pfade, Links, Pflichtstruktur
python3 tools/check-harness.py --ready  # Init-Voraussetzungen und Profil-/Bereichsauswahl
python3 tools/check-harness.py --go     # zusätzlich dokumentierter Go-Status, keine fachliche Abnahme
```

Readiness erkennt Platzhalter/fehlende Einträge und unbekannte/unvollständig eingeordnete Profile/Bereiche. `--ready` läuft vor der Go-Entscheidung, `--go` danach. Beide prüfen weder Sinn/Richtigkeit der Inhalte noch Spec-Erfüllung und erzwingen kein Schreibverbot. Der Agent muss das Init-Go anwenden; Verlässlichkeit separat durch Agentenproben prüfen.

## Export

```sh
sh tools/export-harness.sh /pfad/zum/leeren-ordner
# Aktualisierung nur eines sauberen, als Vorlage markierten Export-Klons:
PRODUKTBEGRIFFE='produktname|domain' sh tools/export-harness.sh /pfad/zum/vorlagen-klon
```

Das Skript lokalisiert seine Quelle unabhängig vom Arbeitsverzeichnis, setzt Projektprofil/vier mitgelieferte Docs, Projektverweise und Learnings zurück. Es exportiert Profile, Werkzeuge und Templates, aber keine Produkt-README, neuen Projekt-Docs, konkreten Ideas/Specs oder Produktcode. Repository-`tests/` und die Repository-Root-README werden nicht übernommen; eine kurze neue Start-README wird erzeugt. Learning-Regeln bleiben, die Einträge sind leer. Leere Ziele werden erst nach Validierung befüllt. Bestehende Ziele benötigen `.harness-template`, sauberes Git und ein unbefülltes Projektprofil; Produktprojekte und übergeordnete Quellordner werden abgelehnt. Kein Commit/Push.

## Weiterentwicklung und Release

Im Produktprojekt Harness-Beobachtungen mit Projekt, Harness-Stand, Auftrag/Randbedingungen, Soll/Ist, Belegen und offenen Fragen lokal in `harness-learnings.md` sammeln. Keine universellen Regeln/Profile/Werkzeuge dort ändern, außer auf konkreten Ausnahmeauftrag; normale Projektbefüllung bleibt erlaubt.

Zum Wochenreview auf Auftrag ausgewählte Learnings mit ihrem Quellkontext im zentralen Vorlagen-Repository `agentic-harness-v6` auswerten. Gilt die Erkenntnis universell, für eine Projektart oder nur lokal? Vor Änderung aktive Learnings lesen, nur ausdrücklich beauftragte Regeln übernehmen und Verweise/Export samt Learning nachführen. Keine automatische Übernahme oder Synchronisierung. Produktfakten bleiben lokal.

Für jede übernommene Änderung das neue Soll und die unverändert geltenden Zusagen festhalten. Passende Tests ergänzen/aktualisieren und betroffene Regression ausführen: nicht nur die geänderte Datei, sondern ihre Wechselwirkungen mit Routing, Core/Init, Profilen, Statusregeln, Checkern und Export. Fehler-/Gegenfälle prüfen; keine Tests lockern, nur damit die Änderung grün wird. Alte Erwartungen nur bei bewusst beschlossener Solländerung ersetzen, übrige Zusagen erhalten.

Ausführbare Werkzeug-/Exportregeln deterministisch prüfen. Änderungen am Agentenablauf zusätzlich in gezielten frischen Sitzungen erproben; Strukturchecks oder Textsuche belegen keine Befolgung. Umfang nach Risiko wählen, nicht jede Woche pauschal alle Projektproben. Im Prüfstand unterscheiden: bestanden, fehlgeschlagen, nicht ausgeführt; ältere Ergebnisse nicht als Nachweis des neuen Stands verwenden. Die zentrale Pflegesuite liegt nur im v6-Repository unter `tests/harness/`, nicht in Produkt-Exports.

Release: Diff, aktive Learnings und aktuellen Prüfstand prüfen, bewusst ausgewählte Änderungen exportieren und den Export gegenprüfen. Commit/Push/Tags nur nach Auftrag. Übernommene Learnings nach dem Release verdichten; Herkunft, Randbedingungen und offene Fragen erhalten. Neue Exporte starten ohne Einträge; bestehende Produktprojekte werden nicht automatisch aktualisiert.

Kleine Textdateien und grüne Strukturtests garantieren keine Agentenqualität. Frische Agentenproben müssen mindestens Init vor Code, Spec vor Verhalten, Fortsetzung und Verhalten bei fehlenden Nachweisen prüfen.
