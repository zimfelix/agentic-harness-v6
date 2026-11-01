# Harness refinement from the Lexware pilot

Scope: repository maintenance on `feat/lexware-crm-pilot`. User explicitly requested review/implementation of useful local learnings; no original-v6 or global-instruction changes in this update. Existing Lexware product files are not upgraded or overwritten.

## Reviewed findings and decisions

| Pilot finding | Implementation decision |
|---|---|
| Technically sound demo, but initially assumed a compulsory appointment flow rather than clarifying the Lexware business goal | Make concise reflection of outcome/workflow/boundaries explicit before a new project, long new task or consequential decision; check request clarity as well as current architecture facts before binding specs/code |
| Existing autonomy rule was contradicted by an invented approval gate; continuation record named only a regression command | Preserve autonomy; require the next authorized action or genuine blocker plus an entry command in ONE active record linked from PROJECT |
| Separate project/background agent was not obvious enough to the user | Announce repository/path and visible/background execution changes before acting |
| Integration roles were unclear | PROJECT distinguishes input sources, provider-owned functions and project-owned actions; no provider-specific core rules |
| One coherent local spec and an optional later roadmap were enough | Keep specs/ideas optional by actual need; no mandatory Idea, new Init document or duplicated work log |
| SQLite/schema/error-handling defects were caught by boundary tests | Keep risk routing and public-boundary verification; no new universal implementation rule for each defect |
| Lexware onboarding, money/document semantics and real-provider limitations | Stay project-specific and use existing relevant business-skill references |

The central distinction is functional intent versus implementation details. Architecture/stack delegation is not permission to silently choose a different business workflow. Clear/delegated requests still proceed without another approval ritual; already settled facts need not be asked again.

## Changes

- `harness/AGENTS.md`: concise intent check, execution-context transparency, concrete continuation semantics.
- `harness/PROJECT.md`: main workflow, integration responsibilities, one active record pointer.
- `harness/specs/README.md`: next implementation action versus mere regression command; completed local milestone versus remaining product goal.
- `harness/README.md`: starter/continuation explanation, without another initialization layer.
- `tests/test_template.py`: exported instruction-content regression, explicitly not an LLM-quality test.

AGENTS + PROJECT remain below the existing 6000-character test limit (5743 characters). Two skills and their risk references remain unchanged. Exporter/client integration is unchanged; an existing project is never automatically re-exported.

## Evidence and limits

The preceding visible Lexware session really was fresh, but received `continue` **and** a later business clarification, and started with existing uncommitted partial code. It completed a synthetic local milestone; reviewer reran 44 product tests, 21 separate CLI checks, six mutations and Brave. This supports practical continuation in that setting, not a clean sole-continue or causal harness comparison.

The new wording was added afterward. Historical `reports/RESULTS.md` and benchmark contracts/results remain frozen; they do not establish effectiveness or token savings of this refinement. Only technical/export/content checks are being applied here. A new, explicitly arranged visible agent trial is needed to test whether the stronger intent cue actually prevents the observed misunderstanding.
