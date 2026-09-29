# Design – Gestaltungsregeln und Nachweis

> - **Typ:** Projektdoku
> - **Status:** Noch offen (Project Init).
> - **Zuständigkeit:** Verbindliche Gestaltungsregeln einer sichtbaren Oberfläche festhalten: Farbrollen, Schrift, Größen, Bausteine, Zustände und den Nachweis im Zielmedium.
> - **Gilt bei:** Jeder sichtbaren Änderung an Layout, Farbe, Schrift, Abständen, Bausteinen oder Interaktion sowie beim Anlegen neuer Ansichten, Seiten oder Abschnitte. Nur für Projekte mit Benutzeroberfläche (Website, Web-/Mobile-App, Desktop); sonst im Projektteil als „nicht relevant“ markiert.
> - **Ladebeziehungen:** Vorher `agentic-harness/harness/project.md`; bei gewähltem Profil zuerst dessen Regeln (z. B. `agentic-harness/profiles/website.md`). Bei Bausteinen und Dateistruktur `agentic-harness/docs/architecture.md`; bei Code-/Stilkonventionen `agentic-harness/docs/code.md`; für Testauswahl `agentic-harness/docs/testing.md`. Vor Abschluss `agentic-harness/harness/verification/gate.md` (kurzer Weg für Oberflächen-Iterationen).
> - **Nicht zuständig:** Inhaltliches Soll und Akzeptanzkriterien (Specs), Seitentexte, Stack-Entscheidungen oder Testbefehle.

## Universeller Rahmen

Nennt das Projektprofil ein Profil (z. B. Website), gelten dessen Standardregeln; diese Datei hält die **Projektwerte** und bewusste Abweichungen davon fest.

Gestaltung driftet, wenn sie nur im Code steht: Schriften werden nicht geladen, Überschriften bekommen je Ansicht eigene Größen, gleiche Muster entstehen mehrfach. Diese Datei hält deshalb **eine Quelle pro Gestaltungsentscheidung** fest. Der Code setzt sie um, Tests und Messung im Zielmedium belegen sie.

### Was hier festgehalten wird

1. **Farbrollen statt Einzelfarben:** Hintergrund, Text, gedämpfter Text, Linie, kleiner Akzent, großer Akzent, Flächen hell/dunkel, Text auf dunklem Grund. Jede Rolle hat genau einen Wert bzw. ein Token.
2. **Schrift und Größenskala:** Schriftfamilie mit Quelle und Lizenz, tatsächlich eingebundene Dateien, Stufen für Seitenaufmacher (H1), Abschnittsüberschrift (H2), Zwischenüberschrift, Fließtext, Kennzeichnung. Ausnahmen ausdrücklich benennen.
3. **Bausteine:** Welche wiederverwendbaren Muster gibt es (Header, Footer, Hero, Abschnittskopf, Karten, Schritte, FAQ, Kontaktblock, Buttons, Links)? Welche Varianten sind erlaubt? Neue Seiten werden aus diesen Bausteinen zusammengesetzt.
4. **Zustände und Interaktion:** Hover, Fokus, gedrückt, geöffnet; Animationen und ihre Dauer. Gleiche Rolle heißt gleiches Verhalten.
5. **Inhaltsnahe Formregeln:** Hervorhebung in Überschriften, Kennzeichnungen, Großschreibung (per Stil, nicht im Text), Pfeile und Linktexte, Satzzeichen am Ende von Überschriften.
6. **Nachweis:** was je Gestaltungsregel gemessen oder visuell beurteilt wird; Prüfgrößen und Werkzeug stehen in `agentic-harness/docs/testing.md`.
7. **Gewählte Profil-Vorschläge:** Welche optionalen Bausteine aus dem Profil übernommen, angepasst oder bewusst weggelassen wurden.

### Regeln für die Arbeit

- Neue Werte zuerst als Rolle/Token hier und im Code anlegen, dann verwenden. Keine neuen Einzelfarben oder Einzelgrößen für eine bestehende Rolle.
- Hier stehen Regeln, keine Einzelwerte je Stelle: Ein Wert für eine einzelne Stelle (z. B. ein Button-Abstand) steht nur im Code als Token. Eine festgelegte Ausrichtung sichert ein gemessener Test; hier steht dann nur die Regel in einer Zeile mit Verweis auf den Test.
- Abweichungen von einer Regel nur nach Entscheidung des Auftraggebers; die Entscheidung ersetzt die alte Regel hier (kein zweiter Absatz daneben).
- Bei Oberflächen-Iterationen nur das Genannte ändern; weitere Auffälligkeiten als Liste berichten (`agentic-harness/harness/core.md`).
- **Nachweis im Zielmedium:** Aussehen ist aus Quelltext nicht ableitbar. Nach sichtbaren Änderungen im Zielmedium (Browser, Emulator, Gerät) messen oder den geänderten Bereich per Screenshot prüfen, bei den Prüfgrößen aus `agentic-harness/docs/testing.md`. Bei Websites z. B. berechnete Stile, Positionen, geladene Schriften und horizontalen Überlauf. Das Werkzeug dafür einmal im Projekt einrichten und in `agentic-harness/docs/testing.md` nennen, statt es je Sitzung neu zu schreiben.
- **Konsistenz-Audit** vor größeren Übergaben: wiederkehrende Rahmen (z. B. Header, Footer, Navigation) überall identisch, Überschriften entsprechen der Skala, wiederkehrende Elemente folgen den Bausteinen, Schriften tatsächlich geladen. Ein Profil kann die Liste konkretisieren.

## Projektspezifische Befüllung

Noch offen (Project Init).
