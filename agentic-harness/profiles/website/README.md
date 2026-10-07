# Website-Profil: Zubehör und Werkzeuge

Regeln und Leseauslöser: [profile.md](profile.md). Optionale Gestaltung/Baukasten/Nachweise unter `references/`; Geräte-Vorschau und Inspiration unter `assets/`. Alles gehört zu diesem einen Profil, keine zweite Regelquelle.

```text
profiles/website/
├── profile.md
├── references/
├── tools/
└── assets/
    ├── device-preview.html
    └── inspiration/
```

## Webtools

Node.js 22+ und ein Browser nötig; keine npm-Pakete. Aus dem Produkt-Root aufrufen, meist als npm-Script. Einstellungen in `website.config.mjs`, nicht in den Profilwerkzeugen ändern. Bei Pi-Browserarbeit Brave verwenden und den tatsächlichen Browser vor Aktionen prüfen.

| Datei unter `tools/` | Aufgabe |
|---|---|
| `konfig.mjs` | Standardwerte + Projektabweichungen, Dateitypen; `ORDNER=…` für statische Entwürfe ohne Build |
| `browser.mjs` | Browsersteuerung, Prüfserver und Seitenliste; Import in Tests |
| `pruefen.mjs` | Überlauf, Schriften, Skript-/Dateifehler, Felder, Tippflächen, Kontrast |
| `serve.mjs` | Vorschau mit Neubau, eigene 404, Geräte-Vorschau unter `/_geraete/` |
| `vorschau-dauerhaft.sh` | Optionaler macOS-Dienst; Einrichtung, `status`, `entfernen` |
| `device-preview.mjs` | Geräte-Vorschau öffnen, Server bei Bedarf starten |
| `screens.mjs` | Screenshots aufnehmen/vergleichen |
| `style-snapshot.mjs` | Berechnete Styles/Zustände aufnehmen/vergleichen |
| `css.mjs`, `unused-css.mjs`, `css-audit.mjs` | CSS lesen, ungenutzte Selektoren prüfen; Entfernen nur auf Auftrag |

```sh
# Gebautes Produkt prüfen (vorher Projekt-Build ausführen):
node profiles/website/tools/pruefen.mjs
# Interner statischer Entwurf ohne Build:
ORDNER=entwuerfe node profiles/website/tools/serve.mjs
```

Vorschau und Prüfungen nutzen Projektpfade aus `website.config.mjs`. `serve.mjs` lädt die Geräte-Vorschau aus `assets/device-preview.html`, nie aus einer Kopie im Produkt-Build. Die Vorschau ist standardmäßig lokal; LAN-Freigabe nur ausdrücklich.

Eigene Produkt-Scripts (Build, Favicons) unter `scripts/`; Webtools nicht dorthin kopieren. Gewählte Struktur im Projektteil von `docs/architecture.md`, Prüfgrößen/Umgebung in `docs/testing.md`, Befehle im Projektprofil. Nachweise und Livegang: [references/nachweis.md](references/nachweis.md).

Bei Änderungen in diesem Profil Einstieg, Referenzen, diese Übersicht und Export abgleichen (`document-contract.md`).
