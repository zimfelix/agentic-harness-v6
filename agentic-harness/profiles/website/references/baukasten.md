# Website-Baukasten (optional)

Übernehmen, anpassen oder weglassen; konkrete Inhalte entstehen pro Projekt. Keine Pflicht zu einer Agentur-Website oder einem bestimmten Stack.

## Rahmen und Seiten

- Header mit Marke, Navigation und Kontakt. Ab mehreren Leistungen optional getrennte Aktion für Leistungssprung und Aufklappmenü; per Touch/Tastatur bedienbar.
- Footer mit Kontakt, Leistungen/Zielgruppen, Unternehmen und Rechtlichem. Kontaktblock am Seitenende mit Haupt-/Zweitaktion.
- Eigene 404 im Seitenrahmen, Serverstatus 404; Assets ab Wurzel, damit tiefe Fehleradressen funktionieren.
- Favicons aus Zeichen/Farb-Tokens per Projekt-Script: SVG, ICO 16/32 px, Apple 180 px; Test gegen aktuelle Quelle, dunkle Tabs berücksichtigen.
- Startseite: Nutzen → Probleme → Angebot → Prozess → belegte Fallstudie/Stimmen → Werte/FAQ → Kontakt. Unbelegte Abschnitte weglassen oder nur im Prototyp klar markieren.
- Leistungsseite: Nutzen/Probleme → Leistungen/Ablauf → Wirkung → Kontakt. Ablaufseite mit Timeline/Ergebnissen/FAQ; Über uns mit Herkunft/Team/belegten Zusagen; Kontakt mit Wegen/Formular. Portfolio erst mit echten Freigaben.
- Hero: Text+Seitenleiste, Timeline, Bilder oder freigegebenes Vollbild. Ohne Fotos tragen Kontur-Icons, Schritte und Ablaufgrafiken; mit Fotos konsistente Formate/Farbtöne.
- Branchen als Gesprächsimpuls: Handwerk direkt/erdig (Erreichbarkeit/Ablauf); Gesundheit ruhig/hell (Vertrauen/Qualifikation); Fahrzeugbetrieb technisch/kontrastreich (Leistungen/Anfahrt). Kein vorgegebener Stil.

## Dateistruktur

Für statische Websites mit kleinem Build, sonst Framework-Konventionen nutzen. Entscheidung vor Code in `docs/architecture.md` festhalten:

| Ort | Zuständigkeit |
|---|---|
| `src/site.*` | Marke, Kontakte, Navigation, Indexierung |
| `src/content.*` | geteilte Texte als Daten |
| `src/pages/` | Seiten aus Bausteinen; Liste ausgelieferter Einstiege |
| `src/components/` | Rahmen/Abschnitte mit Parametern, keine Kundeninhalte |
| `src/styles/` | Tokens → Basis → Komponenten → Seitenausnahmen |
| `src/browser/` | Browserscripts |
| `scripts/` | eigener Build/Erzeugung, keine Webtools-Kopien |
| `tests/` | Verhalten, Rahmen, Routen, Inhalte |
| `website.config.mjs` | nur Abweichungen für bestehende Webtools |

Rahmen/Tokens entstehen mit erster Seite; bekannte wiederkehrende Abschnitte bei zweiter Seite gemeinsam nutzen. Tools unverändert unter `profiles/website/tools/` verwenden.

## Betrieb / Veröffentlichung

Optional für statisches Hosting: `main` → CI Build/Tests → nur grüner Build auf separaten Deploy-Branch → Hosting-Abruf nach Freigabe. Nur CI schreibt den Deploy-Branch; kein Zurückmergen. Bei buildendem Hoster dessen Konventionen übernehmen. Automatischer Webhook erst, wenn jeder grüne Main-Stand veröffentlichungsreif sein darf.

Privates Repository per read-only Deploy Key, einer je Repo. Secrets/Webhooks nie im Repo. Rückrollen mit geprüftem früherem Deploy-Stand. CSS/JS mit Inhalts-Hash einbinden und testen (Cache Busting), damit Browser keine gemischten Stände zeigen. Browser-Tests in CI mit expliziter Browserumgebung/Zeitlimit. Gewählten Betrieb in Architektur, Freigaben im Projektprofil festhalten.
