# S001 – Tenant-safe sales ledger

- **Status:** Implemented
- **Herkunft:** Direkter bestätigter Auftrag „Task CRM — tenant-safe sales ledger“.
- **Ziel und Nutzer:** Lokales Test-CRM mit persistenten Deals, Rechnungen und Audit, isoliert für Tenant a/b.
- **Verhalten:** Vollständiger bestätigter HTTP-Vertrag; keine produktive Authentifizierung.
- **Nicht im Umfang:** UI, Pakete, echte Daten/Provider, Deployment, Zahlungen, E-Mails, Steuerrechtskonformität. Harness-Regeln und zurückgestellte Arbeit unverändert.
- **Offene Fragen / Abhängigkeiten:** Keine Bau-Blocker; delegierte Architektur in `docs/architecture.md`. Request-ID ist nichtleerer Text; Deal-ID opaque Referenz, einschließlich migrierter Integer.

## Akzeptanzkriterien

- **AK1:** `python3 app.py serve --db PATH --port 0` startet auf 127.0.0.1, meldet genau eine JSON-Portzeile; JSON-Antworten und Prozess-Restart mit gleicher DB funktionieren.
- **AK2:** owner/editor/viewer-a/b sind TEST-Bearer-Identitäten. Fehlende/unbekannte Identität 401 auf Business-Routen; Reads für alle, Deals schreiben nur owner/editor, Issue/Void nur owner, sonst 403. Foreign IDs/related lookups verhalten sich wie missing (404); Client-Tenant in Write 400.
- **AK3:** Deal-Erstellung `{title,amount_cents,currency}` ergibt 201 mit ID, new, Version 1. Titel nonblank Text, Centbetrag echter Integer 0..100000000, Currency exakt EUR/USD. JSON-/Form-/Typ-/Feldfehler 400 ohne Mutation. GET-Liste/Detail nur eigene Deals.
- **AK4:** PATCH `{version,status}` nutzt positive echte Integer-Version, Zustandsgraph new → qualified → won/lost. Erfolg 200 und Version+1; stale/invalid/repeated/terminal transition 409, Formfehler 400. Parallel gleiche Version höchstens ein Erfolg, keine Teilmutation.
- **AK5:** Invoice-POST `{deal_id,request_id,tax_bps}` nur für won, Steuersatz echter Integer 0..10000. 201 mit Snapshot net/tax/total/currency/status issued. HALF_UP auf ganze Cent. Ungültige Form 400, missing/foreign Deal 404, nicht won oder bereits mit anderer Request-ID invoiced 409.
- **AK6:** Tenant-scoped persistente Idempotenz: gleicher Request und semantisches Payload 200/SAME Invoice, auch nach Restart; anderes Payload 409 ohne Mutation; gleiche Request-ID anderer Tenant erlaubt. Parallele identische Requests genau ein 201, übrige 200 mit gleicher ID.
- **AK7:** Invoice GET-Liste/Detail tenant-scoped. Void `{reason}` nur nonblank Text, 200 status void mit unveränderten Beträgen; wiederholt 409. Record und Sperre für Deal bleiben erhalten, kein Amount-Editing-Endpunkt.
- **AK8:** GET audit gibt tenant-scoped causal order, action/resource_id; genau ein Event pro erfolgreichem Deal-create/transition/Issue/Void, keines bei Fehler/Read/Replay. Mutation und Audit gemeinsam atomar.
- **AK9:** Bestehende v1-DB mit spezifizierter deals-Tabelle wird durch versionierte Repo-Migration einmal migriert: alle Zeilen/IDs bleiben erhalten, version=1; fresh DB und wiederholter Restart funktionieren, kein foreign-data leak.

## Prüfplan

Vor Umsetzung festgelegt: reine Regeln (Typen, Zustände, HALF_UP) und echte CLI/HTTP/SQLite-Integration für alle AK, Rollenmatrix und tenant-crossing, Invalid-Input-Zähler, Parallelität und Restart. Projektinterne temporäre synthetische Dateien; gesamte Regression und absichtlicher Fehlernachweis gemäß `docs/testing.md`. Pflichtbefehle im Projektprofil. Keine Produktionsabnahme.

## Arbeitsstand

