# Profil Website – bewährte Regeln für Websites

> - **Typ:** Designregel
> - **Status:** Aus einem ersten Website-Projekt (2026) abgeleitet; an weiteren Websites zu bestätigen.
> - **Zuständigkeit:** Projektübergreifende Pflichtregeln, abwählbare Stil-Defaults und optionale Bausteine für Aufbau, Gestaltung, Ausrichtung, Interaktion, Inhalte und Nachweis von Websites festhalten.
> - **Gilt bei:** Projekten, deren Projektprofil „Profil: Website“ nennt, und zwar bei Project Init, sichtbaren Änderungen, neuen Seiten oder Abschnitten, vor Übergaben und vor einer Veröffentlichung. Außerdem auf ausdrücklichen Auftrag in anderen Projekten mit Oberfläche (z. B. „mach es schöner, nutz dafür das Website-Profil“): Dann gelten nur die passenden Teile, und das Projekt hält in `agentic-harness/docs/design.md` fest, welche.
> - **Ladebeziehungen:** Vorher `agentic-harness/harness/project.md`. Gestalterische Projektwerte und bewusste Abweichungen stehen in `agentic-harness/docs/design.md`; Seiten, Routen, Betrieb und Archiv in `agentic-harness/docs/architecture.md`; Prüfgrößen, Methoden und Werkzeuge in `agentic-harness/docs/testing.md`.
> - **Nicht zuständig:** Konkrete Farben, Schriften, Texte oder Seiten eines Projekts festlegen. Projekte ohne dieses Profil und ohne ausdrücklichen Auftrag lesen es nicht.

## Wie das Profil wirkt

Das Profil ergänzt den universellen Harness für Website-Projekte. Es hat drei Teile:

- **Teil A – Pflichtregeln:** nur Konsistenz, Bedienbarkeit, Rechte und Nachweis, keine Stilvorgaben. Gilt in jedem Website-Projekt mit diesem Profil, auch wenn ein ganz anderes Design nachgebaut wird.
- **Teil B – Stil-Defaults:** bewährte Gestaltungsentscheidungen. Gelten als Voreinstellung, sind aber abwählbar; eine Abweichung steht in `agentic-harness/docs/design.md` des Projekts.
- **Teil C – Baukasten:** optionale Bausteine und Seitenaufbauten zum Übernehmen, Anpassen oder Weglassen, je nach Kunde und Branche.

Neue Erkenntnisse kommen je nach Verbindlichkeit in Teil A, B oder C; projektbezogene Werte (Farben, Texte, konkrete Abstände) nie hierher.

## Zusätzliche Init-Fragen für Websites

Ergänzend zum Fragenblock in `agentic-harness/harness/init.md`:

- **Seiten und Navigation:** Seitenumfang, Hauptnavigation, Pflichtseiten (Impressum, Datenschutz), Sprache und Ansprache (du/Sie).
- **Inhalte:** Leistungen, Preise, Referenzen; wer liefert und wer gibt frei?
- **Kontakt und Recht:** tatsächlich zustellbare Kontaktwege, Firmendaten, Formularversand ja/nein.
- **Bilder:** Herkunft und Nutzungsrechte; bis zur Klärung markierte Platzhalter.
- **Betrieb:** Indexierung (Prototyp `noindex`?), Domain, Hosting, Analyse-Werkzeuge.
- **Stil und Baukasten:** Welche Stil-Defaults (Teil B) gelten, welche Bausteine (Teil C) passen zu Branche und Kunde?

# Teil A – Pflichtregeln

## 1. Rahmen und Wiederholung

- Header, Footer und wiederkehrende Blöcke (z. B. Kontaktblock) kommen aus **einer** Quelle und sind überall, wo sie vorgesehen sind, identisch: Markup, Farben, Schriftstärken, Höhe.
- Gleichartige Abschnitte (Hero, Abschnittskopf, FAQ, Schritte, Karten) sind **ein** Baustein mit Varianten, nicht je Seite neu gebaut.
- Ausgeliefert werden die ausdrücklich vorgesehenen Routen: über Navigation, Footer und Links erreichbare Seiten sowie bewusst vorgesehene direkte Einstiege (z. B. Kampagnen-Landingpages, Fehlerseiten). Konzeptseiten bleiben intern und `noindex` und werden nach der Entscheidung archiviert.

