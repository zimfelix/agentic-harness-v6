# Verification Loop

**Gilt bei:** Während der Arbeit und vor Abschluss jeder Änderung. Projektstrategie aus `harness/project.md` und `docs/testing.md`; weitere Docs/Profile nach den Auslösern in `AGENTS.md`.

```text
beauftragtes Soll → Änderung → aktuelle Checks → Soll durch Nachweise belegt?
                                      ↑             │ ja → nachführen / übergeben
                                      └─ Ursache ←─┘ nein
```

## Prüfen

1. **Soll:** Auftrag, Projektgrenzen/Freigaben und betroffene Specs abgleichen. Zugehörige Idea muss „Beauftragt“ sein. Bei Struktur/Sichtbarem auch beschlossene Architektur/Gestaltung prüfen. Ohne verbindliches Soll zurück zur Klärung.
2. **Ist:** Diff und tatsächlichen Baum prüfen: ganzer Auftrag erfüllt, keine schmalere/leichter testbare Ersatzlösung, keine unbeauftragten Extras, Code korrekt eingeordnet, gemeinsame Werte/Bausteine genutzt? Geplantes nicht als Ist ausgeben.
3. **Nachweise:** Pflichtchecks und betroffene Regression auf aktuellem Stand wirklich ausführen. Jeden betroffenen Prüfpunkt/AK einem Test oder begründeten manuellen Check zuordnen, an der Grenze des Nutzerablaufs (CLI, API, UI). Prüfmengen müssen den beauftragten Umfang decken; leere, fehlende oder veraltete Routen/Zustände/Fixtures sind kein Nachweis. Build, Lint, leere Suite und geplante Befehle allein belegen kein Verhalten. Fehlender Pflichtcheck wird eingerichtet oder als Blocker gemeldet, nicht still abgewählt.
4. **Oberfläche:** Im Zielmedium technische Eigenschaften messen und optische Wirkung per Screenshot prüfen, bei den festgelegten Prüfgrößen. Quelltextvergleich belegt kein Aussehen. Kleine Iteration: geänderter Bereich und betroffene gemeinsame Bausteine, kein pauschales Gesamtaudit. Umfangreiche Umbauten/Livegang folgen zusätzlich dem gewählten Profil.
5. **Nachführen:** Berührte Projektdateien widerspruchsfrei und aktuell? Je AK ein Ergebnis und letzter gültiger Nachweis, keine Verlaufsreste oder doppelten Werte (`document-contract.md`). Letztes Befehlsresultat ersetzen; Arbeitsstand und Idea-Teilaufgaben aktualisieren. Relevante Änderungen an Code, Konfiguration, Testdaten oder Umgebung entwerten den alten Nachweis; Git-Commit/Exit-Code allein genügt nicht.

## Entscheidung und Rückweg

- Vollständig nur, wenn das Soll durch aktuelle Nachweise belegt ist und alle Pflicht-/Regressionstests bestanden sind. Spec `Implemented` nur bei gültigen Nachweisen für **sämtliche** geltenden AK; veraltete Nachweise bleiben nicht gültig, nur weil ein AK unverändert ist. Vollständig umgesetzte Idea abschließen und archivieren.
- Fehlendes Soll/Freigabe → klären; fehlende Prüfstrategie → Strategie festlegen; fehlende Umgebung/Befehl → Einrichtung klären; Umsetzungs-/Testfehler → begründete Ursache korrigieren. Stille Fallbacks (Leerwert, Log-und-weiter) auf verdeckten Fehler/Teilzustand prüfen; vereinbarte degradierte Betriebsarten müssen sichtbar und belegt sein. AK nicht verändern, nur damit Tests grün werden.
- Nach Korrektur betroffene Checks und Soll-Abgleich wiederholen. Wiederholt derselbe Fehler sich, Hypothese überprüfen; nach zwei erfolglosen Korrekturen derselben Ursache oder externem Blocker stoppen.
- Bestanden, fehlgeschlagen und nicht ausgeführt getrennt berichten. Neue/geänderte Spec bleibt bei Lücken `Modified`. Refactor ohne Solländerung braucht keinen künstlichen Spec-Statuswechsel.
- Doku-/Harness-Pflege: betroffene Definitionen/Statusregeln, Ladeauslöser, Verweise, Werkzeugabhängigkeiten sowie Kopier-/Exportverhalten gemäß Dokumentenvertrag abgleichen; kein bestandenes Produkt-Gate behaupten. Statische Checks belegen keine zuverlässige Agentenleistung.

Kleine Oberflächen-Iteration ohne neues Verhalten/AK braucht keine Specänderung; Auftrag, geltende Designregeln, Diff und gezielte Nachweise genügen. Eine neue Produktentscheidung geht vorher zurück zur Klärung.
