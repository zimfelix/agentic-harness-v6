# Implementation – Änderung und Nachweise prüfen

> - **Typ:** Prozess
> - **Zuständigkeit:** Das tatsächlich geänderte Verhalten und ausgeführte Prüfungen gegen das ermittelte Soll belegen.
> - **Gilt bei:** Dem vollen Gate-Weg in `harness/verification/gate.md`; beim kurzen Weg gelten dessen verkürzte Nachweisregeln.
> - **Ladebeziehungen:** Vom Gate geladen; Soll aus `harness/verification/requirements.md`, aktive Befehle und Grenzen aus `harness/project.md`. Bei Codearbeit `docs/code.md`, bei Produkt- oder Teständerungen `docs/testing.md`, bei Strukturänderungen `docs/architecture.md`, bei sichtbaren Oberflächenänderungen `docs/design.md` lesen. Ergebnis ans Gate.
> - **Nicht zuständig:** Teststrategie oder Projektbefehle festlegen; Abschluss und Spec-Status entscheidet das Gate.

## Ist und Belege ermitteln

1. Prüfe die tatsächliche Änderung (Code, Tests, Konfiguration, Doku) gegen Auftrag und Soll aus `harness/verification/requirements.md`: Was wurde umgesetzt, ausgelassen oder zusätzlich geändert? Bei Strukturänderungen auch den tatsächlichen Baum und betroffene Abhängigkeiten prüfen. Bei Codeänderungen die Einordnung prüfen: Sind Kopien bestehender Bausteine, zweite Vorkommen ohne gemeinsamen Baustein oder Werte außerhalb ihrer zentralen Stelle entstanden? Solche Funde vor dem Gate nachziehen oder als technische Schuld in `docs/code.md` benennen (`harness/core.md`, „Struktur mitziehen“).
2. Bei Produkt- oder Teständerungen: Wähle aus `docs/testing.md` die für die betroffenen Risiken und Kriterien vorgesehenen Ebenen, Arten, Ausführungsanlässe und Testorte. Führe die dafür **tatsächlich eingerichteten** Befehle aus `harness/project.md` gemäß Anlass und spätestens vor der Gate-Entscheidung aus; fehlende Checks bleiben offen. Prüfe den Ablauf und relevante Fehlerfälle über die geeignete Grenze; schütze echte Daten.
3. Ordne jedem betroffenen AK oder sonstigen Prüfpunkt einen Test oder eine begründete manuelle Prüfung zu, die den aktuellen Änderungsstand tatsächlich geprüft hat; halte Ergebnis und Nachweisgrenzen fest. Bei reiner Doku- oder Prozesspflege prüfe insbesondere geänderte Verweise und Widersprüche. Ein Build, eine leere Suite oder ein geplanter, aber nicht eingerichteter Befehl belegt Nutzerverhalten nicht.
4. Bei sichtbaren Oberflächen belege das **gerenderte** Ergebnis im Zielmedium (Browser, Emulator, Gerät, Terminal): mit der zum Prüfziel passenden Methode: technische Eigenschaften messen (z. B. geladene Schrift, Position, Überlauf), optische Wirkung per Screenshot beurteilen. Die verbindlichen Prüfgrößen stehen im Projektteil von `docs/testing.md`. Ein Vergleich von Quelltext (z. B. HTML- oder CSS-Strings) belegt kein Aussehen. Nicht gemessene Breiten oder Zustände bleiben als offen gekennzeichnet.

**Ergebnis an das Gate:** Beobachtetes Ist, ausgeführte Prüfungen mit Ergebnis sowie nicht ausgeführte oder fehlende Nachweise. Kennzeichne fehlende, leere oder nicht ausführbare Checks als **nicht verifiziert**, nicht als `PASS`. Eine positive Abschlussentscheidung trifft nur `harness/verification/gate.md`.
