# Hidden acceptance oracle — revised QA truth

## Scope and commands

Read the QA briefing (not retained in this repo), all three public `tasks/*.md`, and the prior oracle/notes/tests.
Public tasks are unchanged. No product implementation exists here; no product
acceptance evaluation has been performed. Python standard library only; Dispatch
requires Node on PATH. All inputs and diagnostics are synthetic.

```sh
python3 oracle.py crm PROJECT ARTIFACTS --seed 1
python3 oracle.py import PROJECT ARTIFACTS --seed 1
python3 oracle.py dispatch PROJECT ARTIFACTS --seed 1
python3 -W error::ResourceWarning -m unittest -v test_oracle.py
```

`evaluate(case, project, artifacts, seed=1)` returns named results with
`outcome`: **pass / fail / inconclusive / timeout / harness_error**.
`passed` remains for compatibility and is true ONLY for pass; nonpass results
include `error`. CLI emits this JSON and exits 1 for ANY nonpass result, including
incomplete evidence. Unknown API/CLI case is `harness_error` (CLI exit 1).
**Do not count `passed:false` or CLI nonzero as an observed business failure.**
For comparison report outcome counts and coverage separately: fail is an observed
contract assertion failure; inconclusive is missing evidence; timeout is a QA
watchdog, not a contractual latency violation; harness_error is setup/resource or
unexpected harness failure. Evaluate under equal isolated resource conditions;
recheck timeouts with a larger diagnostic budget before drawing conclusions.

There are **20 CRM, 18 Import, 21 Dispatch** independent groups (59 total).
Each uses a fresh temporary directory under ARTIFACTS, removed on completion.
Groups are internally fail-fast; later groups still run. Every real group reaches
the product in broken-entrypoint tests, verified separately per group, not merely
by aggregate invocation counts. RNG seeds are repeatable per group.

## Contract-faithful corrections and added evidence

- Fabricated `synthetic-missing` invoice deal reference may receive 400 or 404:
  opaque IDs need not use this representation. Actual returned foreign deal IDs
  still require strict 404, including related-resource issuance.
- Void tests still require valid nonblank text reason, explicit client-tenant
  rejection, retained amounts/currency/record, repeated-void conflict, reissue
  prevention, and one successful audit mutation. The unspecified arbitrary
  `extra`-field rejection assertion has been removed, not replaced by a demand
  that implementations accept extra fields.
- New `six-distinct-invoice-requests-one-deal`: race six distinct request IDs on
  one won deal; exactly one 201 and five 409; one actual invoice, correct snapshot
  amounts, one issuance audit event with correct resource ID; restart preserves
  complete invoice list and audit.
- New `six-concurrent-voids-once-only`: exactly one 200 and five 409; read actual
  invoice/list to verify void, identity, deal/request IDs and retained amounts;
  one void audit event, restart state/audit, repeated void and reissue rejection.
  Failure response bodies are not assumed to have an undocumented schema.
- New `provider-conflicting-payload-two-local-stores`: accept P1 through A, enqueue
  conflicting P2 through fresh B against the same provider; invoke work without
  imposing an unspecified conflict exit/response format. Public provider truth
  must remain exactly P1 with its delivery ID, B must not claim delivered, and A
  remains delivered. Exactly two local stores are used by this group.
- Existing fresh-store provider replay now uses reordered nested object keys and
  compares full provider records/IDs, not merely acceptance count.
- Corruption group reaches status/enqueue/status and checks public pending state,
  then reports **inconclusive**: the contract supplies no authoritative filename.
  Marker presence cannot distinguish authoritative state from logs, backups or
  indexes. No guessed file is corrupted, no unbounded byte scan is performed,
  and no malformed-state acceptance assertion is claimed to have executed.
