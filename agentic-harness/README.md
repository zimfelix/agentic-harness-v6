# Agentic Harness für neue Produktprojekte

Dieser technologieoffene Harness ist für neue, leere Produktprojekte gedacht – vom kleinen CLI- oder Web-Produkt bis zu größeren Vorhaben mit klar begrenztem erstem Meilenstein. Diese Datei ist die Anleitung für Menschen im Ordner `agentic-harness/`; Landkarte (`harness-map.md`), Dokumentenvertrag (`document-contract.md`) und Learnings sind dagegen Arbeitsdokumente für den Agenten, die er über die Auslöser in `AGENTS.md` liest; die Root-`README.md` gehört dem jeweiligen Produkt. Der Agent wird über Root-`AGENTS.md` geführt, nicht über diese Anleitung.

## Schnellstart: neues Projekt aus der Vorlage

1. **Anlegen:** auf GitHub „Use this template“ oder den Inhalt der Vorlage ohne `.git` in einen leeren Ordner kopieren. Ohne Git-Repository schlägt der Agent beim Init `git init` vor.
2. **Frei erzählen (optional):** in `agentic-harness/project/brief.md` die Idee in eigenen Worten beschreiben, gern als Stichworte oder kopierte Nachrichten. Ablauf und Themen zum Erzählen stehen in der Root-`README.md`, Abschnitt „Projektstart mit dem Agentic Harness“.

   ```text
   brief.md: frei erzählen ──▶ Init: was ist klar, was fehlt, was muss geklärt werden? ──▶ Anforderungen, Tech-Stack, Projektdateien
   ```
3. **Auftrag geben:** den Ordner mit dem Coding-Agenten öffnen und in eigenen Worten sagen, was entstehen soll, z. B. „Eine Automatisierung, die meine E-Mails sortiert“ oder „Eine Website für einen Tischlereibetrieb“. Weil `harness/project.md` noch `Pending Project Init` enthält, startet der Agent das Init: Er fasst zusammen, was der Brief schon beantwortet, fragt gebündelt nur nach, was zur Umsetzung fehlt, und klärt danach Profil (z. B. Website) oder keines, Stack, Architektur und Tests.
4. **Freigeben:** Nach dem Init den ersten Schritt ausdrücklich beauftragen. Init allein ist keine Implementierungsfreigabe.

Erkenntnisse über den Harness sammelt jedes Projekt in `agentic-harness/harness-learnings.md`; wie erprobte Erkenntnisse zurück in die Vorlage kommen, steht unter „Harness weiterentwickeln“.

Tatsächlicher Arbeits- und Entscheidungsfluss

 ```text
   AGENTS.md → core.md + project.md
                 │          └→ bestätigte Ziele, Grenzen, aktive Prüfbefehle
                 │
                 ├─ Neues Produktprojekt: Init beauftragt oder vor erster
                 │  Produktumsetzung noch „Pending Project Init“?
                 │    └→ init.md
                 │         ├→ Richtung offen? erst billig erkunden (Erkundungsstufen E0–E3:
                 │         │  direkt · Ideenrunde · ein Prototyp · Varianten nur auf Auftrag)
                 │         ├→ Ziel, Grenzen und ersten Schritt klären
                 │         ├→ Architektur und Tech-Stack: 2–3 Optionen → Empfehlung
                 │         ├→ project.md + passende Projekt-Docs befüllen
                 │         ├→ ggf. echte Checks einrichten und ausführen
                 │         └→ zurück zu core.md und zum konkreten Auftrag
                 │            (Init allein ist keine Implementierungsfreigabe)
                 │
                 ↓
   [R1] ───→ AUFTRAG KLÄREN: Ziel, Umfang, Nicht-Ziele, Freigaben
                 │   (beide Fragen prüfen, beide können zutreffen)
                 ├─ Größere Änderung oder offenes Vorhaben?
                 │    └→ Idea als Akte: Offen → Beauftragt → (nach Gate) Umgesetzt → Archiv
                 │
                 ├─ Neues/geändertes Nutzerverhalten beauftragt?
                 │    └→ Bereichs-Spec(s) anlegen/ändern (lebender Soll-Stand):
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
                 │   reine Oberflächen-Iteration? → kurzer Weg: Auftrag + design.md
                 │   → Diff, Build/Tests, Nachweis im Zielmedium → Ergebnis
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
                 │                + berührte Projektdateien sauber?
                 │
                 ├─ JA → Ergebnis berichten; erledigte Teilaufgaben abhaken;
                 │        Spec „Implemented“, wenn alle ihre AK belegt sind;
                 │        Idea „Umgesetzt“ → ideas/archiv/, wenn ganz erledigt
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
                             └─ Entscheidung oder Nachweis weiter unmöglich,
                                oder dieselbe Ursache 2× gescheitert
                                  └→ STOPP: Blocker und offene Checks berichten

           Nach jeder möglichen Korrektur:
           betroffene Prüfungen wiederholen → gate.md erneut vollständig
           durchlaufen (requirements.md + implementation.md + Entscheidung).
 ```


