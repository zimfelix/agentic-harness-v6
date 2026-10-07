---
name: project-init
description: Startet ein Projekt mit dem Auftraggeber in zwei Phasen. Zuerst ein freies Projektgespräch, das in einen Brief übersetzt wird (Ziel, Reifegrad, erstes Ergebnis, Erfolg, Risiken, Ausgangslage). Danach die Technik (Stack, Struktur, Checks, passende Skills). Das Ergebnis wird in den Abschnitt „Projekt“ der AGENTS.md eingetragen. Nutzen, wenn AGENTS.md „Pending Project Init“ zeigt und Produktarbeit beginnen soll oder ein Init ausdrücklich beauftragt ist. Gilt für leere Ordner und für bestehenden Code.
---

# Project Init

Der Harness legt weder Projektart noch Stack, Architektur oder Tests fest. Das entsteht hier gemeinsam mit dem Auftraggeber. Für Annahmen und Rückfragen gilt die Arbeitsweise in `AGENTS.md`: Reversible Annahmen nennst du und arbeitest weiter, Folgenreiches fragst du gebündelt nach.

Die Phasen 0–4 laufen nacheinander; die grafische Übersicht steht in `README.md`.

## 0. Ausgangslage prüfen

- **Bestehender Code:** Lies zuerst den Ist-Stand (Struktur, Stack, Befehle, Tests) und trage ihn ein. Was sich aus dem Code ablesen lässt, wird nicht erfragt.
- **Vorhandener Brief:** Ein eingefügter Text oder eine Datei wie `project-brief.md` dient als Grundlage für das Gespräch und gilt noch nicht als bestätigt.
- **Git:** Ist der Ordner noch kein Repository, schlage `git init` mit einem ersten Commit der unveränderten Vorlage vor.

## 1. Projektgespräch → Brief

Der Auftraggeber erzählt frei, oft diktiert und ungeordnet. Unterbrich ihn nicht mit einem Fragebogen. Übersetze das Gesagte anschließend in diese Felder:

| Feld | Leitfrage |
|---|---|
| Ziel und Nutzer | Welches Problem soll für wen gelöst werden? |
| Reifegrad | Wegwerf-Prototyp, MVP oder dauerhaft gepflegtes Produkt? |
| Erstes Ergebnis, Nicht-Ziele | Was ist der erste beobachtbare Ablauf (Bildschirm, Befehl, Schnittstelle, erzeugtes Ergebnis)? Was gehört ausdrücklich nicht dazu? |
| Erfolgskriterium | Woran erkennen wir, dass das erste Ergebnis ausreicht? |
| Risiken, Grenzen, Freigaben | Echte Daten, Berechtigungen, Zahlungen, Veröffentlichung, Kosten? Wer gibt was frei? |
| Ausgangslage | Bestehender Code, vorgegebener Stack, Betrieb, Einschränkungen? |

Zeige den Brief kompakt und markiere jedes Feld als **bestätigt**, **Annahme** oder **offen**. Stelle nur zu folgenreichen Lücken Fragen, gebündelt in **einem** Block. Nach der Bestätigung trägst du die Felder in `AGENTS.md` unter „Projekt“ ein. Offene Felder bleiben ausdrücklich „offen“, Annahmen stehen unter „Offene Entscheidungen und Annahmen“.

## 2. Technik

Erst jetzt geht es um die technischen Teile. Der Brief bestimmt, wie viel Technik nötig ist; Technik, die erst später gebraucht wird, wird vertagt.