- Real kill group uses bounded delays 10/40/80/160 ms, overlapping replacement
  workers and external process-group SIGKILL. Counts live kills and missed windows,
  supplies two fresh jobs per trial (14 total) so later trials are not idle-only,
  drains at SAME logical time, checks all 14 jobs/deliveries, exact key/payload mapping,
  nonzero actual attempts, and preservation of already observed provider records.
  Genuine state violations still fail. If all state checks succeed the group is
  **inconclusive**, reporting kill/miss counts and unobserved claim/accept/write
  windows. A live runtime alone is not proof of durable ownership at death.
  Delays select kill windows only; they are not recovery leases or retry timing.

Existing groups retain authentication/roles/tenant isolation, deal validation and
state graph/version races, HALF_UP snapshots, identical-request idempotency,
restart and documented CRM v1 migration, causal audit/resource checks; Import
seed/group atomicity, input/run identities, interrupted resume, competing stock
and conservation; Dispatch semantic identities, provider truth, uncertain
reconciliation, logical retries, crash flags, workers/tenants and mixed payloads.
No genuine business assertion was softened beyond the two reviewed ambiguities.

## Bounded resources and cleanup

- Commands drain nonblocking stdout/stderr with selectors, at most 1 MiB per
  stream plus a read chunk, and a total 15s deadline. Infinite output is terminated
  as `harness_error`; deadline as `timeout`. Finally kills/reaps process groups
  and closes both pipes. No unlimited `communicate()` buffer remains.
- Startup reads at most 16 KiB + 1 per poll, retains at most 1 MiB stderr, checks
  output-file sizes, and has an 8s readiness deadline. Oversize is harness_error;
  silent live startup is timeout; exited/invalid startup is fail. Bounded rereads
  are used rather than an incremental framing framework.
- HTTP response reads at most 1 MiB + 1, with 5s socket timeout and a shutdown
  timer. Deadline-caused shutdowns are classified timeout. HTTP header parsing
  uses standard-library line/count bounds. Timer/socket/connection setup cleanup
  handles constructor/start failures; only started timers are joined.
- Temporary startup files are acquired inside cleanup protection; second-file
  allocation failure closes the first. Kill trials also check captured file sizes.
- **Limit:** startup and kill-trial stdout/stderr use regular temporary files.
  Size checks are sampled, not hard filesystem quotas: a very fast child can
  briefly exceed the disk budget between polls (or during bounded cleanup).
  Memory reads remain capped. POSIX process groups cannot contain deliberately
  detached descendants. No large containment framework or platform quota was
  added. Reaping has bounded waits; concurrent suite total time exceeds one
  command deadline by design.

## Remaining coverage limits

No authoritative corruption test, deterministic real-death ownership window,
or universal exactly-once claim is established. Crash flags test public recovery
but cannot prove internal abrupt death. Retry time is always caller logical time.
Interrupted Import group reasons are not fully cross-compared in the middle-resume
group; malformed short/long transfer rows and extra/whitespace seed cases remain
coverage gaps from REVIEW. Migration source/versioning and crash windows, missing
invoice failure-audit variants and voided replay lifecycle variants are not all
covered. No public Import transfer-ledger endpoint exists. Production caveats,
product test quality, hidden schema/layout, package choices and deployment are
not source-reviewed. Loopback requests do not prove absence of other listeners.

The sole SQLite access constructs the contract's CRM v1 fixture, explicitly closed
before startup. Product state is otherwise inspected through public HTTP/CLI.
Unspecified IDs, invoice/list/provider ordering, persistence filenames, conflict
response schema and lock mechanics are not invented. Audit and stock ordering
are specified and remain asserted. Temporary evidence is deleted; JSON diagnostics
remain, within bounded captured output.

## Self-test evidence

`python3 -W error::ResourceWarning -m unittest -v test_oracle.py` passes **17 tests**.
Tests cover schema/all five outcomes, unknown API/CLI cases, independent seeded
isolation/continuation, CLI JSON/nonzero, real helper process deadlines/cleanup,
infinite stdout, oversized stderr and newline-free startup, injected second-file
and timer-start failures, reports/assertions, six-worker helper, and per-group
entrypoint reachability/named fail results for all **59** groups using deliberately
broken error-only programs. These are harness tests, NOT valid-product acceptance
or successful execution of downstream business assertions in broken groups.
