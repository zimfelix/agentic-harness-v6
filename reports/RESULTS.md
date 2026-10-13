# Auswertung: Wie viel Harness brauchen starke Coding-Agenten?

## Kurzurteil

**Für mittelgroße Projekte empfehle ich den schlankeren Ansatz.** Nicht weil er in jedem Lauf besseren Code erzeugt, sondern weil er die nötige Projektorientierung mit deutlich weniger Prozess- und Dokumentationspflichten erreicht. Einen universellen Qualitätssieger beweisen diese Versuche nicht.

Die ausführliche v6.1-Vorlage ist in diesen Fällen nicht erforderlich, um einen brauchbaren Brief, sinnvolle Architekturentscheidungen, Specs, Fortsetzung und ehrliche Nachweise zu erhalten. Sie beseitigt aber auch nicht sämtliche Fehler. Im ersten Dispatch-Lauf hatte nur die schlanke Variante einen reproduzierbaren Statusfehler; in einer zweiten frischen Wiederholung bestanden beide die prüfbaren Fälle. **Intelligenz ersetzt keine unabhängigen Tests. Mehr Markdown garantiert ebenfalls keine Korrektheit.**

## Endgültiger Aufbau

```text
AGENTS.md              Arbeitsvertrag + risikobezogene Verification
PROJECT.md             dieses Projekt: Ziel, Grenzen, Stack, Entscheidungen
specs/                 relevantes Soll, Prüfplan und Fortsetzungsstand
ideas/                 nur bei offenen Optionen / größeren Vorhaben
.agents/skills/        eine bedarfsgeladene Wissens-/Werkzeugsammlung
  business-software/   konkrete Risikoreferenzen, kein Pflicht-Stack
  website-tools/       Website-Grundlagen; Werkzeuge erst bei Bedarf
```

**Kein separater Core, Init, Brief, Verification oder Dokumentenvertrag. Kein zusätzlicher `profiles/`-Katalog.** Der Vorgang Initialisierung bleibt erhalten: freie Beschreibung aufnehmen, bestätigte Fakten von Vorschlägen trennen, Konsequenzen klären, Entscheidungen in PROJECT speichern. Bei beauftragter Umsetzung läuft der Agent danach weiter; ein Gespräch über eine Idee ist dagegen kein Bauauftrag.

Die Profile des eingefrorenen Vergleichskandidaten wurden nach den Hauptversuchen in die zwei Skills konsolidiert. Fachliche Regeln wurden nicht gestrichen: ein Paritätstest vergleicht die Inhalte mit dem vorherigen Routing. Das ist eine Struktur-/Ladewegänderung, **kein zusätzlich bewiesener Leistungsgewinn**. Die komplexen Produktvergleiche unten gelten für den eingefrorenen Kandidaten vor der Konsolidierung; der finale Aufbau bekommt technische Regression und eine separate frische Init-Gegenprobe. Herkunft/Hashes bleiben getrennt nachvollziehbar.

## Was vorab feststehen sollte – und was der Agent entscheiden kann

| Vorab erklären oder ausdrücklich delegieren | Selbstständig im vereinbarten Rahmen |
|---|---|
| Nutzerziel, erster brauchbarer Ablauf, Nicht-Ziele | normale Dateien, Funktionen, interne Aufteilung |
| reale Daten, Rollen, externe Aktionen und Freigaben | Framework-Konventionen, wiederverwendbare Helfer |
| bestätigter Stack und grundlegende Architekturgrenzen | Testauswahl nach Änderung und Risiko |
| fachliche Identität, Statusregeln, Geld-/Zeitsemantik soweit betroffen | konkrete Umsetzung einer bestätigten Regel |
| gewünschte Gestaltung / ausgewählte Referenzen | Gestaltungsvorschläge, reversible UI-Details |
| beobachtbare Erfolgskriterien | Umsetzung bis zu prüfbarem Ergebnis und Handoff |

