# Local work planner

A command-line planner for one freelancer: projects, tasks, effort, priorities, due dates, dependencies, blocked view, a next-work suggestion, import/export and backup/restore. Python 3.10+ standard library only. Data stays local in SQLite.

## Start

```sh
./planner --help                       # all commands; state: data/planner.db (or --db / $PLANNER_DB)
./planner project add acme-site "Acme website"
./planner task add acme-site "Design" --estimate 4h --priority high --due 2026-10-20
./planner task add acme-site "Build" --estimate 1.5h --after 1
./planner blocked | ./planner next | ./planner overview
./planner task done 1
./planner backup                       # -> data/backups/planner-<utc>.json
./planner restore data/backups/<file>.json --yes
scripts/demo.sh                        # synthetic demo in .demo/
python3 -m unittest discover -s tests  # tests
```

Other commands: `project list|rename|delete [--yes] [--detach]`, `task edit|show|reopen|delete [--detach]`, `dep add|remove TASK PREREQ`, `list [--state open|ready|blocked|done|all] [--project]`, `export FILE|- [--project]`, `import FILE [--dry-run]`.

## Semantics (assumptions, reversible)

- **States:** `ready` (open, all prerequisites done), `blocked` (open, a prerequisite is open), `done`. A blocked task can't be marked done. You can only reopen a task if none of its dependents are done.
- **Dependencies** may cross projects. Cycles and self-dependencies are rejected.
- **Delete:** a task or project that others depend on is refused. `--detach` removes those links and lists each removed link. `project delete` with tasks only previews until you add `--yes`.
- **Priority:** `urgent > high > normal (default) > low`. **Due** is a plain date. **Estimate** accepts `90m`, `1.5h`, `2h30m`, or a bare number meaning hours.
- **Next suggestion** (only ready tasks), ordered by:
  1. overdue or due within 2 days
  2. priority
  3. earlier due date (undated last)
  4. unblocks more open tasks
  5. smaller estimate
  6. lower id

  "Today" means the local date; you can override it with `--today`.
- **Import** adds new projects all-or-nothing. If any project key already exists, nothing is imported. Ids in the file are file-local and get new numbers. **Restore** replaces everything with the backup (ids included) after full validation, and first writes a safety backup of the current state.

## Data format

JSON `{"format": "local-work-planner", "version": 1, "projects": [...], "tasks": [...]}`. Example: `examples/synthetic-portfolio.json`.

- **Project fields:** `key`, `name`, optional `created_at`.
- **Task fields:** `id`, `project`, `title`, plus optional `priority`, `estimate_minutes`, `due`, `note`, `done_at` (UTC), `created_at`, `depends_on` (ids within the file).
- **Rejected:** unknown fields, dangling references, cycles, and done tasks with open prerequisites.
- Backups and full exports also contain `exported_at` and `next_task_id`.

## Limits

- Single local user: concurrent CLI runs are serialized, but there's no sync.
- Every write rewrites the whole state, which is fine for a few thousand tasks.
- No automatic or scheduled backups, so your recovery point is the last `backup` you ran.
- Import can't update existing projects.
- Tested only on macOS with Python 3.14.
