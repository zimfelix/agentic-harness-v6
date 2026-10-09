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

Node.js 22+ und Brave nötig; keine npm-Pakete. `BRAVE_PATH` setzt einen abweichenden Brave-Pfad; `CHROME_PATH` wird nur als alter Variablenname akzeptiert, nicht für Chrome. Kein stiller Browser-Fallback. Aus dem Produkt-Root aufrufen, meist als npm-Script. Einstellungen in `website.config.mjs`, nicht in den Profilwerkzeugen ändern. Bei Pi-Browserarbeit Brave verwenden und den tatsächlichen Browser vor Aktionen prüfen.

| Datei unter `tools/` | Aufgabe |
|---|---|
| `konfig.mjs` | Standardwerte + Projektabweichungen, Dateitypen; `ORDNER=…` für statische Entwürfe ohne Build |
| `browser.mjs` | Brave/CDP, Zustandswarten mit Zeitlimit, Prüfserver und nichtleere geprüfte Routenmenge |
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

Werkzeuge prüfen **statische** Buildrouten, keine vollständigen CRM-/SPA-/Auth-Abläufe. Dafür passende Tests gegen die laufende App wählen.

Vorschau und Prüfungen nutzen Projektpfade aus `website.config.mjs`. Optional `routen` als vollständige erwartete Liste, `breiten` als nichtleere Prüfgrößen und `bereit` als Layoutbereitschafts-Ausdruck deklarieren; `warteMs` begrenzt Zustands-/CDP-Warten. Nicht erfolgreiche Dokumentnavigation ist ein Fehler, kein Screenshot-/Style-Nachweis. Ohne `routen` werden Seiten entdeckt und der nötige Soll-Abgleich ausdrücklich ausgewiesen. Konfigurationsänderung erfordert Neustart.

Vergleiche prüfen beide Artefakt-/Zustandsmengen und lehnen leere Mengen ab. Aufnahmen brauchen einen leeren Screenshotordner (Dateinamen kodieren die Route); neue Baselines bewusst erzeugen. Stylefingerprints sind ein ergänzendes Indiz, kein vollständiger Verhaltens-/Pixelbeweis. Vorschau baut bei Start/Quelländerung, zählt den Stand nur nach Erfolg weiter und liefert bei Buildfehler HTTP 503 statt einen alten Stand als aktuell auszugeben. `/_geraete/stand` nennt Aktualität und Quellfingerprint; der Fingerprint deckt den beobachteten Quellordner, nicht alle externen Buildabhängigkeiten. `serve.mjs` lädt die Geräte-Vorschau aus `assets/device-preview.html`, nie aus einer Kopie im Produkt-Build. Die Vorschau ist standardmäßig lokal; LAN-Freigabe nur ausdrücklich.

Eigene Produkt-Scripts (Build, Favicons) unter `scripts/`; Webtools nicht dorthin kopieren. Gewählte Struktur im Projektteil von `docs/architecture.md`, Prüfgrößen/Umgebung in `docs/testing.md`, Befehle im Projektprofil. Nachweise und Livegang: [references/nachweis.md](references/nachweis.md).

Bei Änderungen in diesem Profil Einstieg, Referenzen, diese Übersicht und Export abgleichen (`document-contract.md`).
