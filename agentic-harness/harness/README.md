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

In ein leeres Projekt den Inhalt dieser Vorlage einschließlich versteckter Verzeichnisse und relativer Links kopieren, oder aus einem befüllten Projekt exportieren. Idee frei erzählen; optional `project/brief.md`. Init nimmt bestehende Vorgaben auf, bestätigt den Brief und legt die Technik/Struktur fest. Ein vorhandener Bauauftrag läuft nach Init-Go weiter; Init allein beauftragt keinen Produktbau.

Projektarten liegen nur unter `profiles/<name>/`: `profile.md` routet Fachregeln/Referenzen, `tools/` und `assets/` bündeln das Zubehör. Auswahl/Bereiche stehen in `harness/project.md`; `AGENTS.md` schreibt das Lesen bei passenden Aufgaben vor. Keine native automatische Skill-Erkennung oder Adapter-Synchronisierung. Pflegevorgaben: `document-contract.md`.

Website-Werkzeuge und Setup: `profiles/website/README.md`. Bei Geschäfts-/Personendaten oder Seiteneffekten: `profiles/business-software/profile.md`.

## Prüfen

```sh
python3 tools/check-harness.py          # Pfade, Links, Pflichtstruktur
python3 tools/check-harness.py --ready  # zusätzlich Init-Felder und erforderliche Docs
```

Readiness erkennt Platzhalter/fehlende Einträge. Sie prüft weder Sinn/Richtigkeit der Inhalte noch Spec-Erfüllung und erzwingt kein Schreibverbot. Der Agent muss das Init-Go anwenden; Verlässlichkeit separat durch Agentenproben prüfen.

## Export

```sh
sh tools/export-harness.sh /pfad/zum/leeren-ordner
# Aktualisierung nur eines sauberen, als Vorlage markierten Export-Klons:
PRODUKTBEGRIFFE='produktname|domain' sh tools/export-harness.sh /pfad/zum/vorlagen-klon
```

Das Skript lokalisiert seine Quelle unabhängig vom Arbeitsverzeichnis, setzt Projektprofil/vier mitgelieferte Docs, Projektverweise und Learnings zurück. Es exportiert Profile, Werkzeuge und Templates, aber keine Produkt-README, neuen Projekt-Docs, konkreten Ideas/Specs oder Produktcode. Leere Ziele werden erst nach Validierung befüllt. Bestehende Ziele benötigen `.harness-template`, sauberes Git und ein unbefülltes Projektprofil; Produktprojekte und übergeordnete Quellordner werden abgelehnt. Kein Commit/Push.

## Weiterentwicklung und Release

Vor Harness-/Profil-/Tooländerung aktive Learnings lesen. Gilt die Erkenntnis universell, für eine Projektart oder nur lokal? Nur ausdrücklich beauftragte Regeln übernehmen; im selben Schritt Verweise/Export und Learning mit Grund nachführen. Produktfakten bleiben lokal.

Release: Diff und aktive Learnings prüfen, bewusst ausgewählte Änderungen exportieren, Kopier-/Export-/Konsistenztests ausführen. Commit/Push/Tags nur nach Auftrag. Übernommene Learnings können mit Release-Verweis nach `project/learnings-archiv.md` wandern; neue Vorlage startet ohne Einträge.

Kleine Textdateien und grüne Strukturtests garantieren keine Agentenqualität. Frische Agentenproben müssen mindestens Init vor Code, Spec vor Verhalten, Fortsetzung und Verhalten bei fehlenden Nachweisen prüfen.
