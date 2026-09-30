# Project Init – leeres Projekt beginnen

> - **Typ:** Prozess
> - **Zuständigkeit:** Ein neues, leeres Produktprojekt für den ersten beauftragten Arbeitsschritt vorbereiten.
> - **Gilt bei:** Beauftragtem Project Init für ein neues, leeres Produktprojekt oder vor der ersten Produktumsetzung, wenn `agentic-harness/harness/project.md` noch `Pending Project Init` enthält. Nicht bei Harness-Engineering.
> - **Ladebeziehungen:**
>   - Vorher: `AGENTS.md` → `agentic-harness/harness/core.md` und `agentic-harness/harness/project.md`.
>   - Für Dateirollen und Format: `agentic-harness/harness-map.md` und `agentic-harness/document-contract.md`.
>   - Falls vorhanden: `agentic-harness/project-brief.md` als Ausgangsbeschreibung (keine bestätigte Spec).
>   - Danach: betroffene Projektdateien befüllen; Abschluss nach Abschnitt 4.
> - **Nicht zuständig:** Bestehende Anwendungen analysieren, spätere Features planen oder eine Produktspec als umgesetzt erklären.

**Grundsatz:** Der Harness ist universell und legt weder Projektart noch Stack, Architektur, Tests oder Profil fest. Diese Entscheidungen fallen hier, gemeinsam mit dem Auftraggeber, und landen erst nach Bestätigung in den Projektabschnitten. Fehlt eine Festlegung für ein neues Projekt, ist das kein Mangel des Harnesses, sondern eine Init-Frage.

## 1. Ersten Schritt klären

Kläre Nutzer, Problem und den ersten beobachtbaren Ablauf (z. B. Bildschirm, Befehl, Schnittstelle oder automatisch erzeugtes Ergebnis). Halte Umfang und Nicht-Ziele des ersten Meilensteins fest.

Frage nur nach Daten, Betrieb, Integrationen und Freigaben, die diesen Schritt beeinflussen. Erfinde keine Antworten.

Leite für den ersten Ablauf passende Bausteine, Stack- und Testkandidaten ab. Prüfe entscheidungsrelevante Versionen und Voraussetzungen anhand verfügbarer Quellen oder Werkzeuge. Vergleiche echte Alternativen kurz mit Nutzen und Kosten.

Technische Möglichkeiten bleiben **Vorschläge**, bis sie entschieden sind. Vertage nicht benötigte Technik.

Fasse den ersten Schritt und offene Entscheidungen zusammen. Bündle zusammengehörige, entscheidungsrelevante Rückfragen möglichst in **einem** priorisierten Fragenblock, statt sie nacheinander als Schleifen zu stellen. Bereits gegebene Antworten nicht erneut abfragen. Hole die nötige fachliche Bestätigung ein, bevor du Vorschläge als Projektfakten festhältst.

**Profil wählen:** Profile unter `agentic-harness/profiles/` bündeln Regeln und Init-Fragen für eine Projektart (z. B. `website.md`). Passt eines, trage „Profil: …“ oben im Projektprofil ein, stelle zusätzlich die Init-Fragen des Profils und nutze seine Regeln als Standard. Wann das Profil später gelesen wird, steht in seinem Kopf unter „Gilt bei“; `AGENTS.md` verweist darauf. Was aus dem Profil übernommen, angepasst oder abgewählt wird, steht in der thematisch zuständigen Projektdatei (Grenzen → Projektprofil, Struktur und Betrieb → Architektur, Stack → Code, Prüfungen → Testing, Gestaltung → Design). Passt keines (z. B. CLI, API, Bibliothek, Datenpipeline), arbeite ohne Profil; bewährte Regeln einer neuen Projektart können später als eigenes Profil entstehen.

**Zusatzblock bei sichtbarer Oberfläche** (Website, Web- oder Mobile-App, Desktop-Oberfläche; nur fragen, was für den ersten Schritt zählt):

