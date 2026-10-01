# Gate – Soll und belegtes Ist zusammenführen

> - **Typ:** Prozess
> - **Zuständigkeit:** Entscheiden, ob eine konkrete Änderung innerhalb des Auftrags ausreichend nachgewiesen ist.
> - **Gilt bei:** Abschluss einer Änderung nach dem Ablauf in `agentic-harness/harness/core.md`.
> - **Ladebeziehungen:** Vorher `agentic-harness/harness/project.md` für Grenzen und aktive Prüfungen; dann `agentic-harness/harness/verification/requirements.md` für das Soll und `agentic-harness/harness/verification/implementation.md` für Ist und Nachweise. Beim kurzen Weg für Oberflächen-Iterationen stattdessen `agentic-harness/docs/design.md`. Bei einer Lücke `agentic-harness/harness/verification/fail.md`.
> - **Nicht zuständig:** Projekt-Tests festlegen oder selbst ausführen; Anforderungen und Nachweise stehen in den jeweils zuständigen Dateien.

## Entscheidungsweg

Schematische Übersicht mit verkürzten Dateinamen. Bei Änderungen an Harness-Rollen oder Ladewegen auch dieses Diagramm gegen `AGENTS.md` und `agentic-harness/harness-map.md` prüfen.

```text
AGENTS.md → core.md + project.md (Ziel, Grenzen, aktive Befehle)
                 │
                 ├→ bei Produkt-/Testarbeit: testing.md
                 │    ← Risiken/AK; bei Bedarf architecture.md + code.md
                 │    → gewählte Tests, Testorte und Anlässe
                 ↓
core.md: Änderung umsetzen; ggf. Tests entwickeln und Checks ausführen
                 ↓
gate.md: ein Abschlussdurchlauf
       (kurzer Weg bei reiner Oberflächen-Iteration: Auftrag + design.md
        → Diff, Build/Tests, Nachweis im Zielmedium → Ergebnis)
       ├─ requirements.md ← Auftrag + project.md; ggf. Spec/Architektur
       │                     → Soll (AK/Prüfpunkte)
       └─ implementation.md ← Soll + Änderung + project.md (Befehle)
                               ← testing.md (bei Produkt-/Teständerung)
                               → Ist, Checks auf aktuellem Stand, Nachweisgrenzen
                 ↓
      Soll durch Ist und Nachweise belegt?
       ├─ ja   → Ergebnis berichten; ggf. Spec „Implemented“
       └─ nein → fail.md → Ursache: Soll/Spec, Teststrategie, Setup/Befehl,
                          Umsetzung/Test oder fehlender Nachweis
                          → an betroffener Stelle korrigieren; Checks + Gate
                            erneut prüfen oder Blocker berichten
```

## Entscheidung

Requirements und Implementation lesen `agentic-harness/harness/project.md` und öffnen die für ihre Prüfung nötigen Specs oder Projekt-Docs nach den jeweiligen Auslösern – auch wenn diese bei der Umsetzung noch nicht geladen waren.

