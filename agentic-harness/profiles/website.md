# Profil Website – bewährte Regeln für Websites

> - **Typ:** Designregel
> - **Status:** Aus einem ersten Website-Projekt (2026) abgeleitet; an weiteren Websites zu bestätigen.
> - **Zuständigkeit:** Projektübergreifende Pflichtregeln, abwählbare Stil-Defaults, optionale Bausteine, eine vorgeschlagene Dateistruktur und einen Veröffentlichungsweg für Aufbau, Gestaltung, Ausrichtung, Interaktion, Inhalte, Nachweis und Betrieb von Websites festhalten.
> - **Gilt bei:** Projekten, deren Projektprofil „Profil: Website“ nennt, und zwar bei Project Init, sichtbaren Änderungen, neuen Seiten oder Abschnitten, vor Übergaben und vor einer Veröffentlichung. Außerdem auf ausdrücklichen Auftrag in anderen Projekten mit Oberfläche (z. B. „mach es schöner, nutz dafür das Website-Profil“): Dann gelten nur die passenden Teile, und das Projekt hält in `agentic-harness/docs/design.md` fest, welche.
> - **Ladebeziehungen:** Vorher `agentic-harness/harness/project.md`. Gestalterische Projektwerte und bewusste Abweichungen stehen in `agentic-harness/docs/design.md`; Seiten, Routen, gewählte Dateistruktur, Betrieb und Archiv in `agentic-harness/docs/architecture.md`; Prüfgrößen, Methoden und Werkzeuge in `agentic-harness/docs/testing.md`. Vorlage der Geräte-Vorschau (§6): `agentic-harness/profiles/website/device-preview.html`.
> - **Nicht zuständig:** Konkrete Farben, Schriften, Texte oder Seiten eines Projekts festlegen. Projekte ohne dieses Profil und ohne ausdrücklichen Auftrag lesen es nicht.

## Wie das Profil wirkt

Das Profil ergänzt den universellen Harness für Website-Projekte. Es hat drei Teile:

- **Teil A – Pflichtregeln:** nur Konsistenz, Bedienbarkeit, Rechte und Nachweis, keine Stilvorgaben. Gilt in jedem Website-Projekt mit diesem Profil, auch wenn ein ganz anderes Design nachgebaut wird.
- **Teil B – Stil-Defaults:** bewährte Gestaltungsentscheidungen. Gelten als Voreinstellung, sind aber abwählbar; eine Abweichung steht in `agentic-harness/docs/design.md` des Projekts.
- **Teil C – Baukasten:** optionale Bausteine, Seitenaufbauten, eine bewährte Dateistruktur und ein Veröffentlichungsweg zum Übernehmen, Anpassen oder Weglassen, je nach Kunde, Branche und Stack.

Neue Erkenntnisse kommen je nach Verbindlichkeit in Teil A, B oder C; projektbezogene Werte (Farben, Texte, konkrete Abstände) nie hierher.

## Zusätzliche Init-Fragen für Websites

Ergänzend zum Fragenblock in `agentic-harness/harness/init.md`:

- **Seiten und Navigation:** Seitenumfang, Hauptnavigation, Pflichtseiten (Impressum, Datenschutz), Sprache und Ansprache (du/Sie).
- **Inhalte:** Leistungen, Preise, Referenzen; wer liefert und wer gibt frei?
- **Kontakt und Recht:** tatsächlich zustellbare Kontaktwege, Firmendaten, Formularversand ja/nein.
- **Bilder:** Herkunft und Nutzungsrechte; bis zur Klärung markierte Platzhalter.
- **Betrieb:** Indexierung (Prototyp `noindex`?), Domain, Hosting, Analyse-Werkzeuge; wie ein Stand online geht und wer ihn freigibt (§10).
- **Stil und Baukasten:** Welche Stil-Defaults (Teil B) gelten, welche Bausteine (Teil C) passen zu Branche und Kunde? Wird die Dateistruktur aus Teil C §9 übernommen?

# Teil A – Pflichtregeln

