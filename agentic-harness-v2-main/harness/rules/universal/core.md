# Core – universeller Arbeitsablauf

## Geltung

Dieser Ablauf gilt für neue Projekte unabhängig von Sprache und Plattform. `AGENTS.md` ist die Einstiegskarte; `harness/rules/project-specific/project.md` enthält die konkreten Projektfakten und Grenzen. Ist das Profil noch `Pending Project Init`, kläre das Projekt einmal anhand von `harness/templates/project-init.md`, bevor du mit der ersten Implementierung beginnst. Technik, Architektur und Befehle gehören nicht in diesen Core. Lies die betroffene Spec und nur die für die Aufgabe passenden Regeln; lade keine Ordner auf Vorrat.

## Aufgabe einordnen

1. Verstehe Ziel, Nutzer und gewünschtes Ergebnis. Frage bei offenen Produktentscheidungen oder Risiken gezielt nach, statt sie zu erfinden; unkritische Details entscheide innerhalb der Projektregeln. Vor externen Schreibaktionen, Zugriff auf echte Daten oder Secrets und schwer rückgängig zu machenden Schritten kläre Grenzen und nötige Freigaben, bevor du handelst.
2. Kläre Unklarheiten zunächst im Gespräch. Ist das Vorhaben größer, sollen Entscheidungen über mehrere Gespräche erhalten bleiben oder wird es ausdrücklich gewünscht, nutze `harness/rules/universal/ideas.md` und eine Datei unter `ideas/`. Eine geklärte Idea führt erst nach Bestätigung und Umsetzungsauftrag zu einer oder mehreren Specs; klare Aufträge überspringen diesen Schritt.
3. Neues oder geändertes Nutzerverhalten erhält **vor dem Code** eine kleine Spec nach `harness/templates/story.md`. Ein Bugfix, der bereits spezifiziertes Verhalten wiederherstellt, nutzt die bestehende Spec. Reine Dokumentation, Formatierung oder nachweislich verhaltensgleiches Refactoring benötigen keine neue Spec. Fehlt bei einem Bugfix das erwartete Verhalten, kläre und dokumentiere es zuerst.

## Umsetzen und prüfen

4. Die Spec ist die Quelle für den gewünschten Funktionsumfang, nicht ein Prompt-Protokoll oder technischer Lösungsplan. Halte Ziel, abgegrenzten Umfang und Nicht-Ziel fest; formuliere atomare, beobachtbare Akzeptanzkriterien (AK). Leite für jedes relevante AK einen Nachweis ab: automatisierter Test als Standard; nur wenn nicht sinnvoll, eine begründete, bestandene statische oder manuelle Prüfung in der Spec. Verwende bei nummerierten Stories in Tests einen zuordenbaren Marker wie `SXXX-AK1`.
5. Implementiere die kleinste zusammenhängende Änderung. Wird der Umfang unerwartet um neue Daten, Integrationen, Nutzergruppen oder Betriebsfolgen erweitert, prüfe betroffene Projektgrenzen, Specs und Checks erneut; wiederhole nicht pauschal die gesamte Project Init. Führe währenddessen die kleinsten passenden Checks aus. Welche Testarten gelten, richtet sich nach Risiko und Projekt; `harness/rules/universal/quality.md` erläutert die Auswahl. Konkrete Befehle legt das Projekt fest.
6. Vor Abschluss muss das für den betroffenen Bereich vereinbarte Quality Gate mit **tatsächlich ausgeführten Checks** grün sein. Fehlende oder leere Gate-Konfiguration ist kein Erfolg. Bei Fehlern Ursache als Code-, Test- oder Spec-Problem einordnen, gezielt korrigieren und das Gate wiederholen.

## Abschluss und Pflege

Eine Spec ist `Modified`, wenn sie neu oder inhaltlich geändert wurde oder ihre Erfüllung noch nicht nachgewiesen ist. Setze sie erst auf `Implemented`, wenn alle AK nachweisbar erfüllt und das erforderliche Gate grün sind. Ein reiner Code-Bugfix ohne Spec-Änderung setzt den Status nicht allein deshalb zurück. Verhaltensänderungen liefern Spec, Nachweis und Code gemeinsam; halte betroffene Projektfakten und Dokumentation aktuell.

Halte Specs, Diffs, Antworten und Logs kurz; prüfe nur das Nötige, ohne das Abschluss-Gate auszulassen. Ergänze `learning-state.md` nur auf ausdrücklichen Speicher- oder Sammelauftrag, nie automatisch während eines Gesprächs. Bei ausdrücklich beauftragter Übertragung in globale Agent-Dateien kuratiere nur übertragbare Erkenntnisse, prüfe Dopplungen und folge den globalen Anweisungen. Prüfe vor der Übergabe den Diff gegen Auftrag und Spec; fasse Ergebnis, Prüfungen und offene Punkte kurz zusammen. Folge der Projektregel für Review, Commit und Push; liefere nie fremde oder ungeprüfte Änderungen aus und führe weder Commit/Push ohne ausdrückliche Freigabe noch Force-Push aus. Passe den universellen Harness nicht wegen eines einzelnen Fehlers an; eine Regeländerung braucht eine bewusste, übertragbare Begründung.
