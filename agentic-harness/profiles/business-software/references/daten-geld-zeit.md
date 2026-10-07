# Daten, Geld und Zeit

## Geld

- Beträge sind **Dezimalzahlen oder ganze Cent-Werte**, nie Gleitkommazahlen (`float`, `double`, JavaScript-`number` für Rechnungen).
- Jeder Betrag hat eine Währung, auch wenn es heute nur Euro gibt.
- Die Rundungsregel (z. B. kaufmännisch auf 2 Stellen) und der **Zeitpunkt** des Rundens (je Position oder je Summe) sind eine Fachentscheidung mit Entscheidungsnotiz.
- Bei Verteilungen (z. B. Rabatt auf Positionen) geht kein Cent verloren: Die Summe der Teile ergibt den Gesamtbetrag, der Rest wird nach fester Regel verteilt.
- Steuersätze sind Daten mit Gültigkeitszeitraum und kein Wert im Code.

## Zeit

- Zeitpunkte werden in **UTC** gespeichert. Die Zeitzone zur Anzeige und für fachliche Regeln (z. B. „Geschäftstag“) ist ausdrücklich konfiguriert.
- Ein **Datum ohne Uhrzeit** (Rechnungsdatum, Geburtstag) wird als reines Datum gespeichert, nicht als Mitternacht in UTC.
- Die Fachlogik liest die Uhrzeit nie direkt vom System, sondern über eine übergebene Uhr. Nur so lassen sich Fristen, Monatsende und Sommerzeit testen.
- Fristen („nach 7 Tagen“) legen fest, ob Kalender- oder Werktage gemeint sind und in welcher Zeitzone ein Tag endet.

## Migrationen

- Jede Schemaänderung ist eine versionierte Migration im Repo. Getestet wird ab leerem Stand **und** auf einem Bestand mit Daten.
- Spalten nicht im selben Schritt umbenennen oder löschen, in dem der Code umgestellt wird, wenn alter und neuer Code gleichzeitig laufen können. Stattdessen erweitern, umstellen und erst danach aufräumen.
- Datenmigrationen, die Inhalte umrechnen (z. B. Telefonnummern ins E.164-Format), sind idempotent und melden, was sie nicht umwandeln konnten.

## Importe und Jobs

- Eine natürliche oder technische Kennung je Datensatz verhindert Dubletten. Das **Dublettenkriterium** ist eine Fachentscheidung mit Entscheidungsnotiz.
- Fehlerhafte Zeilen brechen den Import nicht ab, sondern landen mit Grund im Bericht. Ob der Rest übernommen wird, ist eine Fachentscheidung (alles oder nichts bzw. zeilenweise).
- Jobs merken sich, was sie bereits erledigt haben (Kennung und Lauf), damit ein Neustart nach einem Abbruch nichts doppelt auslöst.
