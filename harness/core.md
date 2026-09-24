# Core – Arbeitsablauf von Auftrag bis Übergabe

> **Zuständigkeit:** Ein gemeinsamer Arbeitsablauf; keine Produktfakten, Testbefehle oder zweite Kopie des Gates.

1. Ordne die Aufgabe und das betroffene Projekt ein. Lies `harness/project.md`; solange dort `Pending Project Init` steht, nutze vor der ersten Produktimplementierung `harness/init.md`. Erfinde keine Projektfakten.
2. Kläre Ziel und Umfang. Ein größeres, offenes Vorhaben kann zuerst als Idea unter `ideas/` geklärt werden; erst Bestätigung **und** Umsetzungsauftrag führen zu Specs. Für beauftragtes neues oder geändertes Nutzerverhalten erstelle beziehungsweise aktualisiere eine Spec unter `specs/`. Ein verhaltensgleicher Refactor oder eine reine Dokuänderung braucht nicht automatisch eine neue Produktspec.
3. Lies nur die relevanten, bereits geltenden Dateien aus `docs/`. Kläre Berechtigungen, echte Daten und irreversible Aktionen vor ihrer Ausführung. Setze die kleinste passende Änderung um; bei neuem Umfang prüfe betroffene Specs und Projektgrenzen erneut.
4. Prüfe Änderungen nach `harness/verification/gate.md` gegen Auftrag und tatsächliches Verhalten. Bei Fehlern gilt `harness/verification/fail.md`. Für reine Prozess-/Dokumentationsänderungen ohne Produktspec prüfe insbesondere betroffene Verweise und Widersprüche; behaupte dabei kein erfolgreiches Produkt-Gate.
5. Melde Ergebnis, tatsächlich ausgeführte Prüfungen und offene Punkte. Setze eine Produktspec nur dann auf `Implemented`, wenn **alle** betroffenen Akzeptanzkriterien belegt sind und das erforderliche Gate tatsächlich bestanden wurde; andernfalls bleibt sie `Modified` und die Arbeit wird gegebenenfalls als blockiert berichtet.