- **Erledigt / ausstehend:** Vollständiger beauftragter Vertrag implementiert; in frischer Sitzung am 2026-10-09 durch Code-/Testabgleich und vollständige Regression erneut bestätigt. Keine ausstehende Produktarbeit im Auftrag; Produktcode, Tests, AK und zurückgestellte Ideas unverändert. Start und Grenzen in `README.md`, Architektur in `docs/architecture.md`.
- **Blocker:** Keine für lokale Testnutzung; keine Produktionsfreigabe.
- **Nächster Schritt:** Bei Fortsetzung diese Spec und Architektur lesen, Pflichtregression ausführen. Vor wichtiger DB-Migration Offline-Kopie; vor echter Nutzung Produktionsgates separat beauftragen, nicht automatisch weiterbauen.

## Nachweise

Stand für alle Nachweise: Arbeitsbaum ohne Git-Prüfung, 2026-10-09, Python 3.14.7, lokales System; ausschließlich synthetische Daten und Loopback. Alle unten genannten unittest-Tests in frischer Sitzung erneut bestanden; keine Produktänderungen nötig.

- **AK1:** CLI-Portmeldung/HTTP/Restart · `test_cli_persistence_workflow_audit_and_void`, `test_legacy_migration_http_ids_isolation_and_restarts` · bestanden. Loopback-only Bind zusätzlich am festen Server-Konstruktor geprüft; keine Host-Option.
- **AK2:** Identitäten/Rechtematrix/Tenant-Referenzen · `test_missing_unknown_auth_all_business_routes`, `test_role_matrix_and_tenant_isolation`, Invalid-Shape-Tests mit Client-Tenant · bestanden.
- **AK3:** Deal-Form/Typ/Grenzwerte und GET · `test_deal_shape_json_types_and_boundaries`, `test_role_matrix_and_tenant_isolation` · bestanden, Fehlversuche mit DB-Zählern ohne Mutation.
- **AK4:** Graph/Version/Typen/Parallelität · `test_complete_state_graph`, `test_transition_validation_conflicts_and_missing`, `test_concurrent_same_version_transitions` · bestanden; acht gleichzeitige Requests genau ein 200, sieben 409.
- **AK5:** Invoice-Form, won-Voraussetzung, Snapshot und exakte Steuer · `test_invoice_validation_rounding_and_idempotency_conflicts`, `test_cli_persistence_workflow_audit_and_void`, `test_half_up` · bestanden, einschließlich Null/Maximum und HALF_UP-Ties.
- **AK6:** Replay/Restart/Tenant-Key und Konkurrenz · Workflow-/Invoice-/Rollenmatrix-Tests, `test_concurrent_invoice_requests_and_void`, `test_concurrent_same_request_different_payload`, Legacy-Restart-Test · bestanden; identische acht Requests ein 201/sieben 200, verschiedene Payloads ein 201/ein 409.
- **AK7:** Tenant-Reads, Void, unveränderte Beträge, keine Re-Issue/Amount-Edit · Workflow-/Rollenmatrix-Tests, `test_void_invalid_shapes_and_missing`, paralleler Void-Test · bestanden. Void-Grund gespeichert; Record bleibt erhalten.
- **AK8:** Causal Tenant-Audit und atomarer Rollback · Workflow-/Rollenmatrix-/Concurrency-Tests sowie `test_mutation_and_audit_rollback_on_storage_failure` · bestanden. Absichtlicher Audit-INSERT-Abbruch bei jeder Mutation ergibt 500 ohne Teilcommit; Fehl-Issue reserviert keinen Schlüssel/Deal.
- **AK9:** Versionierte Migration mit ID-/Row-Erhalt, fresh/repeated, Foreign-Key-/Unique-Schutz und Migrationsrollback · sämtliche `MigrationTests` · bestanden; v1-Integer-ID auch als Textreferenz replayfähig; unbekannte neuere Schema-Version unverändert abgelehnt.
- **Pflichtchecks / Regression:** Frische Sitzung: `python3 -m unittest discover -s tests -v`: 18 Tests bestanden (2,805 s); `python3 tools/check-harness.py --ready` und `--go`: konsistent. Ausgeführt mit `PYTHONDONTWRITEBYTECODE=1`; projektinterne Testfixtures anschließend entfernt. Persistierter Erstnachweis der Testsensitivität: absichtliche HALF_UP-Änderung +4999 statt +5000 ließ zwei Ties scheitern, danach zurückgenommen. Diese Mutation wurde in der Verifikationssitzung nicht wiederholt.
- **Nachweisgrenzen:** Nur diese lokale Python-/SQLite-Umgebung; keine Last-/DoS-/Power-Loss-/Backup-Restore-Prüfung, keine Produktionsauth, Compliance oder Deployment-Abnahme. Git ausdrücklich nicht verwendet. Produktionsgates siehe Architektur/README.
