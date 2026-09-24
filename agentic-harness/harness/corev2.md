# Core V2 – Arbeitsablauf von Auftrag bis Übergabe

> - **Typ:** Prozess
> - **Status:** Entwurf; `agentic-harness/harness/core.md` bleibt aktiv.
> - **Zuständigkeit:** Ablauf jeder Projektaufgabe – von der Einordnung bis zum Bericht.
> - **Gilt bei:** Jeder Projektaufgabe nach dem Einstieg über `agentic-harness/AGENTS.md`.
> - **Ladebeziehungen:**
>   - Für die Prüfung dieses Entwurfs: `agentic-harness/document-contract.md`.
>   - Bei jeder Projektaufgabe: `agentic-harness/harness/project.md`.
>   - Bei `Pending Project Init`: `agentic-harness/harness/init.md`.
>   - Je nach Aufgabe: die Dateien in Abschnitt „Lade die passenden Dokumente“.
>   - Vor dem Abschluss: das Verification-Gate aus Abschnitt „Abschluss“.
> - **Nicht zuständig:** Produktfakten, Stack-Konventionen, Vorlageninhalte und konkrete Gate-Befehle. Diese gehören in die jeweils verlinkten Projektdateien.

## 1. Auftrag und Projekt einordnen

Lies `agentic-harness/harness/project.md`. Übernimm bestätigte Projektfakten daraus. Erfinde keine fehlenden Fakten.

Steht dort `Pending Project Init`, führe zuerst `agentic-harness/harness/init.md` aus. Entferne den Status erst, wenn die erste Umsetzung verantwortbar ist. Ein grünes Quality Gate folgt daraus nicht automatisch.

Kläre das gewünschte Ergebnis, den Umfang und die Nicht-Ziele. Ordne die Aufgabe ein:

- **Offene Idee:** Problem oder Umfang müssen erst geklärt werden.
- **Beauftragtes Verhalten:** Nutzerverhalten soll neu entstehen oder sich ändern.
- **Refactor oder Dokumentationspflege:** Bestehendes Verhalten bleibt gleich.
- **Struktur- oder Architekturauftrag:** Bausteine, Abhängigkeiten, Pakete oder Dateilayout ändern sich.

Eine `Ready`-Idea ist allein keine Implementierungsfreigabe. Für die Umsetzung braucht es zusätzlich einen Auftrag.

## 2. Lade die passenden Dokumente

Lade nur die Dateien, deren Auslöser zutrifft. Bei überlappenden Aufgaben lade die betreffenden Dokumente gemeinsam.

### Architektur und Struktur

Bei Änderungen an Bausteinen, Abhängigkeiten, Paketgrenzen oder Dateilayout:

- Lies `agentic-harness/docs/architecture.md`.
- Lies zusätzlich `agentic-harness/docs/code.md`, wenn sich Code- oder Importkonventionen ändern.
- Lies zusätzlich `agentic-harness/docs/testing.md`, wenn sich Testlayout, Testentdeckung oder Testkonventionen ändern.

### Code und Tests

- Bei Codeänderungen oder Refactorings: `agentic-harness/docs/code.md`.
- Beim Planen, Ändern oder Ausführen von Tests: `agentic-harness/docs/testing.md`.
- Für ausführbare Befehle und den aktuellen Gate-Status: `agentic-harness/harness/project.md`.

### Ideas und Specs

- **Offenes Vorhaben:** Lies `agentic-harness/ideas/S000-readme.md`. Wenn du eine Idea anlegst, nutze danach `agentic-harness/harness/templates/idea.md`.
- **Beauftragtes Verhalten:** Lies `agentic-harness/specs/S000-readme.md` und die betroffene Spec. Wenn du eine neue Spec anlegst, nutze `agentic-harness/harness/templates/spec.md`.
- Lies weitere bestehende Specs, wenn die Änderung ihr Verhalten oder ihre Kriterien betreffen könnte.

Eine Idea dient der Klärung. Eine Spec hält beauftragtes Soll-Verhalten fest. Verhaltensgleiche Refactors und reine Dokuänderungen brauchen nicht automatisch eine Produktspec.

### Abschluss

Vor dem Abschluss `agentic-harness/harness/verification/gate.md` lesen.

Das Gate lädt zwei Prüfungen:

- `agentic-harness/harness/verification/requirements.md` gleicht den Auftrag mit dem Soll ab.
- `agentic-harness/harness/verification/implementation.md` prüft Umsetzung und Nachweise.

