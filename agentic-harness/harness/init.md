# Project Init – leeres Projekt beginnen

> - **Typ:** Prozess
> - **Zuständigkeit:** Ein neues, leeres Produktprojekt für den ersten beauftragten Arbeitsschritt vorbereiten: bei offener Richtung zuerst billig erkunden, dann Architektur, Tech-Stack und Prüfungen wählen und die Projektdateien befüllen.
> - **Gilt bei:** Beauftragtem Project Init für ein neues, leeres Produktprojekt oder vor der ersten Produktumsetzung, wenn `harness/project.md` noch `Pending Project Init` enthält. Nicht bei Harness-Engineering.
> - **Ladebeziehungen:**
>   - Vorher: `AGENTS.md` → `harness/core.md` und `harness/project.md`.
>   - Für Dateirollen und Format: `harness-map.md` und `document-contract.md`.
>   - Falls vorhanden: `project/brief.md` als Ausgangsbeschreibung (keine bestätigte Spec); Themen und Ablauf: Root-`README.md`, Abschnitt „Projektstart mit dem Agentic Harness“.
>   - Danach: betroffene Projektdateien befüllen; Abschluss nach Abschnitt 4.
> - **Nicht zuständig:** Bestehende Anwendungen analysieren, spätere Features planen oder eine Produktspec als umgesetzt erklären.

**Grundsatz:** Der Harness ist universell und legt weder Projektart noch Stack, Architektur, Tests oder Profil fest. Diese Entscheidungen fallen hier, gemeinsam mit dem Auftraggeber, und landen erst nach Bestätigung in den Projektabschnitten. Fehlt eine Festlegung für ein neues Projekt, ist das kein Mangel des Harnesses, sondern eine Init-Frage.

**Aufgabenteilung:** Der **Brief** beschreibt, was entstehen soll und warum, auch technische Vorstellungen in eigenen Worten. Das **Init** übersetzt das in einen tragfähigen technischen Rahmen (Architektur, Tech-Stack, Tests, Betrieb) und befüllt die Projektdateien. Dazwischen liegt nur bei offener Richtung ein kurzes **Erkunden**.

## 0. Erkunden oder direkt festlegen?

Lege im Init nur fest, was entschieden ist. Ist die Richtung noch offen, erkunde zuerst so billig wie möglich. Es gilt genau **eine** Erkundungsstufe (E0–E3, nicht zu verwechseln mit den Abschnitten 0–4 dieser Datei):

| Erkundungsstufe | Wann | Vorgehen |
|---|---|---|
| E0 – direkt festlegen | Brief oder Auftrag entscheiden die Richtung (Standardfall) | weiter mit Abschnitt 1 |
| E1 – Ideenrunde in Text | Gestaltung oder Lösungsweg offen | 2–3 klar verschiedene Leitideen in je wenigen Sätzen vorlegen; der Auftraggeber wählt |
| E2 – ein Prototyp | die gewählte Idee muss man sehen oder ausprobieren, bevor man festlegt | einen Wegwerf-Prototyp bauen (bei Software ohne Oberfläche z. B. Trockenlauf mit Beispieldaten oder kleinster technischer Durchstich) |
| E3 – mehrere Varianten | nur wenn ausdrücklich beauftragt | je Variante eine eigene Leitidee und eigene Gestaltung; geteilt werden nur Inhalte und Messwerkzeuge |

Beim Erkunden gelten nur die Pflichtregeln eines passenden Profils (Teil A) und die Prüfschleife im Zielmedium; keine Specs, keine befüllten Projekt-Docs, keine gemeinsame Gestaltungsbasis. Prototypen nutzen die einfachste passende Technik (z. B. statisches HTML mit Beispieldaten als Klick-Prototyp) und legen keinen Tech-Stack fest; frage dafür nicht nach Stack oder Architektur, das entscheidet Abschnitt 1 nach der Auswahl. Ausnahme: Ist die offene Frage die Machbarkeit (z. B. eine Anbindung), nutzt der Durchstich eine vorläufige Technik, die als vorläufig gekennzeichnet bleibt. Unterlagen sind Inspiration, die eigene Leitidee hat Vorrang. Hat das Profil eine Inspirations-Sammlung (Website: `profiles/website/inspiration/README.md`), setzt jeder Entwurf mindestens auf deren Niveau an (Schrift, Inhaltsdichte, Grafik), ohne sie nachzubauen; bewertet der Auftraggeber einen Entwurf als gelungen, schlage einen Eintrag dort vor. Prototypen und Varianten sind intern (`docs/architecture.md`, „Varianten, Konzeptseiten und Archiv“) und liegen in einem eigenen Ordner (z. B. `entwuerfe/`); Werkzeuge eines Profils prüfen ihn ohne Projekt-Setup (Website: `ORDNER=entwuerfe`, `profiles/website/README.md`). `Pending Project Init` bleibt stehen. **Halt nach dem Erkunden:** Lege das Ergebnis zur Auswahl vor und stoppe. Nach der Auswahl folgt das Init (Abschnitte 1–4): Die gewählte Richtung wird Basis, der Rest wandert ins Archiv. Ihre Gestaltung (Schriften, Farben, Bildsprache, Anordnung, Inhaltsdichte) wird übernommen, nicht vereinfacht oder durch Profil-Vorschläge ersetzt; Abweichungen nur mit Zustimmung.

