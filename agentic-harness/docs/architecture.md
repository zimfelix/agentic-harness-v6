# Architektur – Bausteine und Datenfluss

> - **Typ:** Projektdoku
> - **Status:** Noch offen (Project Init).
> - **Zuständigkeit:** Entschiedene Bausteine, ihre Aufgaben, Abhängigkeiten und den Betrieb für den aktuellen Meilenstein erklären.
> - **Gilt bei:** Project Init sowie Architektur-, Schnittstellen-, Betriebs- oder Strukturfragen, neue Seiten oder Routen, Konzept-/Variantenvergleiche und Archivieren.
> - **Ladebeziehungen:** Vorher `agentic-harness/harness/project.md` für Ziel und Grenzen lesen. Bei Codekonventionen zusätzlich `agentic-harness/docs/code.md`; bei Gestaltungsbausteinen `agentic-harness/docs/design.md`; bei Teststruktur `agentic-harness/docs/testing.md`.
> - **Nicht zuständig:** Agentenablauf, Code-Stil, Gestaltungsregeln oder beauftragtes Nutzerverhalten festlegen.

## Universeller Rahmen

Ist, entschiedenes Ziel und offene Möglichkeiten nicht verwechseln. Bausteine nur für einen geklärten Bedarf vorsehen; Paket- und Technologieentscheidungen dieses Projekts hier begründen.

**Betrieb** gehört ebenfalls hierher, sobald er entschieden ist: wo und wodurch das Produkt läuft (z. B. Zeitplan, Ereignis, Aufruf), Umgebungen, Konfiguration, Ort der Zugangsdaten (nie ihre Werte), Protokolle und irreversible Aktionen samt Schutz (z. B. Trockenlauf).

### Varianten, Konzeptseiten und Archiv

- Varianten zum Vergleich (Konzeptseiten, alternative Entwürfe) sind **vorübergehend**: intern kennzeichnen, bei Websites `noindex`, nicht aus dem Produkt verlinken, eigene Tests getrennt halten.
- Nach der Entscheidung verlassen verworfene Varianten und nicht mehr verlinkte Teile den aktiven Baum: löschen oder in einen Archivordner verschieben, der weder gebaut noch getestet noch vom Agenten geladen wird. Den Archivordner im Projektprofil benennen.
- Gebaut und ausgeliefert werden nur ausdrücklich vorgesehene Einstiege: das, was über Navigation und Links erreichbar ist, plus bewusst vorgesehene direkte Einstiege (z. B. Landingpages, Fehlerseiten, API-Endpunkte). Die Liste steht im Projektteil; ein Test sichert sie ab.
- Aus dem Archiv wird nur auf ausdrücklichen Auftrag etwas zurückgeholt oder geändert.

### Trennung von Konfiguration und Bausteinen

Trenne von Anfang an, nicht erst in einem späteren Umbau: projektspezifische Inhalte und Konfiguration (z. B. Namen, Zugänge, Regeln, Texte) von den Bausteinen, die sie verarbeiten oder darstellen; bei Oberflächen zusätzlich die Gestaltungswerte (Tokens nach `agentic-harness/docs/design.md`). Die Dateistruktur dafür wird beim Project Init festgelegt und im Projektteil dieser Datei eingetragen; ein Profil kann eine bewährte Struktur vorschlagen.

- **Zweites Vorkommen → Baustein:** Ein Muster, das zum zweiten Mal gebraucht wird, wird ein Baustein mit Parametern oder Varianten (`agentic-harness/harness/core.md`, „Struktur mitziehen“).
- **Eine Datei, eine Verantwortung:** Mischt eine Datei mehrere Bausteine, Seiten, Ansichten oder Zuständigkeiten, wird sie aufgeteilt, spätestens wenn das nächste Teil dazukommt.
- **Bausteine ohne Projektinhalte:** Texte, Namen, Verweisziele und Anzahlen kommen als Daten herein; ein fester Standardwert nur, wenn er für jeden Einsatz gilt.
- Bausteine werden nach ihrer Rolle benannt, nicht nach dem Ort, an dem sie zuerst vorkamen.

## Projektspezifische Befüllung

Noch offen (Project Init).
