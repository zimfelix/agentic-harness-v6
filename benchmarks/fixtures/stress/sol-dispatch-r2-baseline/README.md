# Task Dispatch

Durable multi-tenant webhook outbox with an independent, local fake provider. Node.js **22.19+**, standard library only; no installation, packages, server, network calls, or real data. Node 22 may print an experimental SQLite warning on stderr.

## Run

From this project directory:

```sh
node app.mjs enqueue --store .data/local --tenant demo --key example --payload '{"message":"synthetic"}'
node app.mjs status --store .data/local --tenant demo
node app.mjs work --store .data/local --provider .data/provider --tenant demo --now 0
node app.mjs provider --provider .data/provider --tenant demo
node --test tests/*.test.mjs
```

Each command emits exactly one JSON object on stdout. Errors emit `{ "error": "..." }` and exit nonzero. The supplied crash flags also emit an error object, then actually SIGKILL the process; an externally killed process cannot guarantee an output object. Payload must be a JSON object. Numeric values are normalized exactly from their JSON source (including values outside JavaScript Number precision/range). Tenant/key are nonblank, case-sensitive and otherwise preserved. Object key order is irrelevant; array order is significant. The same identity with a changed payload conflicts.

`work` handles at most one oldest eligible job. `--now` is a caller-supplied monotonic logical integer (stored/compared exactly using BigInt), never wall-clock time. Modes:

| Mode | Result |
|---|---|
| `ok` (default) | Accept and mark delivered |
| `accepted-timeout` | Accept but leave uncertain |
| `reject` | Dead, no new acceptance |
| `transient` | Pending after attempt 1 (+2 seconds) or 2 (+4); dead after 3 |

Before due time, work returns idle without attempting. It may process a younger eligible job while an older retry is not yet due. Uncertain jobs query provider truth first; existing acceptance marks delivered without another attempt, even at the retry limit. Missing acceptance permits a safe retry under the same identity. `attempts` counts committed fake-provider invocations, including transient/reject, but not claims or reconciliation. A prior accepted identity always returns its existing delivery ID; modes never erase it.

```sh
node app.mjs work --store .data/local --provider .data/provider --tenant demo --now 0 --crash before-send
# Or --crash after-accept (requires an acceptance).
# Restart with the SAME --now; no wall-clock lease or manual repair is needed.
```

## Persistence and recovery

Use **two separate directories**. The local store contains `state.sqlite` and `ownership.sqlite`; the provider contains `provider.sqlite`. SQLite journal files are normal recovery artifacts: never remove them to unlock a store. Fully initialized databases are atomically installed without overwriting another initializer. Malformed existing databases, invalid records, wrong store kind/version, and unsupported journal modes fail visibly; they are not reset to empty.

All local commands serialize on a SQLite transaction in `ownership.sqlite`. The OS releases locks when a process dies. SQLite manages ownership, so a finishing process never unlinks another process’s lock. Lock contention waits at most 30 seconds, then fails visibly; this is a contention timeout, not a job lease or retry clock. Provider transactions independently serialize across workers, even those with different local directories.

A durable claim changes pending to uncertain without consuming an attempt. The fake-provider invocation uses a SQLite attached-database transaction: local attempt increment and provider acceptance commit together. Rollback journals and FULL synchronization provide atomic multi-database commit through SQLite’s superjournal. Marking local success is a subsequent transaction. Thus death before invocation preserves the retry budget; death after acceptance leaves an uncertain job with provider truth available. See `docs/architecture.md` for module responsibilities.

Use the **same provider store for a job’s lifetime**. Provider identities and actual accepted payloads are permanent. Deleting/replacing provider data breaks deduplication. Do not edit databases directly. Leftover `*.init-*` files from death during first-time initialization are unpublished scratch files; with all processes stopped they can be removed, but never treat live SQLite journals as scratch.

### Backup / restore

Stop all processes and copy **both complete directories together**, including any recovery journals; keep the original pair until the copied pair is verified with status/provider commands. Restore to separate directories, then run work to reconcile uncertain jobs. The test suite exercises quiescent copy/restore with an uncertain accepted job. Hot backups, schema upgrades, and automatic rollback migrations are not implemented; schema v1 is the initial format.

## Limits and evidence

- Tested on installed Node **26.8.1**. Uses APIs available in Node 22.19, but execution on that target version has not been verified here.
- Locks, hardlink publication, fsync, and SQLite atomic commits require a trustworthy local filesystem. No NFS, multi-host, arbitrary filesystem, disk-failure or power-loss qualification is claimed. Concurrent initialization and real OS process deaths are tested; physical power cuts are not.
- This is a bounded local fake-provider model. Its transaction boundary deliberately couples invocation accounting to acceptance; it is not a protocol for a real remote service.
- The fake provider supports permanent deduplication. **No universal exactly-once delivery claim**: SMTP and providers without durable idempotency can duplicate or lose delivery after ambiguous failures.
- Tenant filtering is not authentication. Anyone with directory access can inspect all persisted tenants. No encryption, authorization server, payload size quota, retention policy, production monitoring, or large-volume performance qualification is provided. SQLite stores and validation favor correctness over throughput.
- Tests use synthetic data and project-local scratch directories. No real provider, deployment, or live-service evidence exists.
