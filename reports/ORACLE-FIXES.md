# Oracle fixes

## Files changed

- `oracle.py`: added `outcome` to every result with pass/fail/inconclusive/timeout/
  harness_error; kept `passed` true only for pass. CLI still exits nonzero on
  incomplete evidence; unknown CLI/API case now returns structured harness_error.
  Assertion/response-shape failures remain fail; setup/resource failures are
  harness_error; watchdog deadlines are timeout.
- Accepted 400/404 only for the fabricated missing invoice deal reference;
  returned foreign references retain strict 404. Removed only void's arbitrary
  extra-field rejection assertion; reason, tenant, business state and audit
  assertions remain mandatory.
- Removed marker-based corruption targeting and unlimited file scans. Public
  enqueue/state checks run, then corruption reports inconclusive because no
  authoritative path is established. No inferred log/index corruption is scored.
- Added independent six-distinct-request issuance and concurrent-void groups:
  exact success/conflict counts, actual invoice/list state, amounts, audit event
  cardinality/resource IDs, and restart persistence. Added provider conflict
  across two local stores with one independent provider: inspect durable payload,
  delivery ID and local status without assuming conflict response/exit format.
  Existing fresh-store semantic replay now verifies full provider records/IDs.
- Real SIGKILL trials now use 10/40/80/160ms delays, overlapping two replacement
  workers, two fresh jobs per trial (14 jobs total), bounded same-time drain,
  public job/key/payload/attempt checks and preserved provider identities.
  Missed kills are not failures. Successful recovery remains inconclusive with
  live-kill/miss counts because ownership/write/accept windows are unobserved.
- Replaced command communicate buffering with selector-based bounded drains:
  1MiB per stdout/stderr plus one chunk, overall deadline and group cleanup.
  Startup line reads bounded to 16KiB+1; sampled file-size budget and 1MiB stderr
  diagnostics. HTTP response bounded to 1MiB+1 and deadline shutdown classified.
  Kill trial output files also checked against byte budget.
- Exceptional startup acquisition now closes the first temporary file when the
  second fails. Socket/connection/timer construction and timer-start failures
  close resources, with joins only for started timers.
- `test_oracle.py`: expanded from 13 to 17 tests, including all outcome values,
  unknown CLI/API harness errors, new-group registration, infinite/oversized
  output, oversized newline-free startup, injected file/timer setup failures;
  broken-dummy tests now verify entrypoint reachability separately for EVERY
  group, plus named fail outcomes (59 groups: CRM 20, Import 18, Dispatch 21).
- `QA-NOTES.md`: replaced obsolete binary scoring/counts/corruption/kill claims
  with current schema, behavior, budgets, coverage and limitations.

Public tasks and `REVIEW.md` were not edited. No product implementations were
created or evaluated. Error-only dummy entrypoints are harness fixtures only.

## Tests

Ran the requested command three times:
`python3 -W error::ResourceWarning -m unittest -v test_oracle.py`.
All runs: **17 tests passed**, in 7.266s, 6.882s and 7.070s respectively.
The final run includes the fresh-work kill-trial refinement.

## Limits

- Incomplete evidence deliberately keeps CLI exit 1 / passed false. Consumers
  must use outcome, not binary flags, to count observed product violations.
- Corruption authority is unavailable from the public contract; corruption is
  not executed. Real external kill ownership/accept/write windows cannot be
  proven from public APIs; successful state checks are not comprehensive coverage.
- Startup/kill files have sampled size checks, not hard disk quotas; fast writers
  may exceed disk budget between polls or during bounded cleanup. Reads/memory
  retention are bounded. No new sandbox/quota framework was introduced.
- Operational deadlines are not contractual performance limits. POSIX session
  cleanup cannot contain deliberately detached descendants.
- No valid-product acceptance evidence exists. Broken-dummy tests prove group
  reachability and result containment, not all downstream business assertions.
- Remaining REVIEW coverage gaps (Import malformed rows/interrupted reasons,
  migration/lifecycle/failure-audit variants, documentation/source requirements)
  are explicitly listed in QA-NOTES, not silently scored as covered.
