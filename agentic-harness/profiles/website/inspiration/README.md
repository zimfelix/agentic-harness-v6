# Inspiration – gelungene Website-Entwürfe

> - **Typ:** Referenz
> - **Status:** Fünf Einträge (Oberfranken, 2026): drei ganze Entwürfe, zwei Abschnitte.
> - **Zuständigkeit:** Vom Auftraggeber als gelungen bewertete Entwürfe mit Wirkung und tragenden Elementen festhalten, damit neue Entwürfe an diesem Niveau ansetzen.
> - **Gilt bei:** Erkunden von Website-Entwürfen (`agentic-harness/harness/init.md`, Abschnitt 0, E1–E3), neuen Gestaltungsrichtungen und auf Auftrag „in die Sammlung aufnehmen“.
> - **Ladebeziehungen:** Über `agentic-harness/harness/init.md` (Abschnitt 0) und `agentic-harness/profiles/website.md`. Bilder liegen je Eintrag im gleichnamigen Ordner.
> - **Nicht zuständig:** Regeln oder Projektwerte festlegen; die Gestaltung eines Projekts steht in dessen `agentic-harness/docs/design.md`.

## Wie die Sammlung genutzt wird

```text
Erkunden ──▶ Steckbriefe lesen, 1–2 Bilder ansehen ──▶ Niveau und Mittel als Maßstab
                                                     (Schrift, Inhaltsdichte, Grafik)
                                                              │
                     eigene Leitidee je Entwurf ◀─────────────┘  nicht nachbauen
                              │
Auftraggeber findet einen Entwurf gelungen ──▶ Eintrag hier ergänzen
```

- **Maßstab, keine Vorlage:** Übernommen werden Qualität und Mittel (z. B. eigene Schriftpaarung, echte Inhaltsdichte, eine erklärende Grafik), nicht Texte, Logos oder ganze Layouts.
- **Nur Bewertetes:** Ein Eintrag entsteht nur, wenn der Auftraggeber einen Entwurf als gelungen bewertet; seine Worte stehen unter „Wirkung“.
- **Ganzer Entwurf oder einzelner Abschnitt:** Gefällt die Seite als Ganzes, `start.jpg` (Desktop 1440 px, erster Bildschirm), `ganz.jpg` (ganze Seite) und `handy.jpg` (390 px). Gefällt nur ein Teil, ein Ausschnitt `abschnitt-<name>.jpg`; das Lob gehört an den Abschnitt, nicht an die ganze Seite. Lob für einen Teil eines bestehenden Eintrags wird dort als Abschnitt ergänzt.
- **Bilder sind die Quelle, Code ist Zusatz:** Bilder reisen mit der Vorlage und sind ohne laufende Vorschau lesbar. Repo und Datei unter „Quelle“ helfen nur, wenn das Repo erreichbar ist; lokale Adressen (`127.0.0.1:…`) nie als einzige Quelle, sie gelten nur auf einem Rechner und solange die Vorschau läuft.
- **Aufnahme:** mit `browser.mjs` aus `../webtools/` oder als Bildschirmausschnitt, als JPEG, damit die Sammlung klein bleibt (Ziel unter 1 MB je Eintrag).
- **Kurz halten:** ein Steckbrief je Eintrag, höchstens etwa zehn Einträge; schwächere werden ersetzt, nicht angehäuft.

## Steckbrief (Vorlage)

```markdown
### <name> – <Leitidee in drei Wörtern>
- **Herkunft:** Projekt, Datum, Art (Landingpage, Firmenseite …)
- **Wirkung:** wie der Auftraggeber sie beschreibt (z. B. lebendig, einladend)
- **Schrift:** Familien und Rolle (mit Lizenz)
- **Farben:** Grund, Text, Akzente in Worten, ggf. Hex
- **Tragende Elemente:** was die Wirkung ausmacht (Karte, Anordnung, Grafik …)
- **Abschnitte:** `abschnitt-<name>.jpg` – Wirkung in Worten des Auftraggebers, was sie trägt
- **Quelle:** Repo und Datei (falls erreichbar)
- **Bilder:** <ordner>/start.jpg · ganz.jpg · handy.jpg
```

## Einträge

