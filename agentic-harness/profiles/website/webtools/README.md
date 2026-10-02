# Webtools – Werkzeuge des Website-Profils

Allgemeine Prüf- und Vorschau-Werkzeuge für statische Websites. Sie brauchen Node.js 22 oder neuer und Brave oder Chrome, aber keine npm-Pakete. Aufgerufen werden sie immer **aus dem Projektordner**, meist über npm-Skripte.

```text
                         konfig.mjs  ◀── website.config.mjs (Projekt)
                             │ Standardwerte + Abweichungen
          ┌──────────────────┼───────────────────────────────┐
          ▼                  ▼                               ▼
     browser.mjs        serve.mjs ──▶ Vorschau :Port      css.mjs
     Brave fernsteuern   │  baut bei Änderungen neu          CSS lesen
          │              │  /_geraete/ ◀── ../device-preview.html │
          │              ├── device-preview.mjs  öffnet die Geräte-Vorschau
          │              └── vorschau-dauerhaft.sh  macht die Vorschau zum Dauer-Dienst (macOS)
          │                                                  │
          ├──▶ pruefen.mjs         Pflichtregeln Teil A messen    │
          ├──▶ screens.mjs         Screenshots vorher/nachher     │
          ├──▶ style-snapshot.mjs  Style-Fingerabdruck vorher/nachher
          └──▶ unused-css.mjs ◀────────────────────────────────────┘
                   └──▶ css-audit.mjs   ungenutzte CSS-Regeln finden / entfernen
```

| Datei | Aufgabe | Typischer Aufruf |
|---|---|---|
| `konfig.mjs` | Standardwerte (Pfade, Build, Port, Prüfbreiten, interne Ordner), überschrieben von `website.config.mjs` des Projekts | – |
| `browser.mjs` | startet Brave/Chrome headless und steuert ihn; statischer Server für den Build-Ordner; Liste aller Seiten | Import in Tests und Werkzeugen |
| `pruefen.mjs` | misst auf allen Seiten und Prüfbreiten: Überlauf, Schriften, Skriptfehler, fehlende Dateien, Felder unter 16 px, Bedienelemente unter 24 px, Kontrast | `npm run pruefen` |
| `serve.mjs` | lokale Vorschau, baut bei Änderungen neu, eigene 404-Seite, Geräte-Vorschau unter `/_geraete/` | `npm run dev` |
| `vorschau-dauerhaft.sh` | richtet die Vorschau als macOS-Dienst ein (startet beim Anmelden und nach Abstürzen neu) | `npm run vorschau` (`-- status`, `-- entfernen`) |
| `device-preview.mjs` | öffnet die Geräte-Vorschau in Brave, startet die Vorschau bei Bedarf | `npm run geraete` |
| `screens.mjs` | ganzseitige Screenshots aller Seiten; Vergleich zweier Aufnahmen | `npm run screens -- <ordner>` |
| `style-snapshot.mjs` | berechnete Styles aller Elemente je Seite, Breite und Zustand; Vergleich | `npm run styles -- <datei.json>` |
| `css.mjs` | kleiner CSS-Leser (Regeln, Kommentare, `@media`) samt Textposition | von `unused-css.mjs` genutzt |
| `unused-css.mjs` | findet Selektoren, die auf keiner gebauten Seite greifen | Import in Tests |
| `css-audit.mjs` | listet oder entfernt (`--fix`) ungenutzte Selektoren in den Style-Quellen | `npm run audit:css` |

## Pflege

Neue, umbenannte oder entfernte Werkzeuge hier und in [`../README.md`](../README.md) nachtragen. Projektfakten (Namen, Pfade, Farben) gehören nie in diese Dateien, sondern in `website.config.mjs` des Projekts.
