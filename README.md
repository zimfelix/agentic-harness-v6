# Agentic Harness v6.1

Universelle Vorlage für Softwareprojekte mit KI-Coding-Agenten – insbesondere Automatisierungen, CRM und Geschäftssoftware. Repository: `agentic-harness-v6`; die Produktvorlage liegt ausschließlich unter [`agentic-harness/`](agentic-harness/).

```text
Auftrag → Init + dokumentierter Go → Soll/Specs → Umsetzung → Nachweise → Übergabe
```

## Neu in v6.1

- **Geschäftssoftware:** eindeutige Risikobereiche und bedarfsgeladene Referenzen für Fachmodell, Daten/Migrationen, Importe/Jobs, Geld/Zeit, Rechte/Mandanten, Personendaten, Seiteneffekte und Buchhaltung. Importgrenzen, Vorgangsidentität, Parallelität, Wiederaufnahme und ungewisse externe Ergebnisse ausdrücklich geregelt. Keine universelle Schichten-, Broker- oder Frameworkpflicht. [Profil](agentic-harness/profiles/business-software/profile.md) · [Quellen und Grenzen](agentic-harness/profiles/business-software/references/quellen.md)
- **Init und Autonomie:** Arbeitsmodus/Delegation im Projektprofil; `--ready` prüft Voraussetzungen und Profilauswahl, `--go` zusätzlich dokumentierten Go/Status. Keine zusätzliche Freigabeschleife für normale delegierte Implementierungsdetails. Beide Checks sind weder fachliche Abnahme noch Schreibsperre.
- **Nachweise:** Anforderungsabdeckung statt grüner Ersatzprüfungen. Website-Werkzeuge lehnen leere/einseitige Mengen und alte Aufnahmeordner ab, prüfen Routen/Bereitschaft mit Brave und Zeitlimits und zeigen Buildfehler als HTTP 503 statt einen veralteten aktuellen Stand.
- **Learnings und Pflege:** Projektkontext, Soll/Ist, Belege und offene Fragen lokal sammeln; Wochenreview und beauftragte Übernahme hier. Universelle Harness-Änderungen außerhalb dieses Repositories nur auf konkreten Ausnahmeauftrag. Neue Tests und betroffene Regression bei jeder Übernahme; Agentenregeln passend in frischen Sitzungen erproben.

Ein kurzer Einstieg, Core/Init/Verification, Ideas/Specs und ein Ordner `profiles/` bleiben erhalten. Keine neuen nativen Skills, Adapter oder Pi-Extensions.

## Neues Projekt starten

Nur die Vorlage exportieren – **nicht** Repository-`tests/`, diese Root-README, Git-/IDE-Daten oder lokale Auswertungen:

```sh
VERSION=v6.1 sh agentic-harness/tools/export-harness.sh /pfad/zum/leeren-projekt
```

Der Export setzt Projektbefüllung und Learning-Einträge zurück, behält Lernregeln und erzeugt eine eigene kurze Start-README. Eine rohe Kopie von `agentic-harness/` kann dagegen lokale Befüllung/Learnings mitnehmen. Bestehende Produktprojekte werden nicht automatisch aktualisiert.

Projektordner mit dem Agenten öffnen und das Vorhaben beschreiben. Der projektbezogene Einstieg `AGENTS.md` führt durch den Ablauf. [Anleitung und Exportgrenzen](agentic-harness/harness/README.md)

## Struktur und Learnings

```text
agentic-harness/   exportierbare Regeln, Profile, Tools, Templates und Projektgerüste
tests/harness/    nur Repository-Pflege: Regression, opt-in Agentenproben, Prüfbericht
```

```text
Produktprojekt → lokale harness-learnings.md mit Herkunft/Auftrag/Nachweisen
               → Wochenreview auf Auftrag im zentralen v6-Repository
               → lokal belassen / weiter prüfen / beauftragte Vorlage ändern
```

Normale Projektpflege umfasst Projektprofil, Docs/Specs, Projektkonfiguration und projektspezifische Ergänzungen. Keine automatische Regelübernahme oder Synchronisierung. Erledigte Übernahmen sind aus den aktiven Learnings entfernt; echte Unsicherheiten bleiben mit Kontext erhalten. [Offene Learnings](agentic-harness/harness-learnings.md)

## Prüfstand und Grenzen

```sh
python3 agentic-harness/tools/check-harness.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/harness -v
HARNESS_BRAVE_TESTS=1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/harness -v
```

24 Regressionstests einschließlich echtem Brave/HTTP/Export bestanden. Die normale Suite überspringt fünf Brave-Fälle ausdrücklich. Drei kleine Projektarten wurden mit Baseline und präzisiertem Harness geprüft; beide bestanden je 23 unabhängige Prüfgruppen. Zwei Job-Erstläufe benötigten nach dem Zeitlimit eine frische Fortsetzung. Ein bewusst fehlender echter Provider-Nachweis blieb korrekt offen.

Das ist Screening, kein allgemeiner Leistungs-, Sicherheits-, Produktiv- oder Rechtsbeweis. Die zuletzt ergänzte zentrale Lern-/Pflegegrenze ist dokument-/exportgeprüft, nicht erneut in frischen Agentensitzungen erprobt. Die Vorlage bleibt absichtlich `Pending Project Init`; `--ready`/`--go` scheitern vor Befüllung erwartungsgemäß.

[Testanleitung](tests/harness/README.md) · [Ergebnisse und Grenzen](tests/harness/RESULTS.md)
