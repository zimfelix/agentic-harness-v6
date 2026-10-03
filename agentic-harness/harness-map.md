# Harness-Landkarte – Dateirollen und Ladewege

> - **Typ:** Index
> - **Zuständigkeit:** Eigentümer der Themen, direkte Ladewege und die Export-Zuordnung (universell oder projektspezifisch) sichtbar machen.
> - **Gilt bei:** Einstieg in einen unbekannten Harness, Project Init, Export als Vorlage oder Änderung von Dateirollen und Pfaden.
> - **Ladebeziehungen:** Einstieg und Routing: `AGENTS.md`. Markdown-Format: `agentic-harness/document-contract.md`.
> - **Nicht zuständig:** Projektentscheidungen treffen oder Regeln der verlinkten Dateien wiederholen.

## Pfadbasis

Die Tabellen zeigen die tatsächlichen Pfade **relativ zum Ordner `agentic-harness/`**. Dateien im Repo-Root sind mit „(Root)“ markiert. Maßgeblich für das Routing ist `AGENTS.md`.

## Universelle Dateien

Diese Dateien wandern unverändert in eine neue Vorlage.

| Pfad | Eine Verantwortung | Direkter Ladeweg |
|---|---|---|
| `AGENTS.md` (Root, oberer Teil) | Einstieg und Aufgaben-Routing | Immer → `harness/core.md` und `harness/project.md`; weitere Ziele nur nach Auslöser. Der Abschnitt „Projektspezifische Ergänzungen“ gehört dem Projekt. |
| `harness/core.md` | Entscheidungen und Rücksprünge von Auftrag bis Übergabe, Arbeitsbaum und Parallelarbeit | Mit `harness/project.md` über `AGENTS.md`; bei Init → `harness/init.md`; je nach Auftrag Ideas/Specs und Docs; vor Abschluss → `harness/verification/gate.md`. |
| `harness/init.md` | Leeres Projekt für ersten Schritt klären: bei offener Richtung erst billig erkunden (Erkundungsstufen E0–E3); dann Projektart, Stack, Architektur, Tests und Profil (oder keines) mit dem Auftraggeber entscheiden; Zusatzblock bei sichtbarer Oberfläche | Bei Init → `harness-map.md` und `document-contract.md`; danach Projektdateien befüllen. |
| `harness-map.md` | Dateirollen, Ladewege, Export-Zuordnung | Bei Orientierung, Export oder Änderungen der Dokumentstruktur; keine Projektfakten. |
| `document-contract.md` | Format, aktueller Stand statt Verlauf, Richtgrößen, Trennung für den Export | Beim Anlegen, Befüllen oder Verdichten von Projekt-Docs und bei Pfadänderungen. |
| `README.md` | Anleitung zum Harness für Menschen: Schnellstart, Aufbau, Weiterentwicklung und Release, Export | Bei Export- und Release-Aufträgen über `AGENTS.md`; sonst kein Agenten-Ladeweg. |
| `tools/export-harness.sh` | Universelle Dateien exportieren, Projektteile zurücksetzen, auf Reste prüfen; in leeres Ziel oder sauberen Vorlagen-Klon | Nur bei Export oder Release, aufgerufen nach `README.md`; committet und pusht nichts. |
| `ideas/I000-readme.md`, `specs/S000-readme.md` | Ideas als Akte größerer Änderungen (Lebenszyklus, Archiv, Durchsicht) bzw. Bereichs-Specs als lebender Soll-Stand | Bedingt über `AGENTS.md`; betroffene Artefakte lesen, Templates nur bei Neuanlage. |
| `harness/templates/idea.md`, `harness/templates/spec.md` | Form der jeweiligen Artefakte | Nur beim Anlegen von Ideas bzw. Specs. |
| `project/README.md` | Universelle Anleitung zum Projektordner (Brief, Learnings-Archiv); verweist für Ablauf und Themen auf die Root-README | Beim Anlegen eines Briefs und bei Project Init über `harness/init.md`; wird exportiert, `brief.md` und weitere Dateien daneben nicht. |
| `harness/verification/gate.md` | Soll und belegtes Ist zur Abschlussentscheidung verbinden; berührte Specs und Projektdateien auf aktuellen Stand prüfen; kurzer Weg für Oberflächen-Iterationen | Nach Änderung → `harness/verification/requirements.md` und `harness/verification/implementation.md` (beim kurzen Weg `docs/design.md`); für die Prüfung der Projektdateien → `document-contract.md`, bei Specs `specs/S000-readme.md`; bei Lücke → `harness/verification/fail.md`. |
| `harness/verification/requirements.md` | Verbindliches Soll aus Auftrag, Spec, Gestaltungsregeln und Projektgrenzen bestimmen | Vom Gate geladen; `harness/project.md`, betroffene Specs, bei Strukturänderungen `docs/architecture.md`, bei Oberflächen `docs/design.md`. |
| `harness/verification/implementation.md` | Tatsächliche Änderung und Nachweise zum Soll prüfen, bei Oberflächen im Zielmedium | Vom Gate geladen; Prüfungen aus `harness/project.md`, Testpraxis aus `docs/testing.md`, bei Oberflächen `docs/design.md`. |
| `harness/verification/fail.md` | Lücke eingrenzen, korrigieren oder blockiert melden | Nur bei Gate-Lücke; nach Korrektur betroffene Nachweise und Gate wiederholen. |

