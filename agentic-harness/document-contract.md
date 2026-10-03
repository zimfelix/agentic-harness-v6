# Dokumentenvertrag – Markdown-Aufbau und Pflege

> - **Typ:** Designregel
> - **Zuständigkeit:** Einheitlicher, lesbarer Aufbau einzelner Markdown-Dateien.
> - **Gilt bei:** Neue oder inhaltlich befüllte Steuerungs- und Projekt-MD-Dateien, Verdichten gewachsener Projektdateien sowie Export als Vorlage; bestehende Dateien werden schrittweise angepasst.
> - **Ladebeziehungen:** Vor dem Schreiben Rollen und Ladewege in `agentic-harness/harness-map.md` prüfen; aktuelle Pfade über `AGENTS.md`.
> - **Nicht zuständig:** Den gesamten Dateibaum oder den Arbeitsablauf des Agenten festlegen.

## Vor dem Schreiben

1. Bestimme die **eine Hauptaufgabe** der Datei. Was gehört ausdrücklich woanders hin?
2. Kläre ihren **Auslöser**: Wann wird sie gelesen, und über welchen Einstieg erreicht?
3. Kläre ihre **direkten Beziehungen**: Was muss vorher, nur bedingt oder danach gelesen werden?
4. Trage neue Dateien und geänderte Beziehungen zuerst in `agentic-harness/harness-map.md` ein. Kennzeichne geplante Pfade als geplant.
5. Nutze konkrete Pfade ab Repo-Root; kürze sie nur bei echten relativen Markdown-Links, deren Ziel geprüft wurde.

## Standard-Kopf für Steuerungs- und Projektdokumente

Vorlagen und Idea-/Spec-Artefakte einschließlich `ideas/I000-readme.md` und `specs/S000-readme.md` behalten ihr eigenes Format. Auch die für Menschen geschriebene `README.md` braucht keinen Metakopf.

```markdown
# {Titel}

> - **Typ:** {Einstieg | Prozess | Projektdoku | Designregel | Index | Lernnotiz}
> - **Status:** {nur wenn Entwurf, Platzhalter oder Artefaktstatus wichtig ist}
> - **Zuständigkeit:** {eine Aufgabe und ihr Ergebnis}
> - **Gilt bei:** {konkreter Auslöser}
> - **Ladebeziehungen:** {vorher / wenn … / danach: Pfad und Zweck; sonst „Keine“}
> - **Nicht zuständig:** {Abgrenzung, falls Verwechslung möglich}
```

## Inhalt und Prüfung

- Hauptteil passend zum Typ gliedern, nicht überall dieselben Kapitel erzwingen.
- Kurze Sätze und kleine Listen schreiben. Eine Regel pro Gedanke.
- Nur direkte Ladebeziehungen nennen; kein „alle Docs bei Bedarf“ und keine Kopie der Landkarte.
- **Lesen** ist nicht **Ändern**: Ein Link überträgt keine Zuständigkeit.
- Vor Übernahme Auslöser, Pfade, Erreichbarkeit und doppelte Zuständigkeiten prüfen.

## Projektspezifische Gerüste

In `agentic-harness/harness/project.md` und den Projekt-Docs (`agentic-harness/docs/*.md`) bleiben Kopf und „Universeller Rahmen“ erhalten. `agentic-harness/harness/init.md` ersetzt den Platzhalter **„Noch offen (Project Init).“** unter „Projektspezifische Befüllung“ durch bestätigte Inhalte. Die Root-`README.md` enthält nach dem Export einen Vorlagenkopf und den universellen Abschnitt „Projektstart mit dem Agentic Harness“; beim Init ersetzt die Produktbeschreibung (für Menschen, ohne Metakopf) den Vorlagenkopf, vorhandene Produktinhalte werden ergänzt. Der universelle Abschnitt steht unverändert oben unter Titel und lokaler Adresse, die Projektabschnitte darunter; das Export-Skript übernimmt ihn von seiner Überschrift bis zur nächsten Ebene-2-Überschrift.

