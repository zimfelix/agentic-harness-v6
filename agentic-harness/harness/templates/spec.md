# [Spec – beauftragtes Verhalten]

> **Vorlage:** Konkreter Auftrag mit überprüfbarem Soll; ausgefüllte Specs liegen unter `agentic-harness/specs/`.

- **State:** Modified
- **Ziel und Nutzer:** [Wozu wird die Änderung benötigt?]
- **Beschreibung:** [Beobachtbares Verhalten, ohne technischen Lösungsplan.]
- **Nicht im Umfang:** [Bewusste Abgrenzung.]

## Akzeptanzkriterien

- **AK1:** [Ein einzeln prüfbares Verhalten mit klarem Pass/Fail, in ein bis drei Sätzen. Kein Layout-Detail in Pixeln oder Farben: Gestaltung steht in `agentic-harness/docs/design.md`.]
- **AK2:** [Ein relevanter Erfolgs- oder Fehlerfall, falls benötigt.]

## Nachweise

Pro AK nur der **letzte gültige** Nachweis auf dem aktuellen Stand; ersetzte Nachweise löschen, nicht als „früherer Stand“ behalten. Verlauf steht in Git.


- **AK1:** [Prüfziel · Test oder Prüfschritte · geprüfter Stand (Commit oder „uncommittet, Datum Uhrzeit“) · Ergebnis.]
- **AK2:** [Nachweis, falls vorhanden.]
- **Gate:** [Tatsächlich ausgeführter Projektbefehl und Ergebnis.]

Bei inhaltlicher Änderung an einer bereits implementierten Spec zunächst `Modified`. `Implemented` erst nach gültigen Nachweisen für **sämtliche** geltenden AK und bestandenem `agentic-harness/harness/verification/gate.md`; sonst `Modified` und Blocker offen berichten. Bei verhaltensgleichem Refactor ohne Spec-Änderung keinen künstlichen Statuswechsel auslösen. Vorlagen-Platzhalter nicht als bestandene Nachweise übernehmen.
