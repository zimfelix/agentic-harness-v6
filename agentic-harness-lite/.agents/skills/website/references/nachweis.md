# Website – Nachweis, Audit und Livegang

## Geräte-Vorschau

Das Standardwerkzeug wird mit der ersten Seite eingerichtet. Die Vorlage `assets/device-preview.html` aus diesem Skill zeigt die Website gleichzeitig als kleines Handy, Handy, Tablet, Laptop und Monitore, live und klickbar.

- Der lokale Vorschau-Server liefert die Datei **unverändert aus dem Skill** unter `/_geraete/` aus. Sie hat damit dieselbe Herkunft wie die Website, gelangt nie in den Produktions-Build und wird nicht ins Projekt kopiert.
- Unter `/_geraete/stand` meldet der Server die Seitenliste und einen Stand, der sich nach jedem Neubau ändert: `{"stand": …, "seiten": ["/", …]}`. Dann lädt die Vorschau bei Änderungen von selbst neu.
- Ein Befehl (z. B. `npm run geraete`) startet bei Bedarf die Vorschau und öffnet sie in einem neuen Browserfenster. Er steht in der Befehlstabelle von `AGENTS.md`.
- Die Vorschau ersetzt weder Messungen noch ein echtes Gerät (Touch, Pixeldichte).

## Umbau ohne sichtbare Änderung

Gemeint ist ein Refactoring von Markup oder CSS. Bis Reifegrad MVP genügt der Vergleich der betroffenen Seiten in einem Browser. Ab Reifegrad Produkt nimmst du vorher und nachher alle Seiten bei den Prüfgrößen auf und vergleiche zwei Dinge:

1. Screenshots
2. einen Fingerabdruck der berechneten Styles je Element, Breite und Zustand (normal, Hover, Fokus, aufgeklappt, ausgewählt)

Screenshots zeigen keine Zustände, und der Style-Vergleich zeigt keine Fehler im Prüfwerkzeug selbst. Erst beide zusammen belegen „unverändert“. Ist das gebaute Ergebnis (HTML, CSS, Skripte) vorher und nachher bytegleich, genügt dieser Dateivergleich. Das Werkzeug wird einmal im Projekt eingerichtet.

## Konsistenz-Audit

Fällig nach übergreifenden Umbauten und vor Meilenstein-Übergaben:

1. Header und Footer sind überall gleich.
2. Die Schriften sind geladen, und die Überschriften folgen der Skala.
3. Es gibt keinen horizontalen Überlauf.
4. Festgelegte Ausrichtungen fluchten (Toleranz etwa 2 px), und die gewählten Stil-Defaults sind eingehalten.
5. Buttons und Links folgen den Bausteinen.
6. Interne Links und Anker erreichen ihr Ziel.
7. Es gibt keine ungenutzten Selektoren und keine unverlinkten Seiten.

## Livegang-Checkliste

Vor jeder Veröffentlichung ist jeder Punkt erledigt oder in `AGENTS.md` unter „Offene Entscheidungen und Annahmen“ als Blocker genannt.

1. Firmendaten, Anschrift und Rechtstexte (Impressum, Datenschutz, ggf. AGB) sind geprüft und vom Auftraggeber freigegeben; es steht kein Entwurfshinweis mehr auf der Seite.
2. Leistungen, Preise und Zusagen sind bestätigt; es sind keine Platzhalter oder Preisideen sichtbar.
3. Jeder Kontaktweg (E-Mail, Telefon, Formular) ist getestet und zustellbar, und die Erreichbarkeitsangaben stimmen.
4. Name, Logo und Zeichen sind auf Marken- und Ähnlichkeitskonflikte geprüft.
5. Referenzen, Kundenstimmen und Portfolio sind echt und freigegeben, sonst samt Links und Tests entfernt.
6. Für jedes Bild und jede Schrift ist das Nutzungsrecht belegt, und die Bildquellen-Seite stimmt.
7. `noindex` ist entfernt; Domain, Hosting und Weiterleitungen funktionieren. Analyse-Werkzeuge laufen nur mit Einwilligung, wo diese nötig ist.
8. Die Abnahmen sind erfolgt: Aussehen auf allen Prüfgrößen, Texte redaktionell, Bedienung per Tastatur, mit Screenreader und auf einem echten Smartphone, rechtliche Prüfung.
