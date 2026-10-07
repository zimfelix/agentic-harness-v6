# Project Init

**Gilt bei:** Beauftragtem Init oder Produktarbeit bei `Pending Project Init`, auch mit bestehendem Code. Nicht bei reiner Harness-/Dokuarbeit. Vorher Core und Projektprofil, beim Schreiben `document-contract.md` lesen.

## 0. Ausgangslage und Erkundung

Bestand, Git, Struktur, vorhandene Befehle/Tests prüfen. Eine vom Auftraggeber angegebene Ausgangsbeschreibung als Quelle lesen, nicht als bestätigte Spec behandeln. Ohne Git `git init` vorschlagen; Commits nur auf Auftrag.

Ist die Richtung klar, direkt zum Brief. Bei offener Richtung genau eine passende Stufe wählen:

- **E1:** 2–3 Ideen in Text zur Auswahl.
- **E2:** ausdrücklich abgegrenzter Wegwerf-Spike für eine offene Gestaltungs-/Machbarkeitsfrage.
- **E3:** mehrere Varianten nur auf ausdrücklichen Auftrag.

Ein Spike ist keine Ausnahme zum heimlichen Produktbau: Frage, Umfang, Beispieldaten, vorläufige Technik, eigener Ordner (`entwuerfe/` o. Ä.) und Nachweis vorher festhalten. Keine echten Seiteneffekte; Pflichtregeln passender Profile gelten. Keine Produktspec für den Spike nötig. `Pending Project Init` bleibt; Ergebnis vorlegen und zur Auswahl stoppen. Gewählten Entwurf übernehmen, verworfene Varianten aus aktivem Build/Test entfernen oder als Archiv benennen.

## 1. Gespräch → bestätigter Brief

Freie Beschreibung in diese Felder übersetzen; Antworten nicht erneut abfragen:

| Feld | Inhalt |
|---|---|
| Ziel und Nutzer | Problem, Zielgruppe, Nutzen |
| Reifegrad | Prototyp, MVP oder dauerhaftes Produkt |
| Erstes Ergebnis / Nicht-Ziele | Erster beobachtbarer Ablauf und Abgrenzung |
| Erfolgskriterium | Woran wird der erste Schritt geprüft? |
| Risiken, Grenzen, Freigaben | Echte Daten, Rechte, externe Dienste, Kosten, Löschen/Versand/Veröffentlichung |
| Ausgangslage | Bestand, Vorgaben, Betrieb, Material, Kenntnisse |

Je Feld **bestätigt**, **Annahme** oder **offen** markieren. Brief kompakt vorlegen und nötige Bestätigung einholen; nur folgenschwere Lücken gebündelt fragen. Ausdrücklich überlassene reversible Entscheidungen als Annahmen markieren. Bestätigtes in `harness/project.md` eintragen; die optionale Quelldatei muss nicht nachgeführt werden.

Bei Oberfläche zusätzlich nur relevante Lücken: Marke/Material/Rechte, Anmutung/Vorbilder, Zielgeräte, Barrierefreiheit, Inhalte/Freigaben. Keine Produktfakten erfinden.

## 2. Technik und Arbeitsrahmen

