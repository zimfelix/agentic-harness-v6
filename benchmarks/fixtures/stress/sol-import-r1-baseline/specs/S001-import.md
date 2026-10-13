# S001 – Recoverable inventory import

- **Status:** Implemented
- **Herkunft:** Confirmed direct Task Import, shipping mode.
- **Ziel und Nutzer:** Local operators transfer tenant-scoped stock safely across restart and concurrent processes.
- **Verhalten:** Public commands and CSV/JSON contracts in the confirmed task, implemented in full.
- **Nicht im Umfang:** Network, packages, real data, authentication, production deployment, deferred work.
- **Offene Fragen / Abhängigkeiten:** None blocking; docs/architecture.md and docs/testing.md describe delegated implementation choices.

## Akzeptanzkriterien

- **AK1:** Seed validates exact header, row shape, nonblank opaque names and ASCII decimal quantities 0..1000000, rejects duplicates/all invalid files atomically; once per tenant, including empty seeds; preserves initial/zero accounts and other tenants.
- **AK2:** Apply validates header before run creation. Groups include nonadjacent rows in first-appearance order; rows in file order; invalid rows (including blank group) reject their entire group, continue independent groups, allow within-group credits, never negative stock, conserve per-SKU totals.
- **AK3:** Transfer IDs are unique within a file/run; every group containing any duplicated ID rejects regardless of order. Same IDs in other runs are allowed.
- **AK4:** Identity is tenant/run-id plus exact bytes. Same bytes resume or replay stored completed counts/errors; different bytes conflict without mutation; new ID with same bytes is a new intended transfer.
- **AK5:** Failpoint N>=1 terminates nonzero after N durable decisions in this invocation, including last group. Reports are cumulative and atomic with stock/ledger; resume never repeats or changes decided groups. replayed true only when already completed before invocation's run registration.
- **AK6:** Identical concurrent invocations produce once-only movement; distinct contending runs cannot overspend stock; bounded busy waiting and explicit technical errors.
- **AK7:** CLI outputs one JSON value per invocation, domain/input conflicts nonzero; honest completed/interrupted reports with counts and nonblank errors; stock sorted with zero accounts, runs stored reports, both tenant-scoped and empty for unknown tenants.
- **AK8:** Versioned schema migration and recovery strategy documented and tested on empty/built state; tests use isolated synthetic files within project only.

## Prüfplan

Full unittest suite at CLI boundary, including subprocess concurrency and process-death failpoint, parser unit boundaries, SQLite ledger/stock consistency, migration/backup restore and bounded locks. Every AK mapped to concrete tests at completion. Harness ready/go and final structure checker; intentional wrong test assertion to demonstrate detection. No production filesystem/power-loss claims.

## Arbeitsstand

- **Erledigt / ausstehend:** Full CLI, versioned schema, atomic groups/ledger/counters, resumable identity, process-death failpoint, tenant queries, operator README and 24 regression tests complete. No requested work outstanding.
- **Blocker:** None for local synthetic MVP. Production limits in README remain outside this task.
- **Nächster Schritt:** Future sessions read this spec and architecture, run full regression before changing behavior. Do not change deferred work or harness rules.

## Nachweise

Current uncommitted project state, verified 2026-10-09 on Python 3.14.7; no git operations used.

- **AK1:** `test_seed_scope_once_and_opaque_names`, `test_seed_invalid_is_all_or_nothing`, `test_empty_seed_and_unknown_tenant`, `test_bad_header_no_run_or_seed`, `test_numeric_boundaries` — passed.
- **AK2:** `test_nonadjacent_atomic_groups_and_credit_chaining`, `test_last_row_failure_rolls_back_destinations_and_ledger`, `test_invalid_groups_continue_and_blank_group_combines`, `test_multi_sku_conservation_and_ordered_stock` — passed against CLI/SQLite.
- **AK3:** `test_duplicate_ids_invalidate_all_groups_independent_of_order`, `test_malformed_row_duplicate_still_rejects_earlier_group`, `test_exact_bytes_replay_conflict_new_run_and_tenant` — passed.
- **AK4:** `test_exact_bytes_replay_conflict_new_run_and_tenant`, `test_completed_rejected_replay_keeps_decisions`, `test_crash_resume_cumulative_and_last_group` — passed.
- **AK5:** `test_crash_resume_cumulative_and_last_group`, `test_fail_after_n_groups_and_empty_apply`, `test_resume_does_not_reconsider_rejection_after_stock_changes`, `test_uncommitted_process_death_rolls_back` — passed with real process termination and ledger checks.
- **AK6:** `test_parallel_identical_once_only` (8 processes/20 groups), `test_parallel_distinct_runs_cannot_overspend` (10 processes/5 stock), `test_parallel_seed_one_winner_and_fresh_db_migration`, `test_busy_wait_is_bounded_and_recovers`, `test_transient_lock_wait_retries_in_sqlite` — passed.
- **AK7:** `test_json_argument_errors_help_and_file_errors`, scope/sort tests, completed/rejected/interrupted/replayed reports above — passed; `python3 app.py --help` emitted one JSON help object, exit 0.
- **AK8:** `test_parallel_seed_one_winner_and_fresh_db_migration`, `test_backup_restore_and_migration_version_on_populated_state` — passed: initial migration, retained populated v1, unknown newer version rejected without changing version/ledger, backup and interrupted resume on restored copy. No older populated product schema exists yet.
- **Pflichtchecks / Regression:** `python3 -m unittest discover -s tests -v`: 24 tests passed in 17.408s. Intentional runtime mock making quantity always zero caused the numeric test to fail (detector verified, no persisted code mutation). `python3 tools/check-harness.py --ready` and `--go` passed; these check document structure/init only.
- **Not executed / limits:** hardware power-loss, network filesystem, huge-file load, cross-platform production release/security validation. No production durability/auth claim; no packages/network/real data/providers used.
