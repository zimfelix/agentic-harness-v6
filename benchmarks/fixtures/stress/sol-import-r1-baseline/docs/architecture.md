# Architektur

**Zuständigkeit:** Beschlossene Bausteine, Fachmodell, Dateistruktur, Datenfluss und Betrieb. Lesen bei Architektur-, Datenmodell-, Schnittstellen-, Betriebs- oder Strukturänderungen.

## Universeller Rahmen

Vor erstem Produktcode Struktur festlegen: Source, Tests, Konfiguration/Inhalte, Scripts, Assets, ggf. Tokens. Ist, Ziel und offene Optionen unterscheiden. Entscheidungen knapp begründen; keine Abstraktionen auf Vorrat. Fachregeln nur bei Bedarf vom Infrastrukturcode trennen (konkrete Pflichten im gewählten Business-Software-Profil).

Betrieb: Auslöser/Zeitplan, Umgebungen, Secrets-Ort (nie Werte), Protokolle, externe Seiteneffekte und Schutzmaßnahmen. Varianten bleiben intern und getrennt vom Produkt; nach Auswahl löschen/archivieren. Archiv im Projektprofil benennen, nicht laden/bauen/testen. Nur ausdrücklich vorgesehene Einstiege ausliefern.

Werte gehören in Konfiguration/Tokens; die Architektur beschreibt Zuständigkeiten, keine duplizierten Implementierungsdetails.

## Projektspezifische Befüllung

Tenant ist ein unverändert gespeicherter nichtblanker Bezeichner (kein Auth-Nachweis). Account = (tenant, sku, warehouse), bleibt auch mit Nullbestand erhalten. Run = (tenant, run_id) + exakte CSV-Bytes. Group = alle Zeilen mit gleichem group_id; Reihenfolge nach erstem Auftreten. Ledger = erfolgreiche Transfers innerhalb eines Runs. Zustände: interrupted (angelegt/in Arbeit) → completed; Gruppenentscheidungen sind unveränderlich.

Struktur: app.py ist der öffentliche Launcher; src/inventory/cli.py behandelt JSON/Argumente, parsing.py liest und validiert CSV, storage.py besitzt Schema und Transaktionen, service.py führt Gruppen aus. tests/ prüft Regeln und CLI mit isolierten temporären Dateien unter dem Projekt. Keine Pakete, Assets oder externe Dienste.

CSV wird vor Run-Anlage gelesen; exakte Bytes werden gespeichert, Dubletten über die ganze Datei vor Gruppenentscheidung ermittelt. BEGIN IMMEDIATE serialisiert Schreiben: pro Gruppe Bestandsprüfung, Ledger, Entscheidung und Zähler in einer Transaktion; kein Lock über CLI-Aufrufe. Ein weiterer kurzer Commit markiert completed, sodass ein Crash nach der letzten Gruppe noch interrupted bleiben kann. Identische Prozesse prüfen Fortschritt immer unter dem Schreiblock. Failpoint zählt von dieser Invocation entschiedene Gruppen und beendet nach Commit mit os._exit; Wiederaufnahme benötigt keinen Schlaf.

Schema-Version via PRAGMA user_version, versionierte Migrationen in storage.py; unbekannte neuere Version wird abgelehnt. Migrationen laufen exklusiv innerhalb BEGIN IMMEDIATE und dürfen nie Bestände zurücksetzen. Erstversion 0→1; künftige Erweiterungen additiv, mit Tests auf befülltem Altstand; inkompatible Änderungen nur bei gestoppten Clients. Vor Upgrade SQLite-backup bei gestoppten Schreibern, Restore auf separate DB prüfen; Rückweg ist Wiederherstellung plus passender Code, nicht ein behauptetes Downgrade.

Betrieb: manuelle lokale CLI, tenant/run_id zur Korrelation, ein JSON-Ergebnis, keine Payload-Logs. SQLite rollback journal mit FULL synchronous, 5 Sekunden bounded busy timeout je Lock-Anforderung. Keine Netzwerk-Dateisystem-/Hardware-Powerloss-Garantie. Operator korrigiert ungültige Eingaben, verwendet neuen run-id bei geänderten Bytes, setzt interrupted mit identischen Bytes fort. Jeder lokale DB-Leser kann alle Tenants sehen; dies ist Scoping, keine Sicherheitsisolierung. Input/Run-Historie bleibt gespeichert, kein Lösch-/Retentionfeature.
