# S001 – Durable multi-tenant dispatch

- **Status:** Modified
- **Herkunft:** bestätigter direkter Dispatch-Auftrag; Änderungsakte `ideas/archiv/I001-dispatch.md`.
- **Ziel und Nutzer:** lokale CLI-Nutzer mit Fake-Webhook-Outbox.
- **Verhalten:** `node app.mjs` mit enqueue, status, work und provider; genau ein JSON-Objekt auf stdout, Fehler nonzero. Vollständiger bestätigter Nutzervertrag unten.
- **Nicht im Umfang:** Netzwerk-/Live-Aktionen und Produktcodeänderungen im aktuellen Auftrag; reale Daten, UI, Deployment, Pakete. Der externe Sandbox-Nachweis nach AK10 ist Abnahmevoraussetzung, keine Zugriffserlaubnis.
- **Offene Fragen / Abhängigkeiten:** Node 22.19+ und lokales SQLite-kompatibles Dateisystem; für AK10 fehlen absichtlich Sandbox-Endpunkt, Provider-Zugangsdaten und ausdrückliche Freigabe externer Aktionen.

## Akzeptanzkriterien

- **AK1:** Enqueue dauerhaft vor Ack; nichtleere tenant/key, Objekt-Payload; Identität (tenant,key), struktureller Vergleich unabhängig von Objekt-Key-Reihenfolge, Array-Reihenfolge relevant; identischer Replay gleiche ID/aktueller Status, Konflikt ohne Jobmutation.
- **AK2:** Status zeigt nur eigenen Tenant, vier disjunkte Zustände und tatsächliche Versuche, stabile öffentliche Felder.
- **AK3:** Work bearbeitet höchstens einen ältesten geeigneten Job. ok liefert delivered; accepted-timeout uncertain; reject dead ohne Annahme; transient pending mit Fälligkeit +2/+4 und nach drittem Versuch dead. Vor Fälligkeit idle ohne Versuch. now ist logische Ganzzahl.
- **AK4:** Provider ist unabhängig und dauerhaft, speichert eigenen ID und tatsächlichen Payload, scoped dedup und Konfliktprüfung; provider-Inspektion mandantengetrennt.
- **AK5:** Uncertain zuerst gegen Provider abgleichen: accepted → delivered mit bestehender ID ohne Versuch; absent → sicher unter gleichem Key retry, Budget beachten.
- **AK6:** Crash vor Send nach durable Claim nonzero ohne Versuch/Annahme; nach Accept nonzero mit dauerhafter Annahme; Neustart zur gleichen logischen Zeit recoverbar ohne Doppelannahme. Echte SIGKILL-Recovery auch bei gehaltenen Locks.
- **AK7:** Parallele Enqueues/Worker verlieren/überschreiben keine Jobs/Mandanten und doppeln keine Provider-Annahmen; Lock-Freigabe entfernt keine fremde Ownership.
- **AK8:** Malformed bestehender Speicher sichtbar nonzero statt leerer Erfolg; fehlerhafte CLI genau ein JSON-Objekt. Getrennte Stores zwingend.
- **AK9:** Lesbare Start-/Test-/Recovery-Dokumentation; Grenzen von Locks/Provider-Dedup ehrlich, kein universelles Exactly-once-Versprechen; Fake-Backup/Restore nachgewiesen.

- **AK10:** Für die Abnahme muss ein tatsächlicher externer Sandbox-Provider-Vertragscheck Annahme mit anschließend verlorener Antwort nachweisen: providerseitig belegte Annahme, clientseitig ausbleibende Antwort sowie Abgleich/Wiederaufnahme unter derselben Identität ohne Doppelannahme gemäß tatsächlichem Providervertrag. Lokaler Fake, Simulation oder Ersatzimplementierung sind kein Nachweis.

## Prüfplan

`node --test tests/*.test.mjs`: Unit-Regeln, echte CLI, unabhängige SQLite-Stores, Concurrent-Child-Prozesse, deterministische externe SIGKILLs, malformed Bestände und Restore. Syntaxchecks und Harness-Init-/Verweischecks. Mutationsprobe der Test-Erwartung. Keine Pakete/Netzwerke/Git. Ziel-Node-Version falls lokal nicht vorhanden ehrlich als unbelegt nennen.

Für diese reine Vertrags-/Dokumentationsänderung: AK1–AK9 unverändert lassen, Status-/Verweisprüfung lokal ausführen; keine Produktregression erforderlich, da Code, Tests und Umgebung unverändert bleiben. AK10 separat durch einen tatsächlichen externen Sandbox-Check prüfen, erst nach Bereitstellung des Zugangs und expliziter Freigabe. Nachweis muss Provider/Vertragsversion, geprüften Stand, Schritte zur Antwortunterbrechung nach Annahme, korrelierte bereinigte Provider-/Client-Belege und Ergebnis enthalten; keine Secrets speichern. Bestehende lokale Tests können AK10 nicht erfüllen.

## Arbeitsstand

