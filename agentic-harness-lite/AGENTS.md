# AGENTS.md

Arbeitsregeln für Coding-Agenten (Claude Code, Codex, Pi). Hier steht nur, was du aus Code, Git und gesundem Urteil **nicht** selbst ableiten kannst. Ablaufwissen für bestimmte Aufgaben liegt in Skills unter `.agents/skills/` (für Claude Code verlinkt unter `.claude/skills/`). Die Übersicht über Dateien und Entscheidungsfluss steht in `README.md`.

| Skill | Lies ihn, wenn … |
|---|---|
| `project-init` | unten „Pending Project Init“ steht und Produktarbeit beginnen soll, oder ein Init ausdrücklich beauftragt ist |
| `business-software` | er unten unter „Skills“ gewählt ist, bei Änderungen an Fachlogik, Datenmodell, Schnittstellen, Importen, Jobs oder Berechtigungen |
| `website` | er unten unter „Skills“ gewählt ist, bei den in seiner Beschreibung genannten Anlässen |

## Projekt

Status: **Pending Project Init**. Vor der ersten Produktumsetzung den Skill `project-init` nutzen. Harness- oder Doku-Arbeit allein löst kein Init aus.

- **Ziel und Nutzer:** offen
- **Reifegrad:** offen (Prototyp | MVP | Produkt; siehe „Arbeitsrahmen“)
- **Erstes Ergebnis, Nicht-Ziele:** offen
- **Erfolgskriterium:** offen
- **Risiken, Grenzen, Freigaben** (echte Daten, Berechtigungen, Zahlungen, Veröffentlichung, Kosten, irreversible Aktionen): offen
- **Ausgangslage** (bestehender Code, Vorgaben zu Stack oder Betrieb): offen
- **Stack und Struktur:** offen
- **Standards und Qualitätsziele:** offen (verbindliche Standards, Coding-Konventionen, messbare Qualitätsanforderungen; Durchsetzung im Code oder Verweis auf Projekt-Docs)
- **Prüfstrategie:** offen (gewählte Testebenen und risikobezogene Prüfungen, Abgewähltes mit Grund, TDD-Einsatz, Pflichtchecks und Regressionumfang, Umgebung, lokal/CI, offene Checks mit Auslöser)
- **Skills** (je Skill die gewählten Bereiche, Abgewähltes mit Grund): keine gewählt
- **Archiv** (nicht laden, bauen, testen oder ändern): keins

| Zweck | Befehl | Letztes Ergebnis (eine Zeile: Datum · bestanden/fehlgeschlagen · Anzahl) |
|---|---|---|
| Start/Vorschau | offen | – |
| Tests | offen | – |

**Offene Entscheidungen und Annahmen:** offen

**Fortsetzungsstand:** kein aktiver Auftrag. Bei Arbeit ohne Idee/Spec: Auftrag, erledigt/ausstehend, Blocker und nächster Schritt. Sonst Verweis auf deren Arbeitsstand.

**Projekt-Docs:** Wissen, das weder in den Code noch hierher passt, liegt unter `docs/<thema>.md`. Jede solche Datei bekommt hier eine Zeile mit Leseauslöser, z. B. „`docs/design.md`: bei jeder sichtbaren Änderung“.

## Arbeitsrahmen

Wie streng du arbeitest, ergibt sich aus dem Reifegrad im Abschnitt „Projekt“:

- **Prototyp:** Specs sind optional. Als Nachweis reichen ein Smoke-Check des Hauptablaufs und eine Sichtprüfung in einer Umgebung. Platzhalter sind erlaubt, wenn sie gekennzeichnet sind.
- **MVP:** Specs für die Kernabläufe. Automatisierte Tests für den Kernablauf und seine relevanten Fehlerfälle. Oberflächen in einem Browser bzw. einer Zielumgebung bei den Prüfgrößen des Projekts.
- **Produkt:** Specs für jedes beauftragte Verhalten. Tests richten sich nach den Risiken. Volle Prüfmatrix (mehrere Browser oder Umgebungen) und Vorher-nachher-Aufnahmen aller Seiten erst ab hier oder vor einem Livegang. Vor der Veröffentlichung laufen Release- bzw. Livegang-Checks.

