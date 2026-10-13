# Durable multi-tenant outbox
Status: Implemented
Source: confirmed Task Dispatch request. Only local fake delivery is authorized.

## Observable contract
- Enqueue durably identifies (tenant,key); semantic object equality ignores property order, preserves array order, and conflicting payloads fail without mutation. All commands emit one JSON object; failures exit nonzero.
- Tenant status reports only that tenant and exactly pending/uncertain/delivered/dead, with actual durable provider attempts. Provider inspection exposes independently persisted accepted payloads and delivery IDs.
- Work processes at most one eligible job in insertion order. Success, lost response, permanent rejection and transient failure produce the specified statuses. Transient retries are due at +2, +4, then dead on the third attempt; reads and early work never count as attempts.
- Uncertainty is checked against provider truth first. Acceptance is reconciled without another attempt; absence permits safe retry. Claims survive pre-send and post-accept crashes; restarting at the same logical time works without leases/manual repair. Provider deduplication never accepts conflicting payloads or a second delivery for an identity.
- Separate stores, concurrent processes, abrupt SIGKILL, corruption and persistence failures must not lose acknowledged jobs, overwrite tenants or steal a live lock. Malformed stores fail visibly. Queue/provider directories cannot be the same physical directory.
- Logical time is a nondecreasing integer per tenant (equal values allowed); invalid CLI arguments fail before creating storage. Fake attempts are transactions committed into provider receipts, so interrupted uncommitted invocation has no provider effect or counted attempt.

## Current work / continuation
Done: CLI, validated atomic snapshots (including newly created directory entries), recoverable process ownership, independent provider receipts/deduplication, all queue transitions, tests and README recovery documentation. Reviewed implementation against success/failure paths and tenant/ownership invariants; no harness/deferred-work changes or unauthorized providers. Remaining scoped work: none. Blockers: none. Next verification command: `node --test test/*.test.mjs`.

## Evidence
Final uncommitted implementation: `node --test test/*.test.mjs` passed **15/15** on Node v26.8.1 after the directory-durability review. Tests exercise public CLI processes, semantic identity/conflicts, tenant filtering, independent accepted payloads/IDs, all modes, oldest eligible selection, exact deadlines/three-attempt limit, equal logical time, big integers, lost responses, both crash flags, externally issued SIGKILL at claim/provider commit and while acquiring ownership, killed transient/reject receipts, corrupt stores, EIO at enqueue/provider/local-success commits, distinct physical store enforcement, provider binding, and quiescent two-store restore. Test-generated directories were removed.

Three additional final-revision runs of `node --test --test-name-pattern='concurrent enqueues' test/outbox.test.mjs` passed. Each combines duplicate enqueues, two tenants, overlapping enqueues/workers and drain workers, checking no job loss or duplicate acceptance. A deliberately mutated first retry delay (+3 instead of +2) made the retry-deadline test fail at the expected due time; the correct delay was restored before the final suite.

Limits: local POSIX filesystem/cooperative same-host PID liveness only; PID reuse and permission ambiguity can conservatively block file locks. Node 22.19 itself, power-loss/hardware fsync behavior, Windows/network filesystems and real providers were not tested. No universal exactly-once promise. README explains permanent fake-provider deduplication, linear snapshot/receipt growth, backup paths, and unsupported online migration/repair. No production migration or human action is required for a new local store.
