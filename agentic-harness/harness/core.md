# Core – Arbeitsablauf von Auftrag bis Übergabe

> - **Typ:** Prozess
> - **Zuständigkeit:** Entscheidungen und Rücksprünge zwischen Klärung, Umsetzung, Verifikation und Übergabe steuern.
> - **Gilt bei:** Jeder Aufgabe nach dem Einstieg über `AGENTS.md`, auch bei Harness-Arbeit.
> - **Ladebeziehungen:** Vorher `AGENTS.md` und `agentic-harness/harness/project.md`; bei beauftragtem Project Init für ein leeres Produktprojekt oder vor erster Produktumsetzung mit `Pending Project Init` → `agentic-harness/harness/init.md`. Bei größerer Änderung → `agentic-harness/ideas/I000-readme.md`, bei beauftragtem Nutzerverhalten → `agentic-harness/specs/S000-readme.md` und betroffene Bereichs-Specs. Weitere Docs nach dem Auslöser in `AGENTS.md`; beim Nachführen von Projektdateien → `agentic-harness/document-contract.md`; vor Abschluss → `agentic-harness/harness/verification/gate.md`.
> - **Nicht zuständig:** Aufgabenrouting, Dokumentformat, Produktfakten, Testbefehle oder die Entscheidung des Verification-Gates duplizieren.

## Entscheidungsfluss

```text
AGENTS.md → core.md + project.md
                 │
                 ├─ Arbeitsbaum prüfen (git status, parallele Sitzungen)
                 ├─ Init beauftragt / erste Produktumsetzung bei Pending?
                 │     └─ init.md: Richtung offen? → erst billig erkunden (Erkundungsstufen E0–E3)
                 │        → Architektur/Tech-Stack wählen → Projektdateien → zurück zum Auftrag
                 └─ Ziel, Umfang und Freigaben klären (Diktat sinngemäß deuten)
                       beide Fragen prüfen, beide können zutreffen:
                       ├─ größere Änderung oder offenes Vorhaben? → Idea (Offen oder gleich Beauftragt)
                       ├─ neues/geändertes Nutzerverhalten beauftragt? → Bereichs-Spec(s) anlegen/ändern
                       └─ keins von beiden → beauftragten Umfang ohne künstliche Spec festhalten
                                  ↓
                      Docs nach Auslöser in AGENTS.md lesen:
                      architecture.md / code.md / design.md / testing.md
                                  ↓
                      Schritt 3: nur die beauftragte Änderung umsetzen;
                      Struktur mitziehen (2. Vorkommen → Baustein; nicht zwischen Varianten);
                      bei Bedarf Produktcode/Tests ändern und
                      passende Checks schon während der Arbeit ausführen;
                      Projektdateien nachführen (ersetzen statt anhängen)
                                  ↓
                      verification/gate.md: Soll ↔ Ist/Nachweise
                       (voller Weg oder kurzer Weg für Oberflächen-Iterationen)
                       ├─ ausreichend → Ergebnis übergeben; ggf. Spec „Implemented“,
                       │   Idea „Umgesetzt“ → Archiv
                       └─ Lücke → fail.md → je nach Ursache zurück zu
                            Klärung / Docs / Setup / Umsetzung / Checks
                            → betroffene Nachweise + Gate erneut;
                            2× dieselbe Ursache gescheitert oder Blocker → stoppen, berichten
```

Die Dateinamen im Bild sind verkürzt; maßgeblich sind die Pfade im Kopf und das Routing in `AGENTS.md`. Bei geänderten Ladewegen dieses Bild mitprüfen.

## 1. Auftrag einordnen

Lies das Projektprofil für bestätigte Grenzen und tatsächlich eingerichtete Prüfungen. Init nach dem Auslöser in `AGENTS.md`; Harness- oder Dokumentationsarbeit allein löst kein Init aus. Erfinde keine fehlenden Projektfakten.

