# Task Dispatch

Durable tenant-scoped outbox and **local fake provider**, Node.js 22.19+ standard library only. No install, server or outbound network.

## Run

From this project directory:

```sh
node app.mjs enqueue --store ./var/queue --tenant demo --key event-1 --payload '{"type":"example","data":{"n":1}}'
node app.mjs work --store ./var/queue --provider ./var/provider --tenant demo --now 0
node app.mjs status --store ./var/queue --tenant demo
node app.mjs provider --provider ./var/provider --tenant demo
node --test test/*.test.mjs
```

Every normal command (including errors) emits exactly one JSON object to stdout. Errors exit nonzero. `work` accepts `--mode ok|accepted-timeout|reject|transient` (default `ok`). `--crash before-send|after-accept` writes a JSON error and kills itself with SIGKILL; after-accept requires an accepting mode. An externally killed process may produce no output. Retry the enqueue with the same identity/payload if acknowledgment was lost.

Tenant and key must be nonblank; whitespace is preserved in identity. Payload must be a JSON object, with finite numbers. Nested object key order is irrelevant; array order matters. JSON numbers follow JavaScript number semantics. Reusing an identity with different payload fails without changing the queue. Tenant flags are local routing/isolation, **not authentication**: filesystem access is trusted.

`--now` is an integer logical second, not wall time; negative and arbitrarily large integer values are supported. Time must not decrease within a tenant; equal times are allowed. A transient at n is due at n+2; the second transient at execution time m is due at m+4; the third attempt is dead. An early job does not block a younger eligible job. No retry sleeps occur; only lock contention polls briefly.

## Architecture and persistence

- `app.mjs`: validates CLI input, emits JSON and dispatches.
- `lib/storage.mjs`: atomic snapshots and cooperative cross-process ownership.
- `lib/queue.mjs`: enqueue identity, tenant status, logical timing and durable claims/recovery.
- `lib/provider.mjs`: independent permanent acceptance deduplication and attempt receipts.
- `lib/model.mjs`: semantic equality and versioned store validation.

Each directory contains `state.json` (version 1, queue or provider), plus `.owners/` participant records. Data is written to a unique sibling temporary file, fsynced, atomically renamed, then the directory is fsynced **before acknowledgment**. Temporary files from a killed writer are ignored; committed malformed JSON/schema is a visible error, never silently reset. Store roles are validated and queue/provider must be different physical directories (symlink aliases are rejected).

A worker holds the queue lock across its operation; provider locking is always acquired second. Locks serialize even different tenants, favoring correctness over throughput. A Lamport bakery lock publishes an atomic choosing record, selects a ticket, and waits behind live earlier tickets. Participants have unique filenames; a process removes only its own record. Dead PIDs are ignored, so death during acquisition or dispatch needs neither a lease expiry nor manual repair. Dead participant files are retained, never confused with a successor's filename.

Before sending, the queue commits an **uncertain** claim with a unique attempt token and the provider's canonical path. The independent provider transaction commits both its effect (if any) and the receipt for that token. That commit defines an actual fake delivery attempt. An invocation interrupted before its transaction commits has no acceptance and no counted attempt. Local counters are recovered from receipts, not from claim intent. `status` may recover abandoned receipts without marking an acceptance delivered; `work` checks acceptance truth before resending uncertainty. Reject/transient receipts recover their dead/pending result and original logical deadline. Reconciliation never increments attempts. Delivery IDs come from provider truth, not the queue job ID.

These stores are **not one cross-store transaction**. A failure after provider commit leaves local uncertainty; the next worker safely reconciles it. A failure before commit leaves no receipt and allows retry under the same key. Once bound, unfinished jobs cannot be redirected to another provider directory.

## Recovery and limits

Run the same commands/stores after a worker dies, including at the same logical time. Do not edit/reset state or remove lock records while processes are running. Preserve provider history permanently: deleting it destroys the deduplication guarantee. A completely absent snapshot is treated as a new store, so accidental deletion of committed files cannot be distinguished from intentional first use; restore backups rather than reinitializing damaged stores.

For backup/restore, stop **all** writers, copy both directories, and restore both to their original canonical paths (claims and provider binding contain those paths). Quiescent two-store restore is covered by tests. Inconsistent-time backups, relocating stores, schema upgrades, corrupted-data repair and online migrations are not implemented. There is no recovery/reset command that silently discards provider truth.

File locking/durability assumes cooperating processes on **one host**, a local POSIX filesystem with atomic rename and working file/directory fsync, and reliable PID liveness (`kill(pid,0)`). Network filesystems, separate PID namespaces, hostile edits, hardware lying about fsync, and Windows are not supported/tested. PID reuse can make an old dead participant appear live and cause conservative blocking; unusual PID reuse/permission ambiguity cannot be solved universally with portable filesystem locks. Normal observed process death recovers immediately without wall-clock leases. Retained dead records and receipts grow with usage; snapshots/lock scans are linear, so this is not a high-volume production queue. No retention/compaction, authentication or real-provider adapter is included.

Acceptance is at most once here **because this fake provider permanently deduplicates tenant/key and verifies semantic payload**. This is not universal exactly-once delivery; SMTP and providers with expiring/no deduplication may duplicate or require manual uncertainty resolution.

## Verification

Tests launch the actual CLI in separate OS processes using only synthetic data in temporary directories **inside this project**, removed after tests. They cover all modes, deadlines, tenant isolation, identity conflicts, provider truth/IDs, concurrent enqueues and workers, crash flags, externally issued SIGKILL (paused at actual persistence boundaries), failed persistence, malformed stores and quiescent backup/restore. Test-only `--import` instrumentation pauses real writes or injects EIO; production code has no test hooks.

Runtime tested here: Node v26.8.1. Node 22.19 and power-loss/hardware fsync behavior were not independently tested; APIs used are available in Node 22.19. No live-provider evidence is claimed or needed for this fake-only scope.
