# Gate – Prüfungen verbinden, Abschluss entscheiden

> **Zuständigkeit:** Abschlussregel für eine konkrete Änderung; kein Ersatz für ausgeführte Tests.

1. Gleiche Auftrag, betroffene Spec und Grenzen mit `requirements.md` ab.
2. Prüfe Änderung und beobachtbares Verhalten mit `implementation.md`; beachte dabei `docs/testing.md` und den projektspezifischen Prüf-Einstieg aus `harness/project.md`.
3. Halte pro betroffenem Akzeptanzkriterium den tatsächlich ausgeführten Nachweis und sein Ergebnis fest. Eine Prüfung ohne wirksame Checks, eine bloße Build-Meldung bei Verhaltensanforderungen oder ein nicht eingerichtetes Gate gelten nicht als Erfolg.
4. Nur wenn die Anforderungen erfüllt, die erforderlichen Nachweise erbracht und alle geltenden Checks bestanden sind, darf die betroffene Spec `Implemented` werden. Ansonsten `fail.md` folgen und die Grenze der Prüfung berichten. Das Gate setzt keine Statuswerte automatisch.
