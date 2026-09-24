# SXXX – Kurzer Titel

> **Verantwortung:** Diese Vorlage beschreibt eine kleine, beauftragte Verhaltensänderung als prüfbare Story. Sie trennt Ziel, Umfang, Akzeptanzkriterien und Nachweise von technischen Lösungsdetails.

## Meta

- **State:** Modified

## User Story

Als **[Nutzerrolle]** möchte ich **[Funktion]**, damit **[Nutzen]**.

## Beschreibung

Ziel, fachlicher Umfang und wichtiger Ablauf in wenigen Sätzen. Keine technische Lösung und kein Prompt-Verlauf.

## Akzeptanzkriterien

- **AK1:** Ein atomar beobachtbares Verhalten mit eindeutigem Pass/Fail.
- **AK2:** Ein weiterer prüfbarer Fall (nur wenn benötigt).

## Nicht im Umfang

- Bewusst ausgeschlossene Funktion oder spätere Idee.

## Nachweise

Automatisierte Tests tragen einen Marker wie `SXXX-AK1`; keine Testliste doppelt führen. Nur für begründete Ausnahmen verwenden und ungenutzte Zeilen löschen:

- **AKX [Statisch]:** `PASS` — Befehl und beobachtetes Ergebnis.
- **AKY [Manuell]:** `PASS` — Ablauf und beobachtetes Ergebnis.
- **Quality Gate:** projektspezifischer Befehl und Ergebnis.

`State: Implemented` erst nach Nachweis aller AK und bestandenem Quality Gate; sonst `Modified`.
