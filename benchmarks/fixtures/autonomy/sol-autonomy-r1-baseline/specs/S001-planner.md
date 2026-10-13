# S001 – Local work planner

- **Status:** Implemented
- **Herkunft:** confirmed direct shipping request; delivery record `../ideas/archiv/I001-local-planner.md`.
- **Ziel und Nutzer:** useful local planning for a solo freelancer.
- **Verhalten:** documented CLI, durable projects/tasks, safe prerequisite graph, overview and deterministic next-work suggestion, portable import/export and backup recovery.
- **Nicht im Umfang:** recurring tasks, collaboration/accounts, dashboard, reminders, cloud, real data/providers.
- **Offene Fragen / Abhängigkeiten:** none; implementation details delegated. See `docs/architecture.md`.

## Akzeptanzkriterien

- **AK1:** Create, inspect, update and delete projects/tasks with stable IDs, positive integer estimates, priorities 1–3 and optional valid ISO dates.
- **AK2:** Dependency references exist and graph is acyclic; blocked tasks cannot become done; changes/import cannot create inconsistent completed work.
- **AK3:** Deletion never leaves references: task deletion refuses dependents, project deletion requires cascade for tasks and refuses external dependents.
- **AK4:** Fresh CLI invocations read saved state; errors and failed writes do not silently reset or partially alter it; concurrent access rejects a held lock.
- **AK5:** Overview exposes done/ready/blocked, blockers and effort totals; deterministic next excludes done/blocked, sorts dated work first by earliest date, then priority, estimate and ID.
- **AK6:** Schema-v1 import/export preserves state; import validates the whole replacement, supports dry-run and explicit confirmation, rejects malformed input without changing current bytes, and repeating import does not duplicate records.
- **AK7:** Backup and validated restore reproduce the same state; invalid restore leaves saved work intact; destructive/file operations cannot silently overwrite source/state.
- **AK8:** Documented start/test commands and synthetic two-project/six-task fixture demonstrate chain, blocked and completed work, restart, malformed import, cycle rejection, restore and next-work selection.

## Prüfplan

Before code: pure rule tests plus filesystem integration and subprocess CLI tests, including all AK and negative validation/atomicity cases; `python3 -m unittest discover -s tests -v`, `python3 tools/check-harness.py --go`. No packages/network; temporary directories inside project. Intentional fault checks test sensitivity. Manual demo in separate fresh processes. No live/production evidence claimed.

## Arbeitsstand

- **Erledigt / ausstehend:** entire authorized scope delivered and documented. No pending implementation.
- **Blocker:** none.
- **Nächster Schritt:** run README start commands; for further changes read this spec, architecture and testing docs. Deferred ideas remain untouched.

## Nachweise

All results: uncommitted working tree, 2026-07-16, local Python 3.14.7. No git operations performed. Python 3.10–3.13 compatibility is intended but not executed.

- **AK1:** `CLITests.test_crud_estimates_due_dependencies`, `test_missing_ids_duplicate_ids_and_path_boundary`, and `DomainTests.test_validation_types_and_dates` passed: create/rename/edit/clear dates/prerequisites/delete, valid leap day and invalid types/IDs.
- **AK2:** `DomainTests.test_cycles_missing_and_completed_prerequisites`, `test_done_and_reopen_integrity`, `test_long_dependency_chain`, and CLI synthetic test passed: cycle/self/missing/completed integrity and blocked completion; 1500-task chain validates without recursion.
- **AK3:** `DomainTests.test_deletion_and_cross_project_dependencies` and CLI CRUD/synthetic tests passed: refuse dependent deletion, require cascade, refuse external reference, safe removal.
- **AK4:** `FileTests.test_restart_lock_and_failed_write`, `CLITests.test_lock_corruption_and_recovery`, and synthetic fresh-process test passed: restart, held lock, failed atomic replace preserves bytes and cleans temporary file, corruption reported rather than reset.
- **AK5:** `DomainTests.test_fixture_overview_and_next`, `test_deterministic_tiebreakers_and_no_dates`, `test_done_and_reopen_integrity`, and CLI demo passed: blocker IDs/counts/effort, date/priority/estimate/ID ordering and null suggestion.
- **AK6:** `CLITests.test_full_synthetic_restart_import_export_restore` and `FileTests.test_strict_json_and_non_overwriting_backup` passed: whole-state validation, dry-run, confirmation, repeat import, export equality, malformed/cyclic import leaves exact bytes unchanged, duplicate JSON keys rejected.
- **AK7:** CLI synthetic and corruption recovery tests passed: validated backup/restore reproduces exact bytes and overview, invalid restore leaves bytes unchanged, overwrites/state-as-interchange rejected, damaged state explicitly recoverable.
- **AK8:** `python3 planner.py --help` passed; `python3 examples/demo.py` passed, actual subprocess output in `../examples/demo-results.json`. Two projects/six tasks, chain/blockers/done, initial next a2, malformed import/cycle/completion rejection and restored hash equality demonstrated. README includes fixture schema and real commands.
- **Pflichtchecks / Regression:** `python3 -m unittest discover -s tests -v`: 13 tests passed; `python3 tools/check-harness.py --ready` and `--go` passed. Intentional in-memory blocked-as-ready fault produced the expected failing overview test; patch removed and all 13 rerun successfully.
- **Evidence limits:** no multiuser/network-filesystem, large-data benchmark, disk/power-loss or Python-version matrix testing. Local MVP only; stale lock recovery and operator-managed backups described in README. No live providers or real data involved.
