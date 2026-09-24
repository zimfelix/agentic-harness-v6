# Project Init – neues Projekt gezielt initialisieren

> **Zuständigkeit:** Einmaliger Klär- und Einrichtungsablauf vor der ersten Produktimplementierung; keine ausgedachten Produktfakten.

1. Kläre Nutzer, Hauptablauf, Nicht-Ziele, Daten, Integrationen, Risiken, Betriebsumgebung und Freigabegrenzen. Bei vorhandenem Code prüfe Einstieg, Datenfluss und vorhandene Tests. Markiere Unbekanntes als offen.
2. Befülle `harness/project.md` mit bestätigten Grenzen, tatsächlich benutzten Werkzeugen, Start-/Prüfbefehlen und dem Gate-Einstieg. Entferne `Pending Project Init` erst, wenn der erste Umsetzungsschritt verantwortbar ist.
3. Ergänze `README.md` mit dem konkreten Produkt. Pflege `docs/architecture.md`, `docs/code.md` und `docs/testing.md` nur mit Aussagen, die für dieses Projekt bereits gelten; nicht relevante Dateien bleiben kurz oder entfallen im Zielprojekt.
4. Richte einen **echten** Prüf-Einstieg für das Projekt ein und prüfe, dass er im Erfolgs- und Fehlerfall sinnvoll reagiert. Ein fehlender Befehl, eine leere Testsuite oder das Gate des V2-Vergleichsordners gelten nicht als V3-Nachweis. Solange kein brauchbares Gate existiert, darf keine Spec `Implemented` werden.
5. Kläre neues Nutzerverhalten in `specs/` anhand von `harness/templates/spec.md`. Verwende `ideas/` für offene Vorhaben nur bei Bedarf. Aktualisiere die Verweise in der projektbezogenen `AGENTS.md`, ohne Arbeitsregeln dort zu duplizieren.
