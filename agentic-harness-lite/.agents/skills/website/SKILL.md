---
name: website
description: Bewährte Pflichtregeln, Nachweis-Methoden und Livegang-Checkliste für Websites (Rahmen, Schrift, Farben, Abstände, Touch/Hover, Bildschirmbreiten, Inhalte und Recht) samt Geräte-Vorschau, Stil-Defaults und Baukasten. Nutzen beim Init einer Website, bei sichtbaren Änderungen, neuen Seiten oder Abschnitten, Umbauten von Markup oder CSS, vor Übergaben und vor einer Veröffentlichung. In anderen Projekten mit Oberfläche nur auf ausdrücklichen Wunsch.
---

# Website

Die Regeln stammen aus einem ersten Website-Projekt (2026) und sollen an weiteren Websites bestätigt werden. Es gibt drei Verbindlichkeitsstufen:

- **Pflichtregeln** (diese Datei): Konsistenz, Bedienbarkeit, Rechte, Nachweis. Sie gelten auch dann, wenn ein ganz anderes Design nachgebaut wird.
- **Stil-Defaults** (`references/stil-defaults.md`): bewährte Gestaltung. Sie gelten als Voreinstellung und sind abwählbar; eine Abweichung steht in `docs/design.md`.
- **Baukasten** (`references/baukasten.md`): optionale Bausteine, Seitenaufbauten, Branchenhinweise und eine Dateistruktur. Lies ihn beim Init und bei neuen Seiten.

Projektwerte stehen in `docs/design.md`: Farbrollen, Schrift mit Lizenz, Größenskala, Bausteine, gewählte und abgewählte Defaults, Prüfgrößen und Messwerkzeug. Lege die Datei beim Init an und trage sie in `AGENTS.md` unter „Projekt-Docs“ mit dem Leseauslöser „bei jeder sichtbaren Änderung“ ein. Befehle wie Vorschau und Messung gehören in die Befehlstabelle von `AGENTS.md`. Die allgemeinen Regeln aus `AGENTS.md` (Iterationen, keine erfundenen Fakten, Fertig heißt) gelten weiter; hier stehen nur die Website-Ergänzungen.

## Init-Fragen

- **Seiten und Navigation:** Seitenumfang, Hauptnavigation, Pflichtseiten (Impressum, Datenschutz), Sprache und Ansprache (du/Sie)
- **Inhalte:** Leistungen, Preise, Referenzen; wer liefert, wer gibt frei?
- **Kontakt und Recht:** tatsächlich zustellbare Kontaktwege, Firmendaten, Formularversand ja oder nein
- **Bilder:** Herkunft und Nutzungsrechte; bis zur Klärung markierte Platzhalter
- **Betrieb:** Indexierung (Prototyp mit `noindex`?), Domain, Hosting, Analyse-Werkzeuge
- **Stil und Baukasten:** Welche Stil-Defaults gelten, welche Bausteine passen zu Branche und Kunde, wird die vorgeschlagene Dateistruktur übernommen?

## Pflichtregeln

### 1. Rahmen und Wiederholung

- Header, Footer und wiederkehrende Blöcke (z. B. der Kontaktblock) kommen aus **einer** Quelle. Sie sind überall, wo sie vorgesehen sind, identisch: Markup, Farben, Schriftstärken, Höhe.
- Gleichartige Abschnitte (Hero, Abschnittskopf, FAQ, Schritte, Karten) sind **ein** Baustein mit Varianten. Sie werden beim zweiten Vorkommen herausgezogen, weil die Gemeinsamkeit hier von vornherein feststeht.
- Ausgeliefert werden nur ausdrücklich vorgesehene Routen: alles, was über Navigation, Footer und Links erreichbar ist, plus bewusst vorgesehene direkte Einstiege (Landingpages, Fehlerseiten). Konzeptseiten bleiben intern und `noindex` und werden nach der Entscheidung archiviert oder gelöscht.

### 2. Schrift, Größen und Farben

- Jede eingebundene Schrift hat eine Lizenz und wird im Browser als **tatsächlich geladen** geprüft. Sonst fällt sie still auf eine Ersatzschrift zurück.
- Es gibt eine Größenskala für Überschriften und Text; Ausnahmen werden benannt.
- Farben sind Rollen (Hintergrund, Text, gedämpft, Linie, Akzente, helle und dunkle Fläche, Text auf dunkel). Für eine bestehende Rolle gibt es keine Einzelwerte. Texte bleiben auf ihrer Fläche lesbar (Kontrast).
- Großbuchstaben werden per CSS gesetzt, nicht im Text.

### 3. Ausrichtung und Abstände