Bei Fehlschlag zusätzlich `agentic-harness/harness/verification/fail.md` lesen.

## 3. Strukturänderungen vorab konkretisieren

Dieser Schritt gilt auch nach abgeschlossenem Project Init. Der Auslöser ist der Aufgabeninhalt, nicht allein ein Profilstatus.

Vor Änderungen an Architektur, Abhängigkeiten, Paketgrenzen oder Dateilayout:

1. Prüfe den tatsächlichen Datei- und Paketbaum.
2. Lies das bestätigte Ziel in `agentic-harness/docs/architecture.md`.
3. Stelle Ist und Soll gegenüber.
4. Ordne jeden betroffenen Pfad zu: **verschieben, behalten, zusammenführen oder entfernen**.
5. Zeige Abhängigkeitsrichtung, Importfolgen und betroffene Tests.
6. Gleiche diesen Umfang mit dem Auftrag ab. Nutze bestätigte Entscheidungen erneut. Frage nur bei einer echten offenen Entscheidung nach.

Beginne erst, wenn Ziel und Umfang eindeutig sind. Verkleinere einen ausdrücklich beauftragten Umbau nicht stillschweigend auf einen leichteren Teil. `src/` ist keine allgemeine Pflicht.

## 4. Soll-Verhalten festhalten

Bei beauftragtem neuem oder geändertem Nutzerverhalten:

1. Lies `agentic-harness/specs/S000-readme.md`.
2. Lies betroffene bestehende Specs, falls vorhanden.
3. Prüfe, ob weitere bestehende Specs angepasst werden müssen.
4. Lege bei Bedarf eine Spec mit überprüfbaren Akzeptanzkriterien an.
5. Nutze für eine neue Spec `agentic-harness/harness/templates/spec.md`.

Fehlt eine erforderliche Vorlage, melde die Lücke. Erfinde nicht stillschweigend ein Ersatzformat.

## 5. Änderung umsetzen

Setze die kleinste Änderung um, die den **gesamten vereinbarten Umfang** erfüllt. Halte bestätigte Projektgrenzen ein. Ändere keine unabhängigen Bereiche nebenbei.

Kläre Freigaben, bevor du echte Daten, externe Systeme oder irreversible Aktionen veränderst.

Wird während der Umsetzung eine neue Produktentscheidung nötig, stoppe. Kläre sie und aktualisiere die betroffenen Projektdateien oder Specs, bevor du auf der neuen Annahme weiterarbeitest.

## 6. Ergebnis prüfen

Führe die für das Zielprojekt eingerichteten Checks aus. Befehle und Geltungsbereich stehen in `agentic-harness/harness/project.md`. Die Testpraxis steht in `agentic-harness/docs/testing.md`.

Prüfe den Diff gegen Auftrag und bestätigten Zielzustand.

Bei Strukturänderungen gleiche den tatsächlichen Dateibaum mit dem Plan ab. Prüfe außerdem Imports und Testentdeckung.

Ein grüner Testlauf belegt keinen ausgelassenen Move.

Folge `agentic-harness/harness/verification/gate.md`. Fehlt ein erforderlicher Check oder eine erwartete Verification-Datei, behaupte keinen vollständigen Nachweis. Berichte die Lücke.

Bei Fehlschlag: Grenze die Ursache anhand beobachteter Evidenz ein. Kennzeichne unbestätigte Ursachen als Hypothesen. Ändere das Soll nicht nur, um einen Check grün zu bekommen.

## 7. Übergabe

Berichte knapp:

- Was wurde geändert und welcher vereinbarte Umfang erfüllt?
- Welche Befehle oder manuellen Prüfungen liefen tatsächlich, mit welchem Ergebnis?
- Welche Akzeptanzkriterien sind belegt?
- Was bleibt offen, fehlgeschlagen oder nicht verifiziert?

Setze `Implemented` nur, wenn alle betroffenen Akzeptanzkriterien belegt und alle erforderlichen Checks bestanden sind.

Sonst bleibt die Spec `Modified`. Benenne den Blocker.

Ohne Produktspec berichte den geprüften Umfang. Behaupte dann kein Produkt-Gate.

## Bundle-Vollständigkeit

Templates und Verification-Dateien gehören zum Harness-Bundle. Fehlt eine davon im Zielprojekt, melde das Bundle als unvollständig. Überspringe die referenzierte Regel nicht und behaupte keinen vollständigen Nachweis.