**Welche Datei wann gelesen wird**, steht an genau einer Stelle: in der Routing-Tabelle von `AGENTS.md`; Rollen und Ladewege aller Dateien beschreibt `harness-map.md`.

Wie das Gate im Einzelnen arbeitet (welche Datei was liest und liefert, Rücksprungziele je Ursache), zeigt die Grafik in `harness/verification/gate.md`.
## Drei Ebenen

| Ebene | Dateien | Wandert in eine neue Vorlage? |
|---|---|---|
| **Universell** | `AGENTS.md` (oberer Teil), `agentic-harness/harness/` (Core, Init, Verifikation, Vorlagen), `agentic-harness/tools/` (Export-Skript), `document-contract.md`, `harness-map.md`, diese README, `ideas/I000-readme.md`, `specs/S000-readme.md`, `project/README.md`, der Abschnitt „Projektstart mit dem Agentic Harness“ der Root-`README.md` sowie Kopf und „Universeller Rahmen“ von `harness/project.md` und `docs/*.md` | ja, unverändert |
| **Profil** | `agentic-harness/profiles/*.md`, z. B. `website.md`: Teil A Pflichtregeln, Teil B wählbare Stil-Vorschläge (kein Standard), Teil C optionaler Baukasten; Zubehör eines Profils im gleichnamigen Ordner (z. B. `profiles/website/device-preview.html` und die Werkzeuge in `profiles/website/webtools/`) | ja; das neue Projekt wählt beim Init ein passendes Profil (oder keines) und hält Übernahmen und Abweichungen in der thematisch zuständigen Projektdatei fest (z. B. Gestaltung in `docs/design.md`, Prüfgrößen in `docs/testing.md`) |
| **Projekt** | Abschnitt „Projektspezifische Befüllung“ in `project.md` und `docs/*.md`, „Projektspezifische Ergänzungen“ in `AGENTS.md`, Ideas, Specs, `project/brief.md`, Learnings-Einträge, Produktteil der Root-`README.md`, Produktcode, Tests, Archiv | nein; wird zurückgesetzt oder weggelassen |

Neue Erkenntnisse wandern je nach Reichweite: für jedes Projekt → universelle Datei; für eine Projektart → Profil; nur für dieses Produkt → Projektdatei.

## Ausführbare Dateien im Harness

Neben den Markdown-Dateien enthält der Harness wenige Programme. Sie bleiben in jedem Projekt **unverändert**; ein Projekt passt sie nur über Einstellungen an. Ist ein Werkzeug für alle Projekte falsch oder lückenhaft, wird es nicht im Projekt geflickt, sondern als Learning festgehalten und in der nächsten Version verbessert.

**Regeln und Werkzeuge im Verification Loop.** Markdown-Dateien sind Regeln, die der Agent liest. Programme sind Werkzeuge, die er ausführt. Die Werkzeuge sind Teil des Verification Loop: Der Harness legt den Ablauf fest, die Werkzeuge liefern im Schritt „Prüfen“ die Messwerte.

```text
Regel (Profil, .md):  „Felder mindestens 16 px“
      │ Agent liest sie und baut
      ▼
   bauen ──▶ PRÜFEN ──▶ erfüllt? ──ja──▶ übergeben            Ablauf: harness/verification/
               ▲  │          │                                 (gate.md, implementation.md, fail.md)
               │  │         nein ──▶ korrigieren ──┐
               │  └─ Werkzeug misst (z. B. pruefen.mjs):       Messgeräte: Profil-Werkzeuge
               │     „/kontakt/ Feld 15 px ❌“                 (z. B. profiles/website/webtools/)
               └───────────────────────────────────┘
```

Der Ablauf ist universell und gilt für jedes Projekt. Die Werkzeuge hängen am Profil, weil jede Projektart anders gemessen wird; ohne Werkzeuge läuft die Schleife nach Augenmaß.