## 1. Rahmen und Wiederholung

- Header, Footer und wiederkehrende Blöcke (z. B. Kontaktblock) kommen aus **einer** Quelle und sind überall, wo sie vorgesehen sind, identisch: Markup, Farben, Schriftstärken, Höhe.
- Gleichartige Abschnitte (Hero, Abschnittskopf, FAQ, Schritte, Karten) sind **ein** Baustein mit Varianten, nicht je Seite neu gebaut. Herausgezogen wird spätestens beim zweiten Vorkommen, nicht erst in einem späteren Umbau (`agentic-harness/harness/core.md`, „Struktur mitziehen“).
- Ausgeliefert werden die ausdrücklich vorgesehenen Routen: über Navigation, Footer und Links erreichbare Seiten sowie bewusst vorgesehene direkte Einstiege (z. B. Kampagnen-Landingpages, Fehlerseiten). Konzeptseiten bleiben intern und `noindex` und werden nach der Entscheidung archiviert.

## 2. Schrift, Größen und Farben

- Jede eingebundene Schrift hat eine Lizenz und wird im Browser als **tatsächlich geladen** geprüft (sonst fällt sie still auf eine Ersatzschrift zurück).
- Eine Größenskala für Überschriften und Text; Ausnahmen werden benannt.
- Farben als Rollen (Hintergrund, Text, gedämpft, Linie, Akzente, helle/dunkle Fläche, Text auf dunkel), keine Einzelwerte für eine bestehende Rolle. Texte bleiben auf ihrer Fläche lesbar (Kontrast).
- Großbuchstaben per CSS, nicht im Text.

## 3. Ausrichtung und Abstände

- Festgelegte Ausrichtungen (z. B. zwei Spalten fluchten) werden bei den Prüfgrößen aus `agentic-harness/docs/testing.md` gemessen, nicht nur optisch geschätzt.
- Abstände folgen einer Skala (Tokens im Code). Ein Einzelwert für eine einzelne Stelle steht nur im Code; in `design.md` steht er nur, wenn er eine Regel für mehrere Stellen bildet.

## 4. Interaktion, Links und Bildschirmgrößen

- Buttons gleicher Rolle teilen Form, Größe und Hover-Verhalten.
- Linktexte sagen, was passiert („Kontakt aufnehmen“ führt zur Kontaktseite, „E-Mail schreiben“ öffnet eine E-Mail); gleiche Aktion heißt überall gleich.
- Sichtbare Fokusmarkierung; Anker landen sichtbar unter einem angehefteten Header; Navigation per Tastatur und mobil bedienbar.
- **Breite und Bedienart getrennt behandeln:** Die Bildschirmbreite in CSS-Pixeln bestimmt Anordnung, Spalten, Menüform und Schriftgrößen (Media Queries nach Breite; Umbruchpunkte dort, wo der Inhalt sie braucht, nicht nach Gerätenamen; Inhalt mit Höchstbreite, darüber wachsen nur die Ränder). Die Bedienart (Touch, Maus, Tastatur) bestimmt nur das Verhalten und wird über `hover` und `pointer` abgefragt, nie aus der Breite abgeleitet: Tablets mit Tastatur, Laptops mit Touchscreen und schmale Desktop-Fenster gibt es alle.
- **Nichts nur per Hover:** Jede Funktion ist auch per Tippen und per Tastatur erreichbar. Hover-Effekte stehen unter `@media (hover: hover)`, damit sie auf Touch-Geräten nach dem Tippen nicht hängen bleiben.
- **Tippflächen:** mindestens 24 × 24 CSS-Pixel oder so weit auseinander, dass sich 24-px-Kreise um benachbarte Ziele nicht überschneiden (WCAG 2.2, Kriterium 2.5.8); Menüschalter, Buttons und Formularfelder möglichst 44 px hoch.
- **Formularfelder** mit mindestens 16 px Schrift, sonst zoomt Safari auf dem iPhone beim Antippen in die Seite.
- **Bewegung:** Animationen und Übergänge entfallen bei `prefers-reduced-motion: reduce`.

