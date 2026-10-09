# Rechte und Nachvollziehbarkeit

**Gilt bei:** Je betroffenem Bereich Rechte/Mandanten oder Audit/Personendaten. **Zuständigkeit:** Identität, autorisierter Datenzugriff und nachvollziehbare Verarbeitung.

## Rechte und Mandanten

- **Authentication** (Identität prüfen) und **Authorization** (Zugriff erlauben) getrennt festlegen. Rollen/Ressourcen/Operationen in der Architektur, Zusagen in Specs; serverseitig standardmäßig verweigern, solange kein erlaubter Zugriff feststeht.
- Rechte an der autoritativen Anwendungsschnittstelle durchsetzen, nicht nur im UI. API, Import, Export, Hintergrundjobs und direkte Objektzugriffe dürfen die Regeln nicht umgehen. Keine pauschale Auth-Library/Schicht vorschreiben.
- Mandantenkontext aus verlässlich autorisierter Identität/Zuordnung ableiten, nicht ungeprüft aus Requestfeldern. Jede mandantengebundene Ressource/Operation auf diesen Kontext beschränken; globale Referenzdaten ausdrücklich unterscheiden.
- Relevante Tests: erlaubte/verbotene Operation, unbekannte Identität, Objekt außerhalb der Berechtigung und fremder Mandant, falls vorhanden. Webhook-Authentizität zusätzlich nach Seiteneffektreferenz.

## Audit und Personendaten

- Fachlich/rechtlich erforderliche Änderungen nachvollziehbar protokollieren: wer, wann, was und nötige Änderung; keine pauschale Kopie kompletter Vorher-/Nachher-Personendaten. Auditbedarf, Zugriff, Aufbewahrung und Löschkonflikte im Projekt klären.
- Unveränderliches Audit, wenn benötigt, technisch gegen normale Änderung schützen. Datenschutzbedingt nötige Löschung/Anonymisierung mit den bestätigten Aufbewahrungsregeln vereinbaren; „append-only“ löst den Konflikt nicht allein.
- Je relevanter Datenart Zweck, bestätigte Rechtsgrundlage, Aufbewahrung und Lösch-/Auskunftsweg festhalten. Agent erfindet keine Rechtsauslegung. Rechtliche Ausnahmen beziehen sich auf konkrete Daten/Pflichten, nicht auf sämtliche Kundendaten.
- Löschung/Anonymisierung, Auskunft und nötige Einschränkung der Verarbeitung als prüfbare Funktionen vor echter Nutzung einplanen. Nur soweit rechtlich betroffen; Auftraggeber/Fachberatung bestätigt Anforderungen.
- Tests/Entwicklung nutzen erfundene Daten; gewöhnliche Logs/Fehlermeldungen/Commits enthalten keine vertraulichen Personendaten. Unvermeidliche personenbeziehbare Auditkennungen minimieren und geschützt behandeln.

Herleitung bei Profilpflege: `quellen.md` (OWASP und DSGVO); keine Datenschutz-/Rechtsabnahme allein durch Tests.
