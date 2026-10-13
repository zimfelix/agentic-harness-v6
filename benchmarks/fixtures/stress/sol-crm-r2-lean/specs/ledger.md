# S001 — Tenant-safe sales ledger
Status: Implemented
Source: confirmed CRM task; local Python/SQLite only.

## Acceptance
- Authenticate all business routes with the six TEST tokens; unknown/missing =401. Readers read; editor/owner mutate deals; only owner issues/voids. Forbidden =403. Foreign resources/relations =404. Reject client tenant and all unknown fields.
- Deal creation validates nonblank title, exact integer cents 0..100000000, EUR/USD; returns new/version 1. Tenant-only list/detail. PATCH exact positive integer version/status follows new→qualified→won/lost, increments once; stale/invalid transitions =409. Invalid JSON/shapes/types =400 without mutation.
- Won deals issue once ever, even after void. Tax basis points exact integer 0..10000, HALF_UP cents; amounts/currency snapshot. Tenant/request key replay identical semantic payload =200 same ID; first =201; different payload =409. Missing/foreign deal =404. Concurrency and restart retain replay safety.
- Tenant-only invoice list/detail; owner void with nonblank reason retains amounts, repeated void =409. No arbitrary editing. Audit has exactly one causal event per successful mutation, none for read/failure/replay.
- Loopback-only HTTP CLI prints readiness JSON with actual port. JSON responses. Persistence across restarts. Atomic versioned migration from empty and specified v1 preserves rows/IDs, initializes version 1, does not leak foreign rows, and repeats safely.

## Checks and work record
Done: complete local implementation, versioned SQL migrations, public-boundary tests and README. Fresh-session verification reviewed the persisted contract, implementation, migrations and existing tests; reran all 8 tests successfully without implementation changes. Existing harness/deferred files untouched; no git commands, packages, external requests or providers used. Tests used only project-local synthetic temporary databases and loopback HTTP.
Remaining: none within confirmed local scope. Production work is explicitly not authorized; limits are in README/PROJECT.
Blocker: none. Next command if re-verification is needed: `PYTHONDONTWRITEBYTECODE=1 python3 -W error::ResourceWarning -m unittest discover -s tests -v`. No further behavior is authorized.

## Evidence
Fresh-session verification of unchanged implementation: `PYTHONDONTWRITEBYTECODE=1 python3 -W error::ResourceWarning -m unittest discover -s tests -v` — all 8 tests passed (2.356s), Python 3.14.7, real subprocess CLI and loopback HTTP, project-local synthetic on-disk SQLite.
- Auth/rights/isolation: all six identities, missing/unknown identities, foreign/missing detail, transition, issuance and void lookups; tenant-only lists/audit.
- Deals: exact types/ranges/unknown fields, malformed/duplicate-key JSON, new/qualified/won/lost rules, terminal/stale conflicts; eight barrier-synchronized same-version writers yield exactly one success.
- Invoices: zero/max money and rate, below/at/above HALF_UP boundary, bad shapes/types, immutable snapshot, eight barrier-synchronized identical callers yield one 201 and seven 200s with one ID; tenant-scoped key reuse, conflicting payload/key, void/no reissuance, restart replay and causal exact audit sequence.
- Persistence: fresh startup and restarts; v1 rows retain numeric IDs/version initialization and foreign-tenant isolation; repeated migrated restart, integrity/foreign-key checks. A forced migration error rolls back rebuilt tables/version. Forced audit-storage failure rolls back deal creation and voiding.
- Prior-session test challenge (not repeated during fresh-session verification): temporarily replaced HALF_UP with truncation; money-edge test failed at 1 cent/5000 bps (tax 0 vs required 1). Restored formula; final full suite passes. Initial race exposed default HTTP backlog reset; increased backlog, both race tests passed additional isolated runs without retries.
Not tested/claimed: sustained load, power-loss/OS crash, backup restoration, production authentication/security/deployment or legal/tax compliance. The service remains a local TEST adapter, not production software.
