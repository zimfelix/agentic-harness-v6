# Inspiration – je Projekt, nie global

Gestaltung kommt aus Brief, Auftraggeber und den Vorbildern, die er **für dieses Projekt** nennt. Dieser Skill enthält bewusst keine Beispielentwürfe: Sobald konkrete Beispiele mitreisen, sehen neue Websites wie das alte Projekt aus.

- **Ablage im Projekt:** `harness/docs/inspiration/` mit einem Index (`README.md`) und je Eintrag einem Ordner mit Steckbrief und Bildern. Kein Rückkopieren in diesen Skill.
- **Andere Projekte** dienen nur als Inspiration, wenn der Auftraggeber sie ausdrücklich nennt („wie bei Projekt X, aber …“). Dann deren Steckbrief lesen, nicht pauschal übernehmen.
- **Maßstab, keine Vorlage:** übernommen werden Prinzip und Mittel, nicht Texte, Logos, Bilder oder ganze Layouts. Beim Erkunden mehrerer Entwürfe bekommt jeder eine eigene Gestaltung.

Index im Projekt, Spalten: Eintrag · Art (ganzer Entwurf/Abschnitt) · Stark in · Stichworte. **Kategorien für „Stark in“:** Schrift · Farbe · Atmosphäre · Anordnung · Grafik · Bedienung · Details. Nur nennen, was der Auftraggeber lobt oder was die Wirkung nachweislich trägt.

## Aufnehmen

Nur, was der Auftraggeber als gelungen bewertet. Lob für einen Teil gehört an den Abschnitt, nicht an die ganze Seite.

1. Aufnehmen mit `node <skill>/tools/vorbild.mjs <url> <projekt>-<kurzname>` aus dem Projekt-Root: legt den Ordner mit `start.jpg` (Desktop 1440 px, erster Bildschirm), `ganz.jpg` (ganze Seite, halbe Größe), Steckbrief-Gerüst und Indexzeile an, Bilder zusammen unter 1 MB. Gelobter Abschnitt: `--abschnitt <name>=<css-selektor>` ergibt `abschnitt-<name>.jpg`, bei einem bestehenden Eintrag nur das Bild. Ohne URL (App, Bildschirmausschnitt): JPEG mit denselben Namen, Ordner und Steckbrief von Hand.
2. Bilder ansehen (Cookie-Banner, Anmeldefenster?), dann `steckbrief.md` nach dem Muster unten füllen. Die Worte des Auftraggebers wörtlich unter „Auftraggeber“; fehlt eigenes Lob, das offen sagen.
3. In der Indexzeile „Stark in“ und Stichworte ergänzen. Lob für einen Teil eines bestehenden Eintrags: Abschnitt dort ergänzen statt neuer Eintrag.

Bilder sind die Hauptquelle: Sie sind ohne laufende Vorschau lesbar. Repo und Datei unter „Herkunft“ helfen nur, wenn das Repo erreichbar ist; lokale Adressen (`127.0.0.1:…`) nie als Quelle. Höchstens etwa zehn Einträge; schwächere werden ersetzt, nicht angehäuft.

## Steckbrief (Muster)

```markdown
# <eintrag> – <Leitidee in wenigen Wörtern>

- **Herkunft:** Art, Projekt, Datum. Quelle: Repo, Datei.
- **Stark in:** <Kategorien aus dem Index>
- **Auftraggeber:** „<wörtliches Lob>“

## Was gut ist

| Kategorie | Was es ausmacht |
|---|---|
| **<Kategorie>** | konkret: welche Schrift, welche Farben (Hex), welche Anordnung, warum es wirkt |

## Übertragbar

- **Prinzip behalten:** was die Wirkung trägt
- **Frei austauschbar:** was sich ändern darf, ohne die Wirkung zu verlieren

## Bilder

- `<datei>.jpg` – was das Bild zeigt und warum es hier ist
```
