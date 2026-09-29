# Agentic Harness für neue Produktprojekte

Dieser technologieoffene Harness ist für neue, leere Produktprojekte gedacht – vom kleinen CLI- oder Web-Produkt bis zu größeren Vorhaben mit klar begrenztem erstem Meilenstein. Diese Datei ist die Anleitung für Menschen im Ordner `agentic-harness/`; die Root-`README.md` gehört dem jeweiligen Produkt. Der Agent wird über Root-`AGENTS.md` geführt, nicht über diese Anleitung.

## Schnellstart: neues Projekt aus der Vorlage

1. **Anlegen:** auf GitHub „Use this template“ oder den Inhalt der Vorlage ohne `.git` in einen leeren Ordner kopieren. Ohne Git-Repository schlägt der Agent beim Init `git init` vor.
2. **Optional beschreiben:** `agentic-harness/project-brief.md` mit Ziel, Nutzern, Wünschen und bekannten Grenzen anlegen. Der Agent nutzt sie als Ausgangsbeschreibung, nicht als bestätigte Vorgabe.
3. **Auftrag geben:** den Ordner mit dem Coding-Agenten öffnen und in eigenen Worten sagen, was entstehen soll, z. B. „Eine Automatisierung, die meine E-Mails sortiert“ oder „Eine Website für einen Tischlereibetrieb“. Weil `harness/project.md` noch `Pending Project Init` enthält, startet der Agent das Init: gebündelte Rückfragen, danach Profil (z. B. Website) oder keines, Stack, Architektur und Tests.
4. **Freigeben:** Nach dem Init den ersten Schritt ausdrücklich beauftragen. Init allein ist keine Implementierungsfreigabe.

Erkenntnisse über den Harness sammelt jedes Projekt in `agentic-harness/harness-learnings.md`; der Weg zurück in die Vorlage steht unter „Harness als Vorlage exportieren“.

