# Gate – Prüfungen verbinden, Abschluss entscheiden

> **Zuständigkeit:** Abschlussregel für eine konkrete Änderung; kein Ersatz für ausgeführte Tests.

1. Gleiche Auftrag, betroffene Spec und Projektgrenzen nach `requirements.md` ab. Neue Nutzerfunktion ohne Spec ist nicht abschließbar; bei Aufgaben ohne Produktspec den beauftragten Umfang direkt prüfen.
2. Prüfe Diff und beobachtbares Verhalten nach `implementation.md`. `agentic-harness/docs/testing.md` beschreibt die geltende Testpraxis, `tests/` enthält ausführbare Tests; die konkreten Befehle kommen ausschließlich aus dem initialisierten `agentic-harness/harness/project.md`.
3. Erfasse für jedes betroffene Akzeptanzkriterium den **tatsächlich ausgeführten** Nachweis und sein Ergebnis. Ein Build allein, eine leere Testsuite oder ein nicht eingerichteter Prüf-Einstieg belegen Nutzerverhalten nicht.
4. `Implemented` ist nur bei erfüllten Anforderungen, belegten AK und bestandenen erforderlichen Checks zulässig. Fehlt etwas, gilt `fail.md`; melde die Lücke. Bei reiner Pflege von Prozessdokumenten ohne Produktspec prüfe betroffene Texte, Pfade und Widersprüche, ohne ein Produkt-Gate zu behaupten. Dieses Markdown führt keine Checks aus und setzt keinen Status automatisch.
