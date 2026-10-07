# Agentic Harness Lite

Schlanke Vorlage für Softwareprojekte mit KI-Coding-Agenten (Claude Code, Codex, Pi). `AGENTS.md` ist immer geladen und bleibt kurz. Ablaufwissen liegt in Skills, die erst bei Bedarf geladen werden.

**Start:** Ordner mit dem Agenten öffnen und frei erzählen, was entstehen soll.

**Skills und Tool-Adapter:** `.agents/skills/` enthält die gemeinsame, mit dem Projekt versionierte Skill-Quelle. `.claude/skills/` enthält ausschließlich relative Verzeichnislinks dorthin, keine zweite Regelkopie. Die unterschiedlichen Suchpfade sind eine Anpassung an die Agentenwerkzeuge. Mitgelieferte Skills sind nicht automatisch aktiv: Die Auswahl und die geltenden Bereiche stehen im Projektabschnitt von `AGENTS.md`; dessen Skill-Tabelle regelt das Lesen. Eine globale Skill-Installation ist für diese Vorlage nicht erforderlich.

**Pi:** Pi lädt die Projekt-Skills unter `.agents/skills/` erst, wenn du dem Ordner vertraust. Gib dazu einmal `/trust` im Projekt ein; bei `pi -p` brauchst du `--approve`. Ohne Freigabe lädt Pi nur `AGENTS.md`, aber keine Skills. Claude Code und Codex laden die Skills ohne Freigabe.

## Dateien und wer wen lädt

```text
                          ┌────────────────────────────────────────────┐
  jede Sitzung ─────────► │ AGENTS.md                (immer geladen)   │
                          │  ├ Skill-Tabelle ─── wann welcher Skill    │
                          │  ├ Projekt ───────── Brief, Stack, Regeln  │◄── Einstieg ins
                          │  ├ Arbeitsrahmen ─── Strenge je Reifegrad  │    Projektwissen
                          │  ├ Arbeitsweise ──── nicht offensichtliche │
                          │  │                   Regeln                │
                          │  ├ Ideas und Specs / Fertig heißt                    │
                          │  └ Harness selbst ── Änderungsregeln       │
                          └───┬──────────────┬──────────────┬──────────┘
                              │ bei Pending  │ wenn gewählt │ nach Leseauslöser
                              ▼              ▼              ▼
              .agents/skills/project-init    │          docs/<thema>.md
                 SKILL.md                    │          (entsteht beim Init oder bei
                                             │           Bedarf, z. B. architecture.md,
                                             │           decisions/, design.md)
                          ┌──────────────────┴───────────────────┐
                          ▼                                      ▼
     .agents/skills/business-software              .agents/skills/website
        SKILL.md  (CRM, Buchung, Buchhaltung)         SKILL.md
        └ references/                                 ├ references/
           daten-geld-zeit.md                         │  stil-defaults.md
           rechte-und-nachvollziehbarkeit.md          │  baukasten.md
           buchhaltung.md                             │  nachweis.md
           entscheidung-vorlage.md                    └ assets/device-preview.html

  ideas/_vorlage.md ── Format für ideas/Ixxx-*.md (Problem, Scope, Machbarkeit, offene Fragen)
  specs/_vorlage.md ── Format für specs/Sxxx-*.md (Aufträge, AK, Prüfplan, Arbeitsstand)
  .claude/skills/   ── Links auf .agents/skills/ (für Claude Code; Codex und Pi lesen .agents/ direkt)
  harness-learnings.md ── Beobachtungen zum Harness, offen bis geprüft
```

Wer schreibt wohin:

```text
  project-init ──► AGENTS.md „Projekt“, README „Produkt“, docs/*, ideas/*, specs/*
  business-software ──► docs/architecture.md (Glossar, Fachmodell, Schichten, Teststrategie), docs/decisions/
  website      ──► docs/design.md, Befehlstabelle, Blocker unter „Offene Entscheidungen und Annahmen“
  jede Aufgabe ──► Code, Tests, Spec-Nachweise, Befehlstabelle (letztes Ergebnis), Fortsetzungsstand
                  (Arbeitsstand in der Idee/Spec; sonst im Projektabschnitt)
```

## Vorbereitete Ablageorte

| Ort | Inhalt und Leseauslöser |
|---|---|
| `docs/` | Dauerhafte Projektregeln; konkrete Dateien und deren Leseauslöser werden im Projektabschnitt von `AGENTS.md` eingetragen. Noch keine Fach-Dokumente angelegt. |
| `ideas/` | Offene Vorhaben mit Status `Idee`; bei Klärung des betreffenden Vorhabens lesen. |
| `specs/` | Beauftragtes Verhalten mit Status `Modified` oder `Implemented`; bei Umsetzung, Änderung und Prüfung der betreffenden Funktion lesen. |

