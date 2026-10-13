# Architektur

**Zuständigkeit:** Beschlossene Bausteine, Fachmodell, Dateistruktur, Datenfluss und Betrieb. Lesen bei Architektur-, Datenmodell-, Schnittstellen-, Betriebs- oder Strukturänderungen.

## Universeller Rahmen

Vor erstem Produktcode Struktur festlegen: Source, Tests, Konfiguration/Inhalte, Scripts, Assets, ggf. Tokens. Ist, Ziel und offene Optionen unterscheiden. Entscheidungen knapp begründen; keine Abstraktionen auf Vorrat. Fachregeln nur bei Bedarf vom Infrastrukturcode trennen (konkrete Pflichten im gewählten Business-Software-Profil).

Betrieb: Auslöser/Zeitplan, Umgebungen, Secrets-Ort (nie Werte), Protokolle, externe Seiteneffekte und Schutzmaßnahmen. Varianten bleiben intern und getrennt vom Produkt; nach Auswahl löschen/archivieren. Archiv im Projektprofil benennen, nicht laden/bauen/testen. Nur ausdrücklich vorgesehene Einstiege ausliefern.

Werte gehören in Konfiguration/Tokens; die Architektur beschreibt Zuständigkeiten, keine duplizierten Implementierungsdetails.

## Projektspezifische Befüllung

Zielstruktur: `app.mjs` (CLI), `src/store.mjs` (SQLite, OS-Locks, Schema), `src/dispatch.mjs` (Regeln und Fake-Provider), `tests/` (isolierte Tests). Keine Dependencies oder Konfiguration außerhalb der CLI.

Zwei separate Verzeichnisse enthalten jeweils `state.sqlite` und `mutex.sqlite`. Die Mutex-Datenbank hält eine BEGIN-IMMEDIATE-Transaktion über den ganzen Befehl; SQLite/OS gibt Locks nach Prozess-Tod frei. Datencommits erfolgen unabhängig in state.sqlite mit synchronous FULL. Lock-Reihenfolge immer lokal vor Provider; Provider-Inspektion nimmt nur Provider-Lock. Das vermeidet zyklisches Warten. SQLite statt selbstgebauter PID-/Lease-Dateien vermeidet Stale-Lock-Löschrennen.

Glossar: Job = (tenant,key,payload), ID = UUID, enqueue-Reihenfolge = persistente Array-Reihenfolge; Provider-Annahme hat eigene UUID. Zustände: pending → uncertain (dauerhafte Claim vor Send), uncertain → delivered bei Provider-Abgleich; fehlende Annahme erlaubt Retry. Transient → pending mit logischer Fälligkeit oder dead nach Budget, Reject → dead. Claim vor Send zählt noch nicht als Versuch. Provider-Aufrufbeginn zählt; Abgleich zählt nicht. Lokaler Claim und Provider-Commit sind bewusst keine verteilte Transaktion.

Snapshot-Schema Version 1 wird streng validiert, unbekannte/malformed Bestände scheitern sichtbar. Neue leere Stores werden initialisiert; keine automatische Reparatur. Fake-Provider bewahrt Schlüssel und Payload permanent auf. Mandantenfilter sind CLI-Scope, kein Auth-System: wer Dateizugriff hat kann alle Daten lesen.

Betrieb: ausschließlich manuelle CLI-Aufrufe, keine Uhr/Timer für Retry, keine Secrets, kein Netzwerk. Fehler als JSON ohne Payload. Recovery durch erneuten work-Aufruf selbst bei identischem now; Provider ist Wahrheit für Annahmen. Backup/Restore: alle Prozesse stoppen, beide vollständigen Store-Verzeichnisse zusammen kopieren; Tests prüfen Restore. Kein Produktions-Backup-SLA. Lokale SQLite-kompatible Dateisysteme erforderlich; Netzwerk-FS und Strom-/Hardwareausfälle nicht bewiesen. Busy-Timeout ist Lock-Contention-Fehler, keine Lease. Ganze Stores serialisieren Befehle; Skalierung und Überwachung nicht enthalten.