- **Marke und Anmutung:** Name, Logo, vorhandene Farben und Schriften (mit Lizenz), Vorbilder. Vorbilder liefern Struktur, nicht Texte, Bilder oder Logos.
- **Zielgeräte:** Plattformen, Bildschirmgrößen, Barrierefreiheit.
- **Inhalte und Freigaben:** Wer liefert Texte und Bilder, wer gibt sie frei, welche Aussagen dürfen nicht versprochen werden?

**Arbeitsabsprachen** gehören ebenfalls in den Fragenblock, wenn sie noch unklar sind: Wie wird eine lokale Vorschau oder ein lokaler Start erwartet (z. B. laufender Dev-Server)? Wer committet wann? Arbeiten mehrere Agentensitzungen parallel? Werden Aufträge diktiert?

**Git:** Ist das Verzeichnis noch kein Git-Repository, schlage `git init` mit einem ersten Commit des unveränderten Harness vor. Ohne Git fehlt der Ort für den Verlauf (`agentic-harness/document-contract.md`), und die Regeln zu Arbeitsbaum und Parallelarbeit in `agentic-harness/harness/core.md` greifen nicht. Lehnt der Auftraggeber ab, halte das im Projektprofil fest.

## 2. Bestätigtes an die richtige Stelle schreiben

Lies die Inhaltsvorgaben von `agentic-harness/harness/project.md` und den Projekt-Docs. Behalte dort Dokumentkopf und „Universeller Rahmen“, aber prüfe den Kopf beim Befüllen: Stimmen Zuständigkeit, Auslöser, Ladebeziehungen und Abgrenzung zum bestätigten Projekt und zu den tatsächlichen Pfaden?

Ersetze „Noch offen (Project Init)“ unter „Projektspezifische Befüllung“ durch bestätigte Inhalte. Ist ein Bereich nicht entscheidbar oder nicht relevant, kennzeichne ihn ausdrücklich. Entferne den Platzhalterstatus erst nach tatsächlicher Befüllung.

- `agentic-harness/harness/project.md`: bestätigtes Nutzerziel, Umfang, Grenzen und Freigaben; Start- und Prüfbefehle mit dem letzten tatsächlichen Ergebnis (ersetzen, nicht protokollieren).
- `agentic-harness/docs/architecture.md`: bestätigte erste Bausteine, Zuständigkeiten, Datenfluss und entschiedener Betrieb; dazu die **Dateistruktur** vor dem ersten Produktcode: wo Konfiguration, Inhalte, Bausteine und bei Oberflächen die Gestaltungswerte liegen (Grundsatz dort unter „Trennung von Konfiguration und Bausteinen“, Vorschlag ggf. aus dem Profil). Geplantes und Offenes gesondert kennzeichnen.
- `agentic-harness/docs/code.md`: nur geltende Konventionen für den gewählten Stack, einschließlich Benennung und Ablage neuer Bausteine.
- `agentic-harness/docs/testing.md`: aus Ablauf, Risiken, Architektur und Stack passende Testebenen und -arten wählen; Werkzeuge, Teststruktur und Grenzen für den ersten Meilenstein begründen. Bei sichtbarer Oberfläche auch Prüfgrößen (z. B. Bildschirmbreiten), Methoden und Mess-Werkzeug.
- `agentic-harness/docs/design.md`: nur bei sichtbarer Oberfläche. Bestätigte Farbrollen, Schrift mit Lizenz, Größenskala und erste Bausteine eintragen; Unentschiedenes als offen markieren. Ohne Oberfläche den Bereich ausdrücklich als „nicht relevant“ kennzeichnen.
- Root-`AGENTS.md`: bei Bedarf zusätzliche Projekt-Docs mit konkretem Leseauslöser und bestätigte Arbeitsabsprachen (z. B. Live-Vorschau) unter „Projektspezifische Ergänzungen“ eintragen; keine Detailregeln kopieren.