Ein starker Agent kennt allgemeine Programmiertechniken. Er kennt **nicht** automatisch euren gewünschten Workflow, eure Risikoakzeptanz, bestätigte Zusagen oder eure Designpräferenzen. Deshalb sind PROJECT und relevante Specs wertvoller als allgemeine Lehrbuchregeln.

Eine Architektur muss verständlich sein, aber vor dem ersten Code nicht bis zu jedem Dateinamen festgeschrieben werden. Gewöhnliche Entscheidungen dürfen delegiert werden; ein grundlegender Stack-/Dependency-Wechsel ist keine stillschweigende Routinedetailentscheidung. Ausführbare Standards gehören in Werkzeuge und Tests, nicht zusätzlich in mehrere Markdown-Dateien.

## Profile oder Skills?

Ein Projektprofil bleibt als **PROJECT.md** sinnvoll. Ein universelles Verzeichnis namens `profiles/` ist dagegen keine technische Voraussetzung.

Skills können Verfahren, Skripte, Checklisten und Fachreferenzen bündeln. Ihre Vorteile sind eine klar benannte Fähigkeit, knappe Erkennungsmetadaten und bedarfsgeladene Details. Sie sind nicht automatisch besser als ein gut geroutetes Profil: dieselbe Prosa unter `SKILL.md` zu verschieben spart für sich keine Tokens. Sinnvoll ist **eine Quelle statt zwei Kataloge**, kleine Einstiege und gezieltes Nachladen.

- Business-Skill: nur tatsächlich betroffene Integrität, Rechte, Wiederholung, externe Unsicherheit etc.; kein pauschaler Enterprise-Fragenkatalog.
- Website-Skill: reale Inhalte/Bedienung als Grundlagen; Browser-/Screenshot-/Preview-Verfahren erst bei Nutzung. Bilder und Inspiration nur auf passenden Auftrag.
- Keine Skills für jede gewöhnliche Programmiertätigkeit. Erst ein wiederkehrendes Verfahren oder eine beobachtete Wissenslücke rechtfertigt zusätzliche Pflege.
- Kritische Leseauslöser bleiben ausdrücklich in AGENTS. Optionale Skill-Erkennung allein ist keine verlässliche Sicherheitsgrenze.

## Versuchsaufbau und Aussagekraft

Baseline: ursprüngliches v6.1, Commit `dc1af55e0a4abc4be73ddc982ed8c2dc8b8de34a`. Kandidat: eingefrorene `template/`-Inhalte, auch im frühen Commit `f06f60b` erreichbar. Content-Hashes, Modell-/Toolversionen, Phasen, Tokens und Abnahmegruppen: [metrics.json](metrics.json).

Frische getrennte Agentensitzungen, identische Aufgaben, dasselbe Modell/Reasoning/Zeitbudget innerhalb eines Paars, synthetische Daten und lokale Fake-Provider. Pi: `gpt-6.1-sol`, medium. Claude Code: explizit `claude-opus-5-5`, medium; dessen Ergebnisse werden nicht wie ein Pi/Sol-Geschwindigkeitsvergleich behandelt. Native Skills und globale Anpassungen waren in den Produktvergleichen deaktiviert; relevante Dateien blieben explizit lesbar.

Die unabhängige QA erhielt nur die öffentlichen Verträge, nicht die Harnesses oder Implementierungen. Ein zweiter Reviewer prüfte die Abnahme auf unerlaubte Erwartungen und fehlende Beweisgrenzen. Nach Korrektur entstanden **59 benannte Stress-Prüfgruppen**: CRM 20, Import 18, Dispatch 21. Gruppen enthalten mehrere Aussagen, sind aber keine 59 unabhängigen Modellversuche. Zwei Seeds prüfen andere Daten/ausgewählte Zufallsfälle, nicht statistische Modellwiederholungen. Dispatch erhielt zwei unabhängige Implementierungspaare.

