# S001 – Projects, tasks and dependencies

- **Status:** Implemented
- **Herkunft:** direct order, change record `ideas/archiv/I001-local-work-planner.md`.
- **Ziel und Nutzer:** the freelancer maintains projects and tasks with effort, priority, optional due date and prerequisites, persisted locally.
- **Verhalten:** CLI commands `project add|list|rename|delete`, `task add|edit|show|done|reopen|delete`, `dep add|remove`, `list`, `blocked`. State persists in SQLite across invocations. Integrity rules in `docs/architecture.md` §Glossary (invariants) apply to every write; violations are rejected with `error: …`, exit 1, and no change.
- **Nicht im Umfang:** recurring tasks, accounts, reminders, UI. Overview/next in S002, transfer/backup in S003.
- **Offene Fragen / Abhängigkeiten:** none; semantics are delegated assumptions (`README.md` §Semantics).

## Akzeptanzkriterien

- **AK1:** Projects and tasks created in one invocation are visible in a fresh invocation (restart).
- **AK2:** Completing a task with an open prerequisite is refused and names the open prerequisite; the task stays open.
- **AK3:** A dependency that would create a cycle (including self-dependency) is refused; existing dependencies are unchanged.
- **AK4:** Deleting a task or project that other tasks depend on is refused without `--detach`; with `--detach` the links are removed and reported, no dangling reference remains.
- **AK5:** `blocked` lists every open task with an open prerequisite together with what blocks it; `list --state` filters ready/blocked/done/open.
- **AK6:** Reopening a task whose dependents are done is refused (keeps "done ⇒ prerequisites done"); a done task cannot get a new open prerequisite.
- **AK7:** Invalid input (unknown project/task, bad priority, bad estimate, bad date, duplicate project key) gives `error:` and exit ≠ 0 without change.
- **AK8:** Deleting a project with tasks without `--yes` only shows the scope and changes nothing.
- **AK9:** Concurrent writers do not lose each other's changes; a database with a newer schema version is refused.

## Prüfplan

`python3 -m unittest discover -s tests`: rule tests in `tests/test_rules.py`, CLI tests in `tests/test_cli.py` (real entrypoint, temp DB). One deliberate fault (cycle check disabled) must turn AK3 tests red. Demo `scripts/demo.sh` for AK1–AK3/AK5.

## Arbeitsstand

- **Erledigt / ausstehend:** see Nachweise.
- **Blocker:** none.
- **Nächster Schritt:** none.

## Nachweise

- **All AK:** `python3 -m unittest discover -s tests` (tests/test_rules.py, tests/test_cli.py; 21 tests) + `scripts/demo.sh` · uncommitted, 2026-10-10, macOS, Python 3.14.7 · OK. Deliberate faults (blocked tasks in candidates; cycle check disabled) turned 3 resp. 5 tests red.

Regeln: `specs/S000-readme.md`. `Implemented` erst nach vollständigem Nachweis gemäß `harness/verification.md`.