## 5. Inhalte und Recht

- Keine erfundenen Referenzen, Kundenstimmen, Kennzahlen, Zertifikate oder Garantien. Leere Plätze sind sichtbar als Platzhalter gekennzeichnet.
- Bilder nur mit geprüfter Nutzungsfreigabe; die Bildquellen-Seite spiegelt den tatsächlichen Stand.
- Rechtsseiten erfinden keine Pflichtangaben; ein Prototyp ist `noindex` und als Entwurf gekennzeichnet.
- Kontaktwege sind real und zustellbar oder als ungeprüft markiert; ein Formular ohne Server sagt offen, was passiert.
- Vorbilder liefern Struktur, nicht Texte, Bilder oder Logos. Übernommener Wortlaut braucht eine ausdrückliche Freigabe.

## 6. Nachweis

Prüfgrößen und Werkzeug legt das Projekt im Projektteil von `agentic-harness/docs/testing.md` fest (bewährt: 1440, 390, 320 px; dazu mindestens als Sichtprüfung eine Tablet-Breite um 800 px, wo Umbruchpunkte oft knapp greifen, und ein großer Monitor). Je Prüfziel die passende Methode: Schriftladung technisch prüfen, Positionen und Überlauf messen, optische Wirkung per Screenshot beurteilen. Die Bedienart prüft keine Bildschirmbreite: Touch einmal auf einem echten Smartphone, Tastatur einmal ganz durchgehen. Animationen mit beiden Werten von `prefers-reduced-motion` prüfen; ein headless Browser übernimmt sonst still die Einstellung des Rechners.

- **Live-Vorschau** (Standardwerkzeug, mit der ersten Seite einrichten): Ein lokaler Vorschau-Server baut bei geänderten Quellen selbst neu; der Auftraggeber lädt im Browser nur neu. Vor jeder Übergabe prüft der Agent, dass die Vorschau läuft, und startet sie sonst im Hintergrund. Adresse und Befehl stehen in den Projektergänzungen von `AGENTS.md`. Für den Test auf einem echten Smartphone gibt ein eigener Befehl (z. B. `npm run dev:lan`) die Vorschau im lokalen Netz frei, nie als Standard.
- **Geräte-Vorschau** (Standardwerkzeug, mit der ersten Seite einrichten): Die Vorlage `agentic-harness/profiles/website/device-preview.html` zeigt die Website gleichzeitig als kleines Handy, Handy, Tablet, Laptop und Monitore, live und klickbar. Der lokale Vorschau-Server liefert die Datei unverändert unter `/_geraete/` aus (gleiche Herkunft wie die Website, nie im Produktions-Build; keine Kopie im Projekt) und meldet unter `/_geraete/stand` die Seitenliste und einen Stand, der sich nach jedem Neubau ändert (`{"stand": …, "seiten": ["/", …]}`); dann lädt die Vorschau bei Änderungen selbst neu. Ein Befehl (z. B. `npm run geraete`) startet bei Bedarf die Vorschau und öffnet sie in einem neuen Browserfenster. Sie ersetzt weder Messungen noch ein echtes Gerät (Touch, Pixeldichte).
- **Nach einer kleinen Iteration:** geänderter Bereich und betroffene gemeinsame Bausteine.
- **Umbau ohne sichtbare Änderung** (Refactoring von Markup oder CSS): vorher und nachher alle Seiten bei den Prüfgrößen aufnehmen und vergleichen, und zwar (1) Screenshots und (2) einen Fingerabdruck der berechneten Styles je Element, Breite und Zustand (normal, Hover, Fokus, aufgeklappt, ausgewählt). Screenshots zeigen keine Zustände, der Style-Vergleich keine Fehler im Prüfwerkzeug selbst; erst beide zusammen belegen „unverändert“. Ist das gebaute Ergebnis (HTML, CSS, Skripte) vorher und nachher bytegleich, genügt dieser Dateivergleich statt der Aufnahmen. Werkzeug einmal im Projekt einrichten (`agentic-harness/docs/testing.md`).
- **Konsistenz-Audit** nach übergreifenden Umbauten und vor Meilenstein-Übergaben: (1) Header und Footer überall gleich, (2) Schriften geladen, Überschriften nach Skala, (3) kein horizontaler Überlauf, (4) festgelegte Ausrichtungen fluchten (Toleranz etwa 2 px) und gewählte Stil-Defaults aus Teil B sind eingehalten, (5) Buttons und Links folgen den Bausteinen, (6) interne Links und Anker erreichen ihr Ziel, (7) keine ungenutzten Selektoren oder unverlinkten Seiten.
- **Livegang-Checkliste** vor jeder Veröffentlichung; jeder Punkt ist erledigt oder als Blocker im Projektprofil genannt:
  1. Firmendaten, Anschrift und Rechtstexte (Impressum, Datenschutz, ggf. AGB) sind geprüft und vom Auftraggeber freigegeben; kein Entwurfshinweis mehr.
  2. Leistungen, Preise und Zusagen sind bestätigt; keine Platzhalter oder Preisideen sichtbar.
  3. Jeder Kontaktweg (E-Mail, Telefon, Formular) ist getestet und zustellbar; Erreichbarkeitsangaben stimmen.
  4. Name, Logo und Zeichen sind auf Marken- und Ähnlichkeitskonflikte geprüft.
  5. Referenzen, Kundenstimmen und Portfolio sind echt und freigegeben, sonst samt Links und Tests entfernt.
  6. Für jedes Bild und jede Schrift ist das Nutzungsrecht belegt; die Bildquellen-Seite stimmt.
  7. `noindex` ist entfernt, Domain, Hosting und Weiterleitungen funktionieren; Analyse-Werkzeuge nur mit Einwilligung, wo nötig.
  8. Abnahmen sind erfolgt: Aussehen auf allen Prüfgrößen, Texte redaktionell, Bedienung per Tastatur, Screenreader und auf einem echten Smartphone, rechtliche Prüfung.