### Fachliche Resultate

| Aufgabe | v6.1 | Schlanker eingefrorener Kandidat |
|---|---|---|
| CRM: Rollen/Mandanten, Migration, Geld, Idempotenz, Audit, Parallelität | 20 bestanden | 20 bestanden |
| Lagertransfer: atomare Gruppen, globale Dubletten, Resume, knapper Bestand | 18 bestanden | 18 bestanden |
| Dispatch, erster Lauf | 19 bestanden, 2 unklar | 18 bestanden, 1 Fehler, 2 unklar |
| Dispatch, zweite frische Implementierung | 19 bestanden, 2 unklar | 19 bestanden, 2 unklar |
| CRM nach frischer Fortsetzung ohne Chat | 20 bestanden | 20 bestanden |
| CRM-Titeländerung + alte Regression | 24 bestanden nach Transportfortsetzung | 24 bestanden |
| Fehlender echter Provider-Nachweis | korrekt offen / Modified | korrekt offen / Modified |

Alle genannten automatischen Hauptabnahmen liefen mit Seeds 1 und 17. Die veröffentlichbaren Produktextrakte wurden zusätzlich ohne Modellaufruf erneut geprüft: [published-stress-replay.json](published-stress-replay.json).

**Dispatch-Fehler:** neue lokale Queue, gleicher Provider-Key, anderer Payload. Der Provider behält korrekt seine ursprüngliche Annahme; danach scheitert auch die lokale `status`-Abfrage mit `Provider identity payload conflict`, statt den gespeicherten Jobzustand auszugeben. Dieser Fehler wurde diagnostiziert, nicht manuell im Produkt repariert. Der zweite frische Kandidatenlauf vermeidet ihn. Eine einzelne Fehlerbeobachtung belegt weder eine konkrete fehlende Harness-Regel noch allgemeine Unterlegenheit.

**Zwei unklare Dispatch-Prüfbereiche:** Die öffentliche Schnittstelle identifiziert keine sicher autoritative Datei für eine Korruptionsprobe. Externe SIGKILL-Stresstests prüfen Wiederaufnahme und Providerwahrheit, garantieren aber nicht, dass der Kill genau im kritischen Ownership-/Schreibfenster lag. Diese Bereiche gelten ausdrücklich nicht als vollständig bestanden und nicht als Produktfehler. Gefakte interne Abbruchpunkte ersetzen keinen allgemeinen Power-Loss-/Lock-Beweis.

### Freierer Intermediate-Auftrag: lokaler Arbeitsplaner

Python-/Node-Standardbibliothek waren erlaubt, aber Speicher, CLI, Architektur und einige fachliche Semantiken wurden **nicht** vorgeschrieben. Ziele: Projekte/Aufgaben, Dependencies, Zyklen, Vorschlag für nächste Arbeit, Import/Export, Backup/Restore. Keine Accounts, Cloud, UI-Plattform oder Enterprise-Schichten erforderlich.

| Modell | v6.1 | Schlank |
|---|---|---|
| Sol | 10/10 unabhängige Ergebnisse; eigene 13 Tests grün | 10/10; eigene 10 Tests grün |
| Opus 5.5, korrigierte Umgebung | 10/10; eigene 21 Tests grün | 10/10; eigene 20 Tests grün |

Alle vier wählen nachvollziehbare kleine Architekturen, erklären Annahmen und halten die zurückgestellten Funktionen aus dem Scope. Der Sol-Baselineplaner beschränkt Speicher-/Backup-Pfade zusätzlich auf das Repository und dokumentiert manuelle Stale-Lock-Recovery; das ist eine echte, hier nicht nötige Nutzungseinschränkung, kein Datenverlustbeweis. Auch die schlanken Produkte haben Grenzen und technische Trade-offs. Weniger Module allein bedeutet nicht bessere Architektur.

