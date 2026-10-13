# S002 – Project overview and next-work suggestion

- **Status:** Implemented
- **Herkunft:** direct order, change record `ideas/archiv/I001-local-work-planner.md`.
- **Ziel und Nutzer:** the freelancer sees per-project progress and gets a practical, reproducible suggestion of what to do next.
- **Verhalten:** `overview [PROJECT]` shows per project: done/ready/blocked counts, remaining estimated effort, overdue tasks and the task list with state and blockers. `next [--project] [--limit N] [--today DATE]` ranks only ready tasks: (1) due-pressure — overdue or due within 2 days of today first, (2) priority urgent>high>normal>low, (3) earlier due date, undated last, (4) more open tasks unblocked (transitively), (5) smaller estimate, unestimated last, (6) lower id. Each suggestion states its reason.
- **Nicht im Umfang:** reminders/notifications, calendar scheduling, capacity planning.
- **Offene Fragen / Abhängigkeiten:** ordering is a delegated assumption; changing it changes only `planning.rank_key`.

## Akzeptanzkriterien

- **AK1:** `next` never lists blocked or done tasks.
- **AK2:** `next` order follows the stated key and is identical across repeated invocations with the same state and `--today`.
- **AK3:** `overview` shows correct done/ready/blocked counts and remaining estimate per project.
- **AK4:** When no task is ready, `next` says so (exit 0) instead of suggesting something.

## Prüfplan

Rule tests for `rank_key` (each criterion isolated), CLI tests for exclusion, determinism, overview counts, empty case. Deliberate fault: include blocked tasks in candidates → AK1 test must fail.

## Arbeitsstand

- **Erledigt / ausstehend:** see Nachweise.
- **Blocker:** none.
- **Nächster Schritt:** none.

## Nachweise

- **All AK:** `python3 -m unittest discover -s tests` (tests/test_rules.py, tests/test_cli.py; 21 tests) + `scripts/demo.sh` · uncommitted, 2026-10-10, macOS, Python 3.14.7 · OK. Deliberate faults (blocked tasks in candidates; cycle check disabled) turned 3 resp. 5 tests red.

Regeln: `specs/S000-readme.md`. `Implemented` erst nach vollständigem Nachweis gemäß `harness/verification.md`.
