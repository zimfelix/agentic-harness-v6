# Rechnungen, Buchungen und steuerrelevante Belege

Diese Regeln gelten nur, wenn das Projekt Rechnungen, Buchungen oder andere steuerrelevante Belege führt. Rechtliche Anforderungen (z. B. GoBD, E-Rechnung, Aufbewahrungsfristen) bestätigt der Auftraggeber bzw. seine Steuerberatung. Der Agent erfindet keine Rechtsauslegung, sondern markiert offene Punkte.

- **Unveränderbarkeit:** Ein festgeschriebener Beleg oder eine Buchung wird nie geändert oder gelöscht. Korrekturen laufen über **Storno und Neubuchung**, beide mit Verweis aufeinander.
- **Lückenlose Nummernkreise:** Rechnungsnummern werden eindeutig und fortlaufend vergeben, und zwar transaktionssicher, auch bei gleichzeitigen Anfragen. Entwürfe bekommen erst beim Festschreiben eine Nummer.
- **Zeitbezug:** Steuersatz, Firmendaten und Preise werden mit dem Stand zum Belegdatum gespeichert, nicht live nachgeschlagen.
- **Summen:** Netto, Steuer und Brutto je Position und gesamt folgen der dokumentierten Rundungsregel (`references/daten-geld-zeit.md`); ein Test prüft, dass die Summen aufgehen.
- **Exporte** an Buchhaltung oder Steuerberatung (z. B. DATEV-Format, E-Rechnung) werden gegen eine vom Auftraggeber bestätigte Vorlage oder Spezifikation getestet.
- **Aufbewahrung:** Belege werden für die gesetzliche Frist unveränderbar archiviert; Löschanfragen nach DSGVO führen hier zum Sperren statt zum Löschen.