- **Stack:** Übernimm Vorgaben aus der Ausgangslage. Sonst schlägst du Kandidaten vor: Prüfe die entscheidungsrelevanten Versionen an aktuellen Quellen und vergleiche echte Alternativen kurz nach Nutzen und Kosten.
- **Struktur:** Lege vor dem ersten Code fest, wo Konfiguration, Inhalte, Bausteine und bei Oberflächen die Gestaltungs-Tokens liegen.
- **Standards und Qualitätsziele:** Kläre vorhandene Coding-Konventionen und verbindliche technische, fachliche oder rechtliche Standards einschließlich relevanter Versionen und Geltungsbereich. Kläre risikorelevante Qualitätsziele (z. B. Performance, Sicherheit, Barrierefreiheit, Wiederherstellung) als messbare Anforderungen mit Prüfverfahren. Fehlende Vorgaben bleiben offen oder werden ausdrücklich als nicht relevant bestätigt; keine Standards oder Grenzwerte erfinden. Übernimm vorhandene Tool-Konfigurationen als Quelle der Wahrheit. Durchsetzbare Konventionen kommen in Formatter, Linter, Typprüfung oder Tests; nur nicht technisch abbildbares Wissen gehört in den Projektabschnitt oder Projekt-Docs mit Leseauslöser.
- **Tests und Regression:** Wähle nach Reifegrad, Risiken und gewählten Skills die nötigen Testebenen (Unit, Integration, System/E2E) sowie risikobezogene Prüfungen (z. B. Rechte, Sicherheit, Performance, Barrierefreiheit). Halte je Auswahl Prüfziel und Grenze fest, Abgewähltes mit kurzem Grund; kein pauschales Vollpaket und keine Ausnahme von Pflichtchecks des Arbeitsrahmens oder gewählter Skills. Lege Pflichtbefehle, Regressionumfang, nötige Umgebung und Ausführung lokal/CI fest, einschließlich betroffener Nutzerabläufe bei gemeinsamen Bausteinen. Richte vereinbarte CI-Prüfungen passend zum Stack und Repository ein. Offene Checks brauchen Auslöser oder Termin und Zuständigkeit. Der Verification Loop und fehlende Nachweise sind unter „Fertig heißt“ in `AGENTS.md` geregelt.
- **TDD:** Entscheide je Bereich, ob Test-first sinnvoll ist: besonders bei klarer Fachlogik, Grenzfällen und reproduzierbaren Fehlern; bei explorativen Oberflächen oder unbekannten Schnittstellen kann erst ein kleiner Spike nötig sein. Halte Einsatz oder Nicht-Einsatz mit kurzem Grund in der Prüfstrategie fest. Bei TDD: Test aus dem Soll ableiten → erwarteten Verhaltensfehler beobachten → minimal implementieren → refactoren bei grünen Tests. TDD ersetzt weder Akzeptanznachweise noch Regression.
- **Skills:** Passt ein Skill unter `.agents/skills/` zur Projektart (z. B. `business-software` für CRM, Buchung oder Buchhaltung, `website` für Websites), trägst du ihn unter „Skills“ ein, liest ihn und stellst seine Init-Fragen. Mehrere Skills können zugleich gelten. Bietet ein Skill eine Bereichsauswahl an, hältst du die gewählten und abgewählten Bereiche mit fest.
- **Arbeitsabsprachen:** erwartete lokale Vorschau (z. B. laufender Dev-Server), wer wann committet, parallele Agentensitzungen.

Nach der Bestätigung ergänzt du:

- **`AGENTS.md`, Abschnitt „Projekt“:** Stack und Struktur, Standards und Qualitätsziele, Prüfstrategie, Skills, Befehle, offene Entscheidungen und Fortsetzungsstand. Die übrigen Abschnitte bleiben unverändert.
- **`docs/<thema>.md`:** nur, wenn Wissen weder in den Code noch in „Projekt“ passt, z. B. `docs/design.md` bei einer Oberfläche. Für Umfang, Zuständigkeit und Verlinkung gilt „Projektdateien“ in `AGENTS.md`.
- **`README.md`:** Ganz oben ergänzt du einen Abschnitt „Produkt“ mit Zweck und geprüften Startschritten. Die Harness-Übersicht darunter bleibt stehen.
- **Ideas und Specs:** Halte bereits beauftragtes Verhalten nach dem Arbeitsrahmen in `specs/` fest, unklare oder ausdrücklich zurückgestellte Vorhaben in `ideas/`. Für Klärung, Überführung, Vorlagen und Status gilt „Ideas und Specs“ in `AGENTS.md`; beim Init relevante bestätigte Zusammenhänge verlinken, nicht alle Artefakte auf Vorrat laden.

## 3. Checks einrichten

Richte die vereinbarten Checks ein, sobald sie ausführbar sind, und führe sie wirklich aus, lokal und gegebenenfalls in CI. Prüfe einmal mit einem absichtlichen Fehler, ob sie anschlagen; entferne die absichtliche Änderung anschließend und führe die Checks erneut auf dem unveränderten Sollstand aus. Bei Oberflächen richtest du früh ein wiederverwendbares Mess- und Screenshot-Werkzeug ein. Trage das Ergebnis in die Befehlstabelle ein; Checks, die noch nicht eingerichtet sind, stehen dort als offen.

## 4. Go/No-Go

1. Sind Ziel, Reifegrad, erstes Ergebnis und Erfolgskriterium bestätigt? Welche offenen Punkte blockieren **diesen** Bau und welche erst den Livegang?
2. Stehen die bestätigten Fakten an ihrem Ort, und sind Annahmen und Offenes als solche erkennbar?
3. Sind die nötigen Checks eingerichtet und ausgeführt oder mit Auslöser und Zuständigkeit ehrlich als offen markiert? Für den ersten Auftrag erforderliche, aber fehlende Checks sind spätestens vor dessen Abschluss nachzuholen; ein Init-Go ersetzt keinen Verhaltensnachweis.
4. Sind Standards und Qualitätsziele geklärt oder als nicht blockierende Lücke vermerkt, und ist erkennbar, wie sie durchgesetzt und geprüft werden?

**No-Go:** Die blockierenden Fragen gebündelt vorlegen; `Pending Project Init` bleibt stehen. **Go:** Den Status in „Projekt“ entfernen und nicht blockierende Lücken unter „Offene Entscheidungen und Annahmen“ eintragen. Ein Go ist keine Freigabe für die Umsetzung: Danach wird der konkrete Auftrag nach `AGENTS.md` bearbeitet.