## Profile (optional je Projektart)

Werden mitexportiert; ein Projekt nutzt höchstens die zu ihm passenden.

| Pfad | Eine Verantwortung | Direkter Ladeweg |
|---|---|---|
| `profiles/website.md` | Für Websites: Teil A Pflichtregeln (Konsistenz, Bedienbarkeit, Rechte, Nachweis), Teil B wählbare Stil-Vorschläge (kein Standard), Teil C optionaler Baukasten mit Branchenhinweisen, vorgeschlagener Dateistruktur und Veröffentlichungsweg | Nur wenn das Projektprofil „Profil: Website“ nennt oder ein Auftrag es ausdrücklich verlangt; über die allgemeine Profil-Zeile in `AGENTS.md`, zu den Anlässen unter „Gilt bei“ im Profilkopf (Init, sichtbare Änderungen, vor Meilensteinen und Veröffentlichung). Weitere Profile (z. B. Automation, API) nach demselben Muster; jedes nennt seine Anlässe selbst. |
| `profiles/website/device-preview.html` | Vorlage der Geräte-Vorschau: Website gleichzeitig in mehreren Bildschirmbreiten | Kein Agenten-Ladeweg; Einrichtung nach `profiles/website.md` §6. Der Vorschau-Server des Projekts liefert die Datei unverändert aus, statt sie zu kopieren. |
| `profiles/website/README.md` | Übersicht des Profil-Zubehörs: welche Datei welche Aufgabe hat, wie ein Projekt sie nutzt | Für Menschen und beim Ändern des Zubehörs; bei jeder Ergänzung im Profilordner mit anpassen (`document-contract.md`). |
| `profiles/website/inspiration/` | Sammlung gelungener Website-Entwürfe und Abschnitte: `README.md` als Index nach Stärken (Schrift, Farbe, Anordnung …), je Eintrag `steckbrief.md` (was gut ist, was übertragbar ist) und Bilder | Beim Erkunden von Website-Entwürfen über `harness/init.md` Abschnitt 0 und bei Aufträgen mit Bezug auf einen Eintrag; erst Index, dann nur passende Steckbriefe; Ergänzen auf Auftrag „in die Sammlung aufnehmen“. Maßstab, keine Vorlage; wandert mit dem Profil in die Vorlage. |
| `profiles/website/webtools/` | Prüf- und Vorschau-Werkzeuge für Websites (Browser steuern, Pflichtregeln messen, Vorschau mit Neubau, Dauer-Dienst, Screenshots, Style-Vergleich, CSS-Audit); Projekteinstellungen über `website.config.mjs` im Projekt | Kein Agenten-Ladeweg; über npm-Skripte und Tests des Projekts aufgerufen; Einrichtung nach Profil §6 und Teil C §9. |

## Geteilte Dateien: universeller Rahmen + Projektbefüllung

Kopf (außer der Status-Zeile) und „Universeller Rahmen“ sind universell. Status-Zeile und Abschnitt „Projektspezifische Befüllung“ gehören dem Projekt (bei der Root-README: Produktteil oben projektspezifisch, Abschnitt „Projektstart mit dem Agentic Harness“ universell; bei den Learnings: „Zweck und Regeln“ universell, Einträge projektspezifisch): Beim Export wird die Befüllung zu „Noch offen (Project Init).“, der Status von `harness/project.md` zu `Pending Project Init`, der Status der Docs zu „Noch offen (Project Init).“.

