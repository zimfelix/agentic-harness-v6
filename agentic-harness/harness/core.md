# Core – Arbeitsablauf von Auftrag bis Übergabe

> - **Typ:** Prozess
> - **Zuständigkeit:** Entscheidungen und Rücksprünge zwischen Klärung, Umsetzung, Verifikation und Übergabe steuern.
> - **Gilt bei:** Jeder Aufgabe nach dem Einstieg über `AGENTS.md`, auch bei Harness-Arbeit.
> - **Ladebeziehungen:** Vorher `AGENTS.md` und `agentic-harness/harness/project.md`; bei beauftragtem Project Init für ein leeres Produktprojekt oder vor erster Produktumsetzung mit `Pending Project Init` → `agentic-harness/harness/init.md`. Bei offener Idee → `agentic-harness/ideas/I000-readme.md`, bei beauftragtem Nutzerverhalten → `agentic-harness/specs/S000-readme.md` und betroffene Specs. Weitere Docs nach dem Auslöser in `AGENTS.md`; beim Nachführen von Projektdateien → `agentic-harness/document-contract.md`; vor Abschluss → `agentic-harness/harness/verification/gate.md`.
> - **Nicht zuständig:** Aufgabenrouting, Dokumentformat, Produktfakten, Testbefehle oder die Entscheidung des Verification-Gates duplizieren.

## Entscheidungsfluss

```text
AGENTS.md → core.md + project.md
                 │
                 ├─ Arbeitsbaum prüfen (git status, parallele Sitzungen)
                 ├─ Init beauftragt / erste Produktumsetzung bei Pending?
                 │     └─ init.md → Projektdateien → zurück zum Auftrag
                 └─ Ziel, Umfang und Freigaben klären (Diktat sinngemäß deuten)
                       ├─ größeres Vorhaben noch offen? → Idea → Klärung → zurück
                       ├─ neues/geändertes Nutzerverhalten beauftragt? → Spec
                       └─ sonst → beauftragten Umfang ohne künstliche Spec festhalten
                                  ↓
                      Docs nach Auslöser in AGENTS.md lesen:
                      architecture.md / code.md / design.md / testing.md
                                  ↓
                      Schritt 3: nur die beauftragte Änderung umsetzen;
                      Struktur mitziehen (2. Vorkommen → Baustein);
                      bei Bedarf Produktcode/Tests ändern und
                      passende Checks schon während der Arbeit ausführen;
                      Projektdateien nachführen (ersetzen statt anhängen)
                                  ↓
                      verification/gate.md: Soll ↔ Ist/Nachweise
                       (voller Weg oder kurzer Weg für Oberflächen-Iterationen)
                       ├─ ausreichend → Ergebnis übergeben; ggf. Spec „Implemented“
                       └─ Lücke → fail.md → je nach Ursache zurück zu
                            Klärung / Docs / Setup / Umsetzung / Checks
                            → betroffene Nachweise + Gate erneut
```

Die Dateinamen im Bild sind verkürzt; maßgeblich sind die Pfade im Kopf und das Routing in `AGENTS.md`. Bei geänderten Ladewegen dieses Bild mitprüfen.

## 1. Auftrag einordnen

Lies das Projektprofil für bestätigte Grenzen und tatsächlich eingerichtete Prüfungen. Ist Project Init für ein neues, leeres Produktprojekt beauftragt oder steht vor der ersten Produktimplementierung noch `Pending Project Init` im Profil, nutze `agentic-harness/harness/init.md`. Allein Harness- oder Dokumentationsarbeit löst kein Init aus. Erfinde keine fehlenden Projektfakten.

Kläre das gewünschte Ergebnis, den Umfang und Nicht-Ziele. Bei fehlender Entscheidung oder Freigabe nicht stillschweigend eine Annahme zur Projektregel machen.

**Diktierte Eingaben:** Aufträge können diktiert oder transkribiert sein. Deute offensichtliche Hör- und Schreibfehler sinngemäß (ein ähnlich klingendes Wort, das im Kontext keinen Sinn ergibt, meint meist den passenden Fachbegriff). Nenne deine Deutung vor der Umsetzung in einem Satz, wenn sie Inhalte entfernt oder umschreibt oder wenn mehrere Lesarten zu unterschiedlichen Ergebnissen führen. Bei Mehrdeutigkeit mit spürbaren Folgen frage nach, statt zu raten.

## 2. Klärung in beauftragtes Soll überführen

Ist ein größeres Vorhaben noch offen, kläre es als Idea nach `agentic-harness/ideas/I000-readme.md`. Auch eine `Ready`-Idea ist ohne gesonderten Umsetzungsauftrag keine Freigabe. Nach Klärung kehre zur Einordnung des Auftrags zurück.

Bei beauftragtem neuem oder geändertem Nutzerverhalten prüfe betroffene Specs nach `agentic-harness/specs/S000-readme.md`; erstelle oder ändere die nötige Spec mit prüfbaren Kriterien. Für verhaltensgleiche Refactors, Struktur- und Dokumentationsaufträge hält der Auftrag den Umfang fest; sie brauchen nicht pauschal eine neue Produktspec.

Lade die durch den Aufgabeninhalt ausgelösten Docs über `AGENTS.md`. Bei überlappenden Auslösern gelten die betroffenen Dateien gemeinsam, nicht die gesamte Dokumentation auf Vorrat.

## 3. Änderung ausführen und Umfang nachführen

