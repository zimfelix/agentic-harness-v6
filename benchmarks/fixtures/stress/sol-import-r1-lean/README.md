# Recoverable inventory batches

Python 3 standard-library CLI backed by SQLite. No installation or network access required.

```sh
python3 app.py seed --db inventory.db --tenant demo --stock stock.csv
python3 app.py apply --db inventory.db --tenant demo --csv transfers.csv --run-id batch-1
python3 app.py stock --db inventory.db --tenant demo
python3 app.py runs --db inventory.db --tenant demo
python3 -m unittest discover -s tests -v
```

Stock CSV header: `sku,warehouse,quantity`.
Transfer CSV header: `group_id,transfer_id,sku,from_warehouse,to_warehouse,quantity`.
Use UTF-8 CSV, exact header order and cell counts. Names are opaque and preserved exactly, but whitespace-only names are invalid. Quantities use ASCII digits (leading zeros allowed), at most 1000000; transfer quantities must be positive. Empty seed and transfer files with valid headers are allowed. Seed is once per tenant, including empty seeds. Other tenants are isolated. Unknown/unseeded tenants have empty inventory; transfers with no available source stock are rejected.

## Reports and recovery

Every command emits exactly one JSON value. Argument/input failures exit 2 with `status: invalid_input`; run-byte or seed conflicts exit 2 with `status: conflict`; database/filesystem failures exit 2 with `status: storage_error` and a reason. Help also returns JSON (exit 0).

An apply report includes `run_id`, `status`, `applied_groups`, `rejected_groups`, `applied_rows`, `replayed` and ordered `errors` with group IDs/reasons. Counts are cumulative. Completed batches exit 0 even if some or all groups were rejected: inspect rejected counts/errors to distinguish full acceptance, partial acceptance and full rejection. Invalid groups have no stock or ledger effects; independent groups continue. Invalid file headers/CSV syntax/encoding are rejected before run creation. Structurally malformed parsed rows reject their group, including one shared group for empty group IDs. Duplicate transfer IDs anywhere in the file reject every containing group.

To exercise a durable crash boundary:

```sh
python3 app.py apply --db inventory.db --tenant demo --csv transfers.csv --run-id batch-2 --fail-after-groups 1
python3 app.py apply --db inventory.db --tenant demo --csv transfers.csv --run-id batch-2
```

The first command exits 3 after one newly decided group commits, reports `interrupted`, and leaves the run resumable—even when that was the final group. The flag counts decisions made by that invocation, not prior progress. Remove it to finish, or reuse it for another recovery boundary. A completed replay is never interrupted by this flag. Abrupt process loss during a transaction leaves either the entire committed decision or none of it.

Resume with the **same tenant, run ID and exact file bytes**, including newline style. Stored completed reports replay with `replayed: true`. Interrupted resumes report false. A different run ID intentionally executes the same input again; transfer IDs are unique only within each run. No sleep, reset, manual balance adjustment or cross-invocation transaction is needed. Use `runs` to inspect durable progress after unexpected errors. Concurrent identical invocations converge; each response describes its own committed snapshot (another process may subsequently finish an interrupted run).

## Persistence and migrations

SQLite serializes writers with `BEGIN IMMEDIATE`. Each group transaction commits its stock changes, ledger and decision together. A later transaction marks the run completed. Exact input bytes and decisions are retained; reports are derived from those decisions, not volatile counters. Busy waits are bounded at five seconds per lock acquisition; exhausted waits return a storage error and can be retried by invoking the same command. Runs and stock lists are deterministically ordered.

The application atomically initializes version 1 on an empty database using `PRAGMA user_version`. It reopens populated version-1 databases without replacing data. Unknown versions and unversioned nonempty databases require an explicit migration and are refused. Future upgrades must add ordered transactional migration code and tests on empty and synthetic populated databases. Before upgrading, stop writers and back up the complete database; rollback means restoring that backup. Never edit run decisions or stock to recover a run. There is no legacy data importer or destructive reset command.

## Limits

This is a local operator tool, not an authentication/authorization service: tenants scope data but the caller can choose any tenant. Protect the database and CLI with OS access controls. CSVs and grouped balances are processed in memory; Python's CSV field-size limit applies. Stock balances use SQLite signed 64-bit integers; extreme lifetime accumulation beyond that range is not supported. Exact inputs and ledger history grow indefinitely. Concurrency/crash tests cover synthetic local SQLite processes and injected durable boundaries, not power loss, corrupt storage, remote filesystems or a production deployment. Backups, capacity controls and production access policy remain operator responsibilities.