Der Hauptagent hat den unabhängigen Verifikationscode gelesen und **alle 40 Ergebnisse sowie die vier eigenen Suiten erneut ausgeführt**. Ergebnisse: [autonomy-verified.json](autonomy-verified.json); jederzeit ohne Modelle wiederholbar mit `python3 benchmarks/verify_planners.py`.

### Früher Brief / Init

Zusätzlicher deutscher Werkstatt-Brief: Initialisierung ausdrücklich ohne Produktbau; zwei Personen, lokale Tests, unbestätigter Stack und möglicher späterer gemeinsamer Zugriff.

**Beide** verstehen das Ziel, trennen Fakten/Vorschläge/Offenes, geben einen kleinen Datenflussvorschlag und stellen drei relevante Fragegruppen. Beide lassen die nächste Baufreigabe offen und erzeugen keinen Produktcode. Baseline führt mehrere Docs, Idea und Feld-/Readiness-Arbeit; der Kandidat hält den nützlichen Stand allein in PROJECT. Der nachvollziehbare Prozess existiert also auch ohne separate Brief-/Init-Dateien. Die Details wurden retrospektiv gegen den vorab geschriebenen Auftrag geprüft; kein unabhängiger vorregistrierter Init-Oracle. Eine weitere frische Paarung nach der Profile→Skills-Konsolidierung bestätigt denselben Init-Ablauf: beide stellen drei Fragegruppen und schreiben keinen Produktcode; 147 s Baseline gegenüber 72 s finalem Kandidaten. [Separater Nachweis/Hash](consolidated-init.json).

## Aufwand, nicht vermeintliche Intelligenzpunkte

| Erstumsetzung | Sekunden alt → schlank | Frischer Input + Output alt → schlank |
|---|---:|---:|
| Sol CRM | 501 → 295 | 71.828 → 59.804 |
| Sol Import | 416 → 314 | 70.040 → 51.024 |
| Sol Dispatch 1 | 440 → 577 | 92.409 → 57.013 |
| Sol Dispatch 2 | 572 → 618 | 96.761 → 69.696 |
| Sol Arbeitsplaner | 432 → 316 | 61.493 → 48.441 |
| Opus Arbeitsplaner | 460 → 418 | 141.642 → 105.956 |
| Sol früher Brief | 174 → 59 | 32.347 → 11.124 |

„Frisch“ summiert gemeldeten Input, CacheWrite und Output. CacheRead bleibt separat in metrics.json; Tokenarten haben unterschiedliche Kosten und diese Summen sind **keine Rechnung in Euro/Dollar**. Für Opus ist CacheWrite relevant, für die hier gemessenen Sol-Läufe null. Große Gesamttokenzahlen einschließlich wiederholter Cachezugriffe sind kein gleichzeitig gefülltes Context Window. Initial-/Review-/Transportfehler sind nicht heimlich in saubere Erstläufe eingerechnet.

Der eingefrorene Kandidat reduziert den festen Einstieg von 9.102 auf 5.073 Zeichen (ca. 44 %), die Markdown-Menge der Vorlage von 35 auf 19 Dateien und von 95.687 auf 40.037 Zeichen. Nicht alle Dateien werden in einer Sitzung geladen. Die abschließende Skill-Konsolidierung reduziert hauptsächlich Katalog-/Pflegekomplexität, nicht die Menge unverändert wichtiger Fachreferenzen.

**Fazit Aufwand:** weniger neue Tokens in allen hier vollständig vergleichbaren Fällen; schneller bei CRM, Import, Planer und Init, aber langsamer bei beiden Dispatch-Paaren. Parallelität, Cache, Reihenfolge und Serverlast wurden nicht vollständig kontrolliert. Keine belastbare allgemeine Laufzeit-/Kostenquote.

## Fehler der Testumgebung wurden nicht den Harnesses zugeschrieben

