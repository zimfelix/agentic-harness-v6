# Profil Website – Zubehör

Dieser Ordner gehört zum Profil [`../website.md`](../website.md). Das Profil enthält die **Regeln**, dieser Ordner die **fertigen Werkzeuge**, damit jedes Website-Projekt ab der ersten Seite gleich gut geprüft wird. Beides wandert beim Export in die Vorlage.

```text
profiles/
├─ website.md                ← Regeln: Teil A Pflicht, Teil B Stil-Defaults, Teil C Baukasten
└─ website/                  ← dieser Ordner
   ├─ README.md              ← diese Übersicht
   ├─ device-preview.html    ← Geräte-Vorschau: Website als Handy, Tablet, Laptop, Monitor nebeneinander
   └─ webtools/              ← Prüf- und Vorschau-Werkzeuge (Node.js + Brave/Chrome), siehe webtools/README.md
```

## Wie ein Projekt das Zubehör nutzt

```text
Projekt
├─ website.config.mjs   ── nennt nur Abweichungen (Name, Pfade, Build-Befehl, Port …) ──┐
├─ package.json         ── npm-Skripte rufen agentic-harness/profiles/website/webtools/… │
└─ tests/               ── importieren browser.mjs aus webtools/                         │
                                                                                          ▼
                                  webtools/konfig.mjs: Standardwerte + Projektabweichungen
```

Projektspezifisch bleiben im Projekt selbst: der Build (`scripts/build.mjs` o. Ä.), Favicons aus dem eigenen Zeichen und die inhaltlichen Tests.

## Pflege

Wird in diesem Ordner eine Datei ergänzt, umbenannt oder entfernt, diese README und [`webtools/README.md`](webtools/README.md) im selben Schritt anpassen; neue Rollen zusätzlich in `agentic-harness/harness-map.md` eintragen.