## Arbeitsweise

- **Diktat:** Aufträge sind oft diktiert. Deute offensichtliche Hörfehler sinngemäß. Nenne deine Deutung in einem Satz, wenn sie Inhalt entfernt oder umschreibt oder wenn Lesarten zu verschiedenen Ergebnissen führen.
- **Sitzungsstart und Fortsetzung:** Lies vor der Umsetzung den Projektabschnitt, die zum Auftrag gehörende Idee oder Spec einschließlich Arbeitsstand und die Projekt-Docs nach ihren Leseauslösern; prüfe Code und Git-Stand gegen diese Angaben. Ohne konkreten Auftrag setzt du keine Idee oder andere offene Spec eigenmächtig um. Halte vor einer Übergabe oder einem Aufgabenwechsel den Fortsetzungsstand aktuell: in der Idee/Spec, sonst im Projektabschnitt. Markiere veraltete oder fehlende Nachweise als ungeprüft; ein früheres grünes Ergebnis belegt keine spätere Änderung.
- **Annahmen oder Rückfrage:** Reversible Annahmen triffst du selbst, nennst sie und arbeitest weiter. Vor neuen Produktentscheidungen und bei Unklarheiten mit spürbaren Folgen fragst du nach. Bündle die Fragen und frage nichts, was schon beantwortet ist.
- **Freigabe:** Vor irreversiblen Schritten oder Massenaktionen (Versand an Dritte, Löschen, Zahlungen, Veröffentlichung, Änderungen an echten Daten) zeigst du zuerst Probelauf und Umfang: Anzahl, Beispiele, Rückweg. Freigegeben ist erst, was der Auftraggeber **danach** bestätigt. Ein allgemeiner Auftrag wie „schick das raus“ ist noch keine Freigabe.
- **Keine erfundenen Fakten:** Fehlende Projektfakten, Referenzen, Kundenstimmen, Kennzahlen, Zertifikate, Preise oder Rechtsangaben nicht erfinden. Lücken bleiben als Platzhalter sichtbar. Ein Vorschlag wird erst nach Bestätigung zum Projektfakt.
- **Einordnung:** Beim Init und immer dann, wenn ein Auftrag einen neuen Projektteil anderer Art bringt (z. B. eine Mail-Automatisierung in einer Website), ordnest du ihn vor der Umsetzung in wenigen Zeilen ein: passende Skills und Bereiche, Risiken, offene Technikfragen. Ändert sich dadurch die Skill-Auswahl, trägst du sie nach Bestätigung unter „Skills“ ein. Bei Aufgaben innerhalb des Bekannten entfällt die Einordnung.
- **Umfang und Zerlegung:** Setze den ganzen Auftrag um, aber nicht mehr. Zerlege größere Vorhaben in Schritte, die sich einzeln prüfen lassen; ist das Vorhaben noch unklar, klärst du es zuerst als Idee nach „Ideas und Specs“. Berührt eine Änderung die unter „Risiken“ genannten Bereiche, benennst du ihre Auswirkungen vor dem Eingriff.
- **Sichtbare Iterationen:** Ändere nur das Genannte und melde weitere Auffälligkeiten als Liste. Bei „wie vorher, nur …“ stellst du zuerst den vorherigen Stand exakt wieder her und änderst dann nur das Genannte.
- **Eine Quelle je Wert:** Konfiguration, Texte und Gestaltungswerte (Tokens) stehen an einer Stelle. Eine geänderte Regel ersetzt die alte, statt sie zu übersteuern (kein spezifischerer Selektor, kein Sonderfall-Zweig). Wiederkehrende Muster werden zum Baustein, sobald die Gemeinsamkeit klar ist, spätestens beim dritten Vorkommen. Würde das unbeteiligte Teile umbauen, benennst du die Kopie stattdessen in der Übergabe als technische Schuld.
- **Projektdateien:** Dokumentiere nur dauerhaft nötiges Wissen, das nicht bereits im Code, in Konfiguration oder einer anderen Quelle steht. Jede Projekt-Doc hat eine Hauptzuständigkeit, einen konkreten Leseauslöser im Projektabschnitt und nur nötige direkte Verweise; keine leeren Pflichtgerüste oder zusätzliche Indexdatei. Ändert sich ein bestätigter Stand, ersetzt du die Aussage an ihrer Stelle, statt einen Absatz anzuhängen. Der Verlauf steht in Git, Prüfprotokolle gehören in die Übergabe. Schreibe knapp und präzise, ohne bestätigte Anforderungen zu verlieren. Richtgrößen: Abschnitt „Projekt“ und jede Projekt-Doc etwa 6 KB, eine Spec etwa 15 KB. Verdichte zuerst; teile erst bei einem eigenständigen Thema auf.
- **Git:** Pro Arbeitsverzeichnis schreibt nur eine Agentensitzung; parallele Sitzungen arbeiten in eigenen Worktrees. Fremde, nicht committete Änderungen weder überschreiben noch mitcommitten. Commits nur auf Auftrag, mit einem Betreff, der die tatsächliche Änderung beschreibt.