## 7. Zusammenarbeit bei Gestaltungswünschen

- Pro Wunsch nur das Genannte ändern; weitere Funde als Liste anbieten.
- „Wie vorher, nur …“: erst den vorherigen Stand exakt wiederherstellen, dann nur die genannte Änderung.
- Nach jeder Iteration kurz berichten, was sichtbar anders ist, mit Messwert oder Screenshot.
- Gestaltungsentscheidungen des Auftraggebers so sichern, dass sie nicht wieder verloren gehen: als Token oder gemessener Test; in `design.md` nur, wenn sie eine übergreifende Regel oder eine bewusste Abweichung vom Profil sind (kurzer Gate-Weg).

# Teil B – Stil-Defaults (abwählbar)

Bewährt im ersten Website-Projekt; gelten, solange `design.md` nichts anderes festlegt.

- **Eine Schriftfamilie** für die ganze Website.
- **Hervorhebung in Überschriften** nur über Farbe (letzter Teil), nie kursiv oder in anderer Schrift; auf dunklen Flächen die helle Akzentfarbe.
- **Einheitliche Kennzeichnung** über Überschriften (kleines Label mit Zeichen); Überschriften enden einheitlich mit Punkt oder Fragezeichen; kein einzelnes Wort allein in der letzten Zeile.
- **Aufmacher gleichen Typs gleich hoch**, orientiert an der Startseite.
- **Gleichmäßige Innenabstände:** Abschnitte eines Typs haben denselben Innenabstand; Boxen unten denselben wie oben.
- **Grafiken mit Knoten und Linie** (Timelines, Ablaufgrafiken): Die Linie läuft vom Mittelpunkt des ersten bis zum Mittelpunkt des letzten Knotens; Knoten stehen mittig zu ihrer Textzeile, mit gleichen Abständen.
- **Zweispaltige Blöcke:** Die rechte Spalte (Grafik, Timeline, Bildgruppe, Seitenleiste) fluchtet oben mit der ersten Kennzeichnung und unten mit dem Button der Textspalte, füllt deren Höhe und wirkt annähernd quadratisch.
- **Hinterlegte Links** (leichte Fläche, kein Unterstrich), beim Darüberfahren in Akzentfarbe; Haupt- und Zweitbutton gleich, nur die Füllung unterscheidet sich; Eindrück-Effekt beim Darüberfahren.
- **Pfeile:** ↗ führt auf eine andere Seite, ↓ springt innerhalb der aktuellen Seite; maßgeblich sind Quell- und Zielseite, nicht der verwendete Link-Baustein.
- **Ruhige Beschriftungen** in Grafiken (normale oder mittlere Schriftstärke); gedämpfte statt grell weiße Schrift für ruhige Elemente auf dunklen Flächen.
- **Eine Ecken-Sprache** (eckig oder gerundet) für die ganze Website.
- **Schriftgrößen relativ** (`rem`), damit eine im Browser eingestellte größere Standardschrift wirkt; feste Pixel nur für Linien, Rahmen und Icons. Allgemeiner Standard, im ersten Projekt noch in `px` umgesetzt.
- **Rhythmus heller und dunkler Abschnitte** auf allen Seiten gleich (z. B. Kontaktblock immer in derselben Fläche).