Mögliche Projekt-Docs, **noch nicht angelegt**: `docs/architecture.md` für Aufbau, Fachmodell und Betrieb; `docs/design.md` für übergreifende Gestaltung; `docs/code.md` für nicht technisch abbildbare Coding-Guidelines; `docs/testing.md` für eine umfangreichere Teststrategie; `docs/decisions/` für begründete übergreifende Entscheidungen. Nur bei Bedarf anlegen, nicht dieselben Angaben aus Code, Konfiguration oder Projektabschnitt kopieren. Gewählte Skills können bestimmte Docs verlangen.

```text
ideas/Ixxx-*.md (Idee)
    → geklärt + bestätigt + Umsetzung beauftragt
    → specs/Sxxx-*.md (Modified)
    → AK, Pflichtchecks und Regression belegt (Implemented)
    → späterer Änderungsauftrag (wieder Modified)
```

Bei Überführung keine doppelte aktive Beschreibung; Details stehen unter „Ideas und Specs“ in `AGENTS.md`.

## Projektstart (Init)

```text
  Du erzählst frei (Diktat ok)
        │
        ▼
  0 Ausgangslage ── bestehender Code? Git? schon ein Brief vorhanden?
        │
        ▼
  1 Projektgespräch ──► Agent übersetzt in den Brief:
        │               Ziel · Reifegrad · erstes Ergebnis · Erfolg · Risiken · Ausgangslage
        │               je Feld: bestätigt / Annahme / offen
        │               Rückfragen nur bei Folgenreichem, gebündelt
        ▼
  Brief bestätigt ──► AGENTS.md „Projekt“ (fachliche Felder)
        │
        ▼
  2 Technik ── Stack · Struktur · Standards/Qualitätsziele · Tests/TDD/Regression (lokal/CI)
        │       passender Skill (+ seine Init-Fragen)
        │
        ▼
  AGENTS.md „Projekt“ (technische Felder) · docs/ · README „Produkt“ · Specs/Ideen
        │
        ▼
  3 Checks einrichten und wirklich ausführen
        │
        ▼
  4 Go/No-Go ──No-Go──► blockierende Fragen gebündelt, Status bleibt „Pending“
        │
        Go
        ▼
  Status entfernt ──► erster Auftrag läuft nach dem Aufgabenfluss
```

## Jede Aufgabe

```text
  Auftrag
    │
    ▼
  AGENTS.md: Projekt + Arbeitsrahmen (Reifegrad bestimmt die Strenge)
    │  Fortsetzung: zugehörige Idee/Spec und Arbeitsstand + Projekt-Docs nach Leseauslöser lesen
    │  Prüfplan: Pflichtchecks und betroffene Regression vor Umsetzung festlegen
    │
    ├─ neuer Projektteil ──► Einordnung: Skills, Risiken ────────┐
    │                       (Auswahl nach Bestätigung)           │
    ├─ noch unklar ─────────► Idee in ideas/ ──► klären ─────────┤
    │                        (kein Auftrag; Überführung erst nach Beauftragung)
    ├─ neues Verhalten ─────► Spec „Modified“ mit AK ────────────┤
    └─ sonst ───────────────► Umfang = Auftrag ──────────────────┤
                                                                 ▼
                                        Laden nach Bedarf: gewählter Skill, docs/<thema>.md
                                                                 │
                                                                 ▼
                                        Umsetzen (Arbeitsweise; Risiken vorher benennen)
                                                                 │
                                                                 ▼
                                        Fertig heißt: alle AK belegt, erforderliche Regression grün
                                          │                         │
                                        Lücke                       ok
                                          ▼                         ▼
                                        Ursache beheben         Befehlstabelle + Spec-Nachweis
                                        └─► erneut prüfen       nachführen ──► Übergabe
                                        (oder Blocker melden)
```

## Warum so

- **Immer geladen ist nur, was der Agent nicht selbst wissen kann:** Projektfakten, deine Arbeitsabsprachen und Erfahrungswissen. Allgemeines Handwerk wie Tests schreiben oder Git bedienen steht hier nicht.
- **Eine Regel steht an einer Stelle.** Skills ergänzen `AGENTS.md`, wiederholen sie aber nicht. Projekt-Docs entstehen nur bei Bedarf, mit einer Hauptzuständigkeit und konkretem Leseauslöser; erst verdichten, dann gegebenenfalls aufteilen.
- **Strenge nach Reifegrad:** Ein Prototyp braucht keine Specs, ein Produkt schon.

## Als Vorlage weitergeben

Universell ist alles außer dem Abschnitt „Projekt“ in `AGENTS.md`, ausgefüllten Ideen und Specs, Projektinhalten unter `docs/`, dem README-Abschnitt „Produkt“ und dem Produktcode. Im Ziel setzt du „Projekt“ auf `Pending Project Init` zurück. Kopiere die versteckten Verzeichnisse `.agents/` und `.claude/` mit und erhalte die relativen Links unter `.claude/skills/`; übernimm keine ausgefüllten Projektinformationen oder Harness-Prüfprotokolle als Projektwissen.
