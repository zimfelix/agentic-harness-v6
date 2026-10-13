# Architektur

**Zuständigkeit:** Beschlossene Bausteine, Fachmodell, Dateistruktur, Datenfluss und Betrieb. Lesen bei Architektur-, Datenmodell-, Schnittstellen-, Betriebs- oder Strukturänderungen.

## Universeller Rahmen

Vor erstem Produktcode Struktur festlegen: Source, Tests, Konfiguration/Inhalte, Scripts, Assets, ggf. Tokens. Ist, Ziel und offene Optionen unterscheiden. Entscheidungen knapp begründen; keine Abstraktionen auf Vorrat. Fachregeln nur bei Bedarf vom Infrastrukturcode trennen (konkrete Pflichten im gewählten Business-Software-Profil).

Betrieb: Auslöser/Zeitplan, Umgebungen, Secrets-Ort (nie Werte), Protokolle, externe Seiteneffekte und Schutzmaßnahmen. Varianten bleiben intern und getrennt vom Produkt; nach Auswahl löschen/archivieren. Archiv im Projektprofil benennen, nicht laden/bauen/testen. Nur ausdrücklich vorgesehene Einstiege ausliefern.

Werte gehören in Konfiguration/Tokens; die Architektur beschreibt Zuständigkeiten, keine duplizierten Implementierungsdetails.

## Projektspezifische Befüllung

Python 3.10+; `planner.py` ist der öffentliche CLI-Einstieg. `src/workplanner/domain.py` hält reine Validierung, Mutationen und Auswahlregeln; `storage.py` liest/schreibt Schema-v1-JSON und hält einen exklusiven Datei-Lock; `cli.py` übersetzt Argumente und Berichte. `tests/` prüft Regeln, echte Dateien und neue Prozesse; `fixtures/demo.json` ist ausschließlich synthetisch.

Projekt = ID und Name. Aufgabe = ID, Projekt-ID, Titel, positive ganzzahlige Minuten, Priorität, optionales Kalenderdatum, done und prerequisite-IDs. IDs bleiben stabil; Abhängigkeiten können Projekte überqueren. Ready/blocked sind abgeleitet, nicht gespeichert. Done ist nur erlaubt, wenn alle Voraussetzungen done sind; Reopen ist verboten, solange erledigte abhängige Aufgaben existieren. Löschen verweigert eingehende Referenzen; Projektlöschen erfordert expliziten Cascade und verweigert externe Referenzen. Änderungen validieren immer den ganzen Graphen.

Datenfluss: CLI → Store-Lock → Lesen und vollständige Validierung → reine Mutation → Validierung → temporäre Datei im Zielordner, fsync, os.replace. JSON statt SQLite vereinfacht portable Import-/Backupdateien; alle Zugriffe der CLI sind serialisiert. Der Lock ist fail-fast, kein Warte-/Job-System; nach einem Prozessabbruch kann er liegen bleiben und muss nach Ausschluss laufender Prozesse manuell entfernt werden. Kein automatisches Zurücksetzen beschädigter Daten. Backup/Export erzeugen neue Dateien, nie stilles Überschreiben. Restore/Import ersetzen den gesamten Bestand erst nach Validierung und Bestätigung; dry-run berichtet die Auswirkungen.

Betrieb: nur explizite lokale CLI-Aufrufe; keine Secrets, Jobs, Provider oder Hintergrunddienste. Fehler auf stderr, Exit 2, kein Payload-Logging. Nutzer verantwortet regelmäßige Backups; Verlustfenster seit letztem Backup. Schema-Versionen außer 1 werden abgelehnt; künftige Migration braucht eine neue geprüfte Umsetzung. Atomare lokale Dateioperationen sind keine Garantie gegen Hardware-/Dateisystemverlust; Mehrbenutzer-/Netzlaufwerke sind nicht unterstützt. Architekturentscheidung: `decisions/0001-local-json.md`.