Beim Befüllen dieser Gerüste auch den Kopf gegen das Projekt prüfen: Stimmen **Zuständigkeit, Auslöser, Ladebeziehungen und Abgrenzung** noch? Status nur ändern, wenn die Datei tatsächlich befüllt ist. Offene Entscheidungen ausdrücklich offen lassen. Neue Projekt-Docs brauchen einen erreichbaren Leseauslöser; eine geänderte Dateirolle ist Harness-Arbeit.

**Trennung für den Export:** Alles über der Überschrift „Projektspezifische Befüllung“ ist universell, mit Ausnahme der Status-Zeile im Kopf und wandert in eine neue Vorlage. Alles darunter gehört dem Projekt. Universelle Regeln deshalb nie im projektspezifischen Teil einführen, Projektfakten nie im universellen Teil. Die Exportschritte stehen in `agentic-harness/README.md`.

## Wohin gehört was?

Jede Information hat genau einen Ort. Fehlt der passende Ort, entsteht Wildwuchs in immer geladenen Dateien.

| Information | Ort |
|---|---|
| Bestätigtes Ziel, Grenzen, Freigaben, Livegang-Blocker, offene Entscheidungen | `agentic-harness/harness/project.md` |
| Eingerichtete Befehle (je eine Zeile) und **letztes** Ergebnis der Gate-Befehle | `agentic-harness/harness/project.md` (Tabelle, ersetzen) |
| Lebender Soll-Stand je Bereich (AK) samt letztem Nachweis | Bereichs-Spec unter `agentic-harness/specs/` |
| Gewähltes Profil | Name oben im Projektprofil; übernommene, angepasste oder abgewählte Profilteile in der thematisch zuständigen Datei dieser Tabelle |
| Gestaltungsregeln: Farbrollen, Schrift, Größenskala, Bausteine, Zustände (keine Einzelwerte je Stelle) | `agentic-harness/docs/design.md` |
| Bausteine, Dateien, Datenfluss, Archiv | `agentic-harness/docs/architecture.md` |
| Betrieb: Ausführung, Auslöser/Zeitplan, Umgebungen, Konfiguration, Ort der Zugangsdaten (nie Werte), Protokolle | `agentic-harness/docs/architecture.md` |
| Stack, Konventionen, technische Schulden | `agentic-harness/docs/code.md` |
| Teststrategie, Suiten, Werkzeuge, Prüfgrößen und Methoden | `agentic-harness/docs/testing.md` |
| Größere Änderungen und offene Vorhaben (Anlass, Umfang, betroffene Specs, Teilaufgaben, Status); auch Aufgabenlisten und mehrschrittige Pläne | Idea unter `agentic-harness/ideas/`, erledigt unter `ideas/archiv/` |
| Eigenständiges Projektthema ohne passende Doc (Kriterium: „Neue Projekt-Docs“) | `agentic-harness/project/<thema>.md` |
| Verlauf, was wann geändert wurde, einzelne Prüfläufe | Git (Commit-Nachricht) und Übergabe im Chat, **nicht** in Projektdateien |
| Beobachtungen über den Harness, wiederkehrende Agentenfehler, Begründung von Harness-Änderungen | `agentic-harness/harness-learnings.md` (aktiv), `agentic-harness/project/learnings-archiv.md` (erledigt) |

## Aktueller Stand statt Verlauf

Projektprofil, Projekt-Docs und Specs beschreiben den **geltenden** Stand. Der Verlauf steht in Git.

