# Code – Stack und Konventionen

> - **Typ:** Projektdoku
> - **Status:** Noch offen (Project Init).
> - **Zuständigkeit:** Den gewählten Stack und geltende Regeln für Anwendungscode beschreiben.
> - **Gilt bei:** Project Init sowie Codeänderungen und Refactorings.
> - **Ladebeziehungen:** Vorher `harness/project.md` lesen. Bei Modulgrenzen `docs/architecture.md`; bei Gestaltungswerten (Farben, Schrift, Größen, Bausteine) `docs/design.md`; bei Testcode `docs/testing.md` zusätzlich lesen.
> - **Nicht zuständig:** Produktarchitektur, Gestaltungsregeln oder ausführbare Gate-Befehle duplizieren.

## Universeller Rahmen

Nur Regeln für den tatsächlich gewählten Stack festhalten. Kandidaten sind keine Konventionen; aktive Werkzeuge brauchen reale Einrichtung. Befehle und Ergebnisse gehören in das Projektprofil, Gestaltungswerte in `docs/design.md`.

Werte, die mehrfach vorkommen (z. B. Konfiguration, Grenzwerte, Texte, bei Oberflächen auch Gestaltungswerte), stehen an **einer** Stelle und werden referenziert. Eine geänderte Regel ersetzt die alte an ihrer Stelle, statt sie an anderer Stelle zu übersteuern (z. B. per spezifischerem CSS-Selektor oder Sonderfall-Abzweig); nicht mehr genutzter Code wird entfernt oder archiviert.

## Projektspezifische Befüllung

Noch offen (Project Init).
