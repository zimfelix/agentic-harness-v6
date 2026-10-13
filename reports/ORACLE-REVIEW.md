# Independent oracle review

Read all three `tasks/*.md`, all of `oracle.py`, `QA-NOTES.md`, and `test_oracle.py`. No contracts/oracle/products were modified or implemented. Ran `python3 -W error::ResourceWarning -m unittest -v test_oracle.py`: **13 tests passed** (6.529s). These test harness mechanics and broken entrypoints, not valid-product acceptance or the findings below.

## Comparison-critical findings

### 1. P0 — Inconclusive observations are scored as product failures (definite scoring error)

**Locations:** Dispatch `tamper`, `killed`; `evaluate`; `main`.

Contract: “Persistence format is your choice” and “Treat malformed existing persistence as a visible failure, not empty storage success.”

`tamper` requires a changed file containing an unencoded marker. Legitimate compressed, encoded, encrypted, or otherwise marker-less persistence fails before any malformed persistence is supplied. `evaluate` returns `passed: false` and the CLI exits 1, exactly as for contract violations. QA-NOTES explicitly acknowledges this is “not a product contract violation,” but saying INCONCLUSIVE inside an error string does not fix binary scoring. This systematically biases an A/B comparison toward plaintext implementations.

Even finding the marker does not establish the selected file is authoritative state: sorting candidate paths can choose a diagnostic log, backup, or expendable index. Corrupting that file and demanding `status` fail can also reject a correct implementation. Byte discovery is format-independent, but not *role*-independent.

The external-kill group similarly fails a worker which happens to exit before `poll`, rather than demonstrating a recovery defect; this is scheduling-dependent.

**Fix:** introduce a machine-readable `outcome` distinguishing pass, observed violation, inconclusive, and harness error. Exclude inconclusive cases from product-failure counts and publish tested coverage separately for both variants. For corruption, use an independently validated authoritative path or report inconclusive; do not infer authority from marker presence. Retry kill trials within a bounded budget; inability to capture a live worker remains inconclusive, not a product violation.

### 2. P1 — A fabricated missing ID can instead be an invalidly typed ID (ambiguity that can misclassify valid CRM)

**Location:** `non-won-and-missing-invoice-deals`.

Contract: “IDs are opaque; clients should use returned values”; “Unknown fields/invalid body -> 400; missing/foreign deal ->404.”

The oracle sends `deal_id='synthetic-missing'` and requires 404. An implementation returning integer IDs may accept integers as references and reject strings as an invalid body (400). The contract does not define ID representation, nor clearly resolve invalid-ID shape versus missing-resource precedence. Unlike foreign-resource tests, this test invents a representation.

**Fix:** use a valid-shaped reference obtained from the product (for example an ID from an independent database, with collision checks), or accept 400/404 for invented malformed references while retaining strict 404 tests for real foreign IDs. Do not impose a string ID grammar. Resolve any remaining precedence ambiguity before comparing variants.

### 3. P1 — Void unknown-field rejection is not explicitly specified (ambiguous choice)

**Location:** CRM `void`, body `{'reason':'x','extra':1}`.

Contract: “POST /invoices/{id}/void body {reason} ->200 … Reason nonblank text; only issued invoices can be voided, repeated void ->409.” Deal creation and invoice issuance explicitly say unknown fields fail; the void clause does not. Global rejection of `tenant` is explicit and is a sound check, but the arbitrary `extra` 400 requirement is inferred from the body notation.

**Fix:** do not score this inferred requirement as mandatory unless clarified uniformly before A/B evaluation. If tolerated, verify the extra property cannot edit amounts or tenant. Continue to enforce reason validation and explicit tenant rejection.

### 4. P1 — Operational time budgets can determine the winner (coverage/scoring limitation)

**Locations:** `COMMAND_TIMEOUT=15`, `START_TIMEOUT=8`, `HTTP_TIMEOUT=5`, six-way scenarios.

Contract: Import says “Busy waiting must be bounded”; Dispatch says “No real sleeping for retry timing.” Neither promises these exact startup, HTTP, or contention latencies. A correct serialized six-process implementation on a loaded machine can exceed a per-command limit. QA-NOTES calls these QA budgets, yet timeout exceptions become indistinguishable product failures.

**Fix:** retain watchdogs for safety, but classify timeout separately, capture phase/duration, use equal isolated resource conditions, and confirm reproducible deadline failures with a larger diagnostic budget. Distinguish unbounded waits/lease dependence from mere slowness. Do not silently turn a QA budget into an acceptance requirement.

## Resource safety and hanging risks

### 5. P1 — Startup and output handling are not bounded in bytes (definite missing safeguard; hang/OOM risk)

**Locations:** `Server.__enter__`, `Server.request`, `invoke`, Dispatch `tamper`.

CRM contract: “print one JSON line … when ready”; Dispatch: “Commands produce exactly one JSON object on stdout.” Broken products must still be contained by the harness.

Startup polls a regular file with unbounded `readline()` from offset zero. A rapidly growing, newline-free file can make one read run beyond the nominal deadline or consume enormous memory; repeated full rereads compound the cost. Startup failure then reads all stderr. `communicate()` buffers unlimited command stdout/stderr; HTTP `response.read()` has a time bound but no byte bound. Tamper snapshots every file fully, potentially including large logs. Thus a buggy variant can exhaust RAM/disk and disrupt later groups or the other variant despite the claimed timeout containment.

**Fix:** cap startup-line length, stdout/stderr and response bytes; incrementally read startup output under a deadline; cap retained diagnostics and store-scan bytes. Use bounded drains or spooled files with limits for commands. Put resource-limit failures in a harness/resource category. Add helper self-tests for fast infinite output, huge newline-free startup output, and large stderr; do not build products for these tests.

