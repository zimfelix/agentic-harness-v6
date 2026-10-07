# Rechte und Nachvollziehbarkeit

## Rollen und Mandanten

- Rollen und ihre Rechte stehen als Tabelle in `docs/architecture.md`, die Akzeptanzkriterien dazu in den Specs.
- Die Rechte werden in der Anwendungsschicht geprüft, nicht nur in der Oberfläche oder der API-Schicht.
- Die Mandantentrennung wird erzwungen, nicht nur befolgt: Abfragen ohne Mandantenbezug sind technisch nicht möglich oder fallen in Tests auf.
- Je Rolle gibt es mindestens einen Test „darf“ und einen Test „darf nicht“, dazu einen Test für den Zugriff auf einen fremden Mandanten.

## Audit-Trail

- Fachlich relevante Änderungen (Statuswechsel, Beträge, Zuständigkeit, Löschung) werden protokolliert mit wer, wann, was, vorher und nachher.
- Das Protokoll ist für die Anwendung nur anhängbar und nicht änderbar.
- Personendaten im Protokoll werden auf das Nötige beschränkt.

## Personendaten (DSGVO)

- Je Datenart ist festgehalten: Zweck, Rechtsgrundlage (vom Auftraggeber bestätigt, nicht erfunden), Aufbewahrungsdauer und Löschweg.
- Löschen oder Anonymisieren ist eine Funktion mit Test, kein Handgriff in der Datenbank. Aufbewahrungspflichten (z. B. für Rechnungen) gehen vor; dann wird gesperrt statt gelöscht.
- Exporte für Auskunftsanfragen sind möglich, sobald echte Personendaten verarbeitet werden.
- Entwicklungs- und Testumgebungen enthalten nur erfundene oder anonymisierte Daten.
