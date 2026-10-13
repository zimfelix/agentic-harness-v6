# Harness V6 Next — repository maintenance

This repository contains a candidate template and its evaluation, not a product waiting for initialization.

- `template/` is the exportable product harness. Its instructions apply to projects exported from it, not to repository maintenance.
- `benchmarks/tasks/` contains the public, versioned task contracts. Freeze them and the candidate before trials.
- `benchmarks/` contains independent acceptance tests and orchestration. Trial agents must not read hidden acceptance code or other trials.
- `tests/` checks the harness tools and benchmark mechanics. These tests do not prove agent quality.
- `reports/` contains sanitized results, limitations, provenance and the recommendation; no credentials or raw model reasoning.
- `learning-state.md` contains short, unconfirmed local findings until reviewed.

Mode: shipping with concise explanations. Authorized scope: improve the harness, build and execute fair comparisons, and publish to the requested separate private GitHub repository. Do not modify the original v6 repository or global agent configuration.

Preserve genuine failures, timeouts and interventions in results. Never relax an acceptance test to make a candidate win. Correct an objectively wrong oracle against the public contract, document it and re-evaluate both variants. Compare identical model/settings/tools/budgets per pair. No destructive or real business actions.
