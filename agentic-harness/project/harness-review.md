# Review: Harness v4.5

**Zuständigkeit:** Lokaler Auftrag, Quellen und Prüfstand des Umbaus. Kein Teil des Exports und keine zweite Produkt-Spec.

## Auftrag

Ursprünglichen Harness mit sinnvollen Lite-Regeln verschlanken und als `agentic-harness/` im bestehenden Repository `zimfelix/agentic-harness-v5` veröffentlichen. Release v4.5, Repository nicht umbenennen. Nur Profile statt Skill-/Adapterordnern. Nach grüner Prüfung einmalige Testdatei entfernen. Mail-Prototyp, lokaler v4-Export und separate Worktrees bleiben unverändert.

## Review / Quellen

Ursprüngliche Steuerungsdateien, Docs, Templates, Website-Profil/Zubehör sowie Lite-Regeln und Learnings abgeglichen. Primärquellen direkt abgerufen:

- [Anthropic: Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): kleine vollständige Instruktionen und Kontext nach Bedarf; keine Garantie für Regelbefolgung.
- [Anthropic: Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview): gestufte Referenzen als Organisationsprinzip. Native Skill-Erkennung bewusst nicht übernommen; Profile explizit über Agenteneinstieg laden.
- [PyPA: src vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/): `src` als Ausgangsvorschlag für neue Python-Anwendungen, keine universelle Ordnerpflicht für jeden Stack.

Keine umfassende Marktstudie oder unabhängige Agenten-Verhaltensmessung.

## Entscheidungen

Map/ausführliche Metaköpfe und vier Verification-Dateien waren redundant; Einstieg/Verweise und ein Loop genügen. Brief und Technik im Init, keine verpflichtende Promptfolge/Harness-Abhandlung in Produkt-README. Specs für beauftragtes Produktverhalten auch im Prototyp; nur begrenzte Spikes ausgenommen. Struktur vor Code, Refactoring mit Regression, keine blinden Abstraktionen oder zusätzlichen Leergerüste. Profile bündeln nur projektartbezogenes Wissen und passende Werkzeuge; universeller Ablauf bleibt Core/Init/Verification.

`project/` hält optionale Quelldaten/Projektthemen und lokale Review-/Lernnotizen. Aktueller Produktstand in `harness/project.md`; Soll/AK in Specs, Format/Status in `specs/S000-readme.md` und Template. Keine Definition dort duplizieren. Bei jeder Harness-Änderung alle betroffenen Definitionen, Verweise und Werkzeug-/Exportabhängigkeiten abgleichen.

## Arbeitsstand

- **Erledigt:** Profile konsolidiert, parallele Ablagen entfernt, Core/Init/Verification und Spec-Definitionen abgeglichen, Vorschau-Assetpfad angepasst, README v4.5 vorbereitet.
- **Prüfungen:** finale Profilstruktur · 17/17 einmalige Tests bestanden: Kopie ohne Adapter, Profile/Referenzen, Export/Reset, ungeeignete/verschmutzte/Produktziele, Produktreste, Readiness und fehlende Dateien/Referenzen/Asset-Abhängigkeiten als Gegenproben. HTTP-Smoke bestätigt Produktseite, verschobene Geräte-Vorschau und Seitenliste. Strukturcheck, Shell-Syntax aller Harness-Scripts, JavaScript-Syntax aller Website-Module und `git diff --check` bestanden. Testdatei anschließend auf Auftrag entfernt; dauerhafter Checker erhalten. Frühere 13/15-Teststände sind durch diesen Nachweis ersetzt.
- **Offen:** Zuverlässige Agentenbefolgung in frischer Sitzung nicht geprüft; Readiness erzwingt kein Schreibverbot. Kein visueller Browsercheck vorgesehen, da Vorschauinhalt bis auf Pfadkommentar unverändert; HTTP-Pfade werden geprüft.
- **Nächster Schritt:** freigegebenen Stand nach abschließendem Diff-/Exportcheck als v4.5 committen/pushen und Tag veröffentlichen. Danach frische Agentenprobe zur Regelbefolgung, nur auf Auftrag. Keine Produktimplementierung beauftragt.
