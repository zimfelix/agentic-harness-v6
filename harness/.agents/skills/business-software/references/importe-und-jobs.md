# Importe und Jobs

**Gilt bei:** Importen, Batch-/Webhook-Verarbeitung und Hintergrundjobs im gewählten Bereich. **Zuständigkeit:** Fehlergrenzen, Vorgangsidentität und Wiederaufnahme; externe Aktionen zusätzlich nach `seiteneffekte-und-betrieb.md`.

## Verbindliche Zusagen

- Vor Umsetzung Transaktionsgrenze wählen: Gesamtimport, unabhängige Zeilen oder fachlich zusammengehörige Gruppen. Zusammengehörige Änderungen bleiben atomar; ungültige Eingaben führen nach dieser Wahl zu keiner oder ausdrücklich berichteter Teilübernahme.
- Jeder Lauf liefert einen Bericht: neu, geändert, übersprungen, fehlerhaft mit Grund, Abbruch/ungewisser Stand. Validierungs- und Speicherfehler nicht als Erfolg zählen. Keine stillen Teilimporte.
- Datensatzidentität (Dublettenkriterium) und **Vorgangsidentität** (Wiederholung desselben Auftrags) unterscheiden. Gleicher Payload kann ein neuer gewollter Vorgang sein. Gleicher Vorgang im definierten Geltungsbereich erzeugt keine zusätzlichen fachlichen Effekte; weitere technische Laufprotokolle sind erlaubt.
- Schlüssel, Mandanten-/Quellenbezug, anderes Payload bei gleichem Schlüssel, Aufbewahrungs-/Replayzeitraum und Parallelitätsverhalten festlegen. Kennung allein verhindert keine Race Condition; Erfassung des Verarbeitungsstands und fachliche Mutation müssen konsistent sein.
- Jobs haben dauerhaften Fortschritt, erkennbaren Fehlerstatus und Wiederaufnahme nach Abbruch, soweit Wiederholung Effekte/Daten gefährdet. Retry nur für geeignete Fehler, mit Zeitlimit, begrenzten Versuchen und benannter Klärung bei erschöpften Versuchen. Kein blindes Retry auf fachliche Fehler.

## Durchführung nach Bedarf

1. Soll, Eingabeformat, Bestand/Constraints und Quelle der Wahrheit lesen; fehlende Import-/Fehlersemantik zuerst entscheiden.
2. Mit erfundenem Beispiel gültige Zeile, Dublette, ungültige Zeile und zusammengehörige Gruppe darstellen. Probelauf zeigt geplante Änderungen ohne echte Effekte.
3. Verhalten an API/CLI/Jobgrenze prüfen: zweimal derselbe Vorgang, neuer absichtlich gleicher Vorgang, konkurrierende Wiederholung und Abbruch vor/nach persistiertem Fortschritt.
4. Bericht gegen tatsächlichen Datenstand prüfen; Wiederaufnahme darf weder doppeln noch bestätigte Arbeit verlieren. Migrationen zusätzlich leer/mit Bestand prüfen.
5. In der Spec letzten Nachweis und Grenzen festhalten. Echter Batch braucht konkret vereinbarte Freigabe; externe Fehlerfälle aus der Seiteneffektreferenz ergänzen.

Beispiel: Bei einer ungültigen von zehn unabhängigen Zeilen kann zeilenweise Übernahme neun Erfolge plus einen Fehler ergeben. Bei atomarem Gesamtimport werden null Zeilen übernommen. Der Agent wählt das nicht allein aufgrund einfacherer Tests.

Dies ist ein bedarfsgeladenes Verfahren, kein nativ erkannter Skill und keine zweite Quelle für AK. Herleitung bei Profilpflege: `quellen.md` (AWS/Stripe).
