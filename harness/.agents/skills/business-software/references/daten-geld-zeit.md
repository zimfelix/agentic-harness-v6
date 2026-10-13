# Daten, Geld und Zeit

**Gilt bei:** Den betroffenen Bereich aus der Auswahl im Profil lesen, nicht die ganze Datei pauschal anwenden. **Zuständigkeit:** Integrität/Migrationen, exakte Geldrechnung und Zeitsemantik.

## Daten und Migrationen

- Schemaänderungen als versionierte Migrationen im Repo; ab leerem Stand **und** auf repräsentativem erfundenem Bestand testen. Keine manuellen Produktivkorrekturen; Datenkorrekturen als nachvollziehbare, geprüfte Migration/Operation mit Freigabe.
- Fachlich zusammengehörige Schreiboperationen atomar speichern. Eindeutigkeit/Referenzen mit passenden Speicher-Constraints absichern. Eine Transaktion allein verhindert nicht alle Parallelitätsfehler: bei konkurrierender Bearbeitung Konfliktverhalten wählen (z. B. Versionsprüfung, geeigneter Lock oder atomare Operation) und mindestens einen konkurrierenden Fall testen.
- Bei gleichzeitig laufendem altem/neuem Code: Schema zuerst erweitern, Code/Daten umstellen, erst später entfernen. Datenmigrationen haben Wiederholungs-/Abbruchverhalten und Bericht über nicht konvertierbare Werte. Kein pauschales Rollback versprechen, wenn Daten verloren gingen; Wiederherstellungsweg vor Freigabe klären.
- Import-/Batchgrenzen und Wiederaufnahme: `importe-und-jobs.md`. Betrieb/Wiederherstellung: `seiteneffekte-und-betrieb.md` §Betrieb.

## Geld

- Decimal/feste Dezimalskala oder ganze **Minor Units** (kleinste gewählte Währungseinheit) verwenden. Keine binäre Gleitkomma-Dezimalrechnung für Geld. JavaScript-`number` nur für nachweislich sichere Integer, auch bei Zwischenoperationen; Wertebereich, Überlauf und Serialisierung prüfen. Sonst passende Decimal-/Integerrepräsentation wählen.
- Währung und Skala ausdrücklich führen; nicht jede Währung hat zwei Nachkommastellen. Rundungsregel und Zeitpunkt (Position/Summe) sind fachliche Entscheidungen.
- Bei Verteilung bleibt die Gesamtsumme erhalten; Rundungsrest nach fester Regel zuordnen. Relevante Tests: negative Werte/Storno, Grenzwerte, Rundung, Verteilung und Hin-/Rückserialisierung.
- Steuersatz/Preise mit fachlichem Gültigkeitszeitraum führen, sofern betroffen; Belegregeln aus `buchhaltung.md`.

## Zeit

- Eindeutige Zeitpunkte (**Instants**) in UTC; Anzeige/fachlicher Geschäftstag mit vereinbarter Zeitzone. Ein reines Datum (Geburtstag, Rechnungsdatum) ist kein Mitternachts-Instant.
- Wiederkehrende lokale Termine separat als lokale Regel plus Zeitzonenidentität (z. B. `Europe/Berlin`) führen. Für nicht existierende/doppelte Uhrzeiten bei Sommerzeitwechsel eine Regel wählen. „Montags 09:00 lokal“ ist keine konstante UTC-Uhrzeit.
- Fachliche Uhr testbar übergeben, wenn Regeln von „jetzt“ abhängen. Fristen unterscheiden Kalender-/Werktage, Dauer versus lokale Tagesgrenze und die relevante Zeitzone.
- Soweit betroffen: Monatsende, Schaltjahr, Sommerzeitlücke/-doppelung und Wiederholung eines lokalen Zeitplans testen.

Herleitung/Grenzen bei Profilpflege: `quellen.md` (PostgreSQL, MDN, RFC 5545). Konkrete Regeln/Versionen werden im Projekt bestätigt.
