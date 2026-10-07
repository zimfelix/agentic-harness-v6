# Requirements – verbindliches Soll bestimmen

> - **Typ:** Prozess
> - **Zuständigkeit:** Für das Gate Auftrag, betroffene Kriterien und Projektgrenzen als prüfbares Soll abgleichen.
> - **Gilt bei:** Dem vollen Gate-Weg in `harness/verification/gate.md`; beim kurzen Weg für Oberflächen-Iterationen übernimmt das Gate den Abgleich selbst.
> - **Ladebeziehungen:** Vom Gate geladen; vorher `harness/project.md` für Grenzen lesen. Bei neuem oder geändertem Nutzerverhalten betroffene Specs unter `specs/` lesen; bei Strukturänderungen `docs/architecture.md`, bei sichtbaren Oberflächenänderungen `docs/design.md` lesen. Ergebnis an das Gate und `harness/verification/implementation.md` geben.
> - **Nicht zuständig:** Umsetzung oder Testergebnisse beurteilen; das macht `harness/verification/implementation.md`.

## Soll abgleichen

1. Bestimme aus dem **beauftragten** Ziel den Umfang und die Nicht-Ziele. Gleiche sie mit den bestätigten Grenzen und Freigaben in `harness/project.md` ab. Bei Widerspruch oder ungeklärter Entscheidung das Soll nicht selbst erfinden.
2. Bei neuem oder geändertem Nutzerverhalten: Lies die betroffenen Specs und ihre Akzeptanzkriterien (AK); prüfe relevante Erfolgs- und Fehlerfälle sowie weitere betroffene Specs. Fehlt die erforderliche Spec, ist das Soll noch nicht abschließbar. Gehört die Arbeit zu einer Idea, muss sie „Beauftragt“ sein; sie nennt die betroffenen Bereichs-Specs und Abhängigkeiten, die Kriterien selbst stehen nur in den Specs.
3. Bei Refactor, Struktur- oder Dokumentationspflege ohne neues Nutzerverhalten: Prüfe stattdessen den beauftragten Umfang und die geltenden Projektgrenzen. Eine neue Produktspec ist dafür nicht pauschal nötig. Bei Strukturänderungen vergleiche das Ziel in `docs/architecture.md` mit dem Auftrag; geplante Architektur nicht als Ist ausgeben.
4. Bei sichtbaren Oberflächenänderungen gehören die Regeln aus `docs/design.md` zum Soll, auch wenn der Auftrag sie nicht nennt (z. B. Größenskala, Farbrollen, identische wiederkehrende Rahmen). Widerspricht der Auftrag einer Regel, gilt der Auftrag; die Regel wird danach in `docs/design.md` ersetzt.

**Ergebnis an das Gate:** Betroffene AK oder sonstige Prüfpunkte, relevante Grenzen sowie offene Widersprüche. Fehlt ein verbindliches Soll, melde die Lücke statt ein positives Ergebnis zu liefern. Tatsächliche Umsetzung und Belege gehören nach `harness/verification/implementation.md`.
