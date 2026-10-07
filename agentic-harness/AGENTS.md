# Agentic Harness

Immer zuerst `harness/core.md` und `harness/project.md` lesen. Alle Pfade gelten ab diesem Projekt-Root. Harness-Arbeit löst keinen Produkt-Init aus.

| Auslöser | Zusätzlich lesen |
|---|---|
| Init beauftragt oder Produktarbeit bei `Pending Project Init` | `harness/init.md`; vorhandene Ausgangsbeschreibung, falls vom Auftraggeber angegeben |
| Neues/geändertes Nutzerverhalten | `specs/S000-readme.md` und betroffene Specs |
| Größeres oder unklareres Vorhaben | `ideas/I000-readme.md` und betroffene Idea |
| Architektur, Datenmodell, Schnittstellen, Betrieb, Dateistruktur | `docs/architecture.md` |
| Code oder Refactoring | `docs/code.md` |
| Sichtbare Änderung | `docs/design.md` |
| Tests planen, ändern oder ausführen | `docs/testing.md` |
| Fachlogik, dauerhafte Geschäfts-/Personendaten, Seiteneffekte | `profiles/business-software/profile.md`, wenn im Projekt gewählt; bei neuem Bedarf zuerst einordnen |
| Website-Init, sichtbare Website-Änderung, Markup/CSS-Umbau oder Livegang | `profiles/website/profile.md`, wenn gewählt oder ausdrücklich beauftragt |
| Markdown anlegen/ändern oder Dateirollen/Pfade ändern | `document-contract.md` |
| Harness-Schwäche oder Harness/Profil/Tool ändern | `harness-learnings.md` vor der Änderung |
| Abschluss einer Änderung | `harness/verification.md` |
| Export oder Release | `harness/README.md` |

Treffen mehrere Auslöser zu, lies die betroffenen Quellen, nicht alle Dateien auf Vorrat. Templates nur beim Anlegen eines Artefakts. Zusätzliche gewählte Profile und Projekt-Docs werden unten mit konkretem Auslöser verlinkt.

## Projektspezifische Ergänzungen
