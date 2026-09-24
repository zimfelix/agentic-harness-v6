# Harness-Landkarte – Zielbild

> - **Typ:** Designübersicht
> - **Status:** Entwurf; beschreibt noch nicht den aktiven V3-Dateibaum.
> - **Zuständigkeit:** Geplante Dateirollen und direkte Ladewege vor der Neuordnung festlegen.
> - **Gilt bei:** Entwurf, Verschiebung oder Aufteilung von Harness-Dateien.
> - **Ladebeziehungen:** Schreibformat: `agentic-harness/document-contract.md`. Vor der Umsetzung aktuellen Baum und bestehende Projektanweisungen prüfen.
> - **Nicht zuständig:** Inhalte der Einzeldateien oder Laufzeitregeln für Produktcode.

## Grenze dieses Entwurfs

`projekt/` im Bild bezeichnet den **Root eines Zielprojekts**. Alle Pfade unten sind relativ dazu und derzeit **geplant**, nicht automatisch schon vorhanden. Im aktuellen V3-Repo liegen Harness-Dateien noch unter `agentic-harness/`. Diese Landkarte und der Dokumentenvertrag sind Entwurfsdateien, keine geplanten Laufzeitdateien im Bild. Eine Migration ist nicht Teil dieses Schritts.

Für diesen Entwurf gibt es **keinen Installer-Schritt**. `scripts/install.py` und `tests/test_install.py` aus dem Bild sind nicht Teil des folgenden Ladeflusses. `assets/`, `src/` und Produkttests enthalten keine Agentenregeln.

## Einstieg und universeller Ablauf

| Geplanter Pfad | Eigene Verantwortung | Direkter Ladeweg |
|---|---|---|
| `AGENTS.md` | Einstieg; ordnet Aufgabentypen Dateien zu | Immer → `harness/core.md` und `harness/project.md`. Bedingte Ziele stehen in den Zeilen unten. |
| `harness/core.md` | Universelle Schritte von Auftrag bis Übergabe | Nach Einstieg → Projektgrenzen beachten; bei ausstehendem Init → `harness/init.md`; vor Abschluss → `harness/verification/gate.md`. |
| `harness/project.md` | Bestätigte Projektgrenzen, Befehle und Gate-Status | Mit Core lesen. Bei Architekturdetails → `docs/architecture.md`; bei Testregeln → `docs/testing.md`. |
| `harness/init.md` | Zielprojekt einmalig klären und Profil füllen | Nur bei offenem Project Init → `harness/project.md` und betroffene Projekt-Docs. |

## Projektwissen und Artefakte

| Geplanter Pfad | Eigene Verantwortung | Direkter Ladeweg |
|---|---|---|
| `docs/architecture.md` | Produktbausteine, Datenfluss und Abhängigkeitsrichtung | Bei Architektur/Struktur. Bei Codekonventionen → `docs/code.md`; bei Teststruktur → `docs/testing.md`. |
| `docs/code.md` | Code-, Import- und Packaging-Konventionen | Bei Codearbeit. Bei Modulgrenzen → `docs/architecture.md`. |
| `docs/testing.md` | Teststrategie und Testkonventionen | Bei Testarbeit. Für ausführbare Befehle → `harness/project.md`. |
| `harness/templates/idea.md` | Format einer offenen Idea | Beim Anlegen einer Idea → `ideas/`. Keine Implementierungsfreigabe. |
| `harness/templates/spec.md` | Format beauftragten Soll-Verhaltens | Beim Anlegen einer Spec → `specs/`. Keine Produktarchitektur. |
| `ideas/`, `specs/` | Konkrete offene Ideen bzw. beauftragte Anforderungen | Nur betroffene Artefakte lesen; kein pauschales Laden aller Dateien. |

## Abschluss

| Geplanter Pfad | Eigene Verantwortung | Direkter Ladeweg |
|---|---|---|
| `harness/verification/gate.md` | Abschlussentscheidung | Nach Umsetzung → `harness/verification/requirements.md` und `harness/verification/implementation.md`; bei Fehlschlag → `harness/verification/fail.md`. |
| `harness/verification/requirements.md` | Auftrag und Kriterien gegen Soll prüfen | Vom Gate geladen; betroffene Spec und `harness/project.md` nutzen. |
| `harness/verification/implementation.md` | Umsetzung und Nachweise prüfen | Vom Gate geladen; Projektbefehle aus `harness/project.md` nutzen. |
| `harness/verification/fail.md` | Fehlschlag oder fehlenden Nachweis behandeln | Nur bei fehlgeschlagener oder unvollständiger Prüfung. |

## Wenn Dateien entstehen oder Pfade sich ändern

1. Gib neuen Dateien eine eigene Verantwortung und einen Aufgabenauslöser.
2. Trage nur direkte Ladebeziehungen ein: **vorher**, **wenn …**, **danach**.
3. Bei Umbenennung, Verschieben oder Löschen: Suche zuerst alle eingehenden Verweise im Repo. Passe Landkarte und betroffene Dateien im selben Schritt an.
4. Prüfe danach reale Ziele und die Erreichbarkeit vom Einstieg aus. Geplante Pfade sind kein Nachweis für vorhandene Dateien.

Offen vor der Neuordnung: Welche der heutigen `README.md`-Indizes bleiben reine Orientierung, und welche Ladebedingungen wandern in den Projekt-Einstieg? Diese Entscheidung nicht durch doppelte Trigger vorwegnehmen.