- Erste CRM-Paarung und QA-Abschluss von Codex-Quota unterbrochen; neue CRM-Sitzungen separat ausgewiesen. Zwei kostenlose Resets wurden verbraucht, keine Extra-Nutzung aktiviert.
- Opus via Pi abgewiesen, offizieller Claude-Code-Zugang funktioniert. Erste native Paarung konnte wegen eines falschen Bash-Temp-Pfads keine Tests ausführen; beide melden das ehrlich. Korrigierte native Paarung und Bash-Smoke-Check ersetzen nicht rückwirkend diese Resultate.
- Eine CRM-Änderungsphase der Baseline hatte einen WebSocket-Transportfehler; separate frische Fortsetzung beendet die Arbeit und besteht 24 Gruppen. Kein stiller Neustart und keine manuelle Produktkorrektur.
- Der Maskierungs-Kopierer verlor Executable-Bits; der erste Review meldete deshalb einen falschen Demo-Fehler. Original hatte 0755, Maskierung 0644. Copier auf copy2 korrigiert, Original nicht verändert, alle vier Produkte gleich erneut geprüft. Fehlende absichtlich herausgefilterte Harness-Links werden nicht als Produktfehler gewertet. Regression schützt die Kopiermodi. Der ursprüngliche Review bleibt als [diagnostischer Vorbericht](diagnostics-autonomy-initial.md) erhalten und darf nicht als endgültige Abnahme gelesen werden.

## Kann man das vernünftig testen?

**Ja – mit unabhängigen Abnahmen, frischen Kontexten und echten Randfällen.** Damit lassen sich Scope-Verstöße, falsche Fertigmeldungen, Datenintegrität, Fortsetzung und Aufwand konkret beobachten. Auch ein realer Auftrag mit offenen Routineentscheidungen ist prüfbar, ohne eine bestimmte Architektur zum allein richtigen Ergebnis zu erklären.

**Nein – nicht abschließend mit diesem kleinen Experiment.** Wenige Aufgaben, enge Stress-Verträge, ein Runtime/OS-Stand und meist ein Implementierungspaar pro Aufgabe erlauben keine statistische Gleichwertigkeits- oder universelle Sicherheitsbehauptung. Langzeitpflege, komplexe UI, reale Provider, echte Auth, Datenschutz-/Rechtsabnahme, große Legacy-Systeme und viele Sitzungen bleiben offen. Ein Paketvergleich isoliert nicht die Wirkung jedes gestrichenen Satzes oder von Profile-versus-Skills.

Empfohlen: den schlanken Harness in 2–3 echten Intermediate-Projekten einsetzen; nur tatsächlich wiederkehrende Fehler mit Kontext/Nachweisen festhalten. Sinnvolle Maßstäbe: unabhängige Akzeptanz, notwendige Eingriffe, falsche Zusagen, Nacharbeit, Wiederanlauf und Pflegeaufwand. **Nicht nach jedem Fehler eine neue universelle Regel hinzufügen.**

## Prüfen und nutzen

Final ausgeführt: **24/24 technische Tests einschließlich fünf echter Brave-Fälle**, **17/17 Oracle-Selbsttests**, modellfreie Wiederholung aller 40 Planer-Ergebnisse/eigenen Suiten und aller acht Stress-Produktextrakte. Normaler CI-Modus überspringt die fünf Brave-Fälle ausdrücklich; er belegt keinen Browserlauf. Technische Regression, Oracle-Gegenprüfungen und Brave-Prüfungen stehen in der Repository-README. Die erzeugten Produkte sind synthetische Beispiele unter `benchmarks/fixtures/`, nicht Bestandteil der exportierten Vorlage. Rohsessions, Authdateien und Koordinator-Kontext werden nicht veröffentlicht.

Claude liest dieselben Skills per optionalen Symlinks und AGENTS über den expliziten Launcher; keine zweite CLAUDE.md. Details und Grenzen: [CLIENT-COMPATIBILITY.md](CLIENT-COMPATIBILITY.md).
