# Task Dispatch

Durable, multi-tenant webhook outbox with an independent **local fake provider**. No network, packages, real data, or deployment. Requires Node.js **22.19+**, including the built-in `node:sqlite` module (experimental in Node 22; its warning goes to stderr).

## Start

Run from this project directory. Use fictional data and two separate directories:

```sh
node app.mjs enqueue --store .data/local --tenant demo --key event-1 --payload '{"message":"fictional"}'
node app.mjs status --store .data/local --tenant demo
node app.mjs work --store .data/local --provider .data/provider --tenant demo --now 10
node app.mjs provider --provider .data/provider --tenant demo
```

Each command emits one JSON object on stdout. Errors emit `{ "error": "..." }` and exit nonzero. Injected crash commands emit a JSON error, then actually terminate with SIGKILL. An externally killed process cannot guarantee any stdout response.

## Contract

- `enqueue --store DIR --tenant T --key K --payload JSON`: `{id,status}`. Nonblank tenant/key, object payload. Identity is the exact `(tenant,key)` pair; whitespace is not normalized. Equal structured payload replays the same job and current status. Object order is irrelevant; array order matters. Different payload conflicts without changing that job.
- `status --store DIR --tenant T`: `{pending,uncertain,delivered,dead,jobs:[{id,key,status,attempts}]}`. Tenant-scoped, no attempt increment.
- `work --store DIR --provider DIR --tenant T --now INTEGER [--mode ok|accepted-timeout|reject|transient] [--crash before-send|after-accept]`: `{status,id?}`, with status delivered/uncertain/pending/dead/idle. Defaults to ok; handles at most one oldest eligible job. Caller supplies monotonic logical seconds (same value is allowed); there is no retry sleeping. Safe-integer range, with room for retry delays, is required.
- `provider --provider DIR --tenant T`: `{accepted:[{id,key,payload}]}`. These IDs are provider delivery IDs, **not** queue job IDs.

`ok` accepts and delivers; `accepted-timeout` accepts but leaves uncertain; `reject` makes dead without acceptance; `transient` retries after +2 seconds, then +4 from the second attempt's actual execution time, then dead after the third attempt. Not-yet-due jobs are skipped without attempts, so a newer eligible job can proceed.

## Architecture and recovery

`app.mjs` validates CLI arguments. `src/dispatch.mjs` owns identity, ordering, transitions, retries and fake-provider rules. `src/store.mjs` owns durable SQLite snapshots and locks. See [architecture](docs/architecture.md) and [task evidence/handoff](specs/S001-dispatch.md).

Each store directory contains:

- `state.sqlite`: versioned, validated JSON snapshot. Local records contain jobs; provider records contain actual accepted payloads and permanent identity keys. Commits use SQLite synchronous FULL, followed by directory fsync. Initial databases are atomically published by rename after a complete commit.
- `mutex.sqlite`: an OS-managed SQLite write transaction held across the whole command, including commits to the **separate state database**. This lets a claim be durable without releasing worker exclusion.

Locks are always acquired local-first, provider-second. Provider inspection takes only the provider lock. No process deletes lock files or another process's ownership. SQLite/OS releases locks after normal exit **or SIGKILL**, without PID heuristics, wall-clock leases or manual unlocks. Contention waits up to 30 seconds and then fails visibly; it is not a job retry timer.

Before sending, work durably marks the job uncertain. A before-send crash leaves attempts unchanged. An attempt is counted at the start of the fake adapter invocation, including failed/rejected attempts; a crash during that invocation consumes that attempt even if acceptance has not happened. Uncertain jobs consult provider truth first. An existing matching acceptance becomes delivered using its existing provider ID, with no new attempt. If absent, work can retry immediately under the same key, unless the three-attempt budget is exhausted.

```sh
node app.mjs work --store .data/local --provider .data/provider --tenant demo --now 10 --crash after-accept
# Expected nonzero exit. Restart at the same logical time:
node app.mjs work --store .data/local --provider .data/provider --tenant demo --now 10
```

`before-send` crashes after the claim, before provider invocation. `after-accept` crashes only when an acceptance occurs. With reject/transient there is no acceptance and hence no after-accept crash.

Malformed existing state, unsupported versions, conflicting provider payloads, and corrupt SQLite files are visible errors, never interpreted as empty stores. There is no automatic destructive repair. A kill during first initialization may leave an unused `init-*.sqlite` file; it is not authoritative and does not block recovery.

## Tests

```sh
node --test tests/*.test.mjs
node --check app.mjs
node --check src/store.mjs
node --check src/dispatch.mjs
```

Tests use only fictional data in temporary directories **inside this project**, and remove them afterward. They exercise the real CLI, two-store truth, repeated enqueues, all modes, delayed retries, tenant isolation, concurrency, actual injected SIGKILL and external kills with both locks held, malformed persistence, and backup restoration.

## Operational limits

- Use local SQLite-compatible filesystems, with all access through this implementation. Network filesystems, malicious file replacement, permission attacks, power-loss/hardware durability, and multi-host locks are not demonstrated. Whole-store locks serialize tenants; snapshots rewrite the entire dataset. This is a local demonstrator, not a high-throughput production service.
- Tenant filtering is not authentication. Anyone able to run the CLI or read store files can choose a tenant or inspect files. Use OS permissions; no production security boundary is claimed.
- The fake provider supports **permanent durable deduplication** and payload comparison. This is why recovery can avoid a second acceptance. Do not infer universal exactly-once delivery: SMTP and providers with expiring idempotency keys may duplicate or lose effects. Deleting provider history breaks this guarantee.
- Back up only when all processes are stopped: copy **both entire store directories together**, including any SQLite sidecars. Restore both to separate new directories, then inspect status/provider and run work to reconcile. The tests demonstrate this on fake data; there is no production backup SLA or schema migration beyond version 1.
- Tests ran on the available Node v26.8.1. Exact Node 22.19 execution and live-provider behavior are **not evidenced**. No live provider is implemented or in scope.
