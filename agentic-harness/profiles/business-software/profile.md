# Profil Geschäftssoftware

**Gilt bei:** Init oder neuem Geschäftssoftware-Teil sowie Änderungen an Fachlogik, Datenmodell, Schnittstellen, Importen, Jobs und Berechtigungen, wenn gewählt. **Zuständigkeit:** Dauerhafte Geschäfts-/Personendaten und Seiteneffekte (CRM, Mail-Automatisierung, Buchung, Buchhaltung); Regeln gelten nach ausgewählten Bereichen.

Fehler in solcher Software kosten Geld, Daten oder Rechtssicherheit, und sie lebt oft jahrelang. Deshalb gelten hier strengere Regeln als bei einfachen Projekten, aber nur dort, wo sie das Projekt tatsächlich betreffen. Ablauf und Freigaben stehen in `harness/core.md`, Abschluss in `harness/verification.md`; hier stehen nur die risikobezogenen Ergänzungen.

| Referenz | Lies sie, wenn … |
|---|---|
| `references/daten-geld-zeit.md` | Datenmodell, Migrationen, Importe, Jobs, Beträge, Datum oder Uhrzeit betroffen sind |
| `references/rechte-und-nachvollziehbarkeit.md` | Rollen, Mandanten, Personendaten, Audit oder Löschen betroffen sind |
| `references/buchhaltung.md` | das Projekt Rechnungen, Buchungen oder steuerrelevante Belege führt |
| `references/entscheidung-vorlage.md` | du eine Entscheidungsnotiz anlegst |

## Bereiche auswählen

Wähle beim Init oder bei der Einordnung eines neuen Projektteils die zutreffenden Bereiche aus: Fachmodell, Daten und Migrationen, Geld und Zeit, Rechte und Mandanten, Personendaten, Seiteneffekte, Buchhaltung. Halte die Auswahl in `harness/project.md` unter „Profile“ fest, mit einem Halbsatz Begründung für jeden abgewählten Bereich. Ein Beispiel: `business-software (Seiteneffekte, Personendaten, Idempotenz; abgewählt: Geld und Buchhaltung, da keine Beträge)`. Pflichtregeln aus abgewählten Bereichen gelten nicht. Kommt ein Bereich später hinzu, ergänzt du die Auswahl.

## Init-Fragen

Zusätzlich zu `harness/init.md`:

- **Fachbegriffe:** Welche zentralen Begriffe gibt es (z. B. Lead, Kunde, Auftrag, Buchung), und was bedeuten sie genau? Welche Zustände durchlaufen sie?
- **Mandanten und Rollen:** Gibt es mehrere Firmen oder Teams mit getrennten Daten? Welche Rollen dürfen was?
- **Geld und Zeit:** Gibt es Beträge, Währungen, Steuern, Rundung? Termine über Zeitzonen oder Sommerzeit hinweg?
- **Pflichten:** Personendaten (DSGVO), Aufbewahrungsfristen, GoBD, Exportformate?
- **Schnittstellen:** Was kommt rein (Import, Formular, Webhook), was geht raus (Mail, Zahlung, Buchhaltung, n8n)? Wer ist Quelle der Wahrheit?

## Projektdateien

Lege diese Dateien an, sobald das Projekt mehr als einen Baustein oder eine erste Fachentscheidung hat; ab Reifegrad MVP gleich beim Init. Trage nötige zusätzliche Docs mit konkretem Leseauslöser unter „Projektspezifische Ergänzungen“ in `AGENTS.md` ein; `docs/architecture.md` ist bereits im Einstieg geroutet:

- **`docs/architecture.md`** (Auslöser: Änderungen an Fachlogik, Datenmodell, Schnittstellen oder Struktur): Glossar, Fachmodell mit Zuständen und erlaubten Übergängen, Schichten und Abhängigkeitsrichtung, Datenfluss, Betrieb (Jobs, Umgebungen, Ort der Zugangsdaten), Teststrategie je Schicht.
- **`docs/decisions/`** (Auslöser: neue Architektur- oder Fachentscheidung oder Zweifel an einer bestehenden): je Entscheidung eine kurze Notiz nach `references/entscheidung-vorlage.md`. Wird eine Entscheidung abgelöst, bekommt die alte Notiz den Status „ersetzt durch …“. Das ist die bewusste Ausnahme von „ersetzen statt anhängen“: Hier zählt gerade die Begründung über die Zeit.

