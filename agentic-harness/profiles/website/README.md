# Profil Website – Zubehör

Dieser Ordner gehört zum Profil [`../website.md`](../website.md). Das Profil enthält die **Regeln** (Text, den der Agent liest), dieser Ordner die **Werkzeuge** (Programme, die der Agent ausführt). Damit wird jedes Website-Projekt ab der ersten Seite gleich gut geprüft. Beides wandert beim Export in die Vorlage und bleibt in jedem Projekt unverändert.

```text
profiles/
├─ website.md                ← Regeln: Teil A Pflicht, Teil B Stil-Defaults, Teil C Baukasten
└─ website/                  ← dieser Ordner
   ├─ README.md              ← diese Übersicht
   ├─ device-preview.html    ← Geräte-Vorschau: Website als Handy, Tablet, Laptop, Monitor nebeneinander
   └─ webtools/              ← Prüf- und Vorschau-Werkzeuge (Node.js + Brave/Chrome), siehe „Die Werkzeuge“ unten
```

## Regeln, Werkzeuge und der Verification Loop

Die Werkzeuge sind **Teil des Verification Loop**: Der Harness legt den Ablauf fest (`harness/verification/gate.md`, `implementation.md`, `fail.md`), die Werkzeuge liefern im Schritt „Prüfen“ die Messwerte.

```text
website.md: „Felder mindestens 16 px“        ← Regel (wie ein Verkehrsschild)
      │ Agent liest sie und baut die Seite
      ▼
   bauen ──▶ PRÜFEN ──▶ erfüllt? ──ja──▶ übergeben
               ▲  │          │
               │  │         nein ──▶ korrigieren (fail.md)
               │  │                        │
               │  └─ Werkzeuge messen:     │
               │     pruefen.mjs: „/kontakt/ Feld 15 px ❌“   ← Messgerät (wie ein Blitzer)
               │     npm test, Screenshots, Geräte-Vorschau
               └───────────────────────────┘
```

Ohne Werkzeuge läuft die Schleife nach Augenmaß; mit ihnen entscheiden Messwerte, ob eine weitere Runde nötig ist.

## Die Werkzeuge

Allgemeine Prüf- und Vorschau-Werkzeuge für statische Websites. Sie brauchen Node.js 22 oder neuer und Brave oder Chrome, aber keine npm-Pakete, und werden immer **aus dem Projektordner** aufgerufen, meist über npm-Skripte.

```text
                         konfig.mjs  ◀── website.config.mjs (Projekt)
                             │ Standardwerte + Abweichungen
          ┌──────────────────┼───────────────────────────────┐
          ▼                  ▼                               ▼
     browser.mjs        serve.mjs ──▶ Vorschau :Port      css.mjs
     Brave fernsteuern   │  baut bei Änderungen neu          CSS lesen
          │              │  /_geraete/ ◀── device-preview.html │
          │              ├── device-preview.mjs  öffnet die Geräte-Vorschau
          │              └── vorschau-dauerhaft.sh  macht die Vorschau zum Dauer-Dienst (macOS)
          │                                                  │
          ├──▶ pruefen.mjs         Pflichtregeln Teil A messen    │
          ├──▶ screens.mjs         Screenshots vorher/nachher     │
          ├──▶ style-snapshot.mjs  Style-Fingerabdruck vorher/nachher
          └──▶ unused-css.mjs ◀────────────────────────────────────┘
                   └──▶ css-audit.mjs   ungenutzte CSS-Regeln finden / entfernen
```

