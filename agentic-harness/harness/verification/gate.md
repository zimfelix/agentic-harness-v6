# Gate – Soll und belegtes Ist zusammenführen

> - **Typ:** Prozess
> - **Zuständigkeit:** Entscheiden, ob eine konkrete Änderung innerhalb des Auftrags ausreichend nachgewiesen ist.
> - **Gilt bei:** Abschluss einer Änderung nach dem Ablauf in `harness/core.md`.
> - **Ladebeziehungen:** Vorher `harness/project.md` für Grenzen und aktive Prüfungen; dann `harness/verification/requirements.md` für das Soll und `harness/verification/implementation.md` für Ist und Nachweise. Beim kurzen Weg für Oberflächen-Iterationen stattdessen `docs/design.md`. Für die Prüfung berührter Projektdateien `document-contract.md` („Aktueller Stand statt Verlauf“), bei Specs zusätzlich `specs/S000-readme.md`. Bei einer Lücke `harness/verification/fail.md`.
> - **Nicht zuständig:** Projekt-Tests festlegen oder selbst ausführen; Anforderungen und Nachweise stehen in den jeweils zuständigen Dateien.

## Entscheidungsweg

Schematische Übersicht mit verkürzten Dateinamen; je Datei steht, was sie liest und liefert. Bei Änderungen an Harness-Rollen oder Ladewegen auch dieses Diagramm gegen `AGENTS.md` und `harness-map.md` prüfen.

```text
WÄHREND DER ARBEIT   core.md (Schritt 3): ändern → messen → korrigieren
                     welche Checks: testing.md · womit: Befehle aus project.md
        ▼
WEICHE   gate.md: reine Oberflächen-Iteration (kein neues Verhalten, AK oder Entscheidung)?
  ├─ ja ──▶ KURZER WEG (Abschnitt unten)
  │          Soll = Auftrag + design.md (Gestaltungsregeln) + project.md (Grenzen)
  │          Ist  = Diff, Build/Tests, Nachweis im Zielmedium bei den Prüfgrößen aus testing.md
  │          ──▶ Übergabe (core.md, Abschnitt 4)
  └─ nein ─▶ VOLLER WEG
        ▼
SOLL   requirements.md – „Was muss stimmen?“
         liest   Auftrag · project.md (Grenzen, Freigaben) · specs/Snnn (AK)
                 · ideas/Innn (muss „Beauftragt“ sein) · architecture.md (bei Struktur)
                 · design.md (bei Sichtbarem)
         liefert Prüfpunkte bzw. AK + offene Widersprüche; fehlt das Soll → Lücke
        ▼
IST    implementation.md – „Was ist tatsächlich belegt?“
         liest   Soll · Diff · testing.md (Prüfung je Risiko) · project.md (eingerichtete Befehle)
                 · code.md (Einordnung, Kopien)
         liefert je Prüfpunkt Test oder manuelle Prüfung auf aktuellem Stand,
                 gerendert im Zielmedium; Fehlendes = „nicht verifiziert“, nie PASS
        ▼
ENTSCHEIDUNG   gate.md
   ① Soll durch Ist belegt?  (grüner Build allein reicht nicht)
   ② berührte Projektdateien sauber? Punkte 1–5: document-contract.md (Stand statt Verlauf,
     Widersprüche, Richtgröße) · S000-readme.md (ein Ergebnis je AK) · I000-readme.md (Idea)
  ├─ ja ──▶ erledigte Teilaufgaben der Idea abhaken; Spec „Implemented“ nur, wenn alle ihre AK
  │         belegt sind (S000); Idea „Umgesetzt“ → ideas/archiv/, wenn ihr ganzer Umfang erledigt ist (I000)
  │         ──▶ Übergabe (core.md, Abschnitt 4): Ergebnis, Dateien, Prüfungen, Offenes
  └─ nein ─▶ fail.md – „Wo liegt die Ursache?“
               Soll unklar       → Auftraggeber fragen → Spec bzw. project.md
               Gestaltungsregel  → design.md
               Prüfauswahl       → testing.md
               Befehl fehlt      → einrichten, dann project.md
               Umsetzung / Test  → Code bzw. Tests (nur die begründete Ursache)
             ──▶ betroffene Checks + Gate erneut
             2× dieselbe Ursache gescheitert oder Blocker ──▶ stoppen; bestanden,
             gescheitert und nicht ausgeführt getrennt berichten
```

## Entscheidung

Requirements und Implementation lesen `harness/project.md` und öffnen die für ihre Prüfung nötigen Specs oder Projekt-Docs nach den jeweiligen Auslösern – auch wenn diese bei der Umsetzung noch nicht geladen waren.

