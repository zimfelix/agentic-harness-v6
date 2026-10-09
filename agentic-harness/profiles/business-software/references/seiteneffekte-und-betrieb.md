# Seiteneffekte und Betrieb

**Gilt bei:** Externen Aktionen (§Externe Aktionen); dauerhafter Datenhaltung oder regelmäßigem Job (§Betrieb). **Zuständigkeit:** Sichere Ausgangsoperationen, Ausfälle und betrieblicher Rückweg, kein Pflicht-Broker/Cloudstack.

## Externe Aktionen

- Mail, Zahlung, externe API/Export über einen klaren Adapter/Ausgangspfad. Probelauf bzw. isolierter Fake/Sandbox standardmäßig; echter Zielzugriff nur mit konkret vereinbarter Freigabe (Operation, Ziel, Argumente/Menge). Nicht heimlich live schalten, auch nicht als Test.
- Bei lokaler Datenänderung plus Ausgangsauftrag deren Konsistenz sichern, z. B. gemeinsam gespeicherte Outbox, **wenn** ein Ausfall sonst Zustands-/Nachrichtenverlust erzeugt. Eine Outbox kann eine Tabelle sein; kein Broker auf Vorrat.
- Vorgangskennung, Provider-Deduplizierung/Idempotency-Key, Timeout und begrenzte Retry-Regel anhand des tatsächlichen Providervertrags festlegen. Gleicher Schlüssel mit anderem Payload ist ein definierter Konflikt, kein stiller neuer Auftrag. Provider-Key-Aufbewahrung kann kürzer als lokale Wiederholbarkeit sein.
- **Ungewisses Ergebnis:** Externe Annahme plus verlorene Antwort ist nicht gleich „fehlgeschlagen“. Statusabgleich/Provider-Key oder manuelle Klärung wählen. Ohne verlässliche Provider-Deduplizierung (z. B. SMTP) keine Exactly-once-Zusage; mögliche Doppelzustellung versus mögliches Ausbleiben fachlich klären. Outbox/Queue alleine beseitigt diese Grenze nicht.
- Eingehende Webhooks nach Providervertrag auf Herkunft/Signatur prüfen; Identität/Rechte nach der Rechte-Referenz, Verarbeitung/Replays nach `importe-und-jobs.md`.

Prüfen: lokaler Commitfehler, Abbruch vor/nach Versand, Timeout nach Annahme, Replay, parallel konkurrierende Sender, erschöpfte Retries. Fake-/Vertragstest und tatsächlichen Providercheck unterscheiden; fehlende Sandbox ist „nicht geprüft“, kein bestandener Live-Nachweis.

## Betrieb

- In `docs/architecture.md`: Auslöser/Zeitplan, Umgebungen, Secrets-Ort (nie Werte), relevante Lauf-/Korrelationskennung, Fehlerstatus, Wiederaufnahme und Zuständigkeit. Keine Personendaten/Payloads unkontrolliert loggen; kein Monitoringstack ohne Bedarf.
- Vor dauerhafter Nutzung wichtiger Daten: Backup und **getestete Wiederherstellung** mit gewünschtem Verlust-/Ausfallrahmen. Release-/Migrationsweg und Rückweg festlegen; eine vorhandene Backupdatei beweist keinen Restore.
- Bei regelmäßigen Jobs festlegen, wie ein ausgefallener/überlappender Lauf erkannt wird und wer ihn klärt. Shutdown/Neustart darf bestätigte Arbeit nicht unbemerkt verlieren.
- Relevante Betriebsprüfungen und noch offene Livegang-Gates in Prüfstrategie/Projektprofil, nicht als unbegründet „Prototyp“ abwählen.

Herleitung/Grenzen bei Profilpflege: `quellen.md` (AWS/Stripe, OWASP). Ausführliche Durchführung erst bei tatsächlicher Wiederverwendung als eigenständigen Skill erproben.
