# Testing – Auswahl und Praxis der Produktprüfungen

> - **Typ:** Projektdoku
> - **Status:** Noch offen (Project Init).
> - **Zuständigkeit:** Universelle Auswahlhilfe für Tests bieten und die begründete Teststrategie des Projekts festhalten.
> - **Gilt bei:** Project Init sowie Testplanung, Teständerung und Testausführung.
> - **Ladebeziehungen:** Zuerst `agentic-harness/harness/project.md` für Ziel, Risiken und eingerichtete Befehle lesen. Für Bausteine und Grenzen bei Bedarf `agentic-harness/docs/architecture.md`, für Stack und Werkzeugwahl `agentic-harness/docs/code.md`, für Gestaltungsregeln `agentic-harness/docs/design.md` (Prüfgrößen, Methoden und Werkzeuge stehen hier), bei beauftragtem Verhalten die betroffene Spec unter `agentic-harness/specs/`. Zum Abschluss `agentic-harness/harness/verification/gate.md`.
> - **Nicht zuständig:** Produkt-Stack oder Akzeptanzkriterien festlegen, Befehle und Ergebnisse duplizieren oder über ein bestandenes Gate entscheiden.

## Universeller Rahmen

**Testebene** bezeichnet die geprüfte Grenze, **Testart** die geprüfte Eigenschaft oder Methode. Beides kombinieren: Ein Integrationstest kann z. B. einen Berechtigungsfehler prüfen. Projektgröße allein bestimmt keine Pflichtliste; Nutzerablauf, Fehlerrisiko, Daten und Architektur des **ersten Meilensteins** sind maßgeblich. Nicht benötigte Ebenen vertagen statt leere Testsuiten anzulegen.

### Auswahlgrundlage

1. Aus `agentic-harness/harness/project.md` Ziel, Betrieb, Daten, Rechte und Risiken entnehmen; aus betroffenen Specs die Akzeptanzkriterien. Ohne Spec den beauftragten Umfang prüfen.
2. Aus `agentic-harness/docs/architecture.md` die entschiedenen Bausteine und Schnittstellen ableiten; aus `agentic-harness/docs/code.md` Sprache, Laufzeit, Abhängigkeiten und Entwicklungsumgebung. Nicht bestätigte Entscheidungen bleiben offen.
3. Für wichtige Abläufe und relevante Fehlerfälle die kleinste aussagekräftige Kombination aus Ebenen und Arten wählen. Für den beauftragten Ablauf einen Nachweis an einer geeigneten beobachtbaren Grenze vorsehen; isolierte Tests allein belegen kein Zusammenspiel. Werkzeug, Aufwand und Nachweisgrenze begründen.

### Testebenen – wo wird geprüft?

| Ebene | Sinnvoll, wenn … | Belegt nicht allein … |
|---|---|---|
| **Unit** | Verzweigungen, Berechnungen oder Regeln isoliert prüfbar sind. | Zusammenarbeit mit Datenbank, Netzwerk oder UI. |
| **Komponente/Modul** | Ein Baustein über seine öffentliche Schnittstelle samt internem Verhalten geprüft werden soll. | Korrekte Integration mit realen Nachbarn. |
| **Integration** | Persistenz, externe Dienste oder das Zusammenspiel mehrerer Bausteine relevant sind. | Den vollständigen Nutzerablauf. |
| **Schnittstelle/Vertrag** | Zwei Seiten einer API, eines Datenformats oder eines Ereignisses kompatibel bleiben müssen. | Die interne Richtigkeit beider Seiten oder den Gesamtablauf. |
| **System/End-to-End** | Der erste Ablauf über die tatsächlich genutzten Grenzen hinweg funktionieren muss (z. B. CLI, API oder UI). | Alle seltenen Fehlerfälle oder nicht beobachtete Eigenschaften. |

Ebenen sind Auswahlmöglichkeiten, keine Ordnerpflicht. Ein kleines Projekt kann wenige, aber aussagekräftige Tests auf mehreren Grenzen brauchen; ein größeres Projekt trennt Suiten nur, wenn Organisation und Laufzeit es rechtfertigen.

### Testarten und Prüfperspektiven – was wird geprüft?

