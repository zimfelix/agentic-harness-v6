# Projektprofil – Grenzen und Befehle

> - **Typ:** Projektdoku
> - **Status:** Pending Project Init
> - **Zuständigkeit:** Den aktuellen Meilenstein, Projektgrenzen, Freigaben, eingerichtete Befehle und offene Entscheidungen festhalten.
> - **Gilt bei:** Einordnung jeder Aufgabe über `AGENTS.md`; projektspezifisches Befüllen bei `harness/init.md`.
> - **Ladebeziehungen:** Einstieg über `AGENTS.md` und `harness/core.md`. Gewähltes Profil (falls eines genannt ist) unter `profiles/`; Bausteine: `docs/architecture.md`; Gestaltung: `docs/design.md`; Testpraxis: `docs/testing.md`; Verhalten und AK: betroffene Specs unter `specs/`.
> - **Nicht zuständig:** Architekturdetails, Gestaltungsregeln, Codekonventionen oder Akzeptanzkriterien wiederholen.

## Universeller Rahmen

Dieses Profil wird bei jeder Aufgabe gelesen und bleibt deshalb kurz (Projektteil etwa 6 KB). Es nennt oben das gewählte Profil (z. B. „Profil: Website“ → `profiles/`) und sonst nur den **aktuellen** bestätigten Stand: Ziel, Grenzen, Freigaben, eingerichtete Befehle und offene Entscheidungen. Überholte Aussagen werden ersetzt, nicht als Verlauf ergänzt; der Verlauf steht in Git (`document-contract.md`). Betrieb und Bausteine gehören nach `docs/architecture.md`, Gestaltung nach `docs/design.md`, Verhalten und Inhalte in Specs. **Nicht hierher:** Aufgabenlisten und Pläne mit mehreren Schritten (→ Idea mit Teilaufgaben nach `ideas/I000-readme.md`, hier nur der Verweis als nächster Schritt) und Werkzeugdetails (→ `docs/testing.md` bzw. Profil). Befehle: je Befehl eine Zeile mit Zweck; den letzten Lauf nur für die Befehle, die das Gate braucht (z. B. Build, Tests). Ein geklärtes Init ist kein bestandenes Produkt-Gate.

## Projektspezifische Befüllung

Noch offen (Project Init).
