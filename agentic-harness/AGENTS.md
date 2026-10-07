# Agentic Harness – Einstieg

> - **Typ:** Einstieg
> - **Zuständigkeit:** Aufgaben den zuständigen Harness-Dateien zuordnen.
> - **Gilt bei:** Jeder Arbeit in einem Projekt mit diesem Harness.
> - **Ladebeziehungen:** Immer `harness/core.md` und `harness/project.md` lesen; weitere Dateien nur nach den Auslösern unten.
> - **Nicht zuständig:** Den Arbeitsablauf, Produktfakten oder Qualitätsregeln hier erneut erklären.

## Universell, Profil, Projekt

Dieser Harness ist **universell** für Softwareprojekte jeder Art; **Profile** unter `profiles/` ergänzen optional Wissen für eine Projektart (z. B. `website.md`). Projektart, Ziel, Stack, Architektur, Tests und Profil werden beim Project Init (`harness/init.md`) mit dem Auftraggeber geklärt. **Projektspezifisch** sind nur die markierten Projektabschnitte, `project/` (außer dessen `README.md`), Specs, Ideas, Produktcode und Tests; die Zuordnung jeder Datei steht in `harness-map.md`. Einen bestehenden Produktprojektordner nie roh kopieren (Export: `harness/README.md`). Die unbefüllte Variante ist dagegen eigenständig kopierbar: ihr Inhalt wird zum Projekt-Root; alle Pfade hier beziehen sich darauf, im Vorlagen-Repository auf diesen Variantenordner.

## Wohin mit der Aufgabe?

### Produktarbeit

| Auslöser | Zusätzlich lesen | Zweck |
|---|---|---|
| Project Init für ein neues, leeres Produktprojekt beauftragt oder erste Produktumsetzung bei `Pending Project Init` | `harness/init.md`; falls vorhanden `project/brief.md` | Projektziel und Grenzen klären; einen Brief als Ausgangsbeschreibung nutzen, nicht als bestätigte Spec. |
| Produktarchitektur, Produktbausteine oder deren Dateistruktur; Betrieb; neue Seiten, Routen oder Einstiege; Varianten vergleichen, aufräumen, archivieren | `docs/architecture.md` (bei Varianten Abschnitt „Varianten, Konzeptseiten und Archiv“) | Produktaufbau und Abhängigkeiten prüfen; nur Erreichbares bauen; Varianten intern halten. |
| Projektprofil nennt „Profil: …“ oder der Auftrag verlangt ausdrücklich ein Profil | `profiles/<name>.md` nach dessen Kopfzeile „Gilt bei“ | Profilregeln als Standard anwenden; Projektwerte und Abweichungen stehen in der thematisch zuständigen Projektdatei. |
| Sichtbare Änderung an Layout, Farbe, Schrift, Abständen, Bausteinen oder Interaktion; neuer Abschnitt | `docs/design.md` | Farbrollen, Größenskala und Bausteine nutzen; Ergebnis im Zielmedium (z. B. Browser) nachweisen. |
| Codeänderung oder Refactor | `docs/code.md` | Projektbezogene Codekonventionen prüfen. |
| Testplanung, Teständerung oder Testlauf | `docs/testing.md` | Testkonventionen prüfen; Befehle stehen im Projektprofil. |
| Größere Änderung, neue Funktion oder offenes Vorhaben | `ideas/I000-readme.md` und betroffene Idea | Als Akte führen (Offen → Beauftragt → Umgesetzt, danach Archiv); bei Neuanlage `harness/templates/idea.md` verwenden. |
| Neues oder geändertes Nutzerverhalten | `specs/S000-readme.md` und betroffene Bereichs-Spec | Lebenden Soll-Stand des Bereichs prüfen und nachführen; bei Neuanlage `harness/templates/spec.md` verwenden. |
| Abschluss einer Änderung | `harness/verification/gate.md` | Auftrag und Nachweise prüfen (bei reiner Oberflächen-Iteration kurzer Weg); bei Fehlschlag `harness/verification/fail.md`. |

### Projektdateien und Harness pflegen

| Auslöser | Zusätzlich lesen | Zweck |
|---|---|---|
| Markdown-Datei anlegen, befüllen oder verdichten; Harness-Datei umbenennen, verschieben oder löschen; Rolle oder Ladeauslöser einer Datei ändern | `document-contract.md`; bei neuer Datei, Rolle, Pfad oder Auslöser auch `harness-map.md` | Passende Form, aktueller Stand statt Verlauf; Verweise, Köpfe, Einstieg und Landkarte gemeinsam abgleichen (Vertrag, „Bei neuen, umbenannten oder entfernten Dateien“). |
| Harness erstmals einordnen | `harness-map.md` | Dateirollen und Ladewege verstehen; tatsächliche Pfade prüfen. |
| Eine Schwäche oder Unklarheit des Harnesses fällt auf, ein Agentenfehler wiederholt sich, oder eine universelle Harness-Datei, ein Profil oder ein Werkzeug soll geändert werden | `harness-learnings.md` | Vor einer Harness-Änderung die aktiven Einträge prüfen (nichts Bewusstes zurückdrehen); Beobachtung oder Änderung im selben Schritt als Eintrag festhalten; universelle Dateien nur auf ausdrücklichen Auftrag ändern; Projektfakten bleiben in den Projektdateien. |
| Harness exportieren oder Harness-Release in die Vorlage vorbereiten | `harness/README.md` (Abschnitte „Harness weiterentwickeln“ und „Harness als Vorlage exportieren“) und `harness-map.md` | Mit `tools/export-harness.sh` in ein leeres Ziel oder einen sauberen Vorlagen-Klon; Diff zeigen; erst nach Freigabe pushen. |

Treffen mehrere Auslöser zu, lies die betreffenden Dateien; lade nicht alle Docs auf Vorrat. Neue Projekt-Docs nur bei echtem Bedarf (`document-contract.md`, „Neue Projekt-Docs“). Markdown aktualisiert sich nicht selbst: Nach manuellen Änderungen zuerst den Ist-Stand prüfen.

## Aktiver Stand und Pfade

`harness/core.md` regelt den Arbeits- und Entscheidungsfluss einschließlich Arbeitsbaum, Parallelarbeit und Commits. Vor dem ersten Schreibzugriff `git status` prüfen (ohne Git-Repository nach `harness/init.md` klären); fremde, nicht committete Änderungen weder überschreiben noch mitcommitten. Bei Widersprüchen zwischen Pfaden gelten die in dieser Datei genannten.

Produktcode und Produkttests liegen außerhalb der Harness-Dokumente. Bei Widersprüchen zwischen Auftrag, bestehenden Projektanweisungen und Harness kläre die Zuständigkeit vor riskanten Änderungen. Ändere nicht stillschweigend weitere Dateien, nur weil sie verlinkt sind. Ein im Projektprofil benannter Archivordner wird nicht geladen, gebaut oder getestet und nur auf ausdrücklichen Auftrag geändert.

Unter der folgenden Überschrift stehen nur nötige Projektverweise und bestätigte Arbeitsabsprachen, ein Punkt je Thema; universelle Regeln oben nicht kopieren. Leseauslöser für eine Projekt-Doc im Format `- **Thema:** bei <konkretem Auslöser> → project/<thema>.md`. Beim Export als Vorlage wird nur der Teil **über** dieser Überschrift übernommen.

## Projektspezifische Ergänzungen
