# Agentic Harness v5.14

Vorlage für Softwareprojekte mit KI-Coding-Agenten (z. B. Claude Code, Codex, Pi): `AGENTS.md` führt den Agenten von der Klärung über die Umsetzung bis zu einem Verifikations-Gate; `agentic-harness/` enthält Arbeitsablauf, Projekt-Docs, Spec- und Idea-Vorlagen sowie optionale Profile (z. B. Website). Projektart, Stack und Tests legt der Harness nicht fest: Sie werden beim Project Init mit dir geklärt; danach ersetzt der Agent diesen Kopf durch Titel und lokale Adresse des Produkts.

**Start:** Idee in `agentic-harness/project/brief.md` frei erzählen (Themen unten) oder direkt den Ordner mit dem Agenten öffnen und sagen, was entstehen soll. Anleitung: [agentic-harness/README.md](agentic-harness/README.md). Nach dem Project Init steht hier oben die lokale Adresse des Produkts, darunter dieser Abschnitt und danach die Projektabschnitte (Aufbau, lokal ansehen).

## Projektstart mit dem Agentic Harness

Dieses Projekt nutzt den Agentic Harness: `AGENTS.md` führt den Coding-Agenten, `agentic-harness/README.md` erklärt den Harness für Menschen. Dieser Abschnitt ist universell und steht in jedem Projekt unverändert oben, direkt unter der lokalen Adresse; darunter folgen die projektspezifischen Abschnitte.

### Ablauf in Prompts

```text
PROMPT 1  BRIEF + START     du: agentic-harness/project/brief.md frei erzählen (Themen unten), dann
          │                     „Lies AGENTS.md. Brief: agentic-harness/project/brief.md. Auftrag: …“
          │                 Agent (init.md, Abschnitt 0): Richtung klar oder offen?
          ├─ klar (E0) ─────────────────────────────────────────────┐
          └─ offen → ERKUNDEN, genau eine Stufe:                     │
                E1 Ideen in Text · E2 ein Prototyp · E3 Varianten (nur auf Auftrag)
                ⏸ Agent stoppt und legt das Ergebnis zur Auswahl vor   │
PROMPT 2  AUSWAHL           du: „Wir nehmen B.“                       │
          ▼                                                           ▼
          INIT (init.md, Abschnitte 1–4)
          ├─ Brief kurz bestätigen, nur Lücken nachfragen
          ├─ Architektur und Tech-Stack: 2–3 Optionen + Empfehlung
          │     ⏸ du bestätigst (oder sagst ausdrücklich „entscheide selbst“)
          ├─ project.md und docs/ befüllen, Checks einrichten und ausführen
          └─ Go/No-Go ⏸ Agent stoppt vor dem Bau und schlägt den ersten Bauauftrag vor
PROMPT 3  ERSTER BAUAUFTRAG du: „Bau …“
          Bereichs-Spec(s) anlegen → umsetzen → Gate → Übergabe
PROMPT 4+ WEITERENTWICKELN
          ├─ größere Änderung oder neue Funktion → Idea mit Teilaufgaben → Specs → Gate → Archiv
          └─ kleine Änderung („Footer anders“) → Iteration, kurzer Gate-Weg
```

Ist die Richtung schon im Brief klar, entfällt Prompt 2: Prompt 1 führt direkt ins Init. Die Haltepunkte ⏸ sind Stellen, an denen der Agent auf dich wartet.

### Was der Brief und das Init beitragen

```text
1. ERZÄHLEN  (brief.md, Auftraggeber)          2. KONKRETISIEREN  (Project Init, Agent)
   frei und in eigenen Worten:                    prüft wie ein Kontrolleur, was zur Umsetzung fehlt:
   Idee, Problem, Wunsch, Ziel                    ├─ Was ist schon klar? → kurz zur Bestätigung zusammenfassen
   Stichworte aus den Themen unten                ├─ Was fehlt oder widerspricht sich? → gezielt nachfragen
   Unterlagen, Beispiele, No-Gos         ──▶      ├─ Anforderungen präzisieren, Tech-Stack vorschlagen
   bekannte Vorgaben, auch technische             └─ erst Bestätigtes in project.md, docs/ und Specs schreiben
```

Der Brief muss nicht vollständig oder geordnet sein; Stichworte, Freitext oder kopierte Nachrichten genügen. Was er beantwortet, fragt das Init nicht noch einmal ab. Der Brief ist **optional**; ohne ihn klärt das Init alles im Gespräch. Er bleibt als Quelle erhalten und wird nicht nachgeführt, bestätigte Entscheidungen stehen danach in `agentic-harness/harness/project.md`, `docs/` und Specs.

### Themen zum Erzählen

Zum Anlegen nach `agentic-harness/project/brief.md` kopieren und frei ausfüllen; nicht passende Themen weglassen.

```markdown
# Brief – {Projektname}

## Idee und Ziel
Was soll entstehen, welches Problem löst es, was soll danach anders sein?

## Zielgruppen
Wer nutzt es, und was brauchen diese Menschen?

## Inhalte und Daten
Was gibt es schon (Texte, Daten, Bilder, Systeme), was liefert der Auftraggeber, was fehlt?

## Ton und Ansprache
du oder Sie, sachlich oder locker, Sprache(n)

## Vorbilder und No-Gos
Was gefällt (mit Begründung), was auf keinen Fall?

## Technik und Betrieb
Wo und wie soll es laufen (Browser, Handy, Server, eigener Rechner), wer bedient und pflegt es, welche Systeme oder Daten müssen angebunden werden, wie viel Last ist zu erwarten? Was ist gesetzt oder ausgeschlossen (z. B. „muss mit Outlook laufen“, „keine Cloud“), Datenschutz. Eigene Worte genügen; das Init leitet daraus Architektur und Tech-Stack ab.

## Rahmen
Zeit, Budget, Abgabe oder Präsentation, beteiligte Personen und Freigaben

## Unterlagen
Bereitgestellte Dateien (z. B. unter `material/`) und wie sie genutzt werden dürfen
```

