# Quality – risikobasiert nachweisen

> **Verantwortung:** Diese Datei hilft, passende Nachweise nach Risiko auszuwählen. Sie erklärt Testarten und Gate-Prinzipien, führt aber selbst keine Checks aus und ersetzt keine Projektkonfiguration.

Diese Datei hilft bei der **Auswahl** von Prüfungen, nicht bei deren Ausführung. Der Core regelt Spec-State und Korrekturschleife; das Projektprofil benennt das Gate, eine projektspezifische Qualitätsmatrix ordnet bei Bedarf Bereiche zu und die Gate-Konfiguration enthält konkrete Befehle. Keine Testart ist allein wegen ihres Namens Pflicht.

## Passende Nachweise wählen

Gehe vom wichtigsten Nutzerablauf, seinen Akzeptanzkriterien (AK), den berührten Grenzen und dem möglichen Schaden eines Fehlers aus. Wähle den kleinsten zuverlässigen Nachweis; prüfe relevante Fehlerfälle, nicht nur den Erfolgsfall:

| Risiko oder Frage | Möglicher Nachweis |
|---|---|
| Einzelne Regel oder Berechnung | Unit-/Logiktest; bei UI-Bausteinen gegebenenfalls Komponententest. |
| Zusammenspiel, Speicherung, externe Schnittstelle | Integrationstest; Contract-Test, wenn Datenformate zwischen getrennten Systemen verbindlich sind. |
| Wichtigster Ablauf durch die Anwendung | Wenige System-/E2E-Tests über die echte Bediengrenze, wenn das Risiko es verlangt; ein Browser ist nur bei Browserprodukten nötig. |
| Geändertes bestehendes Verhalten | Betroffene Tests erneut ausführen; die Projektsuite bildet das Regressionsnetz. |
| Code, Paket oder Start | Passende Format-, Lint-, Typ- und Build-/Startprüfung; Smoke-Test, wenn ein realer Start sonst ungetestet bleibt. |
| Bedienung oder hohes Schadenspotenzial | Bei UI Basis-Accessibility (Tastatur, Labels, Fokus, verständliche Fehler; Screenreader bei relevanten Abläufen); bei Daten, Rechten oder Fremdsystemen gezielte Sicherheits- und Ausfallprüfungen. |

Performance/Last, Kompatibilität, visuelle Regression, Usability, Recovery und Deployment nur bei entsprechendem Produktziel, Risiko oder konkretem Befund ergänzen. Snapshots ersetzen keine Verhaltensprüfung. Testebene (z. B. Unit), Qualitätsbereich (z. B. Accessibility) und Zweck (z. B. Regression) sind unterschiedliche Blickwinkel – **keine drei getrennten Pflichtsuiten**.

## Verlässlichkeit und Gate

Ein Test soll beobachtbares Verhalten nachweisen, unabhängig und reproduzierbar laufen. Kontrolliere Zufall, Zeit und Testzustand; schütze echte Daten und verwende bei schreibenden Prüfungen isolierte Testdaten. Verknüpfe AK mit ihren Nachweisen, ohne dieselbe Liste mehrfach zu pflegen. Fehlt für gewünschtes Nutzerverhalten ein AK, kläre zuerst die Spec; technische Invarianten und Risiken dürfen zusätzlich eigene Tests begründen.

Das projektbezogene Gate muss tatsächlich passende Checks ausführen; ein grüner Befehl ohne wirksame Prüfungen ist kein Nachweis. Ein projektbezogener Spec-Check kann zulässige States und die Zuordnung von AK zu Nachweisen prüfen und bei Bedarf ins Gate aufgenommen werden; Marker beweisen aber weder fachliche Korrektheit noch vollständige Accessibility. Der Runner meldet Fehler und **ändert weder Code noch Spec-State automatisch**. Die gezielte Korrektur und das erneute Gate stehen im Core.
