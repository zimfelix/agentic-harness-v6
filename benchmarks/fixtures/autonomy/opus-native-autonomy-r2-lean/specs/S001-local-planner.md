# S001 — Local work planner (CLI)
Status: Implemented
Source/scope: confirmed brief (single freelancer, local only, Python stdlib CLI). Excluded: recurring tasks, accounts/collaboration, web UI, reminders, cloud deployment.

## Semantics (consequential assumptions)
- Ids: projects `p<n>`, tasks `t<n>`, never reused (counters persist). Projects may also be referenced by unique (case-insensitive) name.
- Priority: `critical > high > normal > low` (default `normal`). Estimate: optional, integer minutes (input `2h`, `90m`, `1h30m`, `1.5` = hours). Due: optional plain local calendar date `YYYY-MM-DD` (not a timestamp).
- Dependencies may cross projects. Task state: `done`; `blocked` = open with ≥1 unfinished prerequisite; otherwise `ready`.
- A done task never has an unfinished prerequisite: completion with unfinished prerequisites is refused; reopening a task that done tasks depend on is refused; adding an unfinished prerequisite to a done task is refused.
- Deletion never leaves dangling references: deleting a task/project that other tasks (outside the deleted set) depend on is refused, listing the dependents, unless `--detach` is given, which removes those edges and reports them. Deleting a project with tasks requires `--yes`; an automatic backup is written first.
- Next-work suggestion: only `ready` tasks. Each candidate inherits the highest priority and earliest due date from the open tasks it (transitively) unblocks. Order: urgent first (effective due ≤ today+2 days, incl. overdue; by due date then priority), then by priority, effective due (none last), more unblocked tasks first, smaller estimate first (unestimated last), lower id. "Today" = local date, overridable by `--today`.
- Import/backup/export share one JSON schema (`docs/data-format.md`). Import is all-or-nothing: `--replace` swaps the whole state, `--merge` adds the file's projects/tasks with fresh ids (references must be internal to the file). Invalid input changes nothing. Import and restore write an automatic backup of the current state first.

## Acceptance
- A1: Projects and tasks can be created, edited, listed, shown; overview shows per-project counts, remaining estimate, blocked/ready/done, overdue.
- A2: State persists across separate process invocations; writes are atomic and serialized by a file lock.
- A3: Completing a task with unfinished prerequisites fails and changes nothing; `blocked` lists each blocked task with its blockers.
- A4: Dependency cycles (incl. self-dependency) are rejected on add/edit and in imported/restored data.
- A5: Deleting a referenced task/project is refused without `--detach`; with it, edges are removed and reported; no dangling reference remains.
- A6: Malformed import (bad JSON, schema errors, dangling refs, cycles, done-with-open-prereq) fails with a report and leaves the state file byte-identical.
- A7: Export → backup → restore reproduces an identical state; a corrupt state file is reported (not overwritten) and can be recovered with `restore`.
- A8: `next` never suggests blocked or done tasks and is deterministic for a given state and date.
- A9: Synthetic demo: 2 projects, ≥6 tasks, a dependency chain, a blocked and a completed task (`examples/demo.sh`, fixture `examples/sample-project.json`).

## Check and work plan
`python3 -m unittest discover -s tests -v` (CLI subprocess tests at the public boundary + suggestion unit tests); `sh examples/demo.sh`.

Next steps: none required. Possible follow-ups (not authorized): backup pruning, schema migrations.

## Evidence
Uncommitted working tree, 2026-10-10, Python 3.14.7 on macOS. `python3 -m unittest discover -s tests`: 20 tests OK. `sh examples/demo.sh`: exit 0.
- A1: TestBasics (create/edit/show/validation/overview, overdue view).
- A2: every test uses separate processes against one file; test_concurrent_writers_do_not_lose_updates (8 parallel adds → 16 unique tasks).
- A3: test_blocked_task_cannot_be_completed (file byte-identical after refusal), test_blocked_listing.
- A4: test_cycles_rejected (incl. a cross-project cycle), import cases "cycle".
- A5: test_delete_task_refused_or_detached, test_delete_project_cross_project_refs.
- A6: test_malformed_imports_leave_state_intact (10 malformed variants × replace/merge, byte-identical); demo `cmp`.
- A7: test_export_backup_restore_roundtrip, test_corrupt_state_reported_and_recoverable; demo `cmp` export-before vs export-after restore.
- A8: TestNextWork (excludes t1 done; t4/t5/t7 blocked; output repeatable), TestRanking.
- A9: examples/demo.sh + examples/sample-project.json.
Mutation check: disabling the completion guard or cycle detection makes the corresponding tests fail.
Not covered: native Windows (fcntl), power loss during write (atomic rename is relied on, not fault-injected).