## 1. Ersten Schritt klären

**Brief erzählt, Init konkretisiert:** Liegt `project/brief.md` vor, gilt, was er beantwortet, als gegeben: Fasse es kurz zur Bestätigung zusammen, statt es neu abzufragen. Prüfe dann wie ein Kontrolleur, was für die Umsetzung noch fehlt oder sich widerspricht, und frage nur dazu nach. Inhaltliche Themen (Idee, Zielgruppen, Inhalte, Ton, Vorbilder, Vorgaben, Rahmen) stehen einmal in der Root-`README.md`, Abschnitt „Projektstart mit dem Agentic Harness“; dieser Abschnitt ergänzt, was zur Umsetzung dazukommt: Anforderungen, Tech-Stack, Daten, Betrieb, Tests und Arbeitsabsprachen. Fehlt der Brief, kläre die inhaltlichen Themen zuerst im Gespräch.

Kläre Nutzer, Problem und den ersten beobachtbaren Ablauf (z. B. Bildschirm, Befehl, Schnittstelle oder automatisch erzeugtes Ergebnis). Halte Umfang und Nicht-Ziele des ersten Meilensteins fest.

Frage nur nach Daten, Betrieb, Integrationen und Freigaben, die diesen Schritt beeinflussen. Erfinde keine Antworten.

**Architektur und Tech-Stack wählen (Kern des Init):** Leite aus Brief, erstem Ablauf, Daten, Betrieb und gesetzten Vorgaben 2–3 tragfähige Optionen ab (Architektur, Sprache und Frameworks, Datenhaltung, Betrieb, Testwerkzeuge). Vergleiche sie knapp: Passung zum Ziel, Komplexität und Wartung, Kosten und Betrieb, Risiken, Abhängigkeiten, Kenntnisse des Auftraggebers. Empfiehl eine Option mit Begründung; die einfachste, die den ersten Meilenstein und absehbare nächste Schritte trägt, ist der Normalfall. Prüfe entscheidungsrelevante Versionen und Voraussetzungen anhand verfügbarer Quellen oder Werkzeuge. **Halt zur Technikwahl:** Lege Optionen und Empfehlung vor und warte auf Bestätigung, bevor du Projektdateien befüllst; nur wenn der Auftraggeber ausdrücklich selbst entscheiden lässt, gilt die Empfehlung als gekennzeichnete Annahme. Die bestätigte Entscheidung steht mit Begründung und verworfenen Alternativen in `docs/architecture.md`.

Technische Möglichkeiten bleiben **Vorschläge**, bis sie entschieden sind. Vertage nicht benötigte Technik.

Fasse den ersten Schritt und offene Entscheidungen zusammen. Bündle zusammengehörige, entscheidungsrelevante Rückfragen möglichst in **einem** priorisierten Fragenblock, statt sie nacheinander als Schleifen zu stellen. Bereits gegebene Antworten nicht erneut abfragen. Hole die nötige fachliche Bestätigung ein, bevor du Vorschläge als Projektfakten festhältst. **Erlaubte Annahmen:** Lässt der Auftraggeber ausdrücklich Annahmen statt einer Fragerunde zu, beginnt jede in den Projektdateien mit „**Annahme:**“, und das Projektprofil führt unter den offenen Entscheidungen einen Punkt „Annahmen bestätigen“ mit den betroffenen Dateien; eine bestätigte Annahme verliert die Markierung.