Befülle die Root-`README.md` des Zielprojekts ohne Metakopf mit bestätigtem Produktzweck und geprüften Startschritten. Enthält sie nur die Vorlagenbeschreibung aus dem Export, ersetze sie; liegen bereits Produktinformationen vor, ergänze statt zu überschreiben. Die menschliche Harness-Anleitung in `agentic-harness/README.md` bleibt davon getrennt. Erfinde keine Produktfakten.

## 3. Prüf-Einstieg und Verweise prüfen

Richte passende Checks ein, sobald sie ausführbar sind. Führe sie tatsächlich aus. Prüfe bei Bedarf, ob sie einen absichtlichen Fehler erkennen.

Bei sichtbaren Oberflächen richte früh ein wiederverwendbares Mess- und Screenshot-Werkzeug für das Zielmedium ein (z. B. Headless-Browser, Emulator, Terminal-Aufzeichnung) und nenne es in `agentic-harness/docs/testing.md`.

Eine leere Testsuite oder ein geplanter Befehl gilt nicht als bestanden. Halte nicht eingerichtete Checks im Projektprofil offen.

Prüfe auch die Ladebeziehungen in den befüllten Dokumentköpfen. Ergänzte Verweise müssen vom Repo-Root aus auf vorhandene Dateien zeigen. Wenn sich Rollen oder Ladeauslöser geändert haben, passe `AGENTS.md` und `agentic-harness/harness-map.md` gezielt an.

## 4. Abschlusscheck und Übergabe

Vor dem Wechsel zum Produktbau ausdrücklich **Go/No-Go** prüfen:

1. Sind Nutzer, Problem, erster Ablauf, Umfang und Nicht-Ziele des ersten Schritts ausreichend bestätigt? Welche fachlichen, technischen oder rechtlichen Entscheidungen blockieren **diesen** Bau tatsächlich, welche erst einen späteren Livegang?
2. Sind die bestätigten Fakten in `agentic-harness/harness/project.md` und den betroffenen Projekt-Docs an der richtigen Stelle, während Vorschläge, offene Punkte und noch nicht eingerichtete Checks sichtbar offen bleiben? Stimmen die Dokumentköpfe und Verweise mit dem tatsächlichen Baum überein?
3. Sind für den beauftragten Schritt nötige Prüfungen eingerichtet und ausgeführt oder ehrlich als offen markiert? Eine Dokumentprüfung ersetzt keinen Produktcheck.

Bei **No-Go** keine Produktimplementierung beginnen: die verbleibenden blockierenden Fragen gebündelt vorlegen und `Pending Project Init` beibehalten. Bei **Go** die begründete Entscheidung und eventuelle nicht blockierende Livegang-Lücken im Projektprofil festhalten; erst danach zur Einordnung des konkreten Bauauftrags zurückkehren. Der Übergang ist keine automatische Implementierungsfreigabe.

Entferne `Pending Project Init` erst, wenn Ziel, Grenzen und erster Schritt ausreichend geklärt sind. Das bedeutet **nicht**: Produkt-Gate bestanden oder Spec `Implemented`.

Für beauftragtes Nutzerverhalten nutze `agentic-harness/specs/S000-readme.md` und `agentic-harness/harness/templates/spec.md`.

Eine Idea nach `agentic-harness/ideas/I000-readme.md` ist nur bei offenem Klärungsbedarf nötig. Nach dem Init lies das aktualisierte `agentic-harness/harness/project.md` und kehre für den aktuellen Auftrag zu `agentic-harness/harness/core.md` zurück. Init allein ist keine Implementierungsfreigabe. Bleibt eine dafür nötige Entscheidung offen, berichte den Blocker statt auf einer Annahme umzusetzen. Übertragbare Beobachtungen zum Harness, die beim Init auffallen, gehören als offene Kandidaten nach `agentic-harness/harness-learnings.md`, nicht in die Produktdateien.