Tatsächlicher Arbeits- und Entscheidungsfluss

 ```text
   AGENTS.md → core.md + project.md
                 │          └→ bestätigte Ziele, Grenzen, aktive Prüfbefehle
                 │
                 ├─ Neues Produktprojekt: Init beauftragt oder vor erster
                 │  Produktumsetzung noch „Pending Project Init“?
                 │    └→ init.md
                 │         ├→ Ziel, Grenzen und ersten Schritt klären
                 │         ├→ project.md + passende Projekt-Docs befüllen
                 │         ├→ ggf. echte Checks einrichten und ausführen
                 │         └→ zurück zu core.md und zum konkreten Auftrag
                 │            (Init allein ist keine Implementierungsfreigabe)
                 │
                 ↓
   [R1] ───→ AUFTRAG KLÄREN: Ziel, Umfang, Nicht-Ziele, Freigaben
                 │
                 ├─ Größeres Vorhaben noch offen?
                 │    └→ Idea klären → zurück zum Auftrag
                 │         („Ready“ ist noch kein Umsetzungsauftrag)
                 │
                 ├─ Neues/geändertes Nutzerverhalten beauftragt?
                 │    └→ betroffene Spec(s) erstellen/ändern:
                 │       prüfbare Akzeptanzkriterien; zunächst „Modified“
                 │
                 └─ Sonst, z. B. Refactor/Doku/Struktur:
                      Auftrag als Soll; keine künstliche Produktspec
                 │
                 ↓
   [R2] ───→ PASSENDE DOCS LESEN – direkt nach Auslöser in AGENTS.md
                 │
                 ├→ profiles/<name>: nur bei gewähltem Profil, nach dessen „Gilt bei“
                 ├→ architecture.md: Bausteine, Schnittstellen, Betrieb, Archiv
                 ├→ code.md:         gewählter Stack, Codekonventionen
                 ├→ design.md:       Gestaltungsregeln (nur bei Oberfläche)
                 └→ testing.md:      Risiken und Kriterien → geeignete
                                     Testebenen/-arten, Testorte und
                                     Ausführungsanlässe auswählen
                                     (Strategie; führt selbst keine Tests aus)
                 │
                 ↓
   [R3] ───→ core.md, Schritt 3: ÄNDERUNG UMSETZEN
                 │
                 ├→ tatsächlichen Produkt-Source-Code ändern
                 ├→ passende Produkttests erstellen oder ändern
                 ├→ vorgesehene Checks schon während der Arbeit ausführen
                 └→ neues Soll / neue Entscheidung nötig?
                      → zurück zu [R1], Projektdatei/Spec erst klären
                 │
                 ↓
           GATE-DURCHLAUF BEGINNT: gate.md
                 │
                 ├→ requirements.md
                 │    Auftrag + project.md + ggf. Spec/architecture.md
                 │    → betroffene AK und Grenzen = SOLL
                 │
                 └→ implementation.md
                      SOLL + tatsächliche Änderung + project.md (Befehle)
                      + je nach Eingriff Code-/Architektur-Doc
                      + bei Produkt-/Teständerung testing.md
                      │
   [R4] ────────────────┤→ erforderliche Checks auf aktuellem Stand ausführen
                      └→ beobachtetes IST, Ergebnisse und Nachweisgrenzen
                 │
                 ↓
           gate.md ENTSCHEIDET: Belegen IST und Nachweise das SOLL?
                 │
                 ├─ JA → Ergebnis berichten;
                 │        ggf. betroffene Spec „Implemented“
                 │
                 └─ NEIN → fail.md: konkrete Lücke und Ursache bestimmen
                             │
                             ├─ Soll unklar / Freigabe oder Spec fehlt
                             │    └──────────────────────────────→ [R1]
                             │
                             ├─ Teststrategie oder Nachweisgrenze ungeeignet
                             │    └→ testing.md überprüfen ─────→ [R2]
                             │
                             ├─ Prüfbefehl/Umgebung fehlt
                             │    └→ Einrichtung klären; project.md erst
                             │       nach tatsächlicher Einrichtung ändern
                             │       → Checks ausführen ─────────→ [R4]
                             │
                             ├─ Fehler im Source Code oder Produkttest
                             │    └→ Ursache korrigieren ────────→ [R3]
                             │
                             ├─ Prüfung fehlt oder Nachweis ist veraltet
                             │    └→ betroffene Prüfung nachholen → [R4]
                             │
                             └─ Entscheidung oder Nachweis weiter unmöglich
                                  └→ STOPP: Blocker und offene Checks berichten

           Nach jeder möglichen Korrektur:
           betroffene Prüfungen wiederholen → gate.md erneut vollständig
           durchlaufen (requirements.md + implementation.md + Entscheidung).
 ```


 Welche Datei wird wann gelesen?

 ```text
   AUFTRAG
     ↓
   AGENTS.md                         Einstieg: ordnet die Aufgabe zu
     ├─ IMMER → harness/core.md       steuert den Arbeits- und Entscheidungsfluss
     ├─ IMMER → harness/project.md    bestätigte Ziele, Grenzen, aktive Befehle
     │
     ├─ BEI Project Init ───────────→ harness/init.md
     ├─ BEI gewähltem Profil ───────→ profiles/<name>.md (laut „Gilt bei“)
     ├─ BEI Architektur/Betrieb ───→ docs/architecture.md
     ├─ BEI Code/Refactor ──────────→ docs/code.md
     ├─ BEI sichtbarer Änderung ───→ docs/design.md
     ├─ BEI Testplanung/-arbeit ───→ docs/testing.md
     │
     ├─ BEI offener größerer Idee ──→ ideas/I000-readme.md
     │                                └→ konkrete Idea;
     │                                   Vorlage nur bei Neuanlage
     ├─ BEI neuem/geändertem
     │  Nutzerverhalten ────────────→ specs/S000-readme.md
     │                                └→ betroffene Spec(s);
     │                                   Vorlage nur bei Neuanlage
     │
     ├─ VOR Abschluss ──────────────→ harness/verification/gate.md
     └─ BEI Harness-/MD-Pflege ─────→ harness-map.md /
                                      document-contract.md
 ```
