# Inspiration – gelungene Website-Entwürfe

Optionale Referenzen für ausdrücklich gewählte Gestaltungsrichtungen. Drei Beispiele aus Oberfranken-Entwürfen (2026), keine allgemeine Stilvorgabe. Erst diesen Index lesen, dann ausgewählte Steckbriefe/Bilder. Projektentscheidungen stehen in PROJECT oder der projektspezifischen Design-Doc.

## Index

Suchen nach Stärke: Spalte „Stark in“. Details, Farben und Übertragbares im Steckbrief.

| Eintrag | Art | Stark in | Stichworte |
|---|---|---|---|
| [`oberfranken-magazin`](oberfranken-magazin/steckbrief.md) | ganzer Entwurf + 4 Abschnitte | Anordnung (Seitenverlauf) · Grafik · Farbe · Atmosphäre · Schrift | stimmigster Gesamtaufbau, Berge als nahtloser Übergang (zwei Abschnitte wirken wie einer), grünes Design, braun-rote Wellen, Porträtkarten, Kalenderliste, warmes Papier, kleine Themenpunkte; Hero schwach |
| [`oberfranken-kompass`](oberfranken-kompass/steckbrief.md) | ganzer Entwurf | Grafik · Anordnung · Schrift | genial, Sternenkarte auf Dunkel (Aktivität als Helligkeit), simpel und auf den Punkt, Dashboard-Kacheln, relative Zeiten |
| [`oberfranken-frag`](oberfranken-frag/steckbrief.md) | Abschnitt | Anordnung · Bedienung | clean, simpel wie Google, Chat-Hero, Antworten als Mini-Wort-Pillen, Eingabefeld als hellster Punkt |

**Kategorien für „Stark in“:** Schrift · Farbe · Atmosphäre · Anordnung · Grafik · Bedienung · Details. Nur nennen, was der Auftraggeber lobt oder was die Wirkung nachweislich trägt.

## Nutzen

```text
Auftrag: „wie oberfranken-magazin: die lebendige Schrift, die einladende Atmosphäre,
          die Farbzusammensetzung – aber Rot statt Grün“
   │
   ├─▶ Index: Eintrag finden ──▶ steckbrief.md: Abschnitt „Übertragbar“
   │                               Prinzip behalten: heller warmer Grund · dunkle Hauptfarbe ·
   │                               warmer Akzent · kleine Themenpunkte · Serifen-Headline …
   │                               Frei austauschbar: konkrete Farbtöne, Motive …
   └─▶ Bild ansehen, um die Wirkung zu prüfen ──▶ neues Farbset nach demselben Prinzip
```

- **Maßstab, keine Vorlage:** Übernommen werden Prinzip und Mittel, nicht Texte, Logos oder ganze Layouts.
- **Beim Erkunden:** Nur bei passendem Auftrag als Vergleich verwenden; diese Beispiele sind weder Mindest-Inhaltsdichte noch verpflichtendes Layout.

## Aufnehmen

Nur, was der Auftraggeber als gelungen bewertet. Lob für einen Teil gehört an den Abschnitt, nicht an die ganze Seite.

1. Ordner `<projekt>-<kurzname>/` (beschreibender Name), Bilder als JPEG (Ziel unter 1 MB je Eintrag):
   - ganzer Entwurf: `start.jpg` (Desktop 1440 px, erster Bildschirm) und `ganz.jpg` (ganze Seite);
   - Abschnitt: `abschnitt-<name>.jpg`.
   Aufnahme mit `browser.mjs` aus `../../tools/` oder als Bildschirmausschnitt.
2. `steckbrief.md` nach dem Muster unten. Die Worte des Auftraggebers wörtlich unter „Auftraggeber“; fehlt eigenes Lob, das offen sagen.
3. Zeile im Index ergänzen. Lob für einen Teil eines bestehenden Eintrags: Abschnitt dort ergänzen statt neuer Eintrag.

Bilder sind die Hauptquelle: Sie reisen mit der Vorlage und sind ohne laufende Vorschau lesbar. Repo und Datei unter „Herkunft“ helfen nur, wenn das Repo erreichbar ist; lokale Adressen (`127.0.0.1:…`) nie als Quelle. Höchstens etwa zehn Einträge; schwächere werden ersetzt, nicht angehäuft.

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
