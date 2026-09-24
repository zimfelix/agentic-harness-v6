# Fehlschlag – Ursache eingrenzen und offen melden

> **Zuständigkeit:** Umgang mit fehlgeschlagener, fehlender oder unvollständiger Verifikation.

1. Stoppe den Abschluss: kein unbelegtes „fertig“ bei offenen AK oder erforderlichen Checks. Eine neue, geänderte oder nachweislich nicht erfüllte Spec bleibt beziehungsweise wird `Modified`; bei einem verhaltensgleichen Refactor ohne Spec-Änderung erfolgt kein automatischer Statuswechsel.
2. Benenne den ersten Fehler mit beobachtetem Ergebnis. Unterscheide fehlende Spec/Freigabe, Implementierungsfehler, defekten Test und fehlende Testumgebung. Prüfe, ob tatsächlich die geänderte Version getestet wurde; Ursachen sind bis zum Nachweis Hypothesen.
3. Behebe nur eine begründete Ursache und wiederhole den betroffenen Nachweis sowie das erforderliche Gate. Erscheint derselbe Fehler trotz Korrektur erneut, untersuche die Annahme statt dieselbe Aktion endlos zu wiederholen. Ändere das Soll nur nach Klärung des Auftrags.
4. Fehlen Entscheidung, Umgebung oder Nachweis, stoppe und berichte den Blocker sowie bestandene, fehlgeschlagene und nicht ausgeführte Checks. `fail.md` führt selbst keine automatische Reparatur aus.
