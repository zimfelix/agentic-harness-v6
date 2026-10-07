# Website – Baukasten (optional)

## 1. Bausteine und Seitenaufbauten (übernehmen, anpassen oder weglassen)

Erprobt im ersten Website-Projekt mit diesem Harness. Beim Init oder bei neuen Seiten mit dem Auftraggeber auswählen. Die Pflichtregeln aus `SKILL.md` gelten für jeden gewählten Baustein, `references/stil-defaults.md` als Voreinstellung. Die Bausteine beschreiben Aufbau und Zweck; Überschriften, Texte und Ansprache (du/Sie) entstehen je Projekt neu.

### 1.1 Rahmen

- **Header mit Leistungsmenü:** Marke (Zeichen + Name + Unterzeile) links, Navigation mittig, Kontakt-Button rechts; ein Navigationspunkt „Leistungen“ führt zur Angebotssektion und hat einen separaten Pfeil, der die einzelnen Leistungen aufklappt (Desktop auch beim Darüberfahren, per Tastatur; im mobilen ☰-Menü per Antippen oder gleich aufgeklappt). Sinnvoll ab zwei Leistungsbereichen; bei nur einer Leistung ein einfacher Link.
- **Footer mit vier Gruppen:** Marke und Kontaktadressen oben; darunter Leistungen, Branchen oder Zielgruppen, Unternehmen & Kontakt, Rechtliches; unten eine Statuszeile (Standort, Zertifikate nur wenn belegt, Copyright).
- **Kontaktblock am Seitenende:** eine Überschrift, ein Satz, Hauptbutton zur Kontaktaufnahme und Zweitbutton zur Leistungsübersicht.

### 1.2 Seitenaufbau

- **Startseite als Erzählung:** Hero mit Nutzenversprechen → Problemabschnitt mit drei typischen Problemen der Zielgruppe und Icons → Angebot (Hauptleistung zuerst, Zusatzleistung abgesetzt, je vier Themen mit Links) → Prozess in vier Schritten → Fallstudie → Stimmen aus der Praxis → Werte → FAQ → Kontaktblock. Abschnitte ohne echte Inhalte (Fallstudie, Stimmen) weglassen oder als Platzhalter nur im Prototyp.
- **Leistungsseite je Leistungsbereich:** Hero mit Seitenleiste → Probleme → Leistungsübersicht (Zeilen mit Kennzeichnung wie einmalig/laufend) plus Ablaufgrafik → Prozess → Wirkung je Thema, mit Themen als Sprungziele → Kontaktblock.
- **Ablauf-Seite:** Hero mit senkrechter Timeline rechts → Schrittkarten mit „Ergebnis“ → kurze FAQ.
- **Über uns:** Hero mit Herkunft der Gründer und Bildplätzen → Idee mit Zusagen als Timeline → Team mit Porträts → überprüfbare Zusagen mit Links zu Ablauf, Leistungen und Kontakt.
- **Kontakt:** geteilte Karte, links Kontaktwege auf dunkler Fläche, rechts Formular.
- **Portfolio:** Filter nach Leistungsbereich, Karten für Kundenstimmen und gebaute Websites; erst veröffentlichen, wenn echte Beispiele freigegeben sind.

### 1.3 Hero-Varianten

- **Text + Seitenleiste:** rechts zwei kurze, nummerierte Angebotsbereiche (Haupt- und Zusatzleistung) mit Kennzeichnung und hinterlegtem Link.
- **Text + Timeline:** rechts die Schritte eines Ablaufs, auf die Höhe der Textspalte gezogen.
- **Text + Bilder:** rechts zwei oder drei Bilder (Team, Betrieb, Arbeit).
- **Vollbild mit Foto:** großes Foto mit dunklem Verlauf und Text darüber; nur mit hochwertigen, freigegebenen Fotos.

### 1.4 Flächen und Rhythmus