Alle drei entstanden am 03.10.2026 als freie Landingpage-Entwürfe für eine regionale Plattform (Studienprojekt „Plattform Oberfranken“; Quelle: Repo `trendmanagement-oberfranken`, `entwuerfe/a-magazin.html`, `b-dialog.html`, `c-kompass.html`); Inhalte sind erfundene Beispiele. **Wirkung (Auftraggeber):** „smooth, stimmig, herzlich, einladend; Farben besser, Grafiken klar angeordnet, kreativ“ – deutlich stärker als ein späterer Vergleichslauf mit Systemschriften und weniger Inhalt.

### oberfranken-magazin – Redaktionelles Magazin
- **Schrift:** Fraunces (Serifen, Überschriften; Hervorhebung **kursiv in Akzentfarbe**) + Inter (Text); beide SIL OFL, lokal eingebunden.
- **Farben:** warmes Papier `#F6F1E7`, Tinte `#1D1A16`, Waldgrün `#22443A`, Bernstein `#E9A93A` als Licht-Akzent.
- **Tragende Elemente:** große Serifen-Headline mit kursivem Schluss; Karte „Gerade veröffentlicht“ neben dem Hero; gezeichnete Hügel- und Burgsilhouette als Übergang; Kartenraster mit Linien-Grafiken je Thema; Wochenkalender als Liste; dunkler Redaktionsblock; Ablauf in fünf nummerierten Schritten.
- **Bilder:** `oberfranken-magazin/start.jpg` · `ganz.jpg` · `handy.jpg`

### oberfranken-dialog – Chat als Startseite
- **Schrift:** Inter durchgehend, große fette Headline.
- **Farben:** dunkelgrüne Seitenleiste `#13201A`, heller Grund `#F7F6F2`, weiße Karten, Bernstein-Punkte als Kennung.
- **Tragende Elemente:** Aufbau wie ein modernes KI-Chatfenster (Seitenleiste mit Redaktionswissen und Regionen, zentrales Eingabefeld); Profil- und Ortswahl oben rechts; Vorschlagsfragen als Kacheln; „Gerade in deiner Region“ als Karten mit Thema, Ort und Zeit; Hinweis zur Quelle direkt unter dem Eingabefeld.
- **Bilder:** `oberfranken-dialog/start.jpg` · `ganz.jpg` · `handy.jpg`

### oberfranken-kompass – Dashboard mit Karte
- **Schrift:** Bricolage Grotesque (Headline, eigenwillig) + Inter (Text); beide SIL OFL.
- **Farben:** warmes Grau `#F1EFE9`, weiße Kacheln, Nachtblau `#0E1A2B` für die Karte, gelbe Leuchtpunkte, Grün für Redaktion.
- **Tragende Elemente:** persönliche Begrüßung mit Datum, Headline mit grau abgesetztem Mittelteil; Profil als Segment-Umschalter; **Bühnenkarte** (Orte als Sterne, Helligkeit = Zahl der Meldungen); Kachelraster mit „Als Nächstes für dich“, Redaktion und „Region des Tages“ mit Landschaftsgrafik; Sieben-Tage-Spalten mit farbiger Themenkante.
- **Bilder:** `oberfranken-kompass/start.jpg` · `ganz.jpg` · `handy.jpg`

### oberfranken-buehne – Erklärblock auf dunkler Fläche (Abschnitt)
- **Herkunft:** Blindtest 2, Startseite nach Entwurf B „Bühne“ (Repo `oberfranken-harnesstest-2`, `src/pages/startseite.mjs`), 03.10.2026.
- **Wirkung (Auftraggeber):** Anordnung „ziemlich clean“.
- **Abschnitte:** `abschnitt-hinter-den-kulissen.jpg` – zwei Spalten auf Dunkelgrün: links eine große Kennzahl als Satz („25 % Redaktion · 75 % KI“) mit schmalem Balken und kurzer Erklärung, rechts fünf nummerierte Schritte mit Bernstein-Ziffern, fett gesetztem Anfang und feinen Trennlinien; kleine Versal-Kennung über einer Serifen-Überschrift.

### oberfranken-frag – Chat-Hero (Abschnitt)
- **Herkunft:** Blindtest 1, Entwurf A (Repo `oberfranken-harnesstest`, `src/pages/entwurf-a.mjs`), 03.10.2026.
- **Wirkung (Auftraggeber):** Anordnung „ziemlich clean“.
- **Abschnitte:** `abschnitt-hero.jpg` – dunkler Verlauf, Headline mit grau abgesetztem zweitem Wort („Frag Oberfranken.“), weißes Eingabefeld mit rotem Knopf, Profil als Pillen-Auswahl, Beispielfragen als Pillen mit feinen Icons, darunter ein Beispielverlauf.
