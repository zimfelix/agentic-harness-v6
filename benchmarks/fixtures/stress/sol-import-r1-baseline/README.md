# Recoverable inventory transfers

Python 3.9+ and its bundled SQLite only; no installation or network access.
Run from this directory:

```sh
python3 app.py seed --db inventory.sqlite --tenant demo --stock stock.csv
python3 app.py apply --db inventory.sqlite --tenant demo --csv transfers.csv --run-id batch-1
python3 app.py stock --db inventory.sqlite --tenant demo
python3 app.py runs --db inventory.sqlite --tenant demo
python3 -m unittest discover -s tests -v
```

Use synthetic files. Seed header: `sku,warehouse,quantity`. Transfer header:
`group_id,transfer_id,sku,from_warehouse,to_warehouse,quantity`.
CSV is UTF-8 with an exact header (no BOM), supports quoted commas/newlines.
Names are opaque, case-sensitive and not trimmed; whitespace-only names are invalid.
Quantities are ASCII decimal digits, bounded at 1000000; transfers must be positive.
Initial stock may be zero. Blank physical rows are invalid rows, not silently ignored.
Unreadable/non-UTF-8 or syntactically unparseable CSV is rejected as a whole.

Seed is all-or-nothing, once per tenant (even for an empty seed). Apply requires a
seeded tenant. All rows sharing a group belong to one atomic unit, even when
nonadjacent; groups run in first-appearance order. Successful earlier rows within a
group can fund later rows. Invalid groups create neither destination accounts nor
ledger entries. Duplicate transfer IDs anywhere in the file reject every affected
group; IDs can be reused in another run. Successful transfers retain zero accounts.

## Reports and recovery

Every invocation, including help/errors, emits exactly one JSON value on stdout.

| Result | JSON | Exit |
|---|---|---|
| Seed success | `status: seeded`, tenant, accounts | 0 |
| Completed apply, fully accepted | `status: completed`, zero rejected groups | 0 |
| Partially accepted/completely rejected batch | `status: completed`, nonzero rejected groups and reasons | 0 |
| Invalid whole-file input/arguments | `status: invalid_input`, reason | 2 |
| Identity/seed/schema conflict | `status: conflict`, reason | 2 |
| Simulated death | cumulative run report, `status: interrupted` | 3 |
| File/database/lock failure | `status: execution_error`, reason | 4 |
| Stock/runs | sorted JSON array | 0 |

Run reports contain `run_id`, `status`, `applied_groups`, `rejected_groups`,
`applied_rows`, `replayed`, and `errors` (group_id/reason). `runs` returns reports
sorted by run ID; unknown tenants return empty arrays. `stock` sorts by SKU then warehouse.

`--fail-after-groups N` (N>=1) terminates the process after N groups are durably
decided **during this invocation**, even when the last group was decided. If fewer
than N groups remain, the run completes. A rejected group counts toward N.
Resume by invoking the same tenant/run-id with **exactly the same input bytes**,
usually without the failpoint. No delay or lock cleanup is needed. The stored
progress and stock move together; even already rejected decisions remain fixed.
After a death following the final group, resume only marks completion.

Changed bytes with the same tenant/run-id conflict. A different run-id with the
same bytes is a new intended transfer, subject to available stock. Completed replays
return stored counts/errors with `replayed: true`; resume returns false. Actual process
kills may prevent stdout; inspect `runs` and resume identical bytes. On technical
errors do not assume zero progress: inspect stored reports. Fix file access/lock
conditions and retry the same identity, never generate a new ID just to recover.

## Architecture and schema operations

`app.py` launches `src/inventory/cli.py`. `parsing.py` handles boundary validation and
file-wide grouping/duplicate checks; `service.py` simulates each group's balances;
`storage.py` owns versioned SQLite tables and transactions. Tenant-qualified primary
keys scope accounts, runs, decisions and transfer ledger. Each group uses one short
`BEGIN IMMEDIATE` transaction for stock, ledger, decision and counters. Competing
processes re-read the next group under that lock, so identical runs cannot apply
it twice and distinct runs cannot overspend. No transaction spans invocations.

Schema migration 0→1 is automatically atomic, using `PRAGMA user_version` and the
versioned statements in `storage.py`; reopening version 1 leaves existing data intact.
A newer unknown schema is refused. Future migrations must be tested on populated
synthetic old databases as well as empty databases, and preserve interrupted runs.
Stop all clients before a version upgrade. Back up using Python's SQLite `backup()`
API, restore the copy to a separate path, and verify stock/runs and an interrupted
resume before relying on it. Downgrade by restoring the backup with matching old
code, not by changing user_version. The test suite exercises backup/restore.

## Limits

Local trusted-operator CLI: tenant selection is scoping, **not authentication**;
protect DB and input files with OS permissions. Inputs and history are retained.
Files/group plans are held in memory; no huge-file performance claim. SQLite waits
up to five seconds per lock request before reporting an execution error. Successful
commits use FULL synchronous; durability assumes a reliable local filesystem and
SQLite storage stack. Network filesystems, hardware power-loss behavior, production
backup schedules/security and a cross-platform release matrix have not been validated.
No real data or providers were used. Detailed continuation/evidence:
`specs/S001-import.md`, `docs/architecture.md`, `docs/testing.md`.