| Datei | Ebene | Aufgabe |
|---|---|---|
| `tools/export-harness.sh` | universell | exportiert die universellen Dateien und Profile in eine Vorlage oder ein leeres Projekt und prüft auf Projektreste |
| `profiles/website/webtools/konfig.mjs` | Profil Website | Standardwerte aller Webtools (Pfade, Build-Befehl, Port, Prüfbreiten); liest die Abweichungen aus `website.config.mjs` des Projekts |
| `…/webtools/browser.mjs` | Profil Website | startet Brave oder Chrome unsichtbar, steuert ihn und liefert den Build-Ordner aus; Grundlage aller Prüfungen und Browsertests |
| `…/webtools/pruefen.mjs` | Profil Website | misst die Pflichtregeln aus Teil A auf allen Seiten: Überlauf, Schriften, Skriptfehler, fehlende Dateien, Feldgrößen, Bedienelemente, Kontrast |
| `…/webtools/serve.mjs` | Profil Website | lokale Vorschau, baut bei Änderungen neu, eigene 404-Seite, Geräte-Vorschau unter `/_geraete/` |
| `…/webtools/vorschau-dauerhaft.sh` | Profil Website | macht die Vorschau zum macOS-Dienst (startet beim Anmelden und nach Abstürzen neu) |
| `…/webtools/device-preview.mjs` | Profil Website | öffnet die Geräte-Vorschau (`profiles/website/device-preview.html`) in Brave |
| `…/webtools/screens.mjs` | Profil Website | Screenshots aller Seiten vorher und nachher, für Umbauten ohne sichtbare Änderung |
| `…/webtools/style-snapshot.mjs` | Profil Website | Fingerabdruck der berechneten Styles je Element, Breite und Zustand, ebenfalls für Umbauten |
| `…/webtools/css.mjs`, `unused-css.mjs`, `css-audit.mjs` | Profil Website | CSS lesen, ungenutzte Selektoren finden und auf Wunsch entfernen |

Ausführlich mit Grafik und Aufrufen: `profiles/website/README.md`.

**Was ein Website-Projekt selbst anlegt** (projektspezifisch, beim Init oder mit der ersten Seite):

- `website.config.mjs`: nur die Abweichungen von den Standardwerten, z. B. Name, Port oder ruhende CSS-Dateien; passen alle Standardwerte, entfällt die Datei.
- einen Build, der die Website in den Ausgabeordner schreibt (Standard: `scripts/build.mjs` → `dist/`); ein anderer Befehl steht in `website.config.mjs`.
- eigene Erzeugungsskripte nach Profilregel, z. B. Favicons aus dem eigenen Zeichen.
- npm-Skripte, die die Webtools aufrufen (`dev`, `vorschau`, `pruefen`, `screens` …), und inhaltliche Tests; Browsertests importieren `browser.mjs` aus den Webtools.

**Universell heißt: offen bis zum Init.** Der Harness legt weder Projektart noch Stack, Architektur, Tests oder Profil fest. Bei jedem neuen Projekt werden Ziel, erster Ablauf und das dafür Nötige im Project Init neu besprochen. `AGENTS.md` führt dorthin, `harness/init.md` treibt die Klärung und schreibt das Bestätigte in die Projektabschnitte. Fehlende Festlegungen in der Vorlage sind deshalb gewollt.

**Ein weiteres Profil** (z. B. Automation, API) folgt dem Muster von `profiles/website.md`: Kopf mit „Gilt bei“ als Ladeauslöser, zusätzliche Init-Fragen, Teil A Pflichtregeln, Teil B wählbare Vorschläge, Teil C optionaler Baukasten. `AGENTS.md` lädt jedes gewählte Profil über eine allgemeine Zeile; im universellen Teil ist dafür nichts zu ergänzen außer dem Eintrag in `harness-map.md`.

## Harness weiterentwickeln

Die Vorlage enthält nur erprobte Änderungen. Neue Erkenntnisse durchlaufen im Projekt drei Stufen:

1. **Projektwissen** steht im Projektteil der zuständigen Datei, z. B. eine neue Codestruktur in `docs/architecture.md`.
2. **Kandidat:** Wirkt etwas über das Projekt hinaus, hält der Agent es in `harness-learnings.md` fest: Anlass, Ziel-Datei, Stand der Erprobung.
3. **Universell:** Erst auf ausdrücklichen Auftrag, möglichst nach Erprobung, wandert es in eine universelle Datei oder ein Profil.