# Teil C – Baukasten (optional)

## 8. Bausteine und Seitenaufbauten (übernehmen, anpassen oder weglassen)

Erprobt im ersten Website-Projekt mit diesem Harness. Beim Init oder bei neuen Seiten mit dem Auftraggeber auswählen. Teil A gilt für jeden gewählten Baustein, Teil B als Voreinstellung. Die Bausteine beschreiben Aufbau und Zweck; Überschriften, Texte und Ansprache (du/Sie) entstehen je Projekt neu.

### 8.1 Rahmen

- **Header mit Leistungsmenü:** Marke (Zeichen + Name + Unterzeile) links, Navigation mittig, Kontakt-Button rechts; ein Navigationspunkt „Leistungen“ führt zur Angebotssektion und hat einen separaten Pfeil, der die einzelnen Leistungen aufklappt (Desktop auch beim Darüberfahren, per Tastatur; im mobilen ☰-Menü per Antippen oder gleich aufgeklappt). Sinnvoll ab zwei Leistungsbereichen; bei nur einer Leistung ein einfacher Link.
- **Footer mit vier Gruppen:** Marke und Kontaktadressen oben; darunter Leistungen, Branchen oder Zielgruppen, Unternehmen & Kontakt, Rechtliches; unten eine Statuszeile (Standort, Zertifikate nur wenn belegt, Copyright).
- **Kontaktblock am Seitenende:** eine Überschrift, ein Satz, Hauptbutton zur Kontaktaufnahme und Zweitbutton zur Leistungsübersicht.
- **Fehlerseite:** eigene 404-Seite im normalen Seitenrahmen mit Link zur Startseite und zum Kontakt, nicht verlinkt. Der Server liefert sie mit Status 404 aus (z. B. `.htaccess`), die lokale Vorschau ebenso. Stile, Schrift und Skripte über Pfade ab der Wurzel einbinden, sonst fehlen sie unter tiefen Adressen wie `/a/b/c`.
- **Favicons aus dem Zeichen:** SVG, ICO (16 und 32 px) und Apple-Touch-Icon (180 px) per Skript aus dem Zeichen und den Farb-Tokens erzeugen, nicht von Hand. Ein Test prüft, dass sie zum aktuellen Zeichen passen. Für dunkle Browser-Tabs eine farbige Kachel hinter das Zeichen legen. Größere Profilbilder (z. B. für GitHub oder soziale Netzwerke) entstehen aus derselben Vorlage.

### 8.2 Seitenaufbau