- **Profile:** Projektart einordnen, passende Profile lesen und deren Init-Fragen/Bereichsauswahl nutzen. `profiles/business-software/profile.md` für Geschäfts-/Personendaten oder externe Seiteneffekte; `profiles/website/profile.md` für Websites. Gewählte Bereiche und Abgewähltes mit Grund im Projektprofil eintragen. Kein Profil auf Vorrat.
- **Stack:** Gesetztes übernehmen; sonst tragfähige Alternativen kurz nach Nutzen, Aufwand, Kosten und Risiken vergleichen, Empfehlung vorlegen. Entscheidungsrelevante Versionen/Voraussetzungen an Primärquellen prüfen. Technik bestätigen lassen oder ausdrücklich delegierte Entscheidung als Annahme führen.
- **Struktur vor Code:** In `docs/architecture.md` Zuständigkeiten, Abhängigkeits-/Datenfluss, Betrieb und tatsächliche Zielstruktur festlegen: Source, Tests, Konfiguration, Inhalte, Scripts, Assets, ggf. Tokens und Archiv. Für neue Python-Anwendungen ist `src/<paket>/` mit `tests/` der Ausgangsvorschlag; bestehende Struktur/Framework-Konventionen nicht ohne Grund umbauen. Abweichungen begründen. Kein Produktcode im Harness-Ordner.
- **Standards/Qualität:** Geltende Coding-Konventionen und fachliche/technische Standards samt Geltungsbereich klären. Messbare risikorelevante Ziele festlegen; durchsetzbare Regeln in Formatter/Linter/Typprüfung/Tests, nicht in doppelte Prosa. Offenes ausdrücklich benennen.
- **Prüfstrategie:** Aus Ablauf, Risiken und Profilen Ebenen und Fehlerfälle wählen, Abgewähltes begründen. Pflichtbefehle, Regressionumfang, Umgebung, lokal/CI und Auslöser offener Checks festlegen. TDD je Bereich bewusst wählen (klare Regeln/Fehlerfälle besonders geeignet; explorative UI/Schnittstellen ggf. Spike). Keine leeren Pflichtsuiten.
- **Reifegrad:** Prototyp: Hauptablauf plus relevante Risiken und eine Zielumgebung; MVP: automatisierte Kernabläufe/Fehlerfälle; Produkt/Livegang: vereinbarte Kompatibilitäts- und Release-Matrix. Sicherheits-/Daten-/Seiteneffektpflichten werden durch „Prototyp“ nicht aufgehoben. Specs für beauftragtes Produktverhalten bleiben erforderlich.
- **Arbeitsabsprachen:** Lokaler Start/Vorschau, Commits und Parallelarbeit nur klären, soweit offen.

## 3. Persistieren und Prüf-Einstieg

Projektprofil wirklich befüllen, nicht nur einen Brief im Chat zeigen. Architektur ist vor Produktcode erforderlich; Konventionen, Teststrategie und Design in den passenden Docs festhalten, wenn sie nicht bereits eindeutig durch Werkzeuge/Projektprofil beschrieben sind. Nicht relevante Bereiche mit Grund abwählen; keine neuen Leergerüste. Erforderliche Docs mit konkretem Leseauslöser registrieren.

Produkt-README: Zweck, Einrichtung und geprüfter Start, keine obligatorische Harness-Erklärung im Produkttext. Unklare/zurückgestellte Vorhaben in Ideas, konkret beauftragtes Nutzerverhalten vor Umsetzung in Specs festhalten.

Checks einrichten, sobald ausführbar; tatsächlich ausführen und neue Prüflogik mit absichtlichem Fehler gegenprüfen. Leere Suites nicht als bestanden melden. Bei UI wiederverwendbare Mess-/Screenshot-Werkzeuge früh einrichten. Noch nicht ausführbare Produktchecks mit Blocker/Auslöser/Zuständigkeit offen halten; spätestens vor Abschluss der Umsetzung nachholen.

## 4. Init-Go vor Produktcode

`python3 tools/check-harness.py --ready` ausführen und zusätzlich fachlich prüfen:

1. Ziel, Grenzen, erster Ablauf und Erfolg bestätigt oder ausdrücklich delegiert?
2. Stack, Dateistruktur, Profile, Standards, Prüfplan und nötige Docs tatsächlich festgehalten?
3. Welche Fragen blockieren diesen Bau, welche erst den Livegang? Fehlende Checks sichtbar offen mit Nachholplan?

**No-Go:** `Pending Project Init` stehen lassen, Blocker gebündelt melden; kein Produktcode.
**Go:** Begründung und verbleibende nicht blockierende Lücken unter `Init-Go` eintragen, Status auf `Init abgeschlossen` setzen. Zurück zum Core: liegenden Umsetzungsauftrag ausführen, sonst ersten Bauauftrag vorschlagen. Init ist weder automatische Implementierungsfreigabe noch Produktnachweis.