- Gleiche das Soll aus `harness/verification/requirements.md` mit der beobachteten Änderung und den tatsächlich ausgeführten Nachweisen aus `harness/verification/implementation.md` ab. Ein grüner Build oder Testlauf allein belegt nicht, dass der beauftragte Ablauf und die Projektgrenzen erfüllt sind. Nach `docs/testing.md` für betroffene Risiken vorgesehene, aber nicht nachgewiesene Checks bleiben Lücken.
- Bei beauftragtem Nutzerverhalten: Jedes betroffene Akzeptanzkriterium muss belegt sein; erforderliche Prüfungen müssen bestanden sein. `Implemented` setzt zusätzlich gültige Nachweise für sämtliche übrigen geltenden AK der Spec voraus (`specs/S000-readme.md`). Trage in der Spec den neuen Nachweis **anstelle** des alten ein und im Projektprofil nur das letzte Prüfergebnis; Einzelheiten des Durchlaufs gehören in die Übergabe, nicht als neuer Absatz in Projektdateien.
- **Projektdateien prüfen, bevor das Ergebnis gilt:** Die Regeln für Specs und Projektdateien helfen nur, wenn sie beim Abschluss geprüft werden. Prüfe deshalb jede in diesem Durchlauf berührte Spec, das Projektprofil und die Projekt-Docs nach `document-contract.md` („Aktueller Stand statt Verlauf“):
  1. Je AK steht nur der letzte gültige Nachweis; Verlaufsreste (frühere Stände, Umbau-Notizen, Vergleiche mit alten Commits) sind entfernt.
  2. Jedes geänderte oder neue AK hat genau ein unabhängig bewertbares Ergebnis (`specs/S000-readme.md`).
  3. Die berührten Dateien widersprechen einander nicht (z. B. eine Entscheidung im Projektprofil als offen, in einer Doc als entschieden).
  4. Liegt eine Datei über ihrer Richtgröße, verdichte sie jetzt oder nenne in der Übergabe, dass sie geteilt werden sollte.
  5. Gehört die Arbeit zu einer Idea: Sind die dort genannten Bereichs-Specs und Docs nachgeführt? Hake die in diesem Durchlauf erledigten und belegten Teilaufgaben ab. Ist der Umfang vollständig umgesetzt, setze sie auf „Umgesetzt“, trage den Abschluss ein und verschiebe sie nach `ideas/archiv/`; sonst bleibt sie „Beauftragt“ und der Rest wird in der Übergabe genannt.
  Funde in den eigenen Änderungen korrigierst du vor dem Abschluss; ältere Funde nennst du in der Übergabe, statt sie ungefragt umzubauen.
- Ist keine Produktspec erforderlich (z. B. bei verhaltensgleichem Refactor oder Dokuänderung), prüfe den beauftragten Umfang und passende Nachweise ohne künstliche Spec. Für reine Doku- oder Prozesspflege kein bestandenes Produkt-Gate behaupten.
- Bei fehlendem Soll, fehlenden Nachweisen, gescheiterten Checks oder Abweichungen: kein vollständiger Abschluss. Folge `harness/verification/fail.md` und berichte, was offen oder blockiert ist. Diese Datei führt keine Checks aus und setzt keinen Status automatisch.
- Übergabe nach `harness/core.md`, Abschnitt 4; bei Dokumentationsarbeit die bearbeiteten Markdown-Dateien nennen.

## Kurzer Weg für Oberflächen-Iterationen

Für kleine, umkehrbare Anpassungen an Gestaltung, Text oder Layout **innerhalb** bestehender Specs darf das Gate verkürzt laufen. Voraussetzung: kein neues oder geändertes Nutzerverhalten, kein neues oder geändertes Akzeptanzkriterium, keine neue Produktentscheidung und kein Statuswechsel einer Spec.

1. **Soll:** die im Auftrag genannten Änderungen plus die unveränderten Grenzen aus `harness/project.md` und die Regeln aus `docs/design.md`. `requirements.md` muss dafür nicht eigens geladen werden.
2. **Ist und Nachweis:** der tatsächliche Diff, Build und betroffene Tests auf aktuellem Stand sowie ein Nachweis des geänderten Bereichs im Zielmedium (bei Websites im Browser; Messwerte oder Screenshot) bei den im Projektteil von `docs/testing.md` genannten Prüfgrößen. Nicht Gemessenes als offen nennen.
3. **Ergebnis:** knapp berichten nach `harness/core.md` Abschnitt 4.

Prüfumfang beim kurzen Weg: der geänderte Bereich und tatsächlich betroffene gemeinsame Bausteine, kein Gesamtaudit. Ändert die Iteration einen bestehenden Designwert oder hält sie eine Auftraggeber-Entscheidung als Wert in `docs/design.md` fest, bleibt es beim kurzen Weg. Den vollen Weg erzwingen neue Nutzerabläufe, neue oder geänderte AK, Freigaben oder eine neue übergreifende Gestaltungsregel.