- **Startseite als Erzählung:** Hero mit Nutzenversprechen → Problemabschnitt mit drei typischen Problemen der Zielgruppe und Icons → Angebot (Hauptleistung zuerst, Zusatzleistung abgesetzt, je vier Themen mit Links) → Prozess in vier Schritten → Fallstudie → Stimmen aus der Praxis → Werte → FAQ → Kontaktblock. Abschnitte ohne echte Inhalte (Fallstudie, Stimmen) weglassen oder als Platzhalter nur im Prototyp.
- **Leistungsseite je Leistungsbereich:** Hero mit Seitenleiste → Probleme → Leistungsübersicht (Zeilen mit Kennzeichnung wie einmalig/laufend) plus Ablaufgrafik → Prozess → Wirkung je Thema, mit Themen als Sprungziele → Kontaktblock.
- **Ablauf-Seite:** Hero mit senkrechter Timeline rechts → Schrittkarten mit „Ergebnis“ → kurze FAQ.
- **Über uns:** Hero mit Herkunft der Gründer und Bildplätzen → Idee mit Zusagen als Timeline → Team mit Porträts → überprüfbare Zusagen mit Links zu Ablauf, Leistungen und Kontakt.
- **Kontakt:** geteilte Karte, links Kontaktwege auf dunkler Fläche, rechts Formular.
- **Portfolio:** Filter nach Leistungsbereich, Karten für Kundenstimmen und gebaute Websites; erst veröffentlichen, wenn echte Beispiele freigegeben sind.

### 8.3 Hero-Varianten

- **Text + Seitenleiste:** rechts zwei kurze, nummerierte Angebotsbereiche (Haupt- und Zusatzleistung) mit Kennzeichnung und hinterlegtem Link.
- **Text + Timeline:** rechts die Schritte eines Ablaufs, auf die Höhe der Textspalte gezogen.
- **Text + Bilder:** rechts zwei oder drei Bilder (Team, Betrieb, Arbeit).
- **Vollbild mit Foto:** großes Foto mit dunklem Verlauf und Text darüber; nur mit hochwertigen, freigegebenen Fotos.

### 8.4 Flächen und Rhythmus

- Wechsel dunkler und heller Abschnitte als Taktgeber: dunkler Hero, helle Inhalte, ein dunkler Prozess in der Mitte, heller Kontaktblock, dunkler Footer.
- Eine ruhige Zweitfläche (z. B. zartes Grün oder Grau) für Werte und Kontaktblock; eine weiße Fläche für Probleme und Fallstudie.
- Dunkle Flächen mit sanftem Verlauf statt Flachfarbe wirken hochwertiger.

### 8.5 Bilder und Grafiken

- **Ohne Fotos:** eigene Kontur-Icons, nummerierte Schritte, Timelines und Platzhalterflächen tragen die Seite. Gut für den Prototyp und für Betriebe ohne Bildmaterial.
- **Mit Fotos:** feste Plätze im Hero, bei Team-Porträts (Hochformat) und in einer Galerie; alle im gleichen Bildformat und Farbton.
- **Grafiken statt Fotos** für Abläufe (Knoten + Linie), Leistungszeilen mit Kennzeichnung und Icon-Listen für Themen.

### 8.6 Branchenhinweise

| Branche | Anmutung | Bilder | Betonung |
|---|---|---|---|
| Handwerk | kräftig, erdig, direkt | Werkstatt, Baustelle, Ergebnisse vorher/nachher | Erreichbarkeit, Ablauf, regionale Nähe |
| Gesundheit (z. B. Physiopraxis) | ruhig, hell, viel Weißraum | Menschen, Behandlungsräume, Team | Vertrauen, Terminbuchung, Team und Qualifikation |
| Fahrzeugbetrieb | technisch, kontrastreich | Fahrzeuge, Werkstatt, Galerie | Leistungskatalog, Preise, Öffnungszeiten, Anfahrt |

Die Tabelle ist ein Startpunkt für das Gespräch mit dem Auftraggeber, keine Vorgabe.

## 9. Dateistruktur (Vorschlag)

Bewährt für eine statische Website mit kleinem eigenem Build. Bei einem Framework dessen Konventionen nutzen und nur die Trennung übernehmen. Beim Init übernehmen, anpassen oder abwählen: Die gewählte Struktur steht im Projektteil von `agentic-harness/docs/architecture.md`, Benennungsregeln stehen in `agentic-harness/docs/code.md`.