## Pflichtregeln

### 1. Fachmodell und Schichten

- Code, API und Datenbank verwenden die Begriffe aus dem Glossar. Ein neuer Fachbegriff wird zuerst ins Glossar eingetragen.
- Die Fachlogik kennt weder Datenbank noch HTTP noch Dateiformate. Die Abhängigkeiten zeigen nach innen zur Fachlogik. Schnittstellen nach außen (Persistenz, Mail, Uhr, IDs) werden übergeben, damit sie sich testen und austauschen lassen.
- Zustände eines Fachobjekts haben **erlaubte Übergänge**. Ein unerlaubter Übergang ist ein Fehler, kein Sonderfall.
- Abstraktion nur dort, wo heute ein zweiter Einsatz oder ein Test sie braucht. Keine Interfaces auf Vorrat.

### 2. Daten, die stimmen müssen

- Schemaänderungen laufen **nur über versionierte Migrationen**, die vorwärts auf bestehenden Daten laufen. Daten nie von Hand in einer Produktivdatenbank ändern.
- Importe, Jobs und Webhooks sind **idempotent**: Ein zweiter Lauf mit denselben Eingaben ändert nichts. Jeder Import endet mit einem Bericht (neu, geändert, übersprungen, fehlerhaft mit Grund).
- Was zusammengehört, wird in einer Transaktion gespeichert. Keine stillen Teilimporte.
- Eingaben werden an der Grenze geprüft und normalisiert (E-Mail, Telefon, Beträge, Datum). Danach arbeitet die Fachlogik nur mit gültigen Werten.
- Geld und Zeit haben feste Regeln: siehe `references/daten-geld-zeit.md`.

### 3. Rechte, Mandanten, Personendaten

- Berechtigungen und Mandantentrennung sind **Akzeptanzkriterien mit Tests**, keine Nebensache. Jede Abfrage ist auf den Mandanten beschränkt.
- In Tests und Beispielen nur erfundene Testdaten verwenden. Personendaten gehören nicht in Logs, Fehlermeldungen oder Commits.
- Secrets nie im Repo. Wo sie liegen, steht in `docs/architecture.md` (Betrieb), nie der Wert selbst.
- Details zu Audit, Löschen und Aufbewahrung: `references/rechte-und-nachvollziehbarkeit.md`.

### 4. Seiteneffekte nach außen

- Mails, Zahlungen, Exporte an Dritte und Webhooks laufen über eine **Ausgangsstelle** (Postausgang oder Warteschlange) mit **Probelauf** als Standard.
- Echter Versand ist eine Konfiguration, die nur der Auftraggeber nach dem Probelauf freigibt (Freigabeablauf in `harness/core.md`). Der Agent schaltet ihn nie selbst ein, auch nicht „nur kurz zum Testen“.
- Jeder Seiteneffekt hat eine eindeutige Kennung, damit ein Wiederholungslauf ihn nicht doppelt auslöst.

### 5. Tests

- **Fachlogik:** Unit-Tests ohne Datenbank, mit testbarer Uhr. Hier liegen die meisten Tests, auch für Grenzfälle.
- **Persistenz:** gegen eine echte Datenbank derselben Art wie in Produktion, inklusive Migrationen ab leerem Stand.
- **Schnittstellen:** API und CLI über ihre öffentliche Grenze testen, einschließlich Fehlerfällen und Berechtigungen.
- **Pflicht-Grenzfälle**, soweit betroffen: Dubletten, doppelter Lauf, leere und kaputte Eingaben, Rundung, Monatsende, Zeitzonen und Sommerzeit, fremder Mandant, fehlende Berechtigung.
- **Refactor ohne Verhaltensänderung:** Die Verhaltenstests bleiben unverändert und grün. Muss ein Verhaltenstest angepasst werden, hat sich das Verhalten geändert, und das ist dann eine Spec-Frage.

### 6. Entscheidungen festhalten

Eine Entscheidungsnotiz entsteht bei: Wahl von Stack, Datenbank oder Architekturstil; Fachregeln mit Spielraum (z. B. Dublettenkriterium, Rundung, Stornologik); bewusst eingegangenen Kompromissen oder technischen Schulden.