## Ideas und Specs

Ideen liegen unter `ideas/Ixxx-*.md` nach `ideas/_vorlage.md`, beauftragtes **Nutzerverhalten** unter `specs/Sxxx-*.md` nach `specs/_vorlage.md`. Nummern werden je Ordner fortlaufend vergeben, nicht neu nummeriert. Lies nur die zum Auftrag gehörenden Artefakte; Vorlagen nur beim Anlegen oder Überführen. Ob eine Spec nötig ist, regelt der Arbeitsrahmen. Ein konkreter, umsetzbarer Auftrag braucht keinen vorgeschalteten Ideen-Dialog.

- **Idee:** Problem, Nutzer/Nutzen und Scope im Dialog klären; Annahmen hinterfragen und Alternativen prüfen. Auswirkungen gegen vorhandene Specs, relevante Projekt-Docs und Code prüfen, Risiken und offene Entscheidungen festhalten. Das Ideen-Dokument schon während der Klärung pflegen, nicht erst am Ende.
- **Überführen:** Erst wenn Verhalten und Abgrenzung bestätigt, die nötige Machbarkeit geprüft und blockierende Fragen geklärt sind, kann aus der Idee eine Spec werden. Zusätzlich ist ein konkreter Umsetzungsauftrag nötig. Überführe den beauftragten Umfang in eine oder mehrere Specs mit AK und Status `Modified`, halte Herkunfts-ID und relevante Entscheidungen dort fest und aktualisiere eingehende Verweise. Keine doppelte aktive Beschreibung: Bei vollständiger Übernahme entfällt die Ideendatei; bei Teilübernahme bleibt nur der noch offene Umfang samt Spec-Verweisen. Eine geklärte Idee allein ist keine Freigabe.
- Spec-Status: `Modified` (neu, geändert oder noch nicht vollständig belegt) → `Implemented` (alle AK belegt und erforderliche Pflicht- und Regressionstests bestanden).
- Ein AK hat **ein** unabhängig prüfbares Ergebnis. Gestaltungsmaße gehören nicht ins AK, sondern nach `docs/design.md`.
- Ändert oder erweitert ein Auftrag eine Spec, setzt du ihren Status vor der Umsetzung auf `Modified`. Geänderte AK und ihre Nachweise werden ersetzt. Zurück auf `Implemented` geht sie erst nach dem Beleg aller AK und bestandenen erforderlichen Pflicht- und Regressionstests; bei fehlgeschlagenen oder nicht ausgeführten Prüfungen bleibt sie `Modified`, auch bei einem externen Blocker.
- Keine Spec ist nötig für verhaltensgleiche Refactors, Doku und kleine Oberflächen-Iterationen innerhalb bestehender AK.

## Fertig heißt