- Festgelegte Ausrichtungen (z. B. zwei Spalten, die fluchten) werden bei den Prüfgrößen gemessen, nicht nur optisch geschätzt.
- Abstände folgen einer Skala (Tokens im Code). Ein Wert für eine einzelne Stelle steht nur im Code. In `docs/design.md` steht er nur, wenn er eine Regel für mehrere Stellen bildet.

### 4. Interaktion, Links und Bildschirmgrößen

- Buttons gleicher Rolle teilen Form, Größe und Hover-Verhalten.
- Linktexte sagen, was passiert: „Kontakt aufnehmen“ führt zur Kontaktseite, „E-Mail schreiben“ öffnet eine E-Mail. Die gleiche Aktion heißt überall gleich.
- Es gibt eine sichtbare Fokusmarkierung. Anker landen sichtbar unter einem angehefteten Header. Die Navigation ist per Tastatur und mobil bedienbar.
- **Breite und Bedienart getrennt behandeln:**
  - Die Breite in CSS-Pixeln bestimmt Anordnung, Spalten, Menüform und Schriftgrößen. Umbruchpunkte liegen dort, wo der Inhalt sie braucht, nicht bei Gerätenamen. Der Inhalt hat eine Höchstbreite; darüber wachsen nur die Ränder.
  - Die Bedienart (Touch, Maus, Tastatur) bestimmt nur das Verhalten und wird über `hover` und `pointer` abgefragt, nie aus der Breite abgeleitet. Es gibt Tablets mit Tastatur, Laptops mit Touchscreen und schmale Desktop-Fenster.
- **Nichts nur per Hover:** Jede Funktion ist auch per Tippen und per Tastatur erreichbar. Hover-Effekte stehen unter `@media (hover: hover)`, damit sie auf Touch-Geräten nach dem Tippen nicht hängen bleiben.
- **Tippflächen** sind mindestens 24 × 24 CSS-Pixel groß oder so weit voneinander entfernt, dass sich 24-px-Kreise um benachbarte Ziele nicht überschneiden (WCAG 2.2, Kriterium 2.5.8). Menüschalter, Buttons und Formularfelder sind möglichst 44 px hoch.
- **Formularfelder** haben mindestens 16 px Schrift, sonst zoomt Safari auf dem iPhone beim Antippen in die Seite.
- **Bewegung:** Animationen und Übergänge entfallen bei `prefers-reduced-motion: reduce`.

### 5. Inhalte und Recht

- Bilder nur mit geprüfter Nutzungsfreigabe; die Bildquellen-Seite spiegelt den tatsächlichen Stand.
- Rechtsseiten erfinden keine Pflichtangaben. Ein Prototyp ist `noindex` und als Entwurf gekennzeichnet.
- Kontaktwege sind echt und zustellbar oder als ungeprüft markiert. Ein Formular ohne Server sagt offen, was mit den Eingaben passiert.
- Vorbilder liefern Struktur, nicht Texte, Bilder oder Logos. Übernommener Wortlaut braucht eine ausdrückliche Freigabe.

### 6. Nachweis

Die Prüfgrößen legt das Projekt in `docs/design.md` fest; wie breit geprüft wird, richtet sich nach dem Arbeitsrahmen in `AGENTS.md` (bis MVP ein Browser). Bewährt sind 1440, 390 und 320 px, dazu mindestens eine Sichtprüfung bei einer Tablet-Breite um 800 px (dort greifen Umbruchpunkte oft knapp) und auf einem großen Monitor.

Wähle die Methode je Prüfziel:

- Schriftladung technisch prüfen.
- Positionen und Überlauf messen.
- Die optische Wirkung per Screenshot beurteilen.

Die Bedienart lässt sich nicht über die Bildschirmbreite prüfen: Touch einmal auf einem echten Smartphone testen, die Tastaturbedienung einmal ganz durchgehen. Animationen mit beiden Werten von `prefers-reduced-motion` prüfen; ein headless Browser übernimmt sonst still die Einstellung des Rechners.

- **Nach einer kleinen Iteration:** geänderten Bereich und betroffene gemeinsame Bausteine prüfen, kein Gesamtaudit.
- **Geräte-Vorschau, Umbau ohne sichtbare Änderung, Konsistenz-Audit, Livegang:** siehe `references/nachweis.md`. Lies die Datei bei der ersten Seite, bei Refactorings von Markup oder CSS, vor Meilenstein-Übergaben und vor jeder Veröffentlichung.

### 7. Gestaltungswünsche

- Berichte nach jeder Iteration kurz, was sichtbar anders ist, mit Messwert oder Screenshot.
- Sichere Gestaltungsentscheidungen des Auftraggebers so, dass sie nicht verloren gehen: als Token oder als gemessenen Test. In `docs/design.md` gehören sie nur, wenn sie eine übergreifende Regel oder eine bewusste Abweichung von den Defaults sind.