### 6. P2 — Partial setup can leak handles (definite exceptional-path cleanup gaps)

**Locations:** `Server.__enter__` allocates `self.out` and `self.err` before its `try`; `Server.request` creates a socket and starts a timer before its `try`.

If the second temporary-file creation fails, the first is not explicitly closed. If construction/setup or `timer.start()` fails after socket creation, the socket is not explicitly closed. These are resource-pressure exceptional paths, not ordinary acceptance failures; successful self-tests do not cover them.

**Fix:** acquire resources inside an `ExitStack`/outer `try`, register cleanup immediately, and only join a timer that started. Add injected setup-failure tests. Normal subprocess paths otherwise have useful `finally` cleanup and bounded leader waits; I found no ordinary silent-child timeout leak demonstrated by the existing tests.

## Important missing risk checks

These are **coverage limitations**, not claims that unseen implementations are broken.

### 7. P1 — Real kill usually tests runtime startup, not ownership recovery

**Location:** Dispatch `killed` immediately kills after `Popen` and `poll`.

Contract: “Atomic persistence and recoverable ownership across OS process death; a real kill scenario is part of the contract, not only throwing/catching an exception”; “One process finishing must not remove another's lock.”

A worker with unsafe stale-lock recovery can pass because the process is killed before Node loads the application or acquires ownership. The crash flags test output behavior but cannot establish abrupt death, as QA-NOTES correctly acknowledges. There is also no controlled overlap of an old owner's cleanup with a replacement owner's lock.

**Fix:** run bounded, varied-delay kill trials after observing evidence of work/ownership where possible, preserve initial/final public truth, and explicitly mark unobserved claim windows as uncovered. Add overlapping kill/restart/concurrent-worker stress and verify all jobs, payloads, attempts, and provider identities. Avoid wall-clock *recovery* waits; test delays are only for selecting kill windows. Public APIs may still prevent deterministic proof; disclose that rather than score startup kills as comprehensive coverage.

### 8. P1 — Provider-side conflicting payload deduplication is untested

**Location:** Dispatch `intent` uses a fresh local store but only the same payload.

Contract: “Fake provider has durable idempotency scoped to (tenant,key), compares semantic payload,” and stores “actual accepted payload and delivery ID separately.” Local enqueue conflict tests do not exercise provider conflict.

**Fix:** accept `(tenant,key,P1)` with local store A, enqueue `(tenant,key,P2)` in fresh store B using the same provider, work B, and verify provider truth remains exactly P1 with the same delivery ID. Require no false successful delivery of P2, without inventing an unspecified conflict-response format. Also vary semantic object order in the fresh-store replay and assert the original provider record/ID is unchanged, not just its count.

### 9. P1 — Competing distinct invoice requests and concurrent voids are untested

Contract: “already invoiced deal with a DIFFERENT request ->409”; “Changes are atomic”; “only issued invoices can be voided, repeated void ->409”; audit is “Exactly one event per committed mutation.”

The six-identical issue race only tests the request-id uniqueness path. A product can deduplicate requests correctly yet issue multiple invoices for one deal under different request IDs. Sequential void checks do not establish once-only concurrent void behavior.

**Fix:** race distinct request IDs on one won deal: one 201, remaining 409, one invoice and issuance event. Race valid void requests: one 200, remaining 409, retained amounts and exactly one void event. Verify state after restart.

### 10. P2 — Import malformed-row and interrupted-decision coverage has gaps

Contract: “malformed row makes the entire seed invalid”; group rows with invalid input must reject atomically; resumed work must have no “changed completed group decisions.”

Malformed transfer tests cover bad cells but not truncated/extra-column rows. Seed tests cover truncation but not extra columns or whitespace-only names/tenant. Interrupted-middle tests validate counts but do not compare the stored rejected group's ID/reason with the resumed and replayed reports. A product can change or misattribute rejection reasons and still pass. `report()` checks reason count and nonblank text but generally not exact rejected-group membership.

**Fix:** add short/long transfer rows after a valid row in a group and an independent good group; add whitespace-only identifiers and seed extra-column cases. Compare interrupted errors against the corresponding resumed/replayed decisions, and assert rejected group IDs as a set wherever all rejected groups are known. Add a successful transfer quantity of 1000000 (the positive upper boundary is currently only covered for seed stock).

### 11. P2 — Audit mutation rollback, lifecycle replay, and migration coverage are incomplete

Contract: audit has “none for failures, reads or idempotent replay”; voiding never allows reissue; legacy migration must “Preserve all rows/IDs” and “migrate once.”

Some failure groups check invoice lists but not audit, so spurious failed-issuance events can escape. No same-request invoice replay after void/restart checks that replay cannot resurrect an invoice or issue twice. Legacy B's ID/currency/status are not all asserted, no post-migration creation checks ID collision, and migration termination/restart is not exercised. No public check forbids arbitrary invoice amount editing (QA-NOTES acknowledges not inventing endpoints).

**Fix:** assert exact audit actions/resource IDs after non-won/missing issuance failures and conflicts; replay a voided invoice with the original request and verify no resurrection/new event; assert every documented legacy field for both tenants and create fresh deals after migration. Treat source-versioning, forbidden endpoints, and migration crash-window guarantees as separate review/coverage items where no public probe can establish them.

## Bottom line

Prioritize fixing **inconclusive-as-failure scoring**, representation/void ambiguities, and timeout classification before trusting an A/B winner. Then strengthen provider-conflict, real-ownership-death, and distinct-request invoice races. QA-NOTES is candid about several limitations, but disclosure alone does not make binary acceptance results contract-faithful.