Kläre das gewünschte Ergebnis, den Umfang und Nicht-Ziele. **Sparsam fragen:** Frage nur, was das Ergebnis spürbar ändert oder eine Freigabe braucht (echte Daten, Kosten, Unumkehrbares); bündle solche Fragen in einem Block. Sonst nenne eine sinnvolle Annahme in einem Satz und arbeite weiter. Eine Annahme wird nicht stillschweigend zur Projektregel.

**Diktierte Eingaben:** Aufträge können diktiert oder transkribiert sein. Deute offensichtliche Hör- und Schreibfehler sinngemäß (ein ähnlich klingendes Wort, das im Kontext keinen Sinn ergibt, meint meist den passenden Fachbegriff). Nenne deine Deutung vor der Umsetzung in einem Satz, wenn sie Inhalte entfernt oder umschreibt oder wenn mehrere Lesarten zu unterschiedlichen Ergebnissen führen. Bei Mehrdeutigkeit mit spürbaren Folgen frage nach, statt zu raten.

## 2. Klärung in beauftragtes Soll überführen

Größere Änderungen und offene Vorhaben führst du als Idea nach `agentic-harness/ideas/I000-readme.md` (Kriterium dort unter „Wann eine Idea“): Sie ist die Akte der Änderung (Anlass, Umfang, betroffene Bereichs-Specs, Abhängigkeiten, Teilaufgaben, Status). Umgesetzt wird erst, wenn sie „Beauftragt“ ist; ein direkter Umsetzungsauftrag mit klarem Umfang macht sie sofort „Beauftragt“, ohne zusätzliche Rückfrage. Kleine Iterationen brauchen keine Idea.

Bei beauftragtem neuem oder geändertem Nutzerverhalten prüfe die betroffenen Bereichs-Specs nach `agentic-harness/specs/S000-readme.md`; erstelle oder ändere die nötige Spec mit prüfbaren Kriterien. Die Spec hält den lebenden Soll-Stand des Bereichs, nicht den Verlauf der Änderung. Für verhaltensgleiche Refactors, Struktur- und Dokumentationsaufträge hält der Auftrag den Umfang fest; sie brauchen nicht pauschal eine neue Produktspec.

## 3. Änderung ausführen und Umfang nachführen

Setze die kleinste Änderung um, die den **ganzen beauftragten Umfang** erfüllt. Wenn sich dabei neue Architektur-, Code-, Design- oder Testfragen ergeben, prüfe die Auslöser in `AGENTS.md` erneut und lies die jetzt betroffenen Docs vor dem Eingriff. Beachte bestätigte Projektgrenzen; kläre Rechte, echte Daten und irreversible Aktionen vor dem Eingriff.

**Struktur mitziehen:** Ordne neuen Code beim Schreiben in die vorgesehene Struktur ein (`agentic-harness/docs/architecture.md`, `agentic-harness/docs/code.md`), statt sie später in einem Umbau nachzuholen. Wird ein Muster (Abschnitt, Funktion, Wert) zum zweiten Mal gebraucht, mache es jetzt zu einem gemeinsamen Baustein oder einer gemeinsamen Stelle und stelle nur die betroffenen Vorkommen darauf um. Das gehört zur kleinsten vollständigen Änderung und ist keine Nebenbei-Verbesserung, solange sich Verhalten und Aussehen nicht ändern. Würde das Einordnen weitere, nicht betroffene Teile umbauen oder sichtbar etwas ändern, setze den Auftrag um, benenne die Kopie als technische Schuld in `agentic-harness/docs/code.md` und schlage den Umbau vor. **Ausnahme Varianten zum Vergleich:** Sie teilen nur Inhalte und Messwerkzeuge, keine Gestaltung oder Bausteine; zusammengeführt wird erst nach der Auswahl (`agentic-harness/harness/init.md`, Abschnitt 0).