Teststruktur:
```text
   Auftrag + project.md + ggf. Spec (Akzeptanzkriterien)
                       │
                       ├→ architecture.md + code.md
                       │          ↓
                       └────→ testing.md
                              Welche Prüfungen passen zum Risiko?
                              Wo, wie und wann werden sie ausgeführt?
                                         │
                                         ↓
   core.md, Schritt 3: UMSETZUNG
     ├→ Source Code ändern
     ├→ passende Tests erstellen/ändern
     └→ vorgesehene Checks ggf. schon während der Arbeit ausführen
                                         │
                                         ↓
   gate.md: EINE Abschlussprüfung beginnt
     ├→ requirements.md → SOLL: Auftrag, Grenzen, betroffene AK
     └→ implementation.md → IST: tatsächliche Änderung prüfen;
          │                  testing.md heranziehen, erforderliche Checks
          │                  auf aktuellem Stand ausführen, Belege erfassen
          └─────────────────────────┬───────────────────────────────
                                    ↓
                      gate.md entscheidet: Soll ausreichend belegt?
                        ├→ JA: Ergebnis berichten; ggf. Spec „Implemented“
                        └→ NEIN: fail.md → Ursache klären/korrigieren
                                         → betroffene Checks wiederholen
                                         → gate.md erneut durchlaufen
 ```
## Drei Ebenen

| Ebene | Dateien | Wandert in eine neue Vorlage? |
|---|---|---|
| **Universell** | `AGENTS.md` (oberer Teil), `agentic-harness/harness/` (Core, Init, Verifikation, Vorlagen), `document-contract.md`, `harness-map.md`, diese README, `ideas/I000-readme.md`, `specs/S000-readme.md` sowie Kopf und „Universeller Rahmen“ von `harness/project.md` und `docs/*.md` | ja, unverändert |
| **Profil** | `agentic-harness/profiles/*.md`, z. B. `website.md`: Teil A Pflichtregeln, Teil B abwählbare Stil-Defaults, Teil C optionaler Baukasten | ja; das neue Projekt wählt beim Init ein passendes Profil (oder keines) und hält Übernahmen und Abweichungen in der thematisch zuständigen Projektdatei fest (z. B. Gestaltung in `docs/design.md`, Prüfgrößen in `docs/testing.md`) |
| **Projekt** | Abschnitt „Projektspezifische Befüllung“ in `project.md` und `docs/*.md`, „Projektspezifische Ergänzungen“ in `AGENTS.md`, Ideas, Specs, `project-brief.md`, Learnings-Einträge, Root-`README.md`, Produktcode, Tests, Archiv | nein; wird zurückgesetzt oder weggelassen |

Neue Erkenntnisse wandern je nach Reichweite: für jedes Projekt → universelle Datei; für eine Projektart → Profil; nur für dieses Produkt → Projektdatei.

**Universell heißt: offen bis zum Init.** Der Harness legt weder Projektart noch Stack, Architektur, Tests oder Profil fest. Bei jedem neuen Projekt werden Ziel, erster Ablauf und das dafür Nötige im Project Init neu besprochen. `AGENTS.md` führt dorthin, `harness/init.md` treibt die Klärung und schreibt das Bestätigte in die Projektabschnitte. Fehlende Festlegungen in der Vorlage sind deshalb gewollt.

**Ein weiteres Profil** (z. B. Automation, API) folgt dem Muster von `profiles/website.md`: Kopf mit „Gilt bei“ als Ladeauslöser, zusätzliche Init-Fragen, Teil A Pflichtregeln, Teil B abwählbare Defaults, Teil C optionaler Baukasten. `AGENTS.md` lädt jedes gewählte Profil über eine allgemeine Zeile; im universellen Teil ist dafür nichts zu ergänzen außer dem Eintrag in `harness-map.md`.

