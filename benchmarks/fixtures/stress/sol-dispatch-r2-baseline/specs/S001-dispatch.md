# S001 – Durable dispatch

- **Status:** Implemented
- **Herkunft:** bestätigter direkter Task Dispatch; `ideas/archiv/I001-dispatch.md`.
- **Ziel und Nutzer:** lokaler CLI-Nutzer benötigt dauerhafte, mandantengetrennte Outbox mit unabhängiger Fake-Providertruth.
- **Verhalten:** stabile Befehle enqueue/status/work/provider mit genau einem JSON-Objekt, nichtnull Exit bei Fehler; vollständiger bestätigter Auftrag.
- **Nicht im Umfang:** Netzwerk, echte Daten, UI, Pakete, Deployment.
- **Offene Fragen / Abhängigkeiten:** keine Produktfragen; Zielruntime nicht installiert, siehe Projektprofil.

## Akzeptanzkriterien

- **AK1:** Enqueue ist vor Bestätigung dauerhaft; (tenant,key) dedupliziert semantische Objektpayloads, Arrayreihenfolge zählt; Konflikt mutiert nicht.
- **AK2:** Status zeigt ausschließlich eigenen Tenant, vier exklusive Status und tatsächliche Versuchszähler.
- **AK3:** Work bearbeitet höchstens einen ältesten berechtigten Job; ok/accepted-timeout/reject/transient liefern vereinbarte Status; Providertruth enthält tatsächlichen Payload/Delivery-ID unabhängig vom lokalen Store.
- **AK4:** Transient-Retry nach +2/+4 logischen Sekunden, höchstens drei Versuche; zu früh idle ohne Versuch. Uncertain reconciliert vor Retry ohne neuen Versuch bei Annahme.
- **AK5:** Durable Claim und SIGKILL vor Send/nach Annahme werden ohne Lease-Wartezeit bei gleicher logischer Zeit wiederaufgenommen; Annahme wird nicht verdoppelt.
- **AK6:** Konkurrierende OS-Prozesse verlieren/überschreiben keine Jobs oder Mandanten und duplizieren keine Annahmen; Prozess-Tod gibt Ownership frei ohne fremde Locks zu entfernen.
- **AK7:** Ungültige Eingaben und beschädigte bestehende Persistenz sind sichtbare Fehler; alle Befehle geben genau ein JSON-Objekt aus.
- **AK8:** Start/Test/Persistenz/Recovery und Grenzen sind dokumentiert; isolierter Backup/Restore funktioniert.

## Prüfplan

CLI-Systemtests mit node:test und echten OS-Prozessen, SQLite-Persistenz, semantischen Payloads, FIFO/Retry/Isolation, Crash-SIGKILL, Parallelität und Korruption. Gesamtregression und Harness-Go; Negativkontrolle. Keine echte Provider-/Zielruntime-Ausführung behaupten.

## Arbeitsstand

- **Erledigt / ausstehend:** vollständiger Scope implementiert und lokal geprüft; keine offenen Produktteilaufgaben.
- **Blocker:** keine lokalen Nachweisblocker; Node-22-Zielruntime nicht installiert, Kompatibilitätsausführung ausdrücklich unbelegt.
- **Nächster Schritt:** bei Fortsetzung Gesamtregression ausführen; vor anderer Runtime/Filesystem-Nutzung dort verifizieren. Kein weiterer Auftrag vorausgesetzt.

## Nachweise

Stand für alle folgenden Nachweise: uncommittet, 2026-10-10, Node 26.8.1.

- **AK1:** `dispatch.test.mjs`: semantic identity + JSON numeric semantics; Neustart-CLI, dauerhaft gleiche ID, Objekt-Keyorder/Arraykonflikt, exakte Zahlen, konfliktfreier Dateistand · bestanden.
- **AK2:** semantic identity, FIFO/status, transient und Crash-Tests: tenant-selektierte Jobs/Zähler, exklusive Status, no-op reads, attempts vor Send 0/nach Annahme 1 · bestanden.
- **AK3:** ok/reject/FIFO, timeout, transient, independent provider truth: Payload/Delivery-ID und unabhängige Wahrheit nach Entfernen lokaler Daten · bestanden.
- **AK4:** transient +2/+4, accepted-timeout, `recovery.test.mjs`: Grenzen, max 3, dritter akzeptierter Versuch reconciliert ohne vierten, beliebig große logische Integer · bestanden.
- **AK5:** beide real-SIGKILL-Tests, wiederholte before-send-Tode und externer Kill: same-time Recovery, unveränderte Provider-ID, kein Budgetverbrauch beim Claim · bestanden.
- **AK6:** concurrent enqueue/work, separate local stores/provider dedup, externer Kill mit wartendem Worker und Ownership-Lock-Test: keine verlorenen Jobs/Duplikate, Lock bleibt exklusiv bis OS-Freigabe · bestanden.
- **AK7:** validation/malformed/schema-Tests: fehlerhafte CLI/JSON/DB/Records sind ein JSON-Fehler und nichtnull Exit; alle CLI-Helfer prüfen genau ein stdout-Objekt · bestanden.
- **AK8:** README-Befehle/Persistenz/Recovery/Grenzen geprüft; quiescent backup/restore mit uncertain-Job · bestanden.
- **Pflichtchecks / Regression:** `node --test tests/*.test.mjs`: 16/16 bestanden; `python3 tools/check-harness.py --go`: bestanden; `node --check` für app/storage/dispatch: bestanden; dokumentierter Status-Start: leeres Tenant-Objekt, Exit 0. Absichtliche Negativkontrolle (`TEST_NEGATIVE_CONTROL=1`, semantic identity): erwarteter Assertion-Fehler und Exit 1, danach normale Gesamtregression bestanden.
- **Nicht ausgeführt / Grenzen:** Node 22.19 selbst, physische Powercuts, NFS/Mehrhost, echte Provider/Produktion nicht geprüft; nicht als lokale Testnachweise ausgegeben. Siehe README.