| Ort | Inhalt | Gehört nicht hierher |
|---|---|---|
| `src/site.*` | Projektkonfiguration: Marke, Kontaktwege, Navigation, Footer-Gruppen, Indexierung | Seitentexte |
| `src/content.*` | Texte, die auf mehreren Seiten gleich erscheinen | Markup |
| `src/pages/` | je Seite eine Datei: oben Texte als Daten, darunter der Aufbau aus Bausteinen; eine Liste aller gebauten Seiten | eigenes Markup für Abschnitte, die es als Baustein gibt |
| `src/components/` | Bausteine mit Parametern und Varianten (Grundgerüst mit Header und Footer, Hero, Abschnittskopf, FAQ, Schritte, Kontaktblock, Links und Buttons) | Texte, Linkziele, Anzahlen |
| `src/styles/` | Einstiegsdatei mit fester Reihenfolge: Tokens → Grundstil → `components/` (eine Datei je Baustein, Klassen beginnen mit dem Bausteinnamen, Varianten mit `--`) → `pages/` (seiteneigene Abschnitte und benannte Abweichungen) | Einzelfarben für bestehende Rollen, Seitenregeln im Baustein |
| `src/browser/` | Skripte, die im Browser laufen | Build-Logik |
| `scripts/` | Build, Vorschau samt Geräte-Vorschau unter `/_geraete/` (§6), Mess- und Vergleichswerkzeuge | Inhalte |
| `tests/` | allgemeine Tests (Routen, Rahmen, Layout, Anker) getrennt von den inhaltlichen Tests des Projekts | – |

**Reihenfolge beim Bauen:** Die Struktur entsteht mit der ersten Seite (Grundgerüst, Header, Footer und Tokens als Bausteine). Ab der zweiten Seite werden wiederkehrende Abschnitte als Baustein herausgezogen, bevor die Seite als fertig gilt (Teil A §1).

## 10. Betrieb und Veröffentlichung (Vorschlag)

Bewährt für eine statische Website auf einem Webhosting mit Git-Anbindung (z. B. Plesk). Bei einem Hoster, der selbst baut (z. B. Netlify, Cloudflare Pages), dessen Weg nutzen und nur die Freigabe übernehmen. Der gewählte Weg steht im Projektteil von `agentic-harness/docs/architecture.md`.

```text
push main ──▶ CI: build ──▶ test ──┬─ rot  ──▶ Abbruch, Deploy-Branch bleibt
                                   └─ grün ──▶ nur die Build-Ausgabe ──▶ Deploy-Branch (z. B. `live`)
                                                                                │
                              Hosting zieht den Deploy-Branch (Freigabe) ◀──────┘
```

- **Getrennte Branches:** Gearbeitet wird nur auf `main`. Den Deploy-Branch schreibt allein die CI, ohne gemeinsame Historie mit `main` (orphan). Er wird nie zurück gemergt; die Angaben „ahead/behind“ auf GitHub sind für ihn bedeutungslos.
- **Auf den Server kommt nur Getestetes:** nur die Build-Ausgabe, kein Quellcode, keine Tests, keine Abhängigkeiten. Schlägt ein Test fehl, bleibt der Deploy-Branch unverändert.
- **Freigabe bewusst wählen:** Ein manueller Abruf im Hosting-Panel („Pull now“) ist die letzte Sichtprüfung vor dem Veröffentlichen, denn Tests finden keine optischen Fehler. Ein Webhook veröffentlicht automatisch jeden grünen Stand von `main`; das passt erst, wenn `main` immer veröffentlichungsreif ist.
- **Zurückrollen:** den Deploy-Branch auf einen früheren Commit setzen und erneut abrufen.
- Browser-Tests in der CI brauchen dort einen Browser mit Zeitlimit; Zugangsdaten und Webhook-Adressen stehen nie im Repo.
