# Agentic Harness – Einstieg

> - **Typ:** Einstieg
> - **Zuständigkeit:** Aufgaben den zuständigen Harness-Dateien zuordnen.
> - **Gilt bei:** Jeder Arbeit in einem Projekt mit diesem Harness.
> - **Ladebeziehungen:** Immer `agentic-harness/harness/core.md` und `agentic-harness/harness/project.md` lesen; weitere Dateien nur nach den Auslösern unten.
> - **Nicht zuständig:** Den Arbeitsablauf, Produktfakten oder Qualitätsregeln hier erneut erklären.

## Universell, Profil, Projekt

Dieser Harness ist **universell** für Softwareprojekte jeder Art. **Profile** unter `agentic-harness/profiles/` ergänzen optional Wissen für eine Projektart (z. B. `website.md`); ohne passendes Profil wird ohne Profil gearbeitet. Projektart, Ziel, Stack, Architektur, Tests und Profil legt der Harness nicht fest: Sie werden beim Project Init nach `agentic-harness/harness/init.md` mit dem Auftraggeber geklärt und erst dann in die Projektabschnitte geschrieben. **Projektspezifisch** sind nur die markierten Projektabschnitte, Specs, Ideas, Produktcode und Tests. Die Zuordnung jeder Datei steht in `agentic-harness/harness-map.md`, der Export in ein neues Projekt in `agentic-harness/README.md`. Einen bestehenden Projektordner nie roh kopieren.

## Wohin mit der Aufgabe?

| Auslöser | Zusätzlich lesen | Zweck |
|---|---|---|
| Project Init für ein neues, leeres Produktprojekt beauftragt oder erste Produktumsetzung bei `Pending Project Init` | `agentic-harness/harness/init.md`; falls vorhanden `agentic-harness/project/brief.md` | Projektziel und Grenzen klären; einen Brief als Ausgangsbeschreibung nutzen, nicht als bestätigte Spec. |
| Produktarchitektur, Produktbausteine oder deren Dateistruktur; Betrieb; neue Seiten, Routen oder Einstiege | `agentic-harness/docs/architecture.md` | Produktaufbau und Abhängigkeiten prüfen; nur Erreichbares bauen. |
| Konzept- oder Variantenvergleich, Aufräumen, Archivieren | `agentic-harness/docs/architecture.md` (Abschnitt „Varianten, Konzeptseiten und Archiv“) | Varianten intern halten; nach Entscheidung archivieren oder löschen. |
| Projektprofil nennt „Profil: …“ oder der Auftrag verlangt ausdrücklich ein Profil | `agentic-harness/profiles/<name>.md` nach dessen Kopfzeile „Gilt bei“ | Profilregeln als Standard anwenden; Projektwerte und Abweichungen stehen in der thematisch zuständigen Projektdatei. |
| Sichtbare Änderung an Layout, Farbe, Schrift, Abständen, Bausteinen oder Interaktion; neuer Abschnitt | `agentic-harness/docs/design.md` | Farbrollen, Größenskala und Bausteine nutzen; Ergebnis im Zielmedium (z. B. Browser) nachweisen. |
| Codeänderung oder Refactor | `agentic-harness/docs/code.md` | Projektbezogene Codekonventionen prüfen. |
| Testplanung, Teständerung oder Testlauf | `agentic-harness/docs/testing.md` | Testkonventionen prüfen; Befehle stehen im Projektprofil. |
| Größere offene Idee | `agentic-harness/ideas/I000-readme.md` | Idee klären; bei Neuanlage `agentic-harness/harness/templates/idea.md` verwenden. |
| Neues oder geändertes Nutzerverhalten | `agentic-harness/specs/S000-readme.md` und betroffene Spec | Beauftragtes Soll prüfen; bei Neuanlage `agentic-harness/harness/templates/spec.md` verwenden. |
| Abschluss einer Änderung | `agentic-harness/harness/verification/gate.md` | Auftrag und Nachweise prüfen (bei reiner Oberflächen-Iteration kurzer Weg); bei Fehlschlag `agentic-harness/harness/verification/fail.md`. |
| Harness erstmals einordnen oder Project Init durchführen | `agentic-harness/harness-map.md` | Dateirollen und Ladewege verstehen; tatsächliche Pfade prüfen. |
| Markdown-Datei neu anlegen, befüllen oder eine gewachsene Projektdatei verdichten | `agentic-harness/document-contract.md`; bei neuer Datei oder Rolle auch `agentic-harness/harness-map.md` | Passende Form, aktueller Stand statt Verlauf, Verweise und Kopf gegen tatsächliche Rollen und Pfade prüfen. |
| Harness exportieren oder Harness-Release in die Vorlage vorbereiten | `agentic-harness/README.md` (Abschnitte „Harness weiterentwickeln“ und „Harness als Vorlage exportieren“) und `agentic-harness/harness-map.md` | Mit `agentic-harness/tools/export-harness.sh` in ein leeres Ziel oder einen sauberen Vorlagen-Klon; Diff zeigen; erst nach Freigabe pushen. |
| Harness-Pfade, Dateirollen oder Ladeauslöser ändern | `agentic-harness/harness-map.md` und `agentic-harness/document-contract.md` | Betroffene Dokumentköpfe, Einstieg und Verweise gemeinsam abgleichen. |
| Eine Schwäche oder Unklarheit des Harnesses fällt auf, ein Agentenfehler wiederholt sich, oder eine universelle Harness-Datei, ein Profil oder ein Werkzeug soll geändert werden | `agentic-harness/harness-learnings.md` | Vor einer Harness-Änderung die aktiven Einträge prüfen (nichts Bewusstes zurückdrehen); Beobachtung oder Änderung im selben Schritt als Eintrag festhalten; universelle Dateien nur auf ausdrücklichen Auftrag ändern; Projektfakten bleiben in den Projektdateien. |