**Profil wählen:** Profile unter `profiles/` bündeln Regeln und Init-Fragen für eine Projektart (z. B. `website.md`). Passt eines, trage „Profil: …“ oben im Projektprofil ein, stelle zusätzlich die Init-Fragen des Profils und nutze seine Regeln als Standard. Wann das Profil später gelesen wird, steht in seinem Kopf unter „Gilt bei“; `AGENTS.md` verweist darauf. Was aus dem Profil übernommen, angepasst oder abgewählt wird, steht in der thematisch zuständigen Projektdatei (Grenzen → Projektprofil, Struktur und Betrieb → Architektur, Stack → Code, Prüfungen → Testing, Gestaltung → Design). Passt keines (z. B. CLI, API, Bibliothek, Datenpipeline), arbeite ohne Profil; bewährte Regeln einer neuen Projektart können später als eigenes Profil entstehen.

**Zusatzblock bei sichtbarer Oberfläche** (Website, Web- oder Mobile-App, Desktop-Oberfläche; nur fragen, was für den ersten Schritt zählt und nicht schon im Brief steht):

- **Marke und Anmutung:** Name, Logo, vorhandene Farben und Schriften (mit Lizenz), Vorbilder. Vorbilder liefern Struktur, nicht Texte, Bilder oder Logos.
- **Zielgeräte:** Plattformen, Bildschirmgrößen, Barrierefreiheit.
- **Inhalte und Freigaben:** Wer liefert Texte und Bilder, wer gibt sie frei, welche Aussagen dürfen nicht versprochen werden?

**Arbeitsabsprachen** gehören ebenfalls in den Fragenblock, wenn sie noch unklar sind: Wie wird eine lokale Vorschau oder ein lokaler Start erwartet (z. B. laufender Dev-Server)? Wer committet wann? Arbeiten mehrere Agentensitzungen parallel? Werden Aufträge diktiert?

**Git:** Ist das Verzeichnis noch kein Git-Repository, schlage `git init` mit einem ersten Commit des unveränderten Harness vor. Ohne Git fehlt der Ort für den Verlauf (`document-contract.md`), und die Regeln zu Arbeitsbaum und Parallelarbeit in `harness/core.md` greifen nicht. Lehnt der Auftraggeber ab, halte das im Projektprofil fest.

## 2. Bestätigtes an die richtige Stelle schreiben

Lies die Inhaltsvorgaben von `harness/project.md` und den Projekt-Docs. Behalte dort Dokumentkopf und „Universeller Rahmen“, aber prüfe den Kopf beim Befüllen: Stimmen Zuständigkeit, Auslöser, Ladebeziehungen und Abgrenzung zum bestätigten Projekt und zu den tatsächlichen Pfaden?

Ersetze „Noch offen (Project Init)“ unter „Projektspezifische Befüllung“ durch bestätigte Inhalte. Ist ein Bereich nicht entscheidbar oder nicht relevant, kennzeichne ihn ausdrücklich. Entferne den Platzhalterstatus erst nach tatsächlicher Befüllung.

- `harness/project.md`: bestätigtes Nutzerziel, Umfang, Grenzen und Freigaben; Start- und Prüfbefehle je eine Zeile, für die vom Gate gebrauchten mit dem letzten tatsächlichen Ergebnis (ersetzen, nicht protokollieren).
- `docs/architecture.md`: bestätigte erste Bausteine, Zuständigkeiten, Datenfluss und entschiedener Betrieb; dazu die **Dateistruktur** vor dem ersten Produktcode: wo Konfiguration, Inhalte, Bausteine und bei Oberflächen die Gestaltungswerte liegen (Grundsatz dort unter „Trennung von Konfiguration und Bausteinen“, Vorschlag ggf. aus dem Profil). Geplantes und Offenes gesondert kennzeichnen.
- `docs/code.md`: nur geltende Konventionen für den gewählten Stack, einschließlich Benennung und Ablage neuer Bausteine.
- `docs/testing.md`: aus Ablauf, Risiken, Architektur und Stack passende Testebenen und -arten wählen; Werkzeuge, Teststruktur und Grenzen für den ersten Meilenstein begründen. Bei sichtbarer Oberfläche auch Prüfgrößen (z. B. Bildschirmbreiten), Methoden und Mess-Werkzeug.
- `docs/design.md`: nur bei sichtbarer Oberfläche. Bestätigte Farbrollen, Schrift mit Lizenz, Größenskala und erste Bausteine eintragen, bei gewähltem Entwurf aus dessen Gestaltung; Unentschiedenes als offen markieren. Ohne Oberfläche den Bereich ausdrücklich als „nicht relevant“ kennzeichnen.
- Root-`AGENTS.md`: bei Bedarf zusätzliche Projekt-Docs (Kriterium und Ort: `document-contract.md`, „Neue Projekt-Docs“; sie liegen unter `project/`) mit konkretem Leseauslöser und bestätigte Arbeitsabsprachen (z. B. Live-Vorschau) unter „Projektspezifische Ergänzungen“ eintragen; keine Detailregeln kopieren.