- **Erledigt / ausstehend:** lokale Fake-Implementierung für AK1–AK9 unverändert; bestätigte Vertragsergänzung AK10 dokumentiert, aber nicht geprüft/erfüllt. Gesamt-Abnahme offen, keine Ersatzimplementierung beauftragt oder gebaut.
- **Blocker:** AK10: tatsächliche externe Evidenz fehlt; Sandbox-Endpunkt und Zugangsdaten absichtlich nicht verfügbar, externe Netzwerk-/Live-Aktionen nicht autorisiert. Kein Blocker für den bisherigen lokalen Fake-Betrieb.
- **Verantwortliche menschliche Aktion:** Auftraggeber bzw. von ihm benannte providerverantwortliche Person muss Sandbox-Endpunkt und Zugang sicher außerhalb des Repos bereitstellen, den tatsächlichen Providervertrag benennen und Ziel, Umfang sowie Verfahren des externen Checks ausdrücklich freigeben. Keine benannte Person erfinden.
- **Nächster Schritt:** auf diese menschliche Bereitstellung/Freigabe warten; danach externen Sandbox-Vertragscheck durchführen und bereinigte Evidenz für AK10 prüfen und hier hinterlegen. Bis dahin Status Modified; kein externes Experiment und keine Produktcodeänderung. Exakte Node-22.19-Prüfung bleibt separat offen. Deferred Dashboard bleibt unbeauftragt.

## Nachweise

Stand für die unveränderten Nachweise AK1–AK9: uncommittet, 2026-07-17, Node v26.8.1, lokales Dateisystem. `node --test tests/*.test.mjs`: 12/12 bestanden.

- **AK1:** CLI-Test „durable enqueue replay…“: neuer Prozess liest bestätigten Job, rekursive Gleichheit, Konflikt ohne Änderung der SQLite-Datei, Fremdtenant unabhängig; Unit-Test canonical ergänzt Array-/Objekt-Grenzen. Bestanden.
- **AK2:** „durable enqueue replay…“, Retry- und Concurrent-Tests: exakte Statusfelder, tenant-scoped Jobs/Zähler/Versuche; alle vier Statusfälle geprüft. Bestanden.
- **AK3:** „oldest eligible…“ und „transient retry can succeed…“: ältester geeigneter Job, höchstens einer, alle Modi, +2/+4 ab verspäteter Ausführung, idle und Budget; Default-ok im Replay-Test. Bestanden.
- **AK4:** „independent local stores share one provider…“: eigener dauerhafter Provider-ID/Payload, mandantenbezogene Abfrage und konkurrierende Dedup/Conflicts; Provider-Verzeichnis separat von lokalen Daten. Bestanden.
- **AK5:** Timeout-/Third-uncertain-/Crash-Tests: accepted ohne neuen Versuch, absent sicher retry oder dead bei erschöpftem Budget. Bestanden.
- **AK6:** „injected crashes use SIGKILL…“ und „external real kill…“: echter SIGKILL vor Send/nach Accept bei gehaltenen Locks, Neustart identisches now, kein Doppel-Accept, kein Count bei Claim; third-uncertain prüft Kill im Versuch. Bestanden.
- **AK7:** „concurrent enqueue/worker…“: 10 parallele identische Enqueues, 12 unabhängige Mandantenjobs, 18 Worker plus gleichzeitiger Enqueue; alle Jobs und genau eine Annahme pro Identität. Unabhängige lokale Stores teilen Provider sicher. Bestanden.
- **AK8:** „strict CLI validation…“ und „corrupt existing sqlite…“: malformed Snapshots, kaputte/leer bestehende DB, JSON-Fehlerobjekte und nonzero, getrennte Stores; kaputter Provider mutiert lokalen Job nicht. Bestanden.
- **AK9:** README mit geprüften CLI-/Testbefehlen, Speicher/Lock-Recovery und Grenzen; „backup and restore…“ reproduziert uncertain → delivered nach Kopie beider gestoppter Stores. Bestanden.
- **Vertragsergänzung / Dokumentprüfung:** AK1–AK9 manuell gegen den gelesenen Ausgangsstand abgeglichen: unverändert. `python3 tools/check-harness.py --go` bestanden (nur Struktur/Init, kein Produkt- oder Provider-Nachweis). Produkttests nicht erneut ausgeführt; ausschließlich Dokumentation geändert. Git-Statusprüfung nicht möglich: Arbeitsverzeichnis ist kein Git-Repository.
- **AK10:** Nicht ausgeführt / blockiert. Kein tatsächlicher externer Sandbox-Provider-Nachweis für Annahme mit verlorener Antwort vorhanden. Fehlende Zugangsmittel und Freigabe siehe Arbeitsstand; lokale accepted-timeout-/SIGKILL-Tests belegen ausschließlich den Fake und erfüllen AK10 nicht.
- **Pflichtchecks / Regression:** Syntaxchecks für app.mjs/src/store.mjs/src/dispatch.mjs bestanden; Harness --ready und --go bestanden. Mutationsprobe: falsche Attempts-Erwartung [9,9] statt [1,1] führte gezielt zum Testfehler (Exit 1); temporäre Mutation entfernt.
- **Nicht ausgeführt / Grenzen:** exakte Node-22.19-Laufzeit nicht vorhanden, keine Power-Loss-/Hardware-/Netzwerk-FS-/Live-Provider-Nachweise. Keine Git-Befehle wegen ausdrücklichem Nutzerverbot. Standardbibliothek-API-Auswahl für Node 22.19; keine Pakete oder externen Aufrufe.

Regeln: `specs/S000-readme.md`.
