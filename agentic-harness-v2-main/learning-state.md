# Learning State – Harness V2

> **Verantwortung:** Diese Datei sammelt nur ausdrücklich bestätigte Erkenntnisse und Lernnotizen aus diesem Projekt. Sie ist kein Statuslog, keine Spec und kein Ort für automatisch gespeicherte Chatverläufe.

Lokale Sammelstelle für Erkenntnisse aus diesem Projekt. Ich ergänze sie nur,
wenn Felix ausdrücklich sagt, etwas zu speichern oder eine Zusammenfassung hier
festzuhalten. Einträge bleiben kurz; Unsicheres wird als offen markiert.

Bei „Übertrage/pushe den Learning State in die globale/universelle AGENTS.md“
kuratiere ich nur übertragbare Learnings und aktualisiere die globalen Ziele
`~/.pi/agent/AGENTS.md` und `~/.codex/AGENTS.md` gemäß deren Regeln. Ich kopiere
nicht die ganze Datei. „Push“ meint in diesem Zusammenhang das Übertragen der
Erkenntnisse in diese Dateien, nicht `git push`.

## Gesammelte Erkenntnisse

- **Bestätigt:** Der universelle Core bleibt projektübergreifend stabil;
  Unterschiede gehören in Projektprofile oder bedarfsgeladene Regeln.
- **Bestätigt:** Ideas klären größere, offene Vorhaben; Specs beschreiben
  beauftragtes, überprüfbares Verhalten.
- **Bestätigt:** Qualitätsarten helfen passende Nachweise auszuwählen und sind
  kein Pflichtpaket für jedes Projekt.
- **Bestätigt:** Die zehn Projektebenen sind ein Relevanz- und Lückencheck,
  keine Pflicht zu zehn Dokumenten.
- **Bestätigt:** Harness-Regeln haben je einen zuständigen Ablageort; vor neuen
  Regeln benachbarte Dateien auf Dopplungen und Widersprüche prüfen.
- **Bestätigt:** Davids Tielkes Repository ist Struktur- und Begriffsreferenz;
  seine projektspezifischen CRM-, C#- und UI-Vorgaben werden nicht pauschal
  übernommen.
- **Bestätigt:** Universelle Regeln und Templates werden im Starter-Kit
  ausgearbeitet; Projektregeln erhalten ihren konkreten Inhalt bei Project Init.

## Lernstoff angerissen – weiter vertiefen

Diese Themen wurden besprochen; die Liste hält den Lernpfad fest und behauptet
nicht, dass sie bereits sicher beherrscht werden.

- **Python-Grundlagen:** Built-in-Funktionen, Typen und Exceptions;
  `isinstance` gegenüber exaktem `type`-Vergleich; `None`, `dict.get`, Längen-
  und String-Validierung; `with` für Ressourcenverwaltung; `pathlib`-Methoden
  wie `mkdir()` und `with_suffix()`.
- **Fehler und Datenprüfung:** gezieltes Error Handling für `FileNotFoundError`,
  `json.JSONDecodeError`, `PermissionError`, `OSError` und `TypeError`; fachliche
  Validation getrennt von technischen Exceptions.
- **JSON und Speicherung:** JSON Object → `dict`, Array → `list`, String → `str`,
  Number → `int`/`float`, Boolean → `bool`, Null → `None`; `dump`/`load` arbeiten
  mit Dateien, `dumps`/`loads` mit JSON-Text. Serialization/Deserialization,
  strukturierte Textdaten und Atomic Save via temporäre Datei plus `replace()`.
- **OOP und Collections:** Methode vs. Attribut, Klasse/Objekt, Parameter/Argument,
  `@property`, `@staticmethod`, `@classmethod`, `@dataclass`, Vererbung und
  Default-Parameter; veränderliche `list`/`dict`/`set` gegenüber `tuple`.
- **Speicherformate:** JSON für strukturierte Dokumente/Austausch, CSV für
  tabellarische Daten, SQLite als dateibasierte Datenbank und SQL als Abfragesprache.
- **Webstack des Lernprojekts:** TypeScript/TSX, React für UI-Struktur, Vite,
  HTML/CSS/JavaScript und Browser; Vitest für Einheiten/Logik, Playwright für
  Browserabläufe, ESLint für Linting, Prettier für Formatierung und TypeScript
  für Typprüfung.
- **Testbegriffe:** Testebenen (Unit, Komponente, Integration, Contract, System,
  E2E), Qualitätsbereiche (Accessibility, Visual Regression, Performance,
  Security, Usability, Compatibility) und Testzwecke (Smoke, Regression,
  Acceptance, explorativ) sind unterschiedliche Blickwinkel. Spezialformen:
  API-, Snapshot-, Load-, Stress-, Recovery- und Deploymenttests.
- **Minimaler Quality Gate:** Logiktests, Integration, wichtiger E2E-Ablauf,
  Regression, statische Prüfungen, Build/Start und Basis-Accessibility – je nach
  Risiko und Projekt, nicht als pauschale Pflichtsuite.
- **Projekt verstehen:** Ziel/Nutzer und die zehn Projektebenen prüfen;
  Programmeinstieg finden, den Ablauf Eingabe → Logik → Ausgabe verfolgen,
  Verantwortlichkeiten, Kernobjekte, Zustand und Tests untersuchen.