- Wechsel dunkler und heller Abschnitte als Taktgeber: dunkler Hero, helle Inhalte, ein dunkler Prozess in der Mitte, heller Kontaktblock, dunkler Footer.
- Eine ruhige Zweitfläche (z. B. zartes Grün oder Grau) für Werte und Kontaktblock; eine weiße Fläche für Probleme und Fallstudie.
- Dunkle Flächen mit sanftem Verlauf statt Flachfarbe wirken hochwertiger.

### 1.5 Bilder und Grafiken

- **Ohne Fotos:** eigene Kontur-Icons, nummerierte Schritte, Timelines und Platzhalterflächen tragen die Seite. Gut für den Prototyp und für Betriebe ohne Bildmaterial.
- **Mit Fotos:** feste Plätze im Hero, bei Team-Porträts (Hochformat) und in einer Galerie; alle im gleichen Bildformat und Farbton.
- **Grafiken statt Fotos** für Abläufe (Knoten + Linie), Leistungszeilen mit Kennzeichnung und Icon-Listen für Themen.

### 1.6 Branchenhinweise

| Branche | Anmutung | Bilder | Betonung |
|---|---|---|---|
| Handwerk | kräftig, erdig, direkt | Werkstatt, Baustelle, Ergebnisse vorher/nachher | Erreichbarkeit, Ablauf, regionale Nähe |
| Gesundheit (z. B. Physiopraxis) | ruhig, hell, viel Weißraum | Menschen, Behandlungsräume, Team | Vertrauen, Terminbuchung, Team und Qualifikation |
| Fahrzeugbetrieb | technisch, kontrastreich | Fahrzeuge, Werkstatt, Galerie | Leistungskatalog, Preise, Öffnungszeiten, Anfahrt |

Die Tabelle ist ein Startpunkt für das Gespräch mit dem Auftraggeber, keine Vorgabe.

## 2. Dateistruktur (Vorschlag)

Bewährt für eine statische Website mit kleinem eigenem Build. Bei einem Framework dessen Konventionen nutzen und nur die Trennung übernehmen. Beim Init übernehmen, anpassen oder abwählen: Die gewählte Struktur und Benennungsregeln stehen in `AGENTS.md` unter „Projekt“ (Stack und Struktur).

| Ort | Inhalt | Gehört nicht hierher |
|---|---|---|
| `src/site.*` | Projektkonfiguration: Marke, Kontaktwege, Navigation, Footer-Gruppen, Indexierung | Seitentexte |
| `src/content.*` | Texte, die auf mehreren Seiten gleich erscheinen | Markup |
| `src/pages/` | je Seite eine Datei: oben Texte als Daten, darunter der Aufbau aus Bausteinen; eine Liste aller gebauten Seiten | eigenes Markup für Abschnitte, die es als Baustein gibt |
| `src/components/` | Bausteine mit Parametern und Varianten (Grundgerüst mit Header und Footer, Hero, Abschnittskopf, FAQ, Schritte, Kontaktblock, Links und Buttons) | Texte, Linkziele, Anzahlen |
| `src/styles/` | Einstiegsdatei mit fester Reihenfolge: Tokens → Grundstil → `components/` (eine Datei je Baustein, Klassen beginnen mit dem Bausteinnamen, Varianten mit `--`) → `pages/` (seiteneigene Abschnitte und benannte Abweichungen) | Einzelfarben für bestehende Rollen, Seitenregeln im Baustein |
| `src/browser/` | Skripte, die im Browser laufen | Build-Logik |
| `scripts/` | Build, Vorschau samt Geräte-Vorschau unter `/_geraete/` (`references/nachweis.md`), Mess- und Vergleichswerkzeuge | Inhalte |
| `tests/` | allgemeine Tests (Routen, Rahmen, Layout, Anker) getrennt von den inhaltlichen Tests des Projekts | – |

**Reihenfolge beim Bauen:** Die Struktur entsteht mit der ersten Seite (Grundgerüst, Header, Footer und Tokens als Bausteine). Ab der zweiten Seite werden wiederkehrende Abschnitte als Baustein herausgezogen, bevor die Seite als fertig gilt (Pflichtregel 1 in `SKILL.md`).