Vor der Umsetzung bestimmst du aus der Projekt-Prüfstrategie die betroffenen Pflichtchecks und Regressionstests. Halte deren Umfang und Befehle in der Spec fest, bei Arbeit ohne Spec im Fortsetzungsstand. Änderungen an gemeinsamen Bausteinen müssen deren betroffene Nutzerabläufe abdecken; bei unklaren Auswirkungen läuft die gesamte vorhandene Verhaltenstestsuite. Offene Prüfungen, fehlende Umgebung oder rote CI sind keine bestandenen Checks. Fehlt ein erforderlicher Check, richtest du ihn ein oder meldest den Blocker; der Status bleibt nach der Spec-Regel offen.

1. Jeder Punkt des Auftrags und jedes betroffene AK ist durch einen **auf dem aktuellen Stand ausgeführten** Check belegt. Der Check muss an der Grenze laufen, an der Nutzer das Verhalten erleben (CLI, API, UI). Build, Lint, eine leere Testsuite oder ein nur geplanter Befehl belegen kein Verhalten.
2. Sichtbare Oberflächen werden im Zielmedium belegt (Browser, Emulator, Gerät): Eigenschaften messen, Wirkung per Screenshot prüfen. Quelltextvergleiche belegen kein Aussehen.
3. Schlägt etwas fehl, behebst du die Ursache statt das Symptom. AK werden nicht angepasst, damit ein Test grün wird. Tritt derselbe Fehler erneut auf, überprüfe deine Annahme.
4. Fehlen Entscheidung, Umgebung oder Nachweis: nicht „fertig“ melden, sondern Bestandenes, Fehlgeschlagenes und nicht Geprüftes getrennt berichten.
5. Nachführen: In der Befehlstabelle oben das letzte Ergebnis als eine Zeile ersetzen; Einzelheiten und Nachweise gehören in die Spec bzw. die Übergabe, nicht in den Projektabschnitt. In der Spec den Nachweis je AK ersetzen (Prüfziel · Test oder Schritte · Commit oder „uncommittet, Datum“ · Ergebnis). Für den Statuswechsel gilt der Abschnitt „Ideas und Specs“.
6. Übergabe: was geändert wurde, was womit geprüft wurde und mit welchem Ergebnis, welche Annahmen getroffen wurden und was offen ist.

## Harness selbst

Zum Harness gehören diese Datei außer dem Abschnitt „Projekt“, `.agents/skills/`, die Links unter `.claude/skills/`, `ideas/_vorlage.md`, `specs/_vorlage.md` und die Harness-Übersicht in `README.md`.

- **Beobachtungen:** Fällt beim Arbeiten eine Stärke, Schwäche oder Lücke des Harnesses auf, notierst du sie kurz als offenen Punkt in `harness-learnings.md`. Harness-Dateien änderst du nur auf ausdrücklichen Auftrag.
- **Universell oder Projekt:** Auch wenn der Auftrag „im Harness“ sagt, prüfst du zuerst: Gilt die Regel für **jedes** Projekt dieser Art? Dann gehört sie in den Harness. Gilt sie nur für dieses Projekt, gehört sie in den Abschnitt „Projekt“, nach `docs/` oder in den Code. Im Zweifel fragst du mit einer Empfehlung nach. Betrifft eine neue Regel bestehende Daten, gehört eine Migration dazu (Freigabe beachten).
- **Bei einer Harness-Änderung** passt du im selben Schritt alle abhängigen Stellen an:
  1. Suche repo-weit nach betroffenen Pfaden, Datei- und Skill-Namen.
  2. Gleiche die Skill-Tabelle oben, die Verweise in den Skills, die Links unter `.claude/skills/` und die Übersicht in `README.md` an.
  3. Prüfe auf Doppelungen: Jede Regel steht an genau einer Stelle. Skills verweisen auf `AGENTS.md`, statt Regeln zu wiederholen, und `AGENTS.md` wiederholt keine Skill-Inhalte.
  4. Prüfe, dass jeder verwiesene Pfad existiert und jeder Skill über die Tabelle oben erreichbar ist.
