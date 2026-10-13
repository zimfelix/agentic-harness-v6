# Business software — risk routing, not an architecture

Read when changing business logic, persistent data, permissions or external effects. Choose only the relevant sections; no catalogue of everything the project does NOT do. Record project-specific semantics, not a copy of this checklist.

| Actual risk | Targeted reference |
|---|---|
| Schema, concurrent writes, money or time rules | `references/daten-geld-zeit.md`, relevant section only |
| Imports, batches, deduplication, restartable jobs | `references/importe-und-jobs.md` |
| Roles, tenant isolation, personal data/audit | `references/rechte-und-nachvollziehbarkeit.md` |
| External effects, uncertain outcomes, persistent operation | `references/seiteneffekte-und-betrieb.md`, relevant section only |
| Actual accounting/legal documents | `references/buchhaltung.md`; project requirements need confirmation |

Protect the applicable invariants: atomic business mutations, authorization at the authoritative boundary, tenant isolation, honest failure status, safe replay and explicit uncertainty after external effects. Use synthetic test data and local fakes/sandboxes unless real access is specifically authorized.

Choose the simplest architecture that makes the nontrivial rules testable. CRUD needs no mandatory domain/service/repository stack. Framework defaults are a good starting point. Clarify product-specific identity, state transitions, rounding, deletion and permission semantics when consequential; the agent can choose routine implementation techniques.

Deep procedures belong in reusable skills/tools only when they actually save repeated work. These references capture risk constraints, not a mandatory sequence of engineering steps. Source lineage and evidence live in the template repository report, not in every product's initial context.
