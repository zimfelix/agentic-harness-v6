# Task Dispatch

A durable multi-tenant webhook outbox CLI with a **local fake provider only**. Node.js 22.19+; no install step, dependencies, network, server or real delivery.

## Start

Use separate directories (examples write only inside this project):

```sh
node app.mjs enqueue --store ./data/local --tenant alpha --key welcome --payload '{"message":"hello"}'
node app.mjs status --store ./data/local --tenant alpha
node app.mjs work --store ./data/local --provider ./data/fake --tenant alpha --now 10
node app.mjs provider --provider ./data/fake --tenant alpha
node --test tests/*.test.mjs
```

Each normal invocation emits exactly one JSON object on stdout. Errors emit `{ "error": "..." }` and exit nonzero. Simulated crashes also emit an error object, then abruptly exit nonzero without cleanup. An external SIGKILL cannot promise any output. Do not infer delivery from a failed command: query status/provider truth and retry safely.

## Behavior

- Enqueue identity is `(tenant,key)`. Payload must parse as a JSON object. Object key order is irrelevant, array order matters. Equal replay returns the same ID and current status; changed payload conflicts without changing the queue. Numbers use Node's JSON.parse semantics (IEEE-754); extreme exponents are preserved as JSON number tokens rather than converted to null. Use strings for application values requiring arbitrary decimal precision.
- Status exposes only the selected tenant, with `pending`, `uncertain`, `delivered`, `dead` counts and `jobs:[{id,key,status,attempts}]`. This is a trusted local CLI; tenant selection is isolation, **not authentication**. Anyone with filesystem access can inspect the entire snapshot.
- Work handles at most one eligible job in enqueue order. Delayed pending jobs are skipped. `--mode` defaults to `ok`; `accepted-timeout` durably accepts but leaves local uncertainty, `reject` permanently fails, `transient` schedules retry. First/second transient failures schedule +2/+4 logical seconds; the third actual invocation is dead. Due time is inclusive. There is no retry sleep. `--now` accepts arbitrary-size signed integers; callers must supply a monotonic logical clock consistently across workers.
- Uncertain jobs are reconciled first. Already accepted jobs become delivered with the existing provider ID and no resend. A claim with no provider invocation receipt may resend safely on the next work invocation. A failed invocation interrupted before its local update is recovered from its receipt, including its original retry due time. Reconciliation itself is not an attempt.
- `--crash before-send` exits after the durable claim, with zero new attempts. `--crash after-accept` forces accepting behavior (even if another mode is supplied) and exits after synced provider acceptance, before local completion. Restart at the **same logical time** works; no lease expiry or manual repair is needed under the supported liveness assumptions below.

## Persistence and architecture

`app.mjs` parses the CLI. `outbox.mjs` owns queue transitions and the fake provider. `storage.mjs` owns validated snapshots and process-aware mutual exclusion. No external adapter is configured or contacted.

Each directory stores its own version-1 `state.json`:

- Local: enqueue-ordered jobs, original payloads, status/counter/due time, provider delivery ID, and any outstanding claim.
- Fake provider: independently stored actual acceptances with delivery IDs/payloads, plus durable invocation receipts (including reject/transient). Its acceptance identity is permanently tenant/key scoped. Replays with changed semantic payload conflict. Multiple local stores may safely share one fake provider.

Work holds the local lock, durably claims uncertain, then takes the provider lock. The provider atomically commits its invocation receipt and acceptance, if any. Finally local state applies the receipt exactly once and clears the claim. A kill between those commits leaves a recoverable claim; status reports the actual receipt-backed attempt count without mutating local state. Claims remember the original provider's absolute path: recovery must use that same provider directory. A provider is never reconstructed from local delivered flags.

Writes use a unique temporary file, file `fsync`, atomic same-directory rename, then directory `fsync`. Enqueue acknowledges only after syncing. Malformed JSON, unsupported schemas, invalid records and duplicate identities fail visibly, never silently reset. Interrupted unreferenced `.tmp` files are harmless. A missing snapshot means a new empty store; unexplained loss/deletion of a previously populated snapshot cannot be distinguished from initial setup, so protect the directories and backups.

### Locks and limitations

The filesystem lock uses Lamport bakery tickets in `.locks/`: each process publishes a unique choosing record, obtains an ordered ticket, and waits behind live earlier contenders. Atomic publication avoids half-written metadata. A process deletes **only its own** participant. Dead PIDs are ignored, so abandoned claims/locks recover without wall-clock leases, even at identical logical time. Test-only IPC instrumentation allows a parent test process to pause at durable boundaries and SIGKILL the actual CLI.

Supported operational boundary: cooperating processes on one host/PID namespace, consistent local/provider directory roles, local filesystem with coherent directory reads, atomic rename and working file/directory sync. This is not an adversarial security boundary or a distributed/NFS lock. PID reuse, unreaped zombies, permission restrictions and another PID namespace can conservatively make a dead participant appear alive; ambiguous ownership is not force-stolen. Administrators must address that host-level condition after ensuring no worker is running. Crashes can leave participant/temp files; offline removal of those files is safe only after stopping all users of the stores. Large snapshots, bakery scans and permanently retained receipts make this a small-scale local implementation, not a high-throughput broker. Disk-full/sync/permission errors are surfaced; recovery may discover a committed operation whose acknowledgement was lost.

The fake provider explicitly supports **permanent deduplication**. This plus reconciliation guarantees at most one acceptance per identity in this fake, not universal exactly-once delivery. Providers with finite key retention require different replay bounds. SMTP commonly lacks deduplication/reliable reconciliation; an outbox alone cannot eliminate both duplicates and missed delivery.

## Backup, recovery and verification

Stop all participating processes before copying **both** `state.json` files as a consistent pair to a project-local backup. Keep directory paths stable when restoring outstanding claims. Restore both files while stopped; restart and run status/provider/work. Do not restore only the provider to an older state: that erases deduplication truth. Do not reset/delete provider truth to retry a job. No schema migration is currently needed; unknown versions fail instead of upgrading silently. Restoring an older pair intentionally loses subsequent operations; for real production use a separately agreed backup/retention/recovery policy is still required.

Tests use only synthetic data under `.test-data/` and remove their own fixtures. They cover the public CLI, semantic replay/conflict, tenants, all modes, retry limits/boundaries, provider independence, concurrent processes, abrupt injected exits, real SIGSTOP/SIGKILL, attempt receipt recovery, corruption, and stopped snapshot restoration. They do not prove host power-loss behavior, NFS safety, hostile filesystem access or any live-provider contract. The available test runtime is recorded in `specs/outbox.md`; Node 22.19 compatibility is intended, not evidence of a run on that version.