Treffen mehrere Auslöser zu, lies die betreffenden Dateien. Lade nicht alle Docs auf Vorrat. Neue thematische Projekt-Docs brauchen einen klaren Auslöser im Einstieg; verweise auf Regeln statt sie hier zu kopieren.

Vor dem Umbenennen, Verschieben oder Löschen einer Harness-Datei suche repo-weit nach Verweisen auf Pfad und Dateinamen. Aktualisiere betroffene Verweise und Ladewege im selben Schritt. Prüfe danach verbliebene Pfade **und die Köpfe der betroffenen Dateien** gegen den tatsächlichen Baum. Dasselbe gilt, wenn sich Zuständigkeit oder Ladeauslöser ohne Dateiumzug ändern. Nach manuellen Änderungen zuerst den Ist-Stand prüfen; Markdown aktualisiert sich nicht selbst.

## Aktiver Stand und Pfade

`agentic-harness/harness/core.md` regelt den Arbeits- und Entscheidungsfluss. Landkarte und Dokumentenvertrag sind Referenzen für Orientierung und Markdown-Pflege. Bei Widersprüchen zwischen Pfaden gelten die in dieser Datei genannten.

Produktcode und Produkttests liegen außerhalb der Harness-Dokumente. Bei Widersprüchen zwischen Auftrag, bestehenden Projektanweisungen und Harness kläre die Zuständigkeit vor riskanten Änderungen. Ändere nicht stillschweigend weitere Dateien, nur weil sie verlinkt sind.

Vor dem ersten Schreibzugriff `git status` prüfen (ist das Verzeichnis noch kein Git-Repository, nach `agentic-harness/harness/init.md` klären); fremde, nicht committete Änderungen weder überschreiben noch mitcommitten. Parallele Agentensitzungen und Commits regelt `agentic-harness/harness/core.md` (Abschnitt „Arbeitsbaum und Parallelarbeit“). Bei Commits beschreibt der Betreff in einem kurzen, konkreten Satz die tatsächliche Änderung. Vermeide ungenaue Betreffe wie „Update files“.

Ein im Projektprofil benannter Archivordner wird nicht geladen, gebaut oder getestet und nur auf ausdrücklichen Auftrag geändert.

Bei Project Init nur nötige zusätzliche Projektverweise und bestätigte Arbeitsabsprachen unter der folgenden Überschrift eintragen. Universelle Regeln oben nicht kopieren. Beim Export als Vorlage wird nur der Teil **über** dieser Überschrift übernommen.

## Projektspezifische Ergänzungen
