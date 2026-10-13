# Task Dispatch — durable multi-tenant webhook outbox

Build with Node.js 22.19+ standard library only (no npm packages). Entrypoint `node app.mjs`. Local fake provider only: no outbound network, emails, payments or real data. Persistence format is your choice; two SEPARATE stores for local state and fake provider, each addressed by directory paths. Commands produce exactly one JSON object on stdout; errors exit nonzero. Multiple OS processes may share the stores. Write and execute your own tests.

## Queue commands

`enqueue --store DIR --tenant T --key K --payload JSON` -> `{id,status}` with status pending or already existing status. Nonblank tenant/key, payload must parse as a JSON object. Identity = (tenant,key). Same identity and structurally equal payload returns same ID without adding another job; JSON object key order does not matter (array order does). Different payload under the same identity conflicts without mutation. Same key in another tenant is independent. Durability before acknowledging enqueue is required.

`status --store DIR --tenant T` -> `{pending:N,uncertain:N,delivered:N,dead:N,jobs:[{id,key,status,attempts}]}`. Do not expose jobs of other tenants. `attempts` counts actual delivery attempts, not no-op reconciliation/status reads. All persisted jobs are in exactly one of the four statuses.

`work --store DIR --provider DIR --tenant T --now INTEGER [--mode ok|accepted-timeout|reject|transient] [--crash before-send|after-accept]` processes at most one eligible job, oldest enqueue first; mode defaults ok. Return `{status:"delivered"|"uncertain"|"pending"|"dead"|"idle",id?}`.
- Fake provider has durable idempotency scoped to (tenant,key), compares semantic payload, and accepts at most once per identity. It stores the actual accepted payload and delivery ID separately from the local store. `provider --provider DIR --tenant T` -> `{accepted:[{id,key,payload}]}`. Use that command to inspect independent provider truth.
- ok: provider accepts once, local delivered. accepted-timeout: provider accepts, response is lost, local uncertain. reject: permanent provider rejection, local dead, no provider acceptance. transient: temporary failure, local pending until retry time; no acceptance.
- Pending retries: max THREE actual attempts total. First transient failure at now n schedules retry at n+2; second at its execution time m schedules retry at m+4; third makes dead. Before due time: idle, no attempt increment. `--now` is a monotonic logical seconds value supplied by the caller, not wall clock. No real sleeping for retry timing.
- Uncertain jobs reconcile against provider truth BEFORE deciding to resend. If already accepted, mark delivered using the existing provider ID, with NO new attempt. If absent, a later work invocation may retry under the same key safely.
- `--crash before-send`: after a durable claim, process exits nonzero before fake provider invocation. `--crash after-accept`: durable provider acceptance then abrupt exit before local success. Crash must release/recover ownership; restarting at the SAME logical time must not leave a permanently stuck job. Reconciliation after after-accept must not create another acceptance. Do not rely on waiting for wall-clock leases or manual repair.
- Concurrent workers/enqueues at the same stores must not corrupt state, lose jobs, duplicate acceptance or overwrite another tenant. One process finishing must not remove another's lock. Treat malformed existing persistence as a visible failure, not empty storage success.

## Cross-cutting behavior

Atomic persistence and recoverable ownership across OS process death; a real kill scenario is part of the contract, not only throwing/catching an exception. Explain limitations of file locks and provider deduplication. Never claim universal exactly-once delivery: this fake provider explicitly supports permanent deduplication; SMTP may not.

No dashboard, web server, real network provider or deployment is in scope. Keep public command names and JSON fields stable. Provide readable start/test commands and persistence/recovery documentation.
