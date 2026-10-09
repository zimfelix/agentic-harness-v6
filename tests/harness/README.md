# Harness-Regression und Projektproben

Nur für die Pflege dieses Vorlagen-Repositories; `tests/` wird nicht exportiert. Kein Produkt-Init und keine Produktdaten im Harness erforderlich.

## Tests bei übernommenen Learnings

Vor einer Vorlagenänderung neues Soll, betroffene Abhängigkeiten und weiterhin geltende Zusagen bestimmen. Tests für das neue Verhalten sowie Fehler-/Gegenfälle ergänzen, betroffene bestehende Regression beibehalten und auf aktuellem Stand ausführen. Routing, Init/Status, Profile, Checker und Export als zusammenhängenden Vertrag prüfen, soweit betroffen. Keine Erwartung ohne bewusste Solländerung lockern.

Deterministische Tests prüfen ausführbare Mechanik/Export, frische Agentenproben die tatsächliche Befolgung geänderter Arbeitsregeln. Text-/Strukturprüfungen ersetzen Letztere nicht. Umfang risikobezogen wählen und Testlücken offen dokumentieren; frühere grüne Ergebnisse gelten nicht automatisch für neue Regeln. Herkunft/Beobachtung, beschlossene Änderung, betroffene Prüfungen und tatsächliche Ergebnisse im Learning/Prüfbericht verknüpfen. Bestehende Produktprojekte nicht automatisch mit neuer Vorlage überschreiben.

## Deterministische Regression

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/harness -v
HARNESS_BRAVE_TESTS=1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/harness -v
```

Python-Standardbibliothek, Node.js 22+; zweite Variante zusätzlich Brave. Die normale Suite meldet die Brave-Fälle ausdrücklich als übersprungen. Prüft nichtleere/symmetrische Nachweise, deklarierte Routen/Breiten, Browserfehler/-Timeouts, aktuelle Builds, Pfadgrenzen, Profile/Bereiche, Init-Go sowie frischen Export und Schutz befüllter Produktziele. Fehlerfälle sind absichtlich; erwarteter Fehler-Exit zählt als bestandene Gegenprobe, nicht als bestandener Produktablauf.

## Frische Agenten (opt-in)

```sh
pi auth check --provider openai-codex --json
PYTHONDONTWRITEBYTECODE=1 python3 tests/harness/run_agent_probes.py --run-agents
# oder nur den aktuellen Stand:
PYTHONDONTWRITEBYTECODE=1 python3 tests/harness/run_agent_probes.py --run-agents --current-only
```

Nutzen den Provider/das Modell aus `PI_PROVIDER`/`PI_MODEL`, sonst `openai-codex/gpt-6.1-sol`, mit `medium` Reasoning. Kostet Modellaufrufe, bis zu acht Minuten je Erstlauf. Baseline fest auf `47065ef`; aktueller Stand wird am Start kopiert. Drei Fälle: CSV/SQLite-Import, lokales CRM/API und Fake-Ausgangsjob. Öffentliche Verträge und unabhängige Abnahme im Runner, eigene Agententests zusätzlich. Keine UI-/Produktions-/realen Providerabnahmen.

Separate temporäre Projektverzeichnisse, keine Sessions/Extensions/Skills/MCP/Packages. Auf macOS begrenzt `sandbox-exec` Schreibzugriffe auf den jeweiligen Probeordner; **keine vollständige Lese-/Netzwerkisolation**. Modelltransport benötigt Netzwerk. Ohne `sandbox-exec` verbleibt nur Verzeichnistrennung und der Prompt-Rahmen; nicht als Sicherheitstest ausgeben. Pi erhält temporär nur die gewählte Provider-Authentifizierung und ggf. Modellkonfiguration; Konfigurationsverzeichnis mit Modus 0700, Authdatei 0600, Löschung nach dem Lauf. Keine Credentials in Versionskontrolle oder Berichte kopieren; bei hartem Prozessabbruch ggf. übrig gebliebene temporäre Konfiguration sicher entfernen.

JSONL-Protokolle, Prompts, Produktsamples und Abnahmeberichte bleiben im ausgegebenen temporären Arbeitsbereich. Modell-Exit/Timeout, unabhängige Abnahme, Spec-Status und letzter tatsächlich ausgeführter Check getrennt werten. Ein Timeout kann brauchbaren Code hinterlassen, beweist aber keine vollständige Übergabe. Tokenzahlen sind Provider-Usage inklusive Cachezugriff, keine direkten Kosten und kein kontrollierter Leistungsnachweis. Ein Lauf je Kombination genügt nur als Screening.

Nach abgeschlossenen Erstläufen können frische Fortsetzungen samt zurückgestellter Idea und anschließendem absichtlich fehlendem Provider-Nachweis geprüft werden:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/harness/continue_agent_probes.py --run-agents /pfad/zum/ausgegebenen/arbeitsbereich
```

Nur auf Arbeitsbereichen ohne laufende schreibende Agenten starten. Fortsetzung verändert die Probeprojekte und ergänzt beim aktuellen Job zuletzt ein neues offenes Provider-AK; der Produkt-Spec-Status muss dann `Modified` sein. Bestehende Fake-Nachweise ersetzen das AK nicht. Nochmals in denselben Verzeichnissen starten ist kein identischer Erstlauf; für Wiederholung neue Probeprojekte verwenden.

Prüfstand/Beobachtungen: [RESULTS.md](RESULTS.md).
