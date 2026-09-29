# Requirements – verbindliches Soll bestimmen

> - **Typ:** Prozess
> - **Zuständigkeit:** Für das Gate Auftrag, betroffene Kriterien und Projektgrenzen als prüfbares Soll abgleichen.
> - **Gilt bei:** Dem vollen Gate-Weg in `agentic-harness/harness/verification/gate.md`; beim kurzen Weg für Oberflächen-Iterationen übernimmt das Gate den Abgleich selbst.
> - **Ladebeziehungen:** Vom Gate geladen; vorher `agentic-harness/harness/project.md` für Grenzen lesen. Bei neuem oder geändertem Nutzerverhalten betroffene Specs unter `agentic-harness/specs/` lesen; bei Strukturänderungen `agentic-harness/docs/architecture.md`, bei sichtbaren Oberflächenänderungen `agentic-harness/docs/design.md` lesen. Ergebnis an das Gate und `agentic-harness/harness/verification/implementation.md` geben.
> - **Nicht zuständig:** Umsetzung oder Testergebnisse beurteilen; das macht `agentic-harness/harness/verification/implementation.md`.

## Soll abgleichen

1. Bestimme aus dem **beauftragten** Ziel den Umfang und die Nicht-Ziele. Gleiche sie mit den bestätigten Grenzen und Freigaben in `agentic-harness/harness/project.md` ab. Bei Widerspruch oder ungeklärter Entscheidung das Soll nicht selbst erfinden.
2. Bei neuem oder geändertem Nutzerverhalten: Lies die betroffenen Specs und ihre Akzeptanzkriterien (AK); prüfe relevante Erfolgs- und Fehlerfälle sowie weitere betroffene Specs. Fehlt die erforderliche Spec, ist das Soll noch nicht abschließbar. Eine Idea erklärt gegebenenfalls den Hintergrund, ersetzt aber weder Auftrag noch Spec.
3. Bei Refactor, Struktur- oder Dokumentationspflege ohne neues Nutzerverhalten: Prüfe stattdessen den beauftragten Umfang und die geltenden Projektgrenzen. Eine neue Produktspec ist dafür nicht pauschal nötig. Bei Strukturänderungen vergleiche das Ziel in `agentic-harness/docs/architecture.md` mit dem Auftrag; geplante Architektur nicht als Ist ausgeben.
4. Bei sichtbaren Oberflächenänderungen gehören die Regeln aus `agentic-harness/docs/design.md` zum Soll, auch wenn der Auftrag sie nicht nennt (z. B. Größenskala, Farbrollen, identische wiederkehrende Rahmen). Widerspricht der Auftrag einer Regel, gilt der Auftrag; die Regel wird danach in `agentic-harness/docs/design.md` ersetzt.

**Ergebnis an das Gate:** Betroffene AK oder sonstige Prüfpunkte, relevante Grenzen sowie offene Widersprüche. Fehlt ein verbindliches Soll, melde die Lücke statt ein positives Ergebnis zu liefern. Tatsächliche Umsetzung und Belege gehören nach `agentic-harness/harness/verification/implementation.md`.