- Gleiche das Soll aus `agentic-harness/harness/verification/requirements.md` mit der beobachteten Änderung und den tatsächlich ausgeführten Nachweisen aus `agentic-harness/harness/verification/implementation.md` ab. Ein grüner Build oder Testlauf allein belegt nicht, dass der beauftragte Ablauf und die Projektgrenzen erfüllt sind. Nach `agentic-harness/docs/testing.md` für betroffene Risiken vorgesehene, aber nicht nachgewiesene Checks bleiben Lücken.
- Bei beauftragtem Nutzerverhalten: Jedes betroffene Akzeptanzkriterium muss belegt sein; erforderliche Prüfungen müssen bestanden sein. `Implemented` setzt zusätzlich gültige Nachweise für sämtliche übrigen geltenden AK der Spec voraus (`agentic-harness/specs/S000-readme.md`). Trage in der Spec den neuen Nachweis **anstelle** des alten ein und im Projektprofil nur das letzte Prüfergebnis; Einzelheiten des Durchlaufs gehören in die Übergabe, nicht als neuer Absatz in Projektdateien.
- **Projektdateien prüfen, bevor das Ergebnis gilt:** Die Regeln für Specs und Projektdateien helfen nur, wenn sie beim Abschluss geprüft werden. Prüfe deshalb jede in diesem Durchlauf berührte Spec, das Projektprofil und die Projekt-Docs nach `agentic-harness/document-contract.md` („Aktueller Stand statt Verlauf“):
  1. Je AK steht nur der letzte gültige Nachweis; Verlaufsreste (frühere Stände, Umbau-Notizen, Vergleiche mit alten Commits) sind entfernt.
  2. Jedes geänderte oder neue AK hat genau ein unabhängig bewertbares Ergebnis (`agentic-harness/specs/S000-readme.md`).
  3. Die berührten Dateien widersprechen einander nicht (z. B. eine Entscheidung im Projektprofil als offen, in einer Doc als entschieden).
  4. Liegt eine Datei über ihrer Richtgröße, verdichte sie jetzt oder nenne in der Übergabe, dass sie geteilt werden sollte.
  Funde in den eigenen Änderungen korrigierst du vor dem Abschluss; ältere Funde nennst du in der Übergabe, statt sie ungefragt umzubauen.
- Ist keine Produktspec erforderlich (z. B. bei verhaltensgleichem Refactor oder Dokuänderung), prüfe den beauftragten Umfang und passende Nachweise ohne künstliche Spec. Für reine Doku- oder Prozesspflege kein bestandenes Produkt-Gate behaupten.
- Bei fehlendem Soll, fehlenden Nachweisen, gescheiterten Checks oder Abweichungen: kein vollständiger Abschluss. Folge `agentic-harness/harness/verification/fail.md` und berichte, was offen oder blockiert ist. Diese Datei führt keine Checks aus und setzt keinen Status automatisch.
- Übergib das Ergebnis mit einer knappen Übersicht der geänderten Dateien; bei Dokumentationsarbeit nenne insbesondere die bearbeiteten Markdown-Dateien. Berichte außerdem passende Prüfergebnisse und offene Punkte.

## Kurzer Weg für Oberflächen-Iterationen

Für kleine, umkehrbare Anpassungen an Gestaltung, Text oder Layout **innerhalb** bestehender Specs darf das Gate verkürzt laufen. Voraussetzung: kein neues oder geändertes Nutzerverhalten, kein neues oder geändertes Akzeptanzkriterium, keine neue Produktentscheidung und kein Statuswechsel einer Spec.

1. **Soll:** die im Auftrag genannten Änderungen plus die unveränderten Grenzen aus `agentic-harness/harness/project.md` und die Regeln aus `agentic-harness/docs/design.md`. `requirements.md` muss dafür nicht eigens geladen werden.
2. **Ist und Nachweis:** der tatsächliche Diff, Build und betroffene Tests auf aktuellem Stand sowie ein Nachweis des geänderten Bereichs im Zielmedium (bei Websites im Browser; Messwerte oder Screenshot) bei den im Projektteil von `agentic-harness/docs/testing.md` genannten Prüfgrößen. Nicht Gemessenes als offen nennen.
3. **Ergebnis:** knapp berichten, mit Mini-Spur nach `agentic-harness/harness/core.md` Abschnitt 4.

Prüfumfang beim kurzen Weg: der geänderte Bereich und tatsächlich betroffene gemeinsame Bausteine, kein Gesamtaudit. Ändert die Iteration einen bestehenden Designwert oder hält sie eine Auftraggeber-Entscheidung als Wert in `agentic-harness/docs/design.md` fest, bleibt es beim kurzen Weg. Den vollen Weg erzwingen neue Nutzerabläufe, neue oder geänderte AK, Freigaben oder eine neue übergreifende Gestaltungsregel.
