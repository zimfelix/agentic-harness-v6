# S003 – Import, export, backup and restore

- **Status:** Implemented
- **Herkunft:** direct order, change record `ideas/archiv/I001-local-work-planner.md`.
- **Ziel und Nutzer:** the freelancer moves synthetic project data in/out and recovers saved work from a backup.
- **Verhalten:** JSON format documented in `README.md` §Data format with fixture `examples/synthetic-portfolio.json`. `export FILE|- [--project KEY]`, `import FILE [--dry-run]` (additive merge, all-or-nothing), `backup [FILE]`, `restore FILE --yes` (full replace after validation, automatic safety backup). Semantics: `docs/decisions/0001-storage-and-transfer.md`.
- **Nicht im Umfang:** updating existing projects via import, scheduled/automatic backups, cloud sync.
- **Offene Fragen / Abhängigkeiten:** none.

## Akzeptanzkriterien

- **AK1:** Importing the fixture into an empty planner creates its projects/tasks/dependencies and reports counts.
- **AK2:** A malformed import (invalid JSON, schema error, dangling reference, cycle, existing project key) is rejected with a reason and leaves the state identical.
- **AK3:** `backup` → changes → `restore --yes` yields exactly the backed-up state (ids included).
- **AK4:** `restore` of a malformed backup, or without `--yes`, changes nothing; a successful restore first writes a safety backup of the replaced state.
- **AK5:** Export → import into an empty planner reproduces projects, tasks, dependencies and completion.
- **AK6:** `export --project` refuses when tasks have dependencies crossing the exported subset.

## Prüfplan

CLI tests with temp DBs and the fixture; state identity compared via full export (minus `exported_at`). Deliberate fault: skip validation before restore → AK4 malformed test must fail. Demo shows AK2/AK3.

## Arbeitsstand

- **Erledigt / ausstehend:** see Nachweise.
- **Blocker:** none.
- **Nächster Schritt:** none.

## Nachweise

- **All AK:** `python3 -m unittest discover -s tests` (tests/test_rules.py, tests/test_cli.py; 21 tests) + `scripts/demo.sh` · uncommitted, 2026-10-10, macOS, Python 3.14.7 · OK. Deliberate faults (blocked tasks in candidates; cycle check disabled) turned 3 resp. 5 tests red.

Regeln: `specs/S000-readme.md`. `Implemented` erst nach vollständigem Nachweis gemäß `harness/verification.md`.
