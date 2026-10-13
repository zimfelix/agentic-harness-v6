# Architektur

**Zuständigkeit:** Beschlossene Bausteine, Fachmodell, Dateistruktur, Datenfluss und Betrieb. Lesen bei Architektur-, Datenmodell-, Schnittstellen-, Betriebs- oder Strukturänderungen.

## Universeller Rahmen

Vor erstem Produktcode Struktur festlegen: Source, Tests, Konfiguration/Inhalte, Scripts, Assets, ggf. Tokens. Ist, Ziel und offene Optionen unterscheiden. Entscheidungen knapp begründen; keine Abstraktionen auf Vorrat. Fachregeln nur bei Bedarf vom Infrastrukturcode trennen (konkrete Pflichten im gewählten Business-Software-Profil).

Betrieb: Auslöser/Zeitplan, Umgebungen, Secrets-Ort (nie Werte), Protokolle, externe Seiteneffekte und Schutzmaßnahmen. Varianten bleiben intern und getrennt vom Produkt; nach Auswahl löschen/archivieren. Archiv im Projektprofil benennen, nicht laden/bauen/testen. Nur ausdrücklich vorgesehene Einstiege ausliefern.

Werte gehören in Konfiguration/Tokens; die Architektur beschreibt Zuständigkeiten, keine duplizierten Implementierungsdetails.

## Projektspezifische Befüllung

### Structure

| Path | Responsibility |
|---|---|
| `planner` | Executable entrypoint; puts `src/` on the path, calls `planner.cli.main` |
| `src/planner/model.py` | Glossary types (`Project`, `Task`, `Plan`), input parsing, derived task state, `validate_plan` invariants |
| `src/planner/operations.py` | Domain mutations on a `Plan` (add/edit/done/reopen/delete/dependencies) |
| `src/planner/planning.py` | Read-side logic: next-work ranking, project overview |
| `src/planner/transfer.py` | JSON document format (export/backup) ↔ `Plan`, strict validation, merge-import |
| `src/planner/store.py` | SQLite schema + migrations, load/save of a whole `Plan` in one transaction |
| `src/planner/cli.py` | argparse commands, text output, `--yes` guards |
| `tests/` | unittest suites; `examples/` documented fixture; `scripts/demo.sh` synthetic demo |
| `data/` (gitignored) | default database `data/planner.db` and `data/backups/` |

### Glossary and states

- **Project:** unique `key` (lowercase slug), `name`.
- **Task:** integer `id` (never reused, counter `next_task_id`), `project`, `title`, `priority` (`urgent|high|normal|low`), optional `estimate_minutes`, optional `due` (plain calendar date, not an instant), `note`, `done_at` (UTC instant or null), `depends_on` (prerequisite task ids, may cross projects).
- **Derived state:** `done` (done_at set) · `blocked` (open, ≥1 prerequisite open) · `ready` (open, all prerequisites done). Transitions: ready→done, done→open (`reopen`). Not stored, always computed.
- **Invariants (`validate_plan`):** references exist, no self-dependency, no cycle, a done task has only done prerequisites, priorities/estimates/dates valid.

### Data flow

Every write command: `Store.transaction()` (`BEGIN IMMEDIATE` → serializes concurrent CLI runs) → load whole `Plan` → pure operation → `validate_plan` → rewrite tables → commit. Any exception rolls back, so a failed command or import changes nothing. Read commands load the plan without a write lock. SQLite foreign keys (`ON DELETE RESTRICT`) are a second safety net below `validate_plan`.

Schema version lives in `PRAGMA user_version`; `store.MIGRATIONS` is applied in order on open; a database newer than the code is refused.

### Operation

- Local only, started manually; no jobs, network, secrets or logs. Database path: `--db`, else `$PLANNER_DB`, else `data/planner.db`.
- Backup = full JSON document (same schema as export, ids preserved) written atomically (temp file + `os.replace`). Restore validates the file completely, writes an automatic safety backup of the current state, then replaces state in one transaction. Recovery point = last backup the user made; there is no automatic scheduled backup.
- Decisions and alternatives: `docs/decisions/0001-storage-and-transfer.md`.
