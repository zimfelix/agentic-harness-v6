# Agentic Harness v4.5

Eine universelle Vorlage für Softwareprojekte mit KI-Coding-Agenten. Der aktuelle Harness liegt vollständig unter [`agentic-harness/`](agentic-harness/); das bestehende GitHub-Repository behält seinen Namen `agentic-harness-v5`.

## Was sich geändert hat

Die ursprüngliche Vorlage war zu ausführlich und die zusätzliche Lite-Variante sowie Skill-/Adapterordner machten die Orientierung unnötig kompliziert. **v4.5 führt alles in einer Vorlage zusammen:** kurzer Agenteneinstieg, Brief und Technik im Init, ein Verification Loop und nur ein Ordner `profiles/` für Website- und Business-Software-Regeln samt Werkzeugen.

Templates, Ideas, Bereichs-Specs, Dokumentenvertrag und Harness-Learnings bleiben. Init, Dateistruktur und beauftragtes Soll müssen vor Produktcode feststehen; eine kleinere Vorlage allein garantiert keine zuverlässige Agentenarbeit.

## Neues Projekt starten

Den **Inhalt** von `agentic-harness/` in ein leeres Projekt-Root kopieren, nicht das gesamte Repository:

```sh
mkdir -p /pfad/zum/neuen-projekt
cp -R agentic-harness/. /pfad/zum/neuen-projekt/
```

Oder einen bereinigten Export ohne lokale Projektbefüllung/Learnings erzeugen:

```sh
VERSION=v4.5 sh agentic-harness/tools/export-harness.sh /pfad/zum/leeren-projekt
```

Projektordner mit dem Agenten öffnen und frei erzählen, was entstehen soll. Optional zuerst `project/brief.md` schreiben. `AGENTS.md` führt über Init → Soll/Specs → Umsetzung → Nachweise. Details: [Anleitung](agentic-harness/harness/README.md).

## Struktur

```text
agentic-harness/
├── AGENTS.md                  Einstieg und Leseauslöser
├── harness/                   Core, Init, Projektprofil, Verification, Templates
├── profiles/                  Website und Business Software: Regeln, Referenzen, Tools, Assets
├── docs/, project/            Projektwissen und Ausgangsbeschreibung
├── ideas/, specs/             Vorhaben und beauftragtes Verhalten
├── tools/                     Struktur-/Init-Check und Export
├── document-contract.md       Dokumentpflege
└── harness-learnings.md        Beobachtungen zur Agentenarbeit
```

Profile werden ausdrücklich über `AGENTS.md` geladen, nicht als native Skills automatisch entdeckt. Keine parallelen `.agents/`, `.claude/` oder `skills/`-Ordner und keine Synchronisierung.

## Harness prüfen und pflegen

```sh
python3 agentic-harness/tools/check-harness.py
```

Die einmalige Kopier-/Export-/Readiness-Testsuite wurde vor Veröffentlichung ausgeführt und anschließend auf Wunsch entfernt. Strukturtests sind kein Nachweis zuverlässiger Agentenbefolgung. Prüfstand und offene Beobachtungen: [Harness-Learnings](agentic-harness/harness-learnings.md).

Für Harness-Arbeit den Agenteneinstieg `agentic-harness/AGENTS.md` lesen. Produktarbeit gehört in ein exportiertes Projekt, nicht in die Vorlage.
