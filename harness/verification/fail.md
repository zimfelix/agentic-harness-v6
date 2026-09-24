# Fehlschlag – Ursache eingrenzen und offen melden

> **Zuständigkeit:** Umgang mit fehlgeschlagener, fehlender oder unvollständiger Verifikation.

1. Stoppe den Abschluss: keine unbelegte `Implemented`-Markierung und kein „fertig“, solange relevante Kriterien offen sind.
2. Nenne den ersten konkreten Fehler, den betroffenen Nachweis und die Beobachtung. Trenne Codefehler, Test-/Umgebungsfehler und unklare oder widersprüchliche Spec; erfinde keine Ursache.
3. Korrigiere gezielt und wiederhole die betroffene Prüfung plus die erforderlichen Gate-Checks. Wenn die Ursache nicht geklärt werden kann oder eine Freigabe fehlt, stoppe die Reparaturschleife und melde den Blocker.
4. Berichte, was bestanden hat, was fehlgeschlagen ist und was gar nicht geprüft werden konnte. Änderungen am Soll klärst du mit dem Auftraggeber, statt einen fehlschlagenden Test nur für ein grünes Ergebnis umzuschreiben.
