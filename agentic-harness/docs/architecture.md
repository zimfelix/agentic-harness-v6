# Architektur – Bausteine und Datenfluss

> - **Typ:** Projektdoku
> - **Status:** Pending Project Init; noch keine Produktarchitektur bestätigt.
> - **Zuständigkeit:** Die entschiedenen Bausteine, ihre Aufgaben und Abhängigkeiten für den ersten Meilenstein erklären.
> - **Gilt bei:** Project Init sowie Architektur-, Schnittstellen- oder Strukturfragen.
> - **Ladebeziehungen:** Vorher `agentic-harness/harness/project.md` für Ziel und Grenzen lesen. Bei Codekonventionen zusätzlich `agentic-harness/docs/code.md`; bei Teststruktur `agentic-harness/docs/testing.md`.
> - **Nicht zuständig:** Agentenablauf, Code-Stil oder beauftragtes Nutzerverhalten festlegen.

## Bausteine – im Init festzulegen

Welche Teile braucht der erste Ablauf? Für jeden Teil: Aufgabe, Verantwortungsgrenze und Ort im Projekt nennen. Keine Pakete nur für spätere Features anlegen.

## Datenfluss und Schnittstellen – im Init festzulegen

Wo kommen Eingaben her, wer hält oder verändert Zustand, und wo wird das Ergebnis sichtbar? Abhängigkeitsrichtung und externe Grenzen kurz darstellen.

## Entscheidungen und offene Punkte

Gewählte Lösungen mit kurzem Grund festhalten. Vorschläge und spätere Möglichkeiten ausdrücklich von entschiedenen und bereits implementierten Teilen trennen. Keine Technologie aus einem anderen Projekt übernehmen, ohne sie hier zu begründen.
