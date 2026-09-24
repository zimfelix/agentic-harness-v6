# Project Init – einmal pro neuem Projekt

> **Verantwortung:** Diese Vorlage führt durch die einmalige Initialisierung eines konkreten Projekts. Sie legt fest, welche Fakten und Regeln wohin gehören, damit der Harness nicht blind oder doppelt befüllt wird.

Vor der ersten Implementierung das Projektprofil klären; später nur betroffene Themen neu prüfen, nicht den gesamten Katalog wiederholen. Lies `harness/rules/universal/core.md`. Bei bestehendem Code zuerst Einstieg, Hauptablauf (Eingabe → Logik → Ergebnis), Verantwortlichkeiten, Zustand und vorhandene Tests nachvollziehen; Fakten daraus im Projektprofil festhalten. Stelle bei offenen Produkt- oder Sicherheitsentscheidungen gezielte Fragen, statt Antworten zu erfinden.

## Relevanzcheck

Prüfe jede Ebene kurz: **bekannt**, **offen**, **nicht zutreffend** oder **später relevant**. Vertiefe nur das, was für den ersten sinnvollen Nutzerablauf oder ein aktuelles Risiko wichtig ist:

1. **Problem und Nutzer:** Für wen, welcher Nutzen, MVP und Nicht-Ziele?
2. **Produkt/UX:** Wichtigster Ablauf, Bedienung und Fehlerzustände?
3. **Domäne:** Begriffe, Regeln und erlaubte Zustandswechsel?
4. **Daten:** Herkunft, Speicherung, Erhalt und Schutz?
5. **Architektur:** Bausteine, Verantwortlichkeiten und Abhängigkeiten?
6. **Schnittstellen:** Externe Systeme, Verträge, Zugriffe und Fehlerfälle?
7. **Technologie:** Plattform, Runtime, Werkzeuge und Versionen?
8. **Zusammenarbeit:** Sprache, Erklärniveau, Rückfrage- und Review-Grenzen, Commit-/Push-Freigabe?
9. **Qualität/Sicherheit:** Welche Nachweise sind nötig; wie werden Secrets, echte und Testdaten sowie irreversible Aktionen geschützt?
10. **Betrieb:** Wie starten, bauen und gegebenenfalls deployen; wie Fehler erkennen und Daten wiederherstellen?

## Ergebnis und Zuständigkeiten

- **`harness/rules/project-specific/project.md`:** Halte die geklärten Projektfakten, MVP-Grenzen, grobe Architektur, Startweg, Qualitätsplan und Lieferregel fest. Markiere wichtige offene Punkte; erfinde keine Fakten. Entferne `Pending Project Init` erst, wenn die für den ersten Umsetzungsschritt nötigen Entscheidungen geklärt sind. Das bedeutet **nicht**, dass bereits alle künftigen Features oder Checks fertig sein müssen.
- **Projektbezogene `AGENTS.md`:** Ergänze nur knappe Projektgrenzen und Verweise auf tatsächlich geltende Regeln; bestehende Projektanweisungen nicht überschreiben. Die globalen Agent-Dateien von Pi und Codex bleiben bei Project Init unverändert.
- **Weitere `project-specific/*.md`:** Fülle nur die benötigten Kategorien: `code.md` für projektweite Code-/Architekturkonventionen, `python.md` oder `web.md` für verwendete Plattformen, `testing.md` für besondere Testkonventionen. `quality-matrix.md` ist nur bei mehreren Bereichen oder erklärungsbedürftigen Ausnahmen nötig. Nicht passende Dateien bleiben sichtbar mit `Pending Project Init` und werden nicht als Regeln geladen. Verwende die Zuständigkeitskarte in `README.md`; kopiere Regeln nicht in mehrere Dateien. Neue Kategorien (z. B. API-Vertrag oder Migrationen) nur bei konkretem Bedarf.
- **Projekt-README:** Ersetze die Starter-Kit-Einleitung durch Projektziel und Start; passe den Gate-Abschnitt an den tatsächlichen Testeinstieg an. Erhalte die Zuständigkeitskarte, auf die `AGENTS.md` verweist. Eine bereits vorhandene README ergänzen, nicht überschreiben.
- **`learning-state.md`:** Entferne kopierte Starter-Kit-Learnings und nutze die Datei als knappe, manuelle Sammlung bestätigter Erkenntnisse aus diesem Projekt. Aktualisiere sie nicht während eines Gesprächs; nur auf ausdrücklichen Sammelauftrag am Ende eines Chats/Tages. Projektfortschritt bleibt in Projekt-README, Specs und Git nachvollziehbar. Bei späterer Sichtung können übertragbare Erkenntnisse markiert und nur auf ausdrücklichen Auftrag in globale Agent-Dateien kuratiert werden.
- **Quality Gate:** Wähle passende ausführbare Checks für die vorhandenen Bereiche und nenne den Gate-Einstieg in `project.md`. Bei Nutzung des fertigen Python-Runners erstellt der Agent `harness/rules/project-specific/quality-gate.json` mit den projektbezogenen Befehlen; ohne Python richtet er stattdessen einen projekttypischen Gate-Einstieg ein. Markdown-Dateien konfigurieren oder ändern Skripte nicht von selbst. Prüfe beim Einrichten, ob die Checks tatsächlich etwas prüfen; ein Befehl, der ohne Tests erfolgreich endet, ist kein Nachweis. Noch fehlende Anwendungstests entstehen mit den ersten Specs. Solange keine sinnvollen Checks möglich sind, bleibt das Gate unkonfiguriert und rot. Spätestens vor `State: Implemented` einer ersten Story müssen echte Checks eingerichtet und bestanden sein. Wird der Runner geändert oder ersetzt, teste dessen Erfolgs- und Fehlerfall gesondert; die Starter-Kit-Tests werden nicht ins Projekt kopiert (siehe `README.md`).

Beispiel **nur für ein Python-Projekt mit pytest und vorhandenen Tests** (an das Projekt anpassen):

```json
{
  "checks": [
    {"name": "Tests", "command": ["python3", "-m", "pytest", "-q"], "cwd": "."}
  ]
}
```

`command` ist ein Argument-Array, kein Shell-String; `cwd` muss auf einen bestehenden Projektordner zeigen. Eine erste konkrete Nutzfunktion erhält vor der Implementierung eine Spec nach `harness/templates/story.md`. Ideas sind nur für größere ungeklärte Vorhaben nötig.