Erfordert die Arbeit eine neue Produktentscheidung oder ändert sich das Soll, gehe zur Klärung zurück und aktualisiere betroffene Projektdateien oder Specs, bevor du auf der neuen Annahme weiterarbeitest. Bei Strukturänderungen prüfe Ziel, tatsächlichen Baum und Folgen für Abhängigkeiten und Tests; übernimm keine projektspezifische Ordnerstruktur als allgemeine Pflicht.

**Nur das Beauftragte:** Weitere Auffälligkeiten berichtest du als Liste, statt sie nebenbei umzusetzen, es sei denn, der Auftrag erlaubt ausdrücklich eigene Verbesserungen; das Einordnen nach „Struktur mitziehen“ bleibt davon unberührt. Verlangt der Auftraggeber „wie vorher, nur …“, stelle zuerst den vorherigen Stand exakt wieder her und ändere dann nur das Genannte. Sichtbare Änderungen belegst du im Zielmedium (`agentic-harness/docs/design.md`).

**Projektdateien nachführen:** Ändert sich ein bestätigter Stand, ersetze die betroffene Aussage in Projektprofil, Doc oder Spec an ihrer Stelle, statt einen weiteren Absatz anzuhängen (`agentic-harness/document-contract.md`). Neue bestätigte Gestaltungsregeln gehören nach `agentic-harness/docs/design.md`, nicht ins Projektprofil.

## 4. Verifizieren und übergeben

Folge vor dem Abschluss `agentic-harness/harness/verification/gate.md`. Es verbindet Auftrag und Projektgrenzen mit Änderung und tatsächlichen Nachweisen und beschreibt auch den kurzen Weg für Oberflächen-Iterationen. Bei einer Lücke folge dem dort geladenen `agentic-harness/harness/verification/fail.md`: kläre oder korrigiere die Ursache und durchlaufe das Gate erneut. Fehlt eine erforderliche Entscheidung oder ein Nachweis, berichte die Blockade statt Erfolg zu behaupten.

Berichte Ergebnis zuerst, dann geänderte Dateien, tatsächlich ausgeführte Prüfungen und Offenes. `Implemented` einer Spec und „Umgesetzt“ einer Idea setzt nur die Gate-Entscheidung; „Beauftragt“, „Zurückgestellt“ und „Verworfen“ einer Idea folgen der Entscheidung des Auftraggebers.

**Spur auf Wunsch** (z. B. beim Test des Harnesses): zusätzlich in wenigen Zeilen den Entscheidungszweig, tatsächlich gelesene Harness-Dateien und ausgelassene Schritte nennen; ungelesene Dateien nicht behaupten.

## Arbeitsbaum und Parallelarbeit

- Prüfe vor dem ersten Schreibzugriff `git status`. Fremde, nicht committete Änderungen gehören nicht dir: nicht überschreiben, zurücksetzen oder mitcommitten.
- Pro Arbeitsverzeichnis schreibt nur **eine** Agentensitzung. Parallele schreibende Sitzungen nutzen getrennte Worktrees (`git worktree add`) oder getrennte Klone; ein anderer Branch im selben Verzeichnis isoliert nichts. Ist Trennung nicht möglich, wird vorab festgelegt, wer welche Dateien schreibt, und jede Datei direkt vor dem Ändern neu gelesen.
- Ändert sich eine Datei während deiner Arbeit unerwartet, lies zuerst den neuen Stand und kläre die Ursache, statt ihn zu überschreiben. Fremdinhalte, die den Build brechen (z. B. versehentlich eingefügte Shell-Zeilen), nur minimal korrigieren und in der Übergabe melden.
- Committe nur auf Auftrag und nur eigene, zusammengehörige Änderungen mit einem Betreff, der die tatsächliche Änderung beschreibt. Interaktive Git-Befehle (`git add -p`, `rebase -i`) sind für Agenten nicht geeignet.
- Nenne bei der Übergabe offene, nicht committete Änderungen anderer, wenn sie dein Ergebnis berühren.