## Harness als Vorlage exportieren

Aus einem laufenden Projekt heraus, z. B. um die Vorlage mit neuen Erkenntnissen zu aktualisieren. Nur in ein **neues, leeres** Verzeichnis außerhalb der Quelle exportieren. Es gibt noch kein Export-Skript; der Block bricht bei falschen Pfaden oder nicht leerem Ziel ab:

```sh
set -eu
QUELLE=/pfad/zu/diesem/projekt
ZIEL=/pfad/zum/neuen-leeren-projekt
test -f "$QUELLE/AGENTS.md" || { echo "Quelle falsch"; exit 1; }
case "$ZIEL" in "$QUELLE"*) echo "Ziel liegt in der Quelle"; exit 1;; esac
if [ -e "$ZIEL" ] && [ -n "$(ls -A "$ZIEL")" ]; then echo "Ziel nicht leer"; exit 1; fi
mkdir -p "$ZIEL/agentic-harness/ideas" "$ZIEL/agentic-harness/specs"
cd "$QUELLE"
cp AGENTS.md "$ZIEL/"
printf '.DS_Store\n.idea/\n' > "$ZIEL/.gitignore"
cp -R agentic-harness/harness agentic-harness/docs agentic-harness/profiles "$ZIEL/agentic-harness/"
cp agentic-harness/README.md agentic-harness/document-contract.md agentic-harness/harness-map.md agentic-harness/harness-learnings.md "$ZIEL/agentic-harness/"
cp agentic-harness/ideas/I000-readme.md "$ZIEL/agentic-harness/ideas/"
cp agentic-harness/specs/S000-readme.md "$ZIEL/agentic-harness/specs/"
printf '# Neues Produktprojekt\n\nVorlage: Die Anleitung zum Harness steht in [agentic-harness/README.md](agentic-harness/README.md). Diese Datei wird beim Project Init durch die Produkt-README ersetzt.\n' > "$ZIEL/README.md"
```

Danach im Zielordner zurücksetzen:

1. In `agentic-harness/harness/project.md` und jeder Datei unter `agentic-harness/docs/` alles unter „## Projektspezifische Befüllung“ durch **„Noch offen (Project Init).“** ersetzen. Status-Zeile: in `project.md` `Pending Project Init`, in den Docs „Noch offen (Project Init).“. Kopf und „Universeller Rahmen“ bleiben.
2. In `AGENTS.md` unter „## Projektspezifische Ergänzungen“ alle Punkte löschen.
3. In `agentic-harness/harness-learnings.md` die Status-Zeile auf „Noch keine Beobachtungen.“ setzen und alles nach dem Abschnitt „Abgrenzung“ durch „## Beobachtungen“ mit dem Satz „Noch keine Beobachtungen.“ ersetzen.
4. Prüfen: `grep -rniE 'ALTER_PRODUKTNAME|alte-domain|@' "$ZIEL"` darf keine Produktangaben mehr finden (erwartet sind nur allgemeine Beispiele und optionale Verweise auf `project-brief.md`); jeder in Dokumentköpfen genannte `agentic-harness/…`-Pfad existiert, außer ausdrücklich optionalen.

Nicht übernommen werden: Produktcode (`src/`, `scripts/`, `tests/`), `archiv/`, `dist/`, konkrete Ideas und Specs, `project-brief.md`, `.git/` und IDE-Dateien.

Öffne den Zielordner dann mit deinem Coding-Agenten und beauftrage Project Init, z. B. „Kläre den ersten Nutzerablauf und initialisiere dieses neue Produktprojekt.“ Der Agent wählt ein passendes Profil, befüllt `project.md`, die betroffenen Projekt-Docs und die Produkt-`README.md`. Erkenntnisse über den Harness sammelt das neue Projekt wieder in `agentic-harness/harness-learnings.md`.
