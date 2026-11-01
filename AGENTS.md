# Harness V6 — repository maintenance

This repository is the single source of the agentic harness and its own skills, plus their evaluation. It is not a product waiting for initialization.

- `harness/` is the exportable product harness; its instructions apply to exported projects, not to repository maintenance. `harness/.agents/skills/` holds the own skills, linked globally and never copied into projects by default.
- `tools/` exports (`export.py`), updates existing projects (`update.py`), collects project learnings (`learnings.py`) and counts skill usage (`skill_usage.py`).
- `benchmarks/` contains task contracts, independent acceptance tests and orchestration. Trial agents must not read hidden acceptance code or other trials.
- `tests/` checks the harness tools and template invariants. These tests do not prove agent quality.
- `reports/` contains sanitized results, limitations and provenance; no credentials or raw model reasoning.
- `learnings.md` holds this repository's own open observations, in the same format as project learnings.

Own skills and the harness stay project-neutral: no example designs, screenshots, client names or project values. Such material lives in the project it came from (e.g. `docs/inspiration/`).

Mode: shipping with concise explanations. Global agent configuration (`~/.claude/CLAUDE.md`, `~/.pi/agent/AGENTS.md`) changes only on Felix's explicit request. No commits or pushes unless requested.

## Reviewing and adopting learnings

Before harness or skill work, run `python3 tools/learnings.py` and go through new open entries with Felix. Adopting is a review loop, not a fixed recipe; no rule here forces text to be replaced or removed.

```text
entry → 1 classify → 2 draft → 3 review loop ──all yes──▶ 4 adopt → 5 close entry
                                    ▲         │
                                    └─ revise ┘   unclear → ask Felix
```

1. **Classify.** Is it a harness problem at all, or a single incident, a project-specific matter or unclear project instructions (then keep local or reject)? If it is a harness problem, where does it belong: a skill reference (loaded on demand), a skill body, or the core? Most learnings belong in a skill or stay local; the core is the exception for working-agreement problems seen in more than one project.
2. **Draft.** Write the shortest general wording that would have prevented the problem. No project names, histories or examples unless they are the rule itself.
3. **Review loop**, repeated until every answer is yes:
   - Does it make sense as a general rule, not only for this one case?
   - Is it free of repetition, i.e. not already said elsewhere? If something similar exists, sharpen that text instead of adding a second version.
   - Is the wording precise and unambiguous, and consistent with the other rules?
   - Is it categorized correctly, so that not everything ends up in `AGENTS.md`?
   - Does the target file stay focused and readable instead of growing out of proportion? Replacing or merging text is an option when it improves precision, never an obligation.
   - Where the problem is checkable: is there a test or fixture that would have caught it?
4. **Adopt.** Commit with the learning's title, run the full suite and roll out with `tools/update.py`. There is no fixed size limit. `tools/learnings.py` shows the core size; when it grows (roughly above 6,000 characters for `harness/AGENTS.md` plus `PROJECT.md`), review the core's quality: repetition, lines that belong in a skill or reference, imprecise wording. Shorten only where that review finds it.
5. **Close.** Mark the project entry `übernommen (v6 <commit>)`, delete it there and remove project rules the harness now covers.

Preserve genuine failures, timeouts and interventions in benchmark results. Never relax an acceptance test to make a candidate win. No destructive or real business actions.
