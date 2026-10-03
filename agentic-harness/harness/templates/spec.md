# [Spec – Bereich]

> **Vorlage:** Lebender Soll-Stand eines Bereichs mit überprüfbaren Kriterien; ausgefüllte Specs liegen unter `agentic-harness/specs/` (Regeln: `agentic-harness/specs/S000-readme.md`).

- **State:** Modified
- **Bereich:** [Welcher Teil des Produkts? Abgrenzung zu benachbarten Bereichs-Specs.]
- **Zuletzt geändert durch:** [Idea, z. B. `ideas/I005-konto.md`, oder „direkter Auftrag“.]
- **Ziel und Nutzer:** [Wozu dient der Bereich?]
- **Beschreibung:** [Beobachtbares Verhalten, ohne technischen Lösungsplan.]
- **Nicht im Umfang:** [Bewusste Abgrenzung.]

## Akzeptanzkriterien

<!-- Mehr als etwa 15 AK oder unabhängig prüfbare Gruppen? Dann mehrere Specs (Zuschnitt: agentic-harness/specs/S000-readme.md). -->

- **AK1:** [Ein einzeln prüfbares Verhalten mit klarem Pass/Fail, in ein bis drei Sätzen. Kein Layout-Detail in Pixeln oder Farben: Gestaltung steht in `agentic-harness/docs/design.md`.]
- **AK2:** [Ein relevanter Erfolgs- oder Fehlerfall, falls benötigt.]

## Nachweise

Pro AK nur der **letzte gültige** Nachweis auf dem aktuellen Stand; ersetzte Nachweise löschen, nicht als „früherer Stand“ behalten. Verlauf steht in Git.


- **AK1:** [Prüfziel · Test oder Prüfschritte · geprüfter Stand (Commit oder „uncommittet, Datum Uhrzeit“) · Ergebnis.]
- **AK2:** [Nachweis, falls vorhanden.]
- **Gate:** [Tatsächlich ausgeführter Projektbefehl und Ergebnis.]

Bei inhaltlicher Änderung an einer bereits implementierten Spec zunächst `Modified`. `Implemented` erst nach gültigen Nachweisen für **sämtliche** geltenden AK und bestandenem `agentic-harness/harness/verification/gate.md`; sonst `Modified` und Blocker offen berichten. Bei verhaltensgleichem Refactor ohne Spec-Änderung keinen künstlichen Statuswechsel auslösen. Vorlagen-Platzhalter nicht als bestandene Nachweise übernehmen.