| Pfad | Eine Verantwortung | Direkter Ladeweg |
|---|---|---|
| `harness/project.md` | Bestätigtes Ziel, Grenzen, Freigaben, Befehle, Prüfstatus, offene Entscheidungen | Immer mit Core; Architekturdetails → `docs/architecture.md`, Gestaltung → `docs/design.md`, Testpraxis → `docs/testing.md`. |
| `docs/architecture.md` | Bausteine, Schnittstellen, Datenfluss, Betrieb; Varianten und Archiv | Bei Architektur/Struktur, Betrieb, neuen Seiten/Routen/Einstiegen, Konzeptvergleichen und Archivieren; Codekonventionen → `docs/code.md`. |
| `docs/code.md` | Geltender Stack, Abhängigkeiten und Codekonventionen | Bei Codearbeit; Modulgrenzen → `docs/architecture.md`; Gestaltungswerte → `docs/design.md`. |
| `docs/design.md` | Gestaltungsregeln: Farbrollen, Schrift, Größenskala, Bausteine, Zustände, was im Zielmedium nachzuweisen ist (nur bei sichtbarer Oberfläche) | Bei sichtbaren Änderungen, neuen Seiten oder Abschnitten und beim kurzen Gate-Weg. |
| `docs/testing.md` | Auswahl von Testebenen/-arten, Ausführungsanlässen, Werkzeugen und Teststruktur; bei Oberflächen Prüfgrößen und Methoden | Bei Init und Testarbeit aus Ziel, Architektur und Stack; konkrete Befehle → `harness/project.md`. |
| `harness-learnings.md` | Agentic-Coding-Learnings: Harness-Schwächen, wiederkehrende Agentenfehler und dokumentierte Harness-Änderungen, nur aktive Einträge; Regeln und Lebenszyklus im universellen Abschnitt „Zweck und Regeln“ | Über `AGENTS.md` bei einer Harness-Beobachtung, einem wiederholten Fehler und vor jeder Harness-Änderung. Beim Export Einträge leeren. |
| `README.md` (Root) | Oben Produktüberblick, Einrichtung und Start für Menschen (projektspezifisch); unten der universelle Abschnitt „Projektstart mit dem Agentic Harness“ mit Ablauf „Erzählen → Konkretisieren“ und den Themen für den Brief | Beim Init den Produktteil oben befüllen, den universellen Abschnitt unverändert lassen; beim Export Vorlagenkopf + universeller Abschnitt. |

## Nur projektspezifisch

Diese Dateien und Ordner werden **nicht** in eine neue Vorlage übernommen.

| Pfad | Eine Verantwortung | Direkter Ladeweg |
|---|---|---|
| `project/brief.md` (optional) | Ausgangsbeschreibung eines Produkts für Project Init | Bei Project Init über `AGENTS.md`, falls vorhanden; bestätigte Fakten, Annahmen und offene Entscheidungen getrennt halten. |
| `project/learnings-archiv.md` | Erledigte Learnings (in eine Vorlage übernommen) als Spur, warum Regeln existieren | Beim Release beschrieben; vor dem Zurückdrehen einer Regel nachsehen. Projektspezifisch, wird nie exportiert. |
| `project/<thema>.md` (bei Bedarf) | Weitere projektspezifische Docs, z. B. Datenschutz oder Betrieb, wenn ein Thema in keine bestehende Doc passt | Über den Auslöser unter „Projektspezifische Ergänzungen“ in `AGENTS.md`; Kriterium und Format in `document-contract.md`. Je angelegter Doc eine eigene Zeile darunter. Wird nie exportiert. |
| `ideas/Innn-*.md`, `specs/Snnn-*.md` | Akten konkreter Änderungen bzw. Soll-Stand je Bereich; Erledigtes unter `ideas/archiv/` und `specs/archiv/` | Nur betroffene Artefakte über `ideas/I000-readme.md` bzw. `specs/S000-readme.md` lesen. |
| Archivordner (z. B. `archiv/`, Root) | Verworfene oder nicht mehr verlinkte Teile außerhalb von Build, Tests und Ladewegen | Wird nicht geladen; nur auf ausdrücklichen Auftrag öffnen oder ändern. Name steht im Projektprofil. |
| Produktcode, Tests, Assets (Root) | Das Produkt selbst | Über die Projekt-Docs. |

## Bei neuen oder verschobenen Dateien

Vor dem Ändern eingehende Verweise auf Pfad und Dateinamen suchen. Rollen und direkte Beziehungen hier aktualisieren; betroffene Einstiege, Links und Dokumentköpfe im selben Schritt abgleichen. Das gilt auch für neue Ladeauslöser ohne Dateiumzug. Danach reale Ziele prüfen. Geplante Pfade nicht als vorhanden ausgeben.
