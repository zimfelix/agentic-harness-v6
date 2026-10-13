# S001 — Recoverable inventory batches
Status: Implemented
Source: confirmed user task; local Python standard library/SQLite only.

## Acceptance
- Strict CSV headers, row widths, nonblank opaque names and ASCII decimal quantity bounds. Seed validates entirely before mutation, once per tenant, including empty seeds; initial zero accounts persist.
- Group all rows by exact group ID in first-appearance order, including nonadjacent/empty groups. Invalid rows, insufficient stock or globally repeated transfer IDs reject the entire affected group; successful groups conserve SKU totals and may use earlier same-group credits. Rejection creates no accounts or ledger entries.
- Identity is tenant/run ID/exact bytes. Same completed run returns stable cumulative counts/errors with replayed true. Same interrupted run resumes once-only; changed bytes conflict; new IDs intentionally apply anew.
- Stock is tenant-scoped, sorted and includes zero accounts. Runs are tenant-scoped and sorted by run ID. Reports include cumulative counts, errors and completed/interrupted status; error envelopes distinguish invalid_input/conflict/storage_error, and completed rejection reports distinguish partial acceptance through counts/errors.
- Fail injection after N newly decided groups exits nonzero with interrupted cumulative report, including after the final group. Next invocation resumes without changing decisions. Concurrent identical runs converge; distinct runs cannot overspend. Lock waiting is bounded.
- Schema initialization is atomic and versioned; reopening populated schema preserves data; unsupported versions are rejected without domain mutations. All CLI paths emit one JSON value.

## Checks and work
Done: CLI, versioned schema, operator/recovery documentation and subprocess tests. Reviewed implementation against the complete request, including failure paths and tenant scoping. No remaining implementation work or blockers. Next verification command: `python3 -m unittest discover -s tests -v`.

No git commands were used, per the explicit user restriction. No harness rules or deferred work were changed.

## Evidence
Current implementation: `python3 -m unittest discover -s tests -v` passed all 12 tests. Public CLI subprocess checks cover strict atomic seed and tenant isolation; nonadjacent group order, same-group credits, rollback/no rejected accounts or ledger; globally duplicated IDs and malformed rows; exact-byte conflicts, new intended runs and stable completed replay; every injected boundary (including last applied/rejected group), repeated interruption and immutable rejection after later credits; concurrent identical runs, concurrent interrupted resumes, limited-stock contention (2 of 8 distinct groups accepted), and concurrent initial seeding/schema creation. Database inspection verifies stock totals, ledger counts and schema version/preserved data. A held writer lock exhausts the bounded wait and reports storage_error; subsequent access succeeds.

Test sensitivity: temporary isolated mutated copies of `app.py` deliberately violated quantity conservation and the completed replay flag; the respective public CLI tests each failed as expected. Mutants were removed by temporary-directory cleanup; shipping source was not mutated. An initial fixture failure was corrected to preserve its intended blank transfer ID; acceptance was not weakened.

Limits: no power-loss/corrupt-disk/network-filesystem or production evidence. Crash evidence uses the requested injected durable-boundary exits, not OS-kill timing. Initial migration/reopen/unsupported-schema behavior is tested; no prior product schema exists to migrate. README documents local trust, in-memory CSV/field limits, signed-64-bit balance range, indefinite retention and backup/upgrade responsibilities.
