# Architektur

**Zuständigkeit:** Beschlossene Bausteine, Fachmodell, Dateistruktur, Datenfluss und Betrieb. Lesen bei Architektur-, Datenmodell-, Schnittstellen-, Betriebs- oder Strukturänderungen.

## Universeller Rahmen

Vor erstem Produktcode Struktur festlegen: Source, Tests, Konfiguration/Inhalte, Scripts, Assets, ggf. Tokens. Ist, Ziel und offene Optionen unterscheiden. Entscheidungen knapp begründen; keine Abstraktionen auf Vorrat. Fachregeln nur bei Bedarf vom Infrastrukturcode trennen (konkrete Pflichten im gewählten Business-Software-Profil).

Betrieb: Auslöser/Zeitplan, Umgebungen, Secrets-Ort (nie Werte), Protokolle, externe Seiteneffekte und Schutzmaßnahmen. Varianten bleiben intern und getrennt vom Produkt; nach Auswahl löschen/archivieren. Archiv im Projektprofil benennen, nicht laden/bauen/testen. Nur ausdrücklich vorgesehene Einstiege ausliefern.

Werte gehören in Konfiguration/Tokens; die Architektur beschreibt Zuständigkeiten, keine duplizierten Implementierungsdetails.

## Projektspezifische Befüllung

## Aufbau und Datenfluss

`app.py` ist nur CLI-Einstieg und lädt `src/ledger/`. `http.py` bindet ausschließlich 127.0.0.1, übersetzt HTTP/TEST-Bearer-Identität und JSON in Aufrufe. `service.py` validiert den Vertrag und führt mandantengebundene Transaktionen aus. `rules.py` enthält reine Zustands-/Geldregeln. `db.py` öffnet SQLite-Verbindungen und wendet `migrations/001_legacy.sql` und `002_ledger.sql` versioniert/atomar an. `tests/` enthält synthetische Unit- und Subprozess-HTTP-Tests. Keine Pakete, Assets, Provider oder Hintergrundjobs.

Deal = Verkaufschance (Titel, Centbetrag, EUR/USD), Zustand new → qualified → won/lost; Endzustände unveränderbar. Invoice = einmaliger eingefrorener Betrag eines won-Deals, issued → void; Void hebt die Einmaligkeit nicht auf. Request-ID = pro Tenant eindeutiger Issuance-Schlüssel mit gespeichertem semantischem Payload (Deal und Steuersatz). Audit = genau ein kausal geordnetes Ereignis je erfolgreicher Mutation, keine historischen Ereignisse für migrierte Zeilen.

Pro Request eigene SQLite-Verbindung; Schreibtransaktionen beginnen mit BEGIN IMMEDIATE, damit Prüfung, Mutation und Audit zusammen committen. UNIQUE-Constraints schützen Tenant/Request und Tenant/Deal. Beziehungen verwenden zusammengesetzte Tenant/ID-Fremdschlüssel. Reads und related-resource lookups sind immer tenant-scoped. Die serialisierte Schreibsperre ist bewusst ein einfacher lokaler Kompromiss, kein skalierbarer Servercluster. Kein Repository-/DI-Framework nötig.

Frische IDs sind opaque UUID-Text; v1-Integer-IDs werden unverändert erhalten (SQLite-Spalte ohne erzwungene Text-Affinität). API-Referenzen akzeptieren beide Typen; URL-Lookups vergleichen die Textdarstellung. Migration ist eine Transaktion mit user_version-Fortschritt und Rollback bei Fehler; neuere unbekannte Versionen werden abgelehnt. Gleichzeitiger Betrieb alter und neuer Anwendung ist nicht unterstützt.

## Betrieb und Produktionsgrenzen

Manueller CLI-Start; eine JSON-Zeile meldet den tatsächlich gebundenen Port, danach keine Zugriffs-/Payload-Logs. Fehlerantworten sind JSON, technische Fehler werden nicht als fachlicher Erfolg maskiert. Commit vor HTTP-Erfolg; bei verlorener Antwort Issuance mit demselben Request-Schlüssel wiederholen, Deals per Version erneut lesen. Speicherung über Prozessneustarts; TEST-Tokens sind öffentliche Testidentitäten, keine Secrets oder Produktionsauth.

Vor Migration wichtiger Daten Service stoppen und Offline-Kopie anlegen; Migration stellt bei SQL-Fehlern den alten Stand wieder her. Rückweg nach erfolgreicher Migration nur durch Wiederherstellung der Kopie, nicht durch Downgrade neuer Daten. Backup/Restore mit zugesagtem RPO/RTO, Produktionsauth/TLS, Zugriff auf DB-Dateien, Limits/Timeout-Härtung, Monitoring, Datenschutz und rechtskonforme Rechnungsnummern/Aufbewahrung sind vor realer Nutzung durch Betreiber/Fachberatung festzulegen und zu testen. Nicht im Auftrag: Deployment oder rechtliche Abnahme.