So bleiben die universellen Dateien jederzeit freigabefähig. In `harness-learnings.md` stehen nur aktive Einträge (Offen, Lokal übernommen); jede Harness-Änderung bekommt dort sofort einen Eintrag mit Grund. Beim Release übernommene Einträge wandern nach `project/learnings-archiv.md` (Lebenszyklus in `harness-learnings.md`). Die Vorlage startet mit leerer Liste und ohne Archiv. Parallele Sitzungen ändern universelle Dateien nicht nebenbei; sie notieren Kandidaten.

**Release in die Vorlage** gesammelt, wenn erprobte Änderungen vorliegen, nicht nach jeder Sitzung:

1. Auftrag „Harness-Release vorbereiten“. Der Agent zeigt die Änderungen seit dem letzten Release, `git diff harness-vX.Y -- AGENTS.md README.md agentic-harness ':(exclude)agentic-harness/project'` (Projektteile darin ignorieren: konkrete Ideas und Specs, Projektabschnitte; die Leitdateien `ideas/I000-readme.md` und `specs/S000-readme.md` gehören dazu), und die offenen Kandidaten. Dabei auch die Ideas des Projekts durchsehen (`ideas/I000-readme.md`, „Durchsicht“).
2. **Learnings gegenprüfen:** Für jeden Eintrag „Lokal übernommen“ prüft der Agent, ob die Regel noch so in der genannten Zieldatei steht. Fehlt sie oder wurde sie verändert, zieht er sie nach oder setzt den Eintrag zurück auf „Offen“ und meldet das.
3. Du wählst aus; Ausgewähltes wird universell, der Rest bleibt Kandidat.
4. Export mit dem Skript in den Vorlagen-Klon (nächster Abschnitt, mit `VERSION=vX.Y`), Diff prüfen, committen.
5. Nach Freigabe pushen und beide Stände taggen: im Projekt `harness-vX.Y`, in der Vorlage `vX.Y`. Die exportierten Einträge wandern als „In Vorlage vX.Y“ aus `harness-learnings.md` nach `project/learnings-archiv.md`.

## Harness als Vorlage exportieren

Das Skript kopiert nur universelle Dateien und Profile, setzt die Projektteile zurück und prüft auf Reste. Es committet und pusht nichts:

```sh
# leeres oder neues Ziel: neues Projekt oder neue Vorlage
sh agentic-harness/tools/export-harness.sh /pfad/zum/leeren-ordner
# sauberer Git-Klon der Vorlage: Inhalt außer .git und .idea wird ersetzt
PRODUKTBEGRIFFE='produktname|domain|ort' sh agentic-harness/tools/export-harness.sh /pfad/zum/vorlagen-klon
```

Was das Skript tut:

1. Kopiert `AGENTS.md`, `harness/`, `docs/`, `profiles/`, `tools/`, diese README, Vertrag, Landkarte, Learnings sowie `ideas/I000-readme.md`, `specs/S000-readme.md` und `project/README.md`; legt `.gitignore` und eine Root-README aus Vorlagenkopf und dem universellen Abschnitt „Projektstart mit dem Agentic Harness“ an (mit `VERSION=vX.Y` samt Versionsnummer in der Überschrift).
2. Ersetzt in `harness/project.md` und `docs/*.md` alles unter „Projektspezifische Befüllung“ durch „Noch offen (Project Init).“ und setzt die Status-Zeilen zurück (`Pending Project Init` bzw. „Noch offen (Project Init).“).
3. Leert in `AGENTS.md` die „Projektspezifischen Ergänzungen“ und in `harness-learnings.md` alles nach dem Abschnitt „Zweck und Regeln“.
4. Bricht ohne Änderung am Ziel ab, wenn es E-Mail-Adressen, die übergebenen Produktbegriffe oder Verweise auf fehlende `agentic-harness/…`-Dateien findet (außer dem optionalen `project/brief.md`).

Nicht übernommen werden: Produktcode (`src/`, `scripts/`, `tests/`), `archiv/`, `dist/`, konkrete Ideas und Specs, `project/brief.md` und `project/learnings-archiv.md`, die Einträge in `harness-learnings.md`, `.git/` und IDE-Dateien.

Ein neu exportierter Ordner startet wie im Schnellstart: mit dem Agenten öffnen und den Auftrag geben.