Befülle die Root-`README.md` des Zielprojekts ohne Metakopf mit bestätigtem Produktzweck und geprüften Startschritten. Ersetze dabei den Vorlagenkopf aus dem Export durch die Produktbeschreibung oben; liegen bereits Produktinformationen vor, ergänze statt zu überschreiben. Reihenfolge: Titel, lokale Adresse (falls es eine gibt), unverändert der universelle Abschnitt „Projektstart mit dem Agentic Harness“, darunter projektspezifische Abschnitte (z. B. Projektaufbau, „Lokal ansehen“). Die menschliche Harness-Anleitung in `harness/README.md` bleibt davon getrennt. Erfinde keine Produktfakten.

## 3. Prüf-Einstieg und Verweise prüfen

Richte passende Checks ein, sobald sie ausführbar sind. Führe sie tatsächlich aus. Prüfe bei Bedarf, ob sie einen absichtlichen Fehler erkennen.

Bei sichtbaren Oberflächen richte früh ein wiederverwendbares Mess- und Screenshot-Werkzeug für das Zielmedium ein (z. B. Headless-Browser, Emulator, Terminal-Aufzeichnung) und nenne es in `docs/testing.md`.

Eine leere Testsuite oder ein geplanter Befehl gilt nicht als bestanden. Halte nicht eingerichtete Checks im Projektprofil offen.

Prüfe auch die Ladebeziehungen in den befüllten Dokumentköpfen. Ergänzte Verweise müssen vom Repo-Root aus auf vorhandene Dateien zeigen. Wenn sich Rollen oder Ladeauslöser geändert haben, passe `AGENTS.md` und `harness-map.md` gezielt an.

## 4. Abschlusscheck und Übergabe

Vor dem Wechsel zum Produktbau ausdrücklich **Go/No-Go** prüfen:

1. Sind Nutzer, Problem, erster Ablauf, Umfang und Nicht-Ziele des ersten Schritts ausreichend bestätigt? Welche fachlichen, technischen oder rechtlichen Entscheidungen blockieren **diesen** Bau tatsächlich, welche erst einen späteren Livegang?
2. Sind die bestätigten Fakten in `harness/project.md` und den betroffenen Projekt-Docs an der richtigen Stelle, während Vorschläge, offene Punkte und noch nicht eingerichtete Checks sichtbar offen bleiben? Stimmen die Dokumentköpfe und Verweise mit dem tatsächlichen Baum überein?
3. Sind für den beauftragten Schritt nötige Prüfungen eingerichtet und ausgeführt oder ehrlich als offen markiert? Eine Dokumentprüfung ersetzt keinen Produktcheck.

Bei **No-Go** keine Produktimplementierung beginnen: die verbleibenden blockierenden Fragen gebündelt vorlegen und `Pending Project Init` beibehalten. Bei **Go** die begründete Entscheidung und eventuelle nicht blockierende Livegang-Lücken im Projektprofil festhalten; erst danach zur Einordnung des konkreten Bauauftrags zurückkehren. Der Übergang ist keine automatische Implementierungsfreigabe: Stoppe und schlage den ersten Bauauftrag vor (Ablauf in Prompts: Root-`README.md`, Abschnitt „Projektstart mit dem Agentic Harness“).

Entferne `Pending Project Init` erst, wenn Ziel, Grenzen und erster Schritt ausreichend geklärt sind. Das bedeutet **nicht**: Produkt-Gate bestanden oder Spec `Implemented`.

Für beauftragtes Nutzerverhalten nutze `specs/S000-readme.md` und `harness/templates/spec.md`.

Eine Idea nach `ideas/I000-readme.md` ist für größere Änderungen oder offenen Klärungsbedarf da, nicht für den ersten Schritt selbst. Nach dem Init lies das aktualisierte `harness/project.md` und kehre für den aktuellen Auftrag zu `harness/core.md` zurück. Init allein ist keine Implementierungsfreigabe. Bleibt eine dafür nötige Entscheidung offen, berichte den Blocker statt auf einer Annahme umzusetzen. Übertragbare Beobachtungen zum Harness, die beim Init auffallen, gehören als offene Kandidaten nach `harness-learnings.md`, nicht in die Produktdateien.
