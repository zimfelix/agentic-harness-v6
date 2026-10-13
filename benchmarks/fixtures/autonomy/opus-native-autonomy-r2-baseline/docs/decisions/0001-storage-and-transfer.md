# 0001 – SQLite state, whole-plan validation, JSON for export/backup

- **Status:** entschieden
- **Datum:** 2026-10-10
- **Entschieden von:** Agent als reversible Annahme (delegated by the order)

## Kontext
Single local user, stdlib only. State must survive restarts, invalid states (cycles, broken references, done-before-prerequisite) must never be committed, malformed imports must not damage state, backups must be restorable.

## Entscheidung
- SQLite (`sqlite3`) as the store: atomic commits, crash safety, `BEGIN IMMEDIATE` locking for concurrent CLI runs, FK constraints.
- Each write loads the whole plan, applies a pure operation, runs `validate_plan`, rewrites the tables in the same transaction. One place for all invariants.
- One JSON document format (`local-work-planner`, version 1) for export, import and backup.
- **Import = additive merge, all-or-nothing.** Project keys in the file must not exist yet (re-importing the same file is rejected, nothing duplicated); task ids in the file are file-local references and get new ids; dependencies may only point to tasks inside the file.
- **Restore = full replace**, ids preserved, only after complete validation and with an automatic safety backup; requires `--yes`.
- Deleting a task/project that other tasks depend on is refused; `--detach` removes those dependency links explicitly and reports them.

## Alternativen
- JSON file as store: simpler, but needs own locking and gives no FK safety net.
- Import as replace: would make import identical to restore and easy to destroy work by accident.
- Cascading delete of dependents: deletes more than asked for.

## Folgen
Full rewrite per command limits practical size to a few thousand tasks. Merge import cannot update existing projects; that would need a new order (update semantics).
