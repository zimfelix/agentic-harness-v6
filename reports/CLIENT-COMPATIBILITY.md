# Pi and Claude: one content source

**Nachtrag 2026-11-01:** `--claude` wurde durch `--with-skills` ersetzt. Standard ist jetzt: keine Skill-Kopie im Projekt, Skills kommen über globale Links auf `harness/.agents/skills/` dieses Repos (siehe README). Befehle unten sind darauf angepasst; die Alias-Beschreibung gilt für `--with-skills`.

Integration and skill-catalogue consolidation were added after freezing the main compared harness. Risk rules are preserved by parity tests; loading paths/packaging changed. This is independently tested export/start tooling plus a supplementary initialization probe, not a new broad model-performance claim.

## Paths matter

- Pi discovers `AGENTS.md` and `.agents/skills/<name>/SKILL.md` natively.
- Claude Code's documented project location is `.claude/skills/<name>/SKILL.md`. Do not assume `.agents/skills` is natively advertised to Claude.
- Claude Code does not automatically apply project `AGENTS.md` in the same way as Pi. A project `CLAUDE.md` copy is deliberately NOT maintained.

```sh
# New/empty project; skills come from the global links:
python3 tools/export.py /path/to/project

# Only without global links (cloud, other machine): bundled copy + Claude aliases
python3 tools/export.py /path/to/project --with-skills

# Pi: normal discovery.
python3 tools/launch.py --project /path/to/project --client pi

# Claude: explicitly append the current AGENTS.md; normal native skill discovery.
python3 tools/launch.py --project /path/to/project --client claude

# Inspect startup without a model call:
python3 tools/launch.py --project /path/to/project --client claude --dry-run
```

`--with-skills` copies the skills and adds one relative directory symlink per skill:

```text
.agents/skills/business-software/   ← risk references, single source
.agents/skills/website-tools/      ← website knowledge/scripts/assets, single source
.claude/skills/<name>              → ../../.agents/skills/<name>
AGENTS.md                         ← sole project working agreement
```

Aliases contain no second rule text; edits need no synchronization. No global directory/configuration is touched. Native clients still require appropriate trust/permissions; the wrapper does not bypass them. Without `--with-skills` or the global links, direct SKILL.md paths in AGENTS remain readable, but native Claude skill discovery must not be claimed. There is no separate profiles directory in the final template.

## Limits and checks

- Export tests check alias resolution stays inside the exported project and points to the canonical source; verify no `CLAUDE.md` or copied skill exists.
- Launcher tests verify it reads CURRENT AGENTS.md on each start and preserves client arguments. It does not cache or duplicate the file.
- macOS/Unix symlinks are the supported alias mechanism. Other environments may require symlink privileges; export fails rather than silently copying. Windows not tested.
- Comparisons used isolated Pi with native skill loading disabled equally, or isolated Claude with AGENTS explicitly appended and customizations disabled. Those backend comparisons do not test automatic website-skill selection.
- Initial native Claude trial's Bash failed because its internal temporary directory was outside the test write boundary. `CLAUDE_CODE_TMPDIR` now uses the allowed per-run directory. An actual Bash/Python write/read smoke test passed after correction. Initial runs remain in the report and are not relabeled successful autonomous builds.

Sources checked locally during the review: [Claude skills locations and symlinks](https://code.claude.com/docs/en/skills#where-skills-live), [Claude CLI flags](https://code.claude.com/docs/en/cli-reference), installed Pi `docs/skills.md` and `docs/configuration.md`. CLI versions/environment and actual comparison outcomes are recorded in the results.