| Art | Auslöser / Leitfrage |
|---|---|
| **Funktional und Grenzfälle** | Erfüllt der Ablauf sein Soll auch bei ungültigen, leeren oder extremen Eingaben? |
| **Regression und Smoke** | Bleibt betroffenes Verhalten nach Änderungen erhalten? Startet der wichtigste Ablauf überhaupt? Ein Smoke-Check ersetzt keine tieferen Nachweise. |
| **Berechtigung und Sicherheit** | Können Rollen nur Erlaubtes tun; sind Eingaben, Secrets und sensible Daten geschützt? Nur relevante Bedrohungen prüfen. |
| **Datenintegrität und Zustand** | Bleiben Daten bei Speichern, Wiederholen, Abbruch und Fehler konsistent? Nur bei zustandsbehaftetem Verhalten. |
| **Ausfall, Wiederanlauf und Parallelität** | Was passiert bei Timeouts, Teilausfällen, Wiederholung oder konkurrierenden Zugriffen? Nur bei entsprechendem Risiko. |
| **Leistung und Kapazität** | Gibt es eine begründete Latenz-, Last- oder Ressourcenanforderung? Keine pauschalen Lasttests. |
| **Barrierefreiheit und Nutzbarkeit** | Ist eine relevante Oberfläche für die vorgesehenen Nutzer bedienbar? Automatische Checks ggf. durch menschliche Prüfung ergänzen. |
| **Kompatibilität** | Müssen ausdrücklich mehrere Umgebungen, Plattformen oder Versionen unterstützt werden? |
| **Eigenschaftsbasiert/Fuzzing** | Gibt es komplexe Invarianten oder breite Eingaberäume, die Beispieltests schlecht abdecken? |
| **Gerendertes Verhalten (Navigation, Scrollen, Layout)** | Hängt die Korrektheit von gerendertem Verhalten ab, z. B. Ankersprünge unter angehefteten Headern, Menüs, Umbrüche oder Bildschirmgrößen? Solches Verhalten ist aus Quelltext nicht ableitbar: im Zielmedium (Browser, Emulator, Terminal) messen (Position, Sichtbarkeit), nicht nur Markup prüfen, und die Nutzer nicht damit testen lassen. |
| **Aussehen und Gestaltungskonsistenz** | Gibt es verbindliche Gestaltungsregeln (`agentic-harness/docs/design.md`), die über Seiten hinweg gelten müssen, z. B. geladene Schrift, Größenskala, identische wiederkehrende Rahmen, kein Überlauf? Im Zielmedium messen oder per Screenshot vergleichen, nicht über Quelltext. |
| **Fachliche Akzeptanz/Exploration** | Muss ein Mensch den Nutzerablauf beurteilen oder einen noch unklaren Fehler erkunden? Schritte und beobachtetes Ergebnis festhalten; manuell ist eine Methode, keine eigene Testebene. |

Lint, Typprüfung und Build sind ergänzende Qualitätschecks, aber allein kein Nachweis für Nutzerverhalten. Coverage-Zahlen zeigen geprüften Code, nicht automatisch erfüllte Akzeptanzkriterien.

### Werkzeuge, Struktur und Isolation auswählen

Werkzeuge anhand des **gewählten** Stacks, der zu prüfenden Grenze und verfügbarer Versionen auswählen; es gibt keine allgemeine Testsprache oder ein verpflichtendes Framework. Erst nach Prüfung und Einrichtung als aktiv bezeichnen. Tests können nach Verhalten, Baustein oder Ebene organisiert werden; keine feste `tests/`- oder `src/`-Struktur voraussetzen. Testdaten, Fixtures und Ersatzobjekte so wählen, dass Tests unabhängig und reproduzierbar bleiben; reale Integrationen dort nutzen, wo nur sie das Risiko belegen. Keine Produktdaten oder Secrets in Testfixtures übernehmen.

**Quelltextvergleiche sparsam einsetzen:** Exakte Quelltext-Strings (z. B. HTML, CSS, generierte Ausgaben) in Tests sind zerbrechlich (jede Stiländerung bricht sie) und blind für echte Fehler (eine nicht geladene Schrift fällt nicht auf). Nutze sie nur für harte Inhaltsgrenzen, etwa verbotene Versprechen, Pflichtkennzeichnungen oder das Fehlen von Formularversand. Aussehen und Layout prüfen gemessene Eigenschaften im Zielmedium.

**Werkzeuge einmal einrichten:** Mess-, Screenshot- oder Audit-Skripte, die mehr als einmal gebraucht werden, gehören ins Projekt (mit Befehl in `agentic-harness/harness/project.md`), nicht in eine temporäre Sitzung. Eine Gegenprobe gegen einen absichtlich kaputten Stand zeigt, dass ein neuer Test im Zielmedium wirklich prüft. Bei sichtbarer Oberfläche legt der Projektteil dieser Datei Prüfgrößen (z. B. Bildschirmbreiten), Methoden und Werkzeug fest; `agentic-harness/docs/design.md` hält nur die zu prüfenden Regeln.

## Projektspezifische Befüllung

Noch offen (Project Init).