## 2. Schrift, Größen und Farben

- Jede eingebundene Schrift hat eine Lizenz und wird im Browser als **tatsächlich geladen** geprüft (sonst fällt sie still auf eine Ersatzschrift zurück).
- Eine Größenskala für Überschriften und Text; Ausnahmen werden benannt.
- Farben als Rollen (Hintergrund, Text, gedämpft, Linie, Akzente, helle/dunkle Fläche, Text auf dunkel), keine Einzelwerte für eine bestehende Rolle. Texte bleiben auf ihrer Fläche lesbar (Kontrast).
- Großbuchstaben per CSS, nicht im Text.

## 3. Ausrichtung und Abstände

- Festgelegte Ausrichtungen (z. B. zwei Spalten fluchten) werden bei den Prüfgrößen aus `agentic-harness/docs/testing.md` gemessen, nicht nur optisch geschätzt.
- Abstände folgen einer Skala (Tokens im Code). Ein Einzelwert für eine einzelne Stelle steht nur im Code; in `design.md` steht er nur, wenn er eine Regel für mehrere Stellen bildet.

## 4. Interaktion und Links

- Buttons gleicher Rolle teilen Form, Größe und Hover-Verhalten.
- Linktexte sagen, was passiert („Kontakt aufnehmen“ führt zur Kontaktseite, „E-Mail schreiben“ öffnet eine E-Mail); gleiche Aktion heißt überall gleich.
- Sichtbare Fokusmarkierung; Anker landen sichtbar unter einem angehefteten Header; Navigation per Tastatur und mobil bedienbar.

## 5. Inhalte und Recht

- Keine erfundenen Referenzen, Kundenstimmen, Kennzahlen, Zertifikate oder Garantien. Leere Plätze sind sichtbar als Platzhalter gekennzeichnet.
- Bilder nur mit geprüfter Nutzungsfreigabe; die Bildquellen-Seite spiegelt den tatsächlichen Stand.
- Rechtsseiten erfinden keine Pflichtangaben; ein Prototyp ist `noindex` und als Entwurf gekennzeichnet.
- Kontaktwege sind real und zustellbar oder als ungeprüft markiert; ein Formular ohne Server sagt offen, was passiert.
- Vorbilder liefern Struktur, nicht Texte, Bilder oder Logos. Übernommener Wortlaut braucht eine ausdrückliche Freigabe.

## 6. Nachweis

Prüfgrößen und Werkzeug legt das Projekt im Projektteil von `agentic-harness/docs/testing.md` fest (bewährt: 1440, 390, 320 px). Je Prüfziel die passende Methode: Schriftladung technisch prüfen, Positionen und Überlauf messen, optische Wirkung per Screenshot beurteilen.

- **Nach einer kleinen Iteration:** geänderter Bereich und betroffene gemeinsame Bausteine.
- **Konsistenz-Audit** nach übergreifenden Umbauten und vor Meilenstein-Übergaben: (1) Header und Footer überall gleich, (2) Schriften geladen, Überschriften nach Skala, (3) kein horizontaler Überlauf, (4) festgelegte Ausrichtungen fluchten (Toleranz etwa 2 px) und gewählte Stil-Defaults aus Teil B sind eingehalten, (5) Buttons und Links folgen den Bausteinen, (6) interne Links und Anker erreichen ihr Ziel, (7) keine ungenutzten Selektoren oder unverlinkten Seiten.
- **Livegang-Checkliste** vor jeder Veröffentlichung; jeder Punkt ist erledigt oder als Blocker im Projektprofil genannt:
  1. Firmendaten, Anschrift und Rechtstexte (Impressum, Datenschutz, ggf. AGB) sind geprüft und vom Auftraggeber freigegeben; kein Entwurfshinweis mehr.
  2. Leistungen, Preise und Zusagen sind bestätigt; keine Platzhalter oder Preisideen sichtbar.
  3. Jeder Kontaktweg (E-Mail, Telefon, Formular) ist getestet und zustellbar; Erreichbarkeitsangaben stimmen.
  4. Name, Logo und Zeichen sind auf Marken- und Ähnlichkeitskonflikte geprüft.
  5. Referenzen, Kundenstimmen und Portfolio sind echt und freigegeben, sonst samt Links und Tests entfernt.
  6. Für jedes Bild und jede Schrift ist das Nutzungsrecht belegt; die Bildquellen-Seite stimmt.
  7. `noindex` ist entfernt, Domain, Hosting und Weiterleitungen funktionieren; Analyse-Werkzeuge nur mit Einwilligung, wo nötig.
  8. Abnahmen sind erfolgt: Aussehen auf allen Prüfgrößen, Texte redaktionell, Bedienung per Tastatur und Screenreader, rechtliche Prüfung.

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
- **Rhythmus heller und dunkler Abschnitte** auf allen Seiten gleich (z. B. Kontaktblock immer in derselben Fläche).

