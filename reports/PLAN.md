# Pre-registered comparison plan

Written before trial product implementations or acceptance results. Objective: the smallest useful harness for intermediate software projects, not an enterprise process standard.

## Variants and attribution

- Baseline: exported v6.1, source commit `dc1af55e0a4abc4be73ddc982ed8c2dc8b8de34a` of `zimfelix/agentic-harness-v6`.
- Candidate: `template/`, frozen into a content-hashed snapshot before runs. Short working agreement + PROJECT; coherent specs; optional ideas/docs; risk-triggered business references; static website tooling as one portable skill. No mandatory init checker, complete opt-out catalogue or document-maintenance protocol on every Markdown edit.
- This is a whole-package comparison, not a causal test of each removed sentence. Wording/language, structure and documentation obligations differ. Profiles-to-skills packaging is not isolated by backend tasks.

## Trials

Three demanding backend contracts, NOT model-specific instructions: tenant-safe CRM/invoicing/audit and legacy migration (Python/SQLite); atomic resumable inventory groups (Python/SQLite); durable process-safe dispatch with provider uncertainty and retry timing (Node.js). Each receives identical task text, tool access, fresh context, synthetic data, time budget and model/settings within each pair. Use gpt-6.1-sol medium; independent repetitions if quota allows. Both are given enough authority to implement, but not a prescribed implementation architecture.

A separate less-prescriptive intermediate-project brief checks whether the agent can choose scope/layout/storage and state assumptions without enterprise machinery. It uses a prewritten outcome/rubric, not claims that one exact architecture is correct. Opus 5.5 is available, but remaining Anthropic weekly quota is low: a matched pair only if feasible; no inference from Codex performance to untested Opus outcomes.

Each main first build receives 900 seconds. Do not continue an unfinished run invisibly: timeout is recorded; any fresh-session continuation is a separate phase with its own budget/results. No manual product fixes by the harness author. Alternate run ordering and use fresh directories. Repeated seeded acceptance checks do not count as independent agent repetitions.

## Independent acceptance

Public contracts are frozen in `benchmarks/tasks/`. Independent QA author receives only those contracts, not either harness/candidate code. Hidden tests call public CLI/HTTP interfaces; direct DB access only creates the specified legacy migration fixture. Hidden tests are not readable by trial agents. Tests include malformed input/no mutation, tenant/role boundaries, persistence, competing OS processes, group atomicity, idempotency vs new intent, crash recovery, financial rounding and provider uncertainty. Every group must actually run; no skip-to-success.

Validate oracle helper/failure detection and have a second reviewer compare it to the contracts. Any discovered oracle error is documented and both variants re-evaluated identically. A buggy implementation failing the oracle is not automatically evidence that the oracle is correct.

Later phases: resume from project files with no conversation; meaningful requirement change with regression; deliberately unavailable real provider evidence. Preserve deferred work, truthfully expose blockers. Keep initial/continuation/change results separate.

## Measurements and decision rule

Primary: independent acceptance failures, integrity/security failures, false completion, unauthorized work and required human intervention. Secondary: wall time, uncached input, output, cache read/write, tool calls, documentation/read burden. Provider usage is not a direct currency cost or context-window size. Timeout stream usage may be incomplete. Record infrastructure/model failures separately.

Recommend candidate only if no observed material quality regression in completed comparable pairs, while genuinely simplifying recurring context/maintenance. A mixed result yields a qualified recommendation, not a forced winner. One or two samples per cell cannot establish statistical equivalence or universal safety. Recommend real-project follow-up regardless.

## Isolation and publication

Separate temporary projects; no shared writers, global instructions/extensions/skills/MCP disabled equally. Explicit risk references remain reachable. macOS sandbox limits writes to each project/run output and denies reads of oracle/source snapshots/other trials. This is NOT full read or network isolation: model transport needs network. No real application credentials/data/providers. Trial secrets are temporary, mode 0600, removed after execution. Raw events/reasoning stay local and are not published. Sanitized counts, failures, provenance and selected synthetic product artifacts may be published privately for reproducibility.

Check CodexBar before batches. Below 10% remaining, stop launching more Codex work and attempt one user-authorized free reset via CodexBar; verify counters before resuming. No paid extra usage activation. Anthropic quota is independent and has no assumed reset credits.
