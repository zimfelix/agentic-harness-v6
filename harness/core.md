# Core – Arbeitsablauf von Auftrag bis Übergabe

> **Zuständigkeit:** Ein gemeinsamer Arbeitsablauf; keine Produktfakten, Testbefehle oder zweite Kopie des Gates.

1. Lies `harness/project.md`. Solange dort `Pending Project Init` steht, nutze `harness/init.md` und beginne keine Produktimplementierung auf Basis angenommener Fakten.
2. Kläre Ziel und Umfang. Größere oder offene Vorhaben können zuerst als Idea unter `ideas/` geklärt werden; das ist noch kein Umsetzungsauftrag. Für beauftragtes neues oder geändertes Verhalten erstelle beziehungsweise aktualisiere eine Spec unter `specs/`. Ein verhaltensgleicher Refactor braucht nicht automatisch eine neue Spec.
3. Lade nur die für die Aufgabe passenden Dateien aus `docs/`. Kläre kritische Berechtigungen, echte Daten und irreversible Aktionen vor ihrer Ausführung. Setze die kleinste passende Änderung um.
4. Prüfe nach `harness/verification/gate.md` gegen Auftrag und tatsächliches Verhalten. Bei Fehlern gilt `harness/verification/fail.md`.
5. Melde Ergebnis, ausgeführte Prüfungen und offene Punkte. Setze eine Spec nur dann auf `Implemented`, wenn **alle** betroffenen Akzeptanzkriterien belegt sind und das erforderliche Gate tatsächlich bestanden wurde; andernfalls bleibt sie `Modified` beziehungsweise wird als blockiert berichtet. Keine Behauptung über nicht ausgeführte Prüfungen.