Setze die kleinste Änderung um, die den **ganzen beauftragten Umfang** erfüllt. Wenn sich dabei neue Architektur-, Code-, Design- oder Testfragen ergeben, prüfe die Auslöser in `AGENTS.md` erneut und lies die jetzt betroffenen Docs vor dem Eingriff. Beachte bestätigte Projektgrenzen; kläre Rechte, echte Daten und irreversible Aktionen vor dem Eingriff.

**Struktur mitziehen:** Ordne neuen Code beim Schreiben in die vorgesehene Struktur ein (`agentic-harness/docs/architecture.md`, `agentic-harness/docs/code.md`), statt sie später in einem Umbau nachzuholen. Wird ein Muster (Abschnitt, Funktion, Wert) zum zweiten Mal gebraucht, mache es jetzt zu einem gemeinsamen Baustein oder einer gemeinsamen Stelle und stelle nur die betroffenen Vorkommen darauf um. Das gehört zur kleinsten vollständigen Änderung und ist keine Nebenbei-Verbesserung, solange sich Verhalten und Aussehen nicht ändern. Würde das Einordnen weitere, nicht betroffene Teile umbauen oder sichtbar etwas ändern, setze den Auftrag um, benenne die Kopie als technische Schuld in `agentic-harness/docs/code.md` und schlage den Umbau vor.

Erfordert die Arbeit eine neue Produktentscheidung oder ändert sich das Soll, gehe zur Klärung zurück und aktualisiere betroffene Projektdateien oder Specs, bevor du auf der neuen Annahme weiterarbeitest. Bei Strukturänderungen prüfe Ziel, tatsächlichen Baum und Folgen für Abhängigkeiten und Tests; übernimm keine projektspezifische Ordnerstruktur als allgemeine Pflicht.

**Iterationen an sichtbaren Oberflächen:** Setze pro Auftrag nur die genannten sichtbaren Änderungen um. Weitere Auffälligkeiten berichtest du als Liste, statt sie nebenbei umzusetzen, es sei denn, der Auftrag erlaubt ausdrücklich eigene Verbesserungen. Das Einordnen nach „Struktur mitziehen“ ändert nichts Sichtbares und bleibt davon unberührt. Verlangt der Auftraggeber „wie vorher, nur …“, stelle zuerst den vorherigen Stand exakt wieder her und ändere dann nur das Genannte. Belege jede Iteration im Zielmedium (z. B. Browser) nach `agentic-harness/docs/design.md`.

**Projektdateien nachführen:** Ändert sich ein bestätigter Stand, ersetze die betroffene Aussage in Projektprofil, Doc oder Spec an ihrer Stelle, statt einen weiteren Absatz anzuhängen (`agentic-harness/document-contract.md`). Neue bestätigte Gestaltungsregeln gehören nach `agentic-harness/docs/design.md`, nicht ins Projektprofil.

## 4. Verifizieren und übergeben

Folge vor dem Abschluss `agentic-harness/harness/verification/gate.md`. Es verbindet Auftrag und Projektgrenzen mit Änderung und tatsächlichen Nachweisen und beschreibt auch den kurzen Weg für Oberflächen-Iterationen. Bei einer Lücke folge dem dort geladenen `agentic-harness/harness/verification/fail.md`: kläre oder korrigiere die Ursache und durchlaufe das Gate erneut. Fehlt eine erforderliche Entscheidung oder ein Nachweis, berichte die Blockade statt Erfolg zu behaupten.

Berichte den erreichten Umfang, beobachtete Prüfergebnisse und offene Punkte. Ändere den Status einer Produktspec nur gemäß der Gate-Entscheidung; ohne Produktspec kein künstlicher Statuswechsel und bei reiner Prozess-/Dokuänderung kein behauptetes Produkt-Gate.

Ergänze bei der Übergabe eine **Mini-Spur im Chat** (wenige Zeilen, kein neues Artefakt): Welcher Entscheidungszweig galt, welche dafür relevanten Markdown-Dateien wurden tatsächlich gelesen, welche Dateien geändert und welche Prüfungen wirklich ausgeführt oder offen gelassen? Trenne Lesen von Ändern und prüfe, ob ein für diesen Zweig nötiger Schritt fehlt; behaupte weder ungelesene Dateien noch ein nicht durchlaufenes Produkt-Gate. Die Mini-Spur dokumentiert den Ablauf, ersetzt aber keine Prüfung und löst keinen zusätzlichen Verification-Durchlauf aus.

## Arbeitsbaum und Parallelarbeit

- Prüfe vor dem ersten Schreibzugriff `git status`. Fremde, nicht committete Änderungen gehören nicht dir: nicht überschreiben, zurücksetzen oder mitcommitten.
- Pro Arbeitsverzeichnis schreibt nur **eine** Agentensitzung. Parallele schreibende Sitzungen nutzen getrennte Worktrees (`git worktree add`) oder getrennte Klone; ein anderer Branch im selben Verzeichnis isoliert nichts. Ist Trennung nicht möglich, wird vorab festgelegt, wer welche Dateien schreibt, und jede Datei direkt vor dem Ändern neu gelesen.
- Ändert sich eine Datei während deiner Arbeit unerwartet, lies zuerst den neuen Stand und kläre die Ursache, statt ihn zu überschreiben. Fremdinhalte, die den Build brechen (z. B. versehentlich eingefügte Shell-Zeilen), nur minimal korrigieren und in der Übergabe melden.
- Committe nur auf Auftrag und nur eigene, zusammengehörige Änderungen mit einem Betreff, der die tatsächliche Änderung beschreibt. Interaktive Git-Befehle (`git add -p`, `rebase -i`) sind für Agenten nicht geeignet.
- Nenne bei der Übergabe offene, nicht committete Änderungen anderer, wenn sie dein Ergebnis berühren.