- Ändert sich eine bestätigte Aussage, ersetze sie an ihrer Stelle. Hänge keinen weiteren Absatz („früherer Stand“, „aktueller Stand“, „Stand vom …“) an und lass keine überholten Varianten stehen.
- Specs führen pro Akzeptanzkriterium nur den letzten gültigen Nachweis. Nachweise ersetzter Stände entfallen.
- Datumsangaben nur, wo sie entscheidungsrelevant sind (z. B. Stand eines Prüflaufs oder einer Freigabe).
- **Richtgrößen** (bei geteilten Dateien nur der Abschnitt „Projektspezifische Befüllung“, weil der universelle Rahmen unterschiedlich lang ist): `agentic-harness/harness/project.md` etwa 6 KB, eine Projekt-Doc etwa 6 KB, eine Spec etwa 15 KB oder etwa 15 AK (Zuschnitt: `agentic-harness/specs/S000-readme.md`). Wird eine Grenze überschritten, verdichte zuerst; trenne erst dann ein eigenständiges Thema in eine eigene Datei oder Spec. Das Gate prüft berührte Projektdateien darauf (`agentic-harness/harness/verification/gate.md`).
- Bestätigte Entscheidungen beim Verdichten nicht stillschweigend löschen: Sie wandern an die zuständige Stelle (z. B. Gestaltung nach `agentic-harness/docs/design.md`, Verhalten in die Spec).

## Neue Projekt-Docs

Ein neues Thema wird zuerst in eine bestehende Datei eingeordnet. Eine **eigene Projekt-Doc** lohnt sich erst, wenn das Thema eigene Regeln oder Entscheidungen braucht, bei mehreren Aufgaben gelesen wird und in keine bestehende Doc passt, ohne deren Richtgröße zu sprengen (z. B. Datenschutz bei einem CRM, Betrieb einer Automation). Nicht auf Vorrat anlegen.

```text
neues Thema
  ├─ passt in eine bestehende Datei?                → dort einordnen (Standard)
  ├─ eigenständig, wiederholt gebraucht, nur DIESES Projekt
  │     → agentic-harness/project/<thema>.md        (wird nie exportiert)
  └─ für ALLE Projekte bzw. eine Projektart sinnvoll
        → Eintrag in harness-learnings.md → beim Release als Profil-Doc oder universelle Doc mit Gerüst
```

Eine neue Projekt-Doc bekommt den Standard-Kopf (Typ „Projektdoku“), einen konkreten Leseauslöser unter „Projektspezifische Ergänzungen“ in `AGENTS.md` im Format `- **Thema:** bei <konkretem Auslöser> → agentic-harness/project/<thema>.md` und eine eigene Zeile mit ihrem Pfad in `agentic-harness/harness-map.md` (unter der allgemeinen Zeile `project/<thema>.md`). Der Auslöser nennt Aufgaben, nicht das Thema allein: „bei personenbezogenen Daten, Löschung oder Auskunft“ statt „Datenschutz“. Unter `agentic-harness/docs/` liegen nur Docs mit universellem Rahmen und Abschnitt „Projektspezifische Befüllung“; das Export-Skript erwartet diese Trennung dort in jeder Datei.

## Bei neuen, umbenannten oder entfernten Dateien

1. **Vorher:** Suche repo-weit nach dem alten Pfad, Dateinamen und relativen Markdown-Links. Prüfe, welche Dateien darauf angewiesen sind.
2. **Gemeinsam ändern:** Passe diese Verweise, den Einstieg und die Landkarte an. Entferne Verweise nur, wenn die Beziehung wirklich entfällt. Liegt die Datei im Zubehörordner eines Profils (`agentic-harness/profiles/<name>/`), passe auch die `README.md` dieses Ordners und seiner Unterordner an; sie beschreibt, welche Datei welche Aufgabe hat.
3. **Nachher:** Prüfe alle verbliebenen Verweise und die Ladebeziehungen in betroffenen Dokumentköpfen gegen reale Dateien. Geplante Pfade bleiben ausdrücklich als geplant markiert.

Ändern sich Rollen oder Ladeauslöser ohne Umbenennung, gilt derselbe Abgleich für die betroffenen Köpfe, den Einstieg und die Landkarte. Prüfe sie bei solchen Änderungen, nicht pauschal bei jeder Produktaufgabe.

Auch eine manuelle Löschung kann bestehende Verweise brechen. Beim nächsten Harness-Änderungsauftrag zuerst den aktuellen Baum prüfen; Markdown aktualisiert sich nicht selbst.

Der Vertrag bleibt im Harness für spätere Projekt-Docs verfügbar. Er beschreibt Schreibformat und Pfadpflege; `AGENTS.md` und `agentic-harness/harness/init.md` regeln, wann er zu laden ist.
