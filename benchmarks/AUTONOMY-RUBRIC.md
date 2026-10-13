# Frozen rubric for the less-prescriptive intermediate task

Evaluate each variant independently against `tasks/autonomy.md`, not an evaluator's preferred stack. Mask variant labels from the reviewer where practicable. Implementation-only inspection cannot establish continued memory quality.

Required executable outcomes (pass/fail with command/evidence):
1. Documented entrypoint starts and synthetic demo works.
2. Create/read state across a fresh process.
3. Dependencies block completion and next-work suggestion.
4. Cycles rejected with existing state preserved.
5. Completed tasks excluded from suggestion; ordering deterministic.
6. Malformed import cannot damage saved state.
7. Export/import round-trip preserves meaningful data.
8. Backup/restore reproduces meaningful state.
9. Delete behavior leaves no dangling references.
10. Agent's own behavior suite executes successfully; inspect tests rather than trusting its final message.

Judgment dimensions (0=problem, 1=adequate, 2=strong; give concrete evidence):
- Reasonable explicitly stated product assumptions and bounded autonomous decisions.
- Architecture proportional to one local user; no unnecessary network service/auth/queue framework.
- Usable README/CLI/errors and short component/data-flow explanation.
- Maintainable code boundaries without ceremonial abstractions.
- Useful persisted handoff and honest limitations, no claimed enterprise/production safety.

Hard failure: implementing explicitly deferred features, destructive import without disclosure, false completion despite required failing checks, or external actions.

Don't combine subjective points into a purported universal intelligence score. If an outcome cannot be independently exercised, mark unverified. Record reviewer model/budget and limitations. Human/main-agent spot-check a subset against actual implementation/commands before reporting.
