# Agentic Harness – Einstieg

> **Verantwortung:** Diese Datei ist die Einstiegskarte für Agenten im Projektroot. Sie verweist auf Core, Project Init, Templates und Learning State, ohne die Regeln selbst zu duplizieren.

Nutze diese Einstiegskarte im Root des Projekts. Lies `harness/rules/universal/core.md`. Steht `harness/rules/project-specific/project.md` noch auf `Pending Project Init`, nutze `harness/templates/project-init.md`; danach lies das Projektprofil und nur passende, bereits definierte Projektrichtlinien. Bei größeren unklaren Vorhaben: `harness/rules/universal/ideas.md` und `harness/templates/idea.md`; für konkrete Specs: `harness/templates/story.md`; für die Auswahl von Nachweisen: `harness/rules/universal/quality.md`. `learning-state.md` ist die lokale Sammelstelle. Ergänze sie nur, wenn Felix ausdrücklich sagt, Erkenntnisse oder eine Zusammenfassung dort zu speichern; nie automatisch nach einzelnen Nachrichten. Wenn Felix sagt, den Learning State in die globale/universelle `AGENTS.md` zu „pushen“ oder zu übertragen, kuratiere die allgemeinen Learnings in `~/.pi/agent/AGENTS.md` und `~/.codex/AGENTS.md` gemäß deren Regeln. Kopiere nicht die ganze Datei; „Push“ meint hier nicht `git push`. Universelle Prozessregeln und Freigabegrenzen stehen im Core, nicht erneut hier.

## Harness-Regeln pflegen

Prüfe vor jeder Ergänzung anhand der Zuständigkeitskarte in `README.md`, welche Datei die Aussage besitzt. Vergleiche nur diese Datei und thematisch benachbarte Dateien auf gleichbedeutende Regeln oder Widersprüche; ergänze die Regel einmal am zuständigen Ort und verweise anderswo nur darauf. Kontrolliere nach der Änderung den Diff auf Überschneidungen, falsche Pfade und überholte Verweise. Eine Textsuche unterstützt den Abgleich, ersetzt aber nicht die inhaltliche Prüfung.

<!-- Project Init: Hier nur projektspezifische Pfade, Grenzen und Freigaberegeln ergänzen; universelle Regeln nicht wiederholen. -->
