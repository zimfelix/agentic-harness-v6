# Nachweis und Livegang

## Einrichtung und Prüfumfang

Bestehende Werkzeuge unter `profiles/website/tools/` verwenden; Übersicht/Setup: `profiles/website/README.md`. Keine Kopien ins Produkt. Abweichungen in `website.config.mjs`, Aufrufe als Projektbefehle registrieren. Passung zu Stack/Betrieb prüfen; alternativen gleichwertigen Nachweis begründen, keine blinde Werkzeugpflicht.

Prüfgrößen nach Ziel/Reifegrad in `docs/testing.md` festlegen (Ausgangspunkt 1440/390/320 px, Tablet um 800 px und großer Monitor nach Bedarf). Brave ist der Browser der mitgelieferten Werkzeuge. Ein Browser für frühe Prototypen genügt, vor Livegang vereinbarte Kompatibilitätsmatrix. Erwartete statische Routen in `website.config.mjs` unter `routen` deklarieren oder den dokumentierten Soll-Abgleich separat nachweisen; keine leere Prüfliste. SPA-/Auth-/dynamische Abläufe mit passenden Tests gegen die laufende App prüfen, nicht allein über statische `index.html`-Suche. Schriftladung technisch, Positionen/Überlauf messend, optische Wirkung per Screenshot prüfen. Touch wird nicht durch schmale Breite bewiesen; echter Smartphone-/Tastaturcheck vor entsprechendem Livegang. Animationen mit beiden Reduced-Motion-Werten.

## Vorschau

Lokale Vorschau mit Neubau bei Änderungen, Adresse/Befehl im Projektprofil. Vor UI-Übergabe prüfen, ob sie läuft. Dauer-Dienst auf macOS nur wenn gewünscht; LAN-Freigabe explizit, nicht Standard.

`profiles/website/assets/device-preview.html` unverändert aus dem Toolordner unter `/_geraete/` ausliefern, nie im Produktions-Build. Vorschau-Stand unter `/_geraete/stand` mit Seitenliste, Aktualität und neuem Stand nur nach erfolgreichem Build. HTTP 503/`aktuell:false` ist kein aktueller Nachweis. Beobachteter Quellordner wird auch auf Inhaltsänderungen/Löschen geprüft; andere Buildabhängigkeiten bei Änderungen gezielt neu prüfen. Geräte-Vorschau ersetzt keine Messung/echtes Gerät.

## Refactoring und Meilenstein

Verhaltensgleiches Markup/CSS-Refactoring: betroffene Seiten/Zustände vorher/nachher in Projekt-Prüfgrößen vergleichen. Bei Produkt/übergreifendem Umbau ganze relevante Seitenmatrix: Screenshots und berechnete Styles (`screens.mjs`, `style-snapshot.mjs`); bytegleicher Build kann den visuellen Vergleich ersetzen, nicht zusätzliche Verhaltenschecks. Beide Aufnahme-/Zustandsmengen müssen nichtleer und vollständig sein; neue Aufnahmen in leere Ordner, keine alten Dateien mitmischen. Routen-/Dateinamenänderungen erfordern eine bewusst erneuerte Baseline. Bereitschaft nach Load/Schriften/Layout, bei asynchroner App zusätzlich per `bereit`-Ausdruck; erfüllte Bereitschaft ist kein Nachweis vollständiger Interaktion.

Meilenstein-Audit: gemeinsamer Rahmen, geladene Schriften/Skala, kein Überlauf, Ausrichtungen, gewählte Stilregeln, Buttons/Links, erreichbare Routen/Anker, ungenutzte Selektoren. Nicht benötigte Checks begründet abwählen; Pflicht-/risikorelevante Checks nicht als „Prototyp“ wegdefinieren.

## Livegang

Jeder relevante Punkt erledigt oder als Blocker im Projektprofil:

1. Firmendaten und Rechtstexte geprüft/freigegeben.
2. Leistungen, Preise, Zusagen bestätigt, keine Platzhalter.
3. Kontaktwege/Formular tatsächlich zustellbar getestet.
4. Name/Zeichen auf Konflikte geprüft.
5. Referenzen/Stimmen echt und freigegeben, sonst entfernt.
6. Bild-/Schriftrechte belegt, Quellenliste aktuell.
7. Domain/Hosting/Weiterleitungen funktionieren, `noindex` bewusst gesetzt/entfernt; Analyse nur mit nötiger Einwilligung.
8. Vereinbarte Text-, Design-, Bedienungs-, Geräte-, Screenreader- und Rechtsabnahmen erfolgt.

Diese Checkliste ersetzt weder Rechtsberatung noch technische Abnahme.
