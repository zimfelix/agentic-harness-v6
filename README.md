# Agentic Harness – zwei Vorlagen

Dieses Repository enthält zwei eigenständige Varianten für Softwareprojekte mit KI-Coding-Agenten. Wähle **eine**, nicht beide. Die Root-README erklärt Auswahl und Kopieren; jede Variante enthält ihre eigene `AGENTS.md` und Anleitung.

```text
agentic-harness-v5/
├── .gitignore
├── README.md
├── agentic-harness/          vollständige Variante (Basis v5.17)
│   ├── AGENTS.md
│   ├── README.md
│   ├── harness/             Core, Init, Verification, Vorlagen und Anleitung
│   ├── docs/, project/, ideas/, specs/
│   └── profiles/, tools/
└── agentic-harness-lite/     schlanke Variante
    ├── AGENTS.md
    ├── README.md
    ├── .agents/skills/       gemeinsame Skill-Quelle
    ├── .claude/skills/       relative Links auf dieselben Skills
    └── docs/, ideas/, specs/
```

## Welche Variante?

| Variante | Geeignet, wenn … | Anleitung |
|---|---|---|
| Vollständig | du den ausführlicheren Core, getrennte Projekt-Docs, Ideas als Änderungsakten, Bereichs-Specs und Profil-Werkzeuge verwenden möchtest | [agentic-harness/README.md](agentic-harness/README.md), Details: [harness/README.md](agentic-harness/harness/README.md) |
| Lite | du wenige dauerhaft geladene Regeln, bedarfsgeladene Skills und Docs sowie einzelne prüfbare Specs bevorzugst | [agentic-harness-lite/README.md](agentic-harness-lite/README.md) |

Beide klären Projekt, Stack und Prüfungen im Init und verlangen aktuelle Nachweise vor dem Abschluss. Ihre Abläufe und Statusregeln sind bewusst nicht vollständig identisch; die Varianten werden nicht miteinander vermischt.

## In ein neues Projekt kopieren

Kopiere den **Inhalt des gewählten Variantenordners** in ein leeres Projekt-Root, einschließlich versteckter Dateien und Verzeichnislinks. Nicht den gesamten Repository-Root und nicht nur die sichtbaren Dateien kopieren.

```sh
# Aus dem Root dieses Repositories; /pfad/zum/neuen-projekt muss leer sein.
mkdir -p /pfad/zum/neuen-projekt
cp -R agentic-harness-lite/. /pfad/zum/neuen-projekt/
# Alternativ vollständig: cp -R agentic-harness/. /pfad/zum/neuen-projekt/
```

Danach liegt `/pfad/zum/neuen-projekt/AGENTS.md` direkt im Projekt-Root. Öffne dieses Projekt mit dem Agenten und beschreibe, was entstehen soll. Alle internen Pfade gelten ab diesem Root. Bei Lite müssen die Links unter `.claude/skills/` erhalten bleiben; die Skill-Freigabe für Pi steht in der Lite-Anleitung.

Die Variantenordner sind unbefüllte Vorlagen. Bereits ausgefüllte Produktprojekte nicht roh kopieren: bei der vollständigen Variante den Export verwenden; bei Lite Projektabschnitt, konkrete Ideen/Specs, Projekt-Docs und Produktinhalte gemäß deren Anleitung zurücksetzen. Harness-Prüfnotizen sind keine Produktfakten.

## Vollständige Variante exportieren

```sh
sh agentic-harness/tools/export-harness.sh /pfad/zum/leeren-projekt
```

Der Export funktioniert auch aus einem anderen Arbeitsverzeichnis, kopiert nur diese Variante und setzt ihre Projektteile zurück. Er committet und pusht nichts. Für eine Änderung bestehender Vorlagen zuerst Umfang und Diff prüfen.

## Den Harness selbst pflegen

Im Repository-Root gibt es bewusst keine gemeinsame `AGENTS.md`. Öffne für Harness-Arbeit den betroffenen Variantenordner oder lade dessen `AGENTS.md` ausdrücklich. Eine Änderung der Sammlung oder ihrer Paketstruktur wird durch den konkreten Auftrag gesteuert; sie ist kein Produkt-Init. Verweise, Export und Kopierbarkeit beider Varianten nach Strukturänderungen prüfen.
