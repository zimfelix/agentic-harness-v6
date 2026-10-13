# Architektur

**Zuständigkeit:** Beschlossene Bausteine, Fachmodell, Dateistruktur, Datenfluss und Betrieb. Lesen bei Architektur-, Datenmodell-, Schnittstellen-, Betriebs- oder Strukturänderungen.

## Universeller Rahmen

Vor erstem Produktcode Struktur festlegen: Source, Tests, Konfiguration/Inhalte, Scripts, Assets, ggf. Tokens. Ist, Ziel und offene Optionen unterscheiden. Entscheidungen knapp begründen; keine Abstraktionen auf Vorrat. Fachregeln nur bei Bedarf vom Infrastrukturcode trennen (konkrete Pflichten im gewählten Business-Software-Profil).

Betrieb: Auslöser/Zeitplan, Umgebungen, Secrets-Ort (nie Werte), Protokolle, externe Seiteneffekte und Schutzmaßnahmen. Varianten bleiben intern und getrennt vom Produkt; nach Auswahl löschen/archivieren. Archiv im Projektprofil benennen, nicht laden/bauen/testen. Nur ausdrücklich vorgesehene Einstiege ausliefern.

Werte gehören in Konfiguration/Tokens; die Architektur beschreibt Zuständigkeiten, keine duplizierten Implementierungsdetails.

## Projektspezifische Befüllung

`app.mjs` validiert CLI und gibt ein JSON-Objekt aus. `src/storage.mjs` hält SQLite-Schema, Validierung und Transaktionen; `src/dispatch.mjs` hält Outbox/Fake-Provider-Regeln. `tests/` prüft mit isolierten projektinternen Verzeichnissen.

Zwei getrennte Verzeichnisse: lokale `state.sqlite` (Jobs) und Provider-`provider.sqlite` (permanente Annahmen). Lokale `ownership.sqlite` dient ausschließlich als OS-verwalteter SQLite-Transaktionslock. Kein PID-/Lease-Lock, keine Lockdatei wird entfernt. Alle lokalen Befehle nehmen diesen Lock; Tod des Prozesses gibt ihn frei.

Job: Identität (tenant,key), UUID, sequenzielle Enqueue-Reihenfolge, semantisch kanonischer Payload (Objektschlüssel sortiert, JSON-Zahlen aus Quelltext exakt normalisiert mit JSON.parse-Reviver/JSON.rawJSON), pending/uncertain/delivered/dead, attempts, retry_at, provider_id. Logische Retry-Zeit ist nullable Dezimaltext, verglichen mit BigInt; null ist sofort berechtigt. Durable claim setzt uncertain ohne Versuchszähler. Danach verbindet eine SQLite-ATTACH-Transaktion tatsächlichen Fake-Aufruf und lokalen Versuchszähler atomar (DELETE journal, FULL sync, Superjournal). Annahme und lokale Erfolgsmarkierung sind getrennte Commits: Crash nach Annahme lässt uncertain. Reconciliation fragt Provider vor Retry ab, verbraucht keinen Versuch. Vor-Send-Crash lässt uncertain und attempts unverändert. Retry pending→uncertain→pending/dead; uncertain→delivered bei Providerannahme oder sicherer neuer Versuch bei Abwesenheit.

Schema v1; unbekannte Version, ungültige Inhalte oder beschädigte DB sind Fehler. Initialisierung installiert eine vollständig synchronisierte neue DB mittels atomarem Hardlink ohne Überschreiben. Keine Migration älterer Produktdaten, da Erstversion.

Betrieb: nur CLI-Auslöser, keine Secrets, keine Timer, logische Uhr pro Aufruf. Benutzer mit Dateirechten kann alle Mandanten lesen: Tenant-Filter ist keine Authentifizierung. Lokales vertrauenswürdiges Dateisystem mit SQLite-Locking/fsync/Hardlinks erforderlich; kein NFS-/Mehrhostversprechen. Stoppen aller Prozesse, beide Store-Verzeichnisse gemeinsam sichern und wiederherstellen; getesteter Restore im Systemtest. Keine Löschung von Dedup-Identitäten: deren permanente Aufbewahrung ist Teil des Fake-Vertrags. Keine universelle Exactly-once-Zusage (insbesondere nicht SMTP).