| Datei in `webtools/` | Aufgabe | Typischer Aufruf |
|---|---|---|
| `konfig.mjs` | Standardwerte (Pfade, Build-Befehl, Port, Prüfbreiten, interne Ordner) + Abweichungen aus `website.config.mjs` des Projekts; Dateitypen für Vorschau und Prüfserver; mit `ORDNER=<ordner>` statischer Modus ohne Build und ohne Konfiguration (z. B. Entwürfe beim Erkunden) | – |
| `browser.mjs` | startet Brave oder Chrome unsichtbar und steuert ihn; statischer Server für den Build-Ordner; Liste aller Seiten | Import in Tests und Werkzeugen |
| `pruefen.mjs` | misst auf allen Seiten und Prüfbreiten: Überlauf, Schriften, Skriptfehler, fehlende Dateien, Felder unter 16 px, Bedienelemente unter 24 px, Kontrast | `npm run pruefen`; Entwürfe: `ORDNER=entwuerfe node <webtools>/pruefen.mjs` |
| `serve.mjs` | lokale Vorschau, baut bei Änderungen neu, eigene 404-Seite, Geräte-Vorschau unter `/_geraete/` | `npm run dev`; Entwürfe ohne Build: `ORDNER=entwuerfe PORT=… node <webtools>/serve.mjs` |
| `vorschau-dauerhaft.sh` | richtet die Vorschau als macOS-Dienst ein (startet beim Anmelden und nach Abstürzen neu) | `npm run vorschau` (`-- status`, `-- entfernen`) |
| `device-preview.mjs` | öffnet die Geräte-Vorschau in Brave, startet die Vorschau bei Bedarf | `npm run geraete` |
| `screens.mjs` | ganzseitige Screenshots aller Seiten; Vergleich zweier Aufnahmen | `npm run screens -- <ordner>` |
| `style-snapshot.mjs` | berechnete Styles aller Elemente je Seite, Breite und Zustand; Vergleich | `npm run styles -- <datei.json>` |
| `css.mjs` | kleiner CSS-Leser (Regeln, Kommentare, `@media`) samt Textposition | von `unused-css.mjs` genutzt |
| `unused-css.mjs` | findet Selektoren, die auf keiner gebauten Seite greifen | Import in Tests |
| `css-audit.mjs` | listet oder entfernt (`--fix`) ungenutzte Selektoren in den Style-Quellen | `npm run audit:css` |

Projektfakten (Namen, Pfade, Farben) gehören nie in diese Dateien, sondern in `website.config.mjs` des Projekts.

## Wie ein Projekt das Zubehör nutzt

```text
Projekt
├─ website.config.mjs   ── nennt nur Abweichungen (Name, Pfade, Build-Befehl, Port …) ──┐
├─ package.json         ── npm-Skripte rufen agentic-harness/profiles/website/webtools/… │
├─ tests/               ── importieren browser.mjs aus webtools/                         │
└─ scripts/             ── projekteigene Programme (siehe unten)                         │
                                                                                          ▼
                                  webtools/konfig.mjs: Standardwerte + Projektabweichungen
```

## Der Ordner `scripts/` im Projekt

```text
Wann?   beim Project Init oder spätestens mit der ersten Seite, sobald die Dateistruktur feststeht
Was?    nur projekteigene Programme, die von Aufbau oder Marke DIESES Projekts abhängen:
          ├─ build.mjs        baut die Website in den Ausgabeordner (Standard: dist/)
          ├─ favicons.mjs     erzeugt Favicons aus dem eigenen Zeichen und den eigenen Farben
          └─ lib/             Hilfen dafür, z. B. die Favicon-Vorlage
Nicht?  Kopien der Webtools; Vorschau, Messen und Vergleichen kommen immer aus webtools/
Wo?     Regel: ../website.md Teil C §9 (Dateistruktur) · Überblick: agentic-harness/README.md,
        Abschnitt „Ausführbare Dateien im Harness“ · gewählte Struktur des Projekts:
        agentic-harness/docs/architecture.md (Projektteil)
```

Wird der Build anders gestartet oder liegt die Ausgabe woanders, steht das in `website.config.mjs`. Dann finden die Webtools beides.

## Pflege

Wird in diesem Ordner oder in `webtools/` eine Datei ergänzt, umbenannt oder entfernt, diese README im selben Schritt anpassen. Sie ist die einzige Beschreibung des Zubehörs. Neue Rollen zusätzlich in `agentic-harness/harness-map.md` eintragen.
