# S001 — Local project/work planner
Status: Implemented
Source: confirmed local planner brief; future ideas excluded.

## Observable contract
- A1: CLI creates, edits, inspects and deletes projects/tasks; estimates are nonnegative integer minutes, priority 1–5, optional real ISO calendar date. IDs are stable and globally unique within each entity type. State survives new processes.
- A2: Dependencies may cross projects. Missing references, self-dependencies and cycles fail without mutation. Completion requires all direct prerequisites done (transitively enforced). Reopening cannot invalidate completed dependents. Delete refuses referenced tasks or nonempty projects, never silently removes edges.
- A3: Overview reports done/ready/blocked, unfinished blockers and effort totals. Next chooses only ready unfinished tasks using priority descending, due date ascending with null last, effort ascending, then ID. Empty readiness reports no suggestion.
- A4: Strict versioned JSON import is whole-state replacement with explicit `--replace`, validated before commit. Invalid JSON/schema/references/cycles/completion leaves saved state unchanged. Export and backup are round-trippable; output cannot overwrite files without explicit `--overwrite`, nor target database/sidecars. Restore requires `--replace`, can bypass invalid stored payload, and uses the same validation. Repeated import does not duplicate work.
- A5: Synthetic fixture has two projects, at least six tasks, dependency chain, blocked and completed tasks. Public CLI tests demonstrate persistence, malformed import preservation, cycles, exact backup recovery, and next-work exclusions. Concurrent writers preserve both changes; interrupted/failing transaction rolls back.

## Verification
`python3 -m unittest discover -s tests -v`: 10 tests passed on the delivered implementation (latest run 6.144s, no warnings). All mutations/queries exercised through fresh CLI subprocesses, with additional storage interruption checks. `python3 examples/demo.py`: passed and output inspected. `python3 planner.py --help`: passed.

## Evidence / continuation
- A1: CRUD test covers create/edit/date clearing/delete; demo/persistence test compares exported state exactly to fixture in fresh processes.
- A2: blocked completion, actual cycle, self/missing/duplicate dependencies, restrictive deletion and reopening failures preserve exact state. Long 1,200-task chain accepts and cyclic edge rejects.
- A3: overview counts/blockers/effort and readiness checked; ranking checks each tiebreaker, project filtering and cross-project blockers; completed-only state returns null.
- A4: malformed syntax/duplicate keys/schema/types/calendar dates/references/cycles/completion imports preserve exact state. Backup restoration equals original document, including restoration into a fresh database and recovery from malformed stored JSON. Replay has no duplicates. Output overwrite/database/sidecar protection and output failure tested.
- A5: demo confirms two projects/seven tasks/chain, blocked and completed work; next is ready `a2` despite higher-priority blocked/completed tasks. Two concurrent CLI writers retain both additions. Exception and killed uncommitted writer roll back.
- Test sensitivity: isolated project-local copy with cycle validation disabled produced three expected test failures (mutation was never applied to delivered files); temporary copy cleaned up.
- Review: changed/new product files reviewed against request; no git commands, network, packages, external data or external writes. Harness rules and deferred work unchanged. Failure paths preserve references and state; whole-state replacement and explicit edge removal are documented destructive scopes.

Done: complete CLI, transactional storage, strict format, synthetic fixture/demo, documentation and behavior tests. Remaining authorized work: none. Blocker: none. Next command for a new session: `python3 -m unittest discover -s tests -v` (or `python3 examples/demo.py` to inspect the example).
Limits: no tested physical power-loss/filesystem corruption durability, Windows or network-filesystem behavior; backups are manual, unencrypted and unauthenticated. Physically corrupt SQLite recovery requires a new database path. No future/deferred features implemented.
