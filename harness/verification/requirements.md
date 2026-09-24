# Anforderungen – Auftrag und Akzeptanzkriterien abgleichen

> **Zuständigkeit:** Prüfen, ob die Änderung dem beauftragten Soll entspricht; keine Wiederholung der Spec.

- Welche beauftragte Spec und welche Akzeptanzkriterien (AK) sind betroffen? Bei neuem/geändertem Nutzerverhalten ohne Spec erst den Auftrag klären; eine Idea allein genügt nicht.
- Stimmen Ziel, Nicht-Ziele und relevante Fehlerfälle mit dem Auftrag überein, ohne unerlaubte Nebenwirkungen oder neue Berechtigungen?
- Bleiben die bestätigten Projektgrenzen aus `harness/project.md` gewahrt? Prüfe bei Strukturänderungen `docs/architecture.md` auf Widersprüche; eine geplante Architektur ist nicht automatisch implementiert.
- Sind weitere bestehende Specs vom neuen Verhalten betroffen? Passe nur tatsächlich veränderte Anforderungen an und markiere sie bis zum Nachweis `Modified`.

**Ergebnis:** Betroffene AK, Grenzen und Abweichungen benennen. Hier wird das Soll geprüft; tatsächliche Testergebnisse gehören nach `implementation.md`.