# Teil C – Baukasten (optional)

## 8. Bausteine und Seitenaufbauten (übernehmen, anpassen oder weglassen)

Erprobt im ersten Website-Projekt mit diesem Harness. Beim Init oder bei neuen Seiten mit dem Auftraggeber auswählen. Teil A gilt für jeden gewählten Baustein, Teil B als Voreinstellung.

### 8.1 Rahmen

- **Header mit Leistungsmenü:** Marke (Zeichen + Name + Unterzeile) links, Navigation mittig, Kontakt-Button rechts; ein Navigationspunkt „Leistungen“ führt zur Angebotssektion und hat einen separaten Pfeil, der die einzelnen Leistungen aufklappt (Desktop auch beim Darüberfahren, per Tastatur und mobil per Antippen). Sinnvoll ab zwei Leistungsbereichen; bei nur einer Leistung ein einfacher Link.
- **Footer mit vier Gruppen:** Marke und Kontaktadressen oben; darunter Leistungen, Branchen oder Zielgruppen, Unternehmen & Kontakt, Rechtliches; unten eine Statuszeile (Standort, Zertifikate nur wenn belegt, Copyright).
- **Kontaktblock am Seitenende:** eine Überschrift, ein Satz, Hauptbutton „Kontakt aufnehmen“ und Zweitbutton zur Leistungsübersicht.

### 8.2 Seitenaufbau

- **Startseite als Erzählung:** Hero mit Nutzenversprechen → „Kommt dir bekannt vor?“ mit drei Problemen und Icons → Angebot (Hauptleistung zuerst, Zusatzleistung abgesetzt, je vier Themen mit Links) → Prozess in vier Schritten → Fallstudie → Stimmen aus der Praxis → Werte → FAQ → Kontaktblock. Abschnitte ohne echte Inhalte (Fallstudie, Stimmen) weglassen oder als Platzhalter nur im Prototyp.
- **Leistungsseite je Leistungsbereich:** Hero mit Seitenleiste → Probleme → „Was du bekommst“ (Zeilen mit Kennzeichnung wie Einmalig/Betreuung) plus Ablaufgrafik → Prozess → „Was sich ändert“ mit Themen als Sprungziele → Kontaktblock.
- **Ablauf-Seite:** Hero mit senkrechter Timeline rechts → Schrittkarten mit „Ergebnis“ → kurze FAQ.
- **Über uns:** Hero mit Herkunft der Gründer und Bildplätzen → Idee mit Zusagen als Timeline → Team mit Porträts → „Woran du uns messen kannst“.
- **Kontakt:** geteilte Karte, links Kontaktwege auf dunkler Fläche, rechts Formular.
- **Portfolio:** Filter nach Leistungsbereich, Karten für Kundenstimmen und gebaute Websites; erst veröffentlichen, wenn echte Beispiele freigegeben sind.

### 8.3 Hero-Varianten

- **Text + Seitenleiste:** rechts zwei kurze Angebotsbereiche mit Kennzeichnung („01 / Hauptleistung“, „02 / Zusatzleistung“) und hinterlegtem Link.
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
