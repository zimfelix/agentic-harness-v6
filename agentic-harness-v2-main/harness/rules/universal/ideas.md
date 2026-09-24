# Ideas – größere Vorhaben klären

> **Verantwortung:** Diese Datei regelt, wie ein größeres oder unklares Vorhaben im Dialog geklärt wird. Sie schützt Ideas davor, bereits Specs oder Implementierungsaufträge zu werden.

Der Core entscheidet, ob eine Idea nötig ist. Diese Datei regelt nur die Klärung; `harness/templates/idea.md` gibt die Form vor. Eine Idea ist keine Spec und kein Implementierungsauftrag.

## Im Dialog

1. Beginne mit Problem, betroffenen Nutzern und Nutzen. Kläre danach den gewünschten Umfang und eine bewusste Grenze; besprecht Technik erst, wenn sie für Machbarkeit oder Risiko relevant ist.
2. Hinterfrage Annahmen und prüfe passende Alternativen. Stelle wenige konkrete Fragen pro Runde; schlage bei offenen Entscheidungen Optionen mit Folgen und einer Empfehlung vor, statt Antworten zu erfinden.
3. Prüfe nur relevante Auswirkungen gegen vorhandene Specs, Projektgrenzen, Daten, Schnittstellen und Code. Halte bestätigte Entscheidungen samt kurzem Grund sowie offene Fragen laufend in **einer** Idea-Datei unter `ideas/` fest (`Draft`). Kein Chat-Protokoll und keine zweite Sammlung von Akzeptanzkriterien.

## Übergang

`Ready` erst nach ausdrücklicher Bestätigung: Problem und Nutzen sind klar, der Umfang ist begrenzt, wesentliche offene Entscheidungen sind geklärt und erkennbare Auswirkungen sind geprüft. Details ohne Einfluss auf die nächste Entscheidung dürfen offenbleiben. Wenn Machbarkeit unklar bleibt, benenne das Risiko oder schlage einen kleinen Prüfversuch vor; behaupte keine Gewissheit.

Erst nach einem **separaten Umsetzungsauftrag** leite eine oder mehrere kleine Specs aus der Idea ab. Verlinke die entstandenen Specs in der Idea und setze sie auf `Übernommen`. Bleibt der Auftrag aus, bleibt die bestätigte Idea `Ready` – ohne Codearbeit.
