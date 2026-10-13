# Project starter — Agentic Harness V6

Describe the desired outcome and delegated scope. The agent reads `AGENTS.md` and `PROJECT.md`, briefly reflects the intended workflow/boundaries, resolves consequential ambiguity and works toward observable acceptance checks. No separate init checker, mandatory questionnaire or extra approval for already clear/delegated work. A fresh chat in this project should use the active work record linked from PROJECT; its next action is not necessarily just another test run.

After the first implementation, replace this file with the product's purpose, actual setup/start/test commands and known limitations.

Risk references and optional website tooling live in `.agents/skills/`; there is no separate profiles catalogue. `AGENTS.md` gives explicit loading triggers, so relevant risk guidance does not rely solely on optional skill detection. No extension or npm installation is needed. For Claude, export with `--claude` and use the repository's `tools/launch.py` to load this project's AGENTS.md without a CLAUDE.md copy.
