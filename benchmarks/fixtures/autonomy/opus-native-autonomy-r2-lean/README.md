# Local work planner

A single-user, local command-line planner for freelance projects. It tracks projects and tasks with effort estimates, priorities, optional due dates and dependencies. It shows what is blocked, refuses to complete work whose prerequisites are open, suggests what to do next and keeps JSON backups. It needs only Python 3 (standard library), with no packages and no network access. Tested with Python 3.14 on macOS. The file lock uses `fcntl`, so it runs on macOS/Linux but not native Windows.

## Start

```sh
python3 planner.py --help             # or: python3 -m planner --help
python3 planner.py project add "Website relaunch"
python3 planner.py task add "Website relaunch" "Write copy" --estimate 3h --priority high --due 2026-10-20
python3 planner.py task add p1 "Publish" --after t1
python3 planner.py next               # what to do now, with reasons
python3 planner.py blocked            # what waits for what
python3 planner.py overview [p1]      # all projects, or one project with its task table
python3 planner.py task done t1
```

State lives in `data/planner.json` next to `planner.py`. Override it with `--data PATH` or `PLANNER_DATA`. `--today YYYY-MM-DD` (or `PLANNER_TODAY`) fixes "today" for due-date logic.

| Command | Purpose |
|---|---|
| `project add/list/edit/delete` | Projects are referenced by id (`p1`) or by their unique name |
| `task add/edit/show/list/done/reopen/delete` | `task list --status ready\|blocked\|done\|open --project P` |
| `task depend T1 T2,T3` / `task undepend` | T1 can only be done after T2 and T3 |
| `blocked`, `next [--project P] [--limit N]`, `overview [P]` | Views |
| `export [--out FILE]`, `import FILE --replace\|--merge [--dry-run]` | JSON exchange, see [docs/data-format.md](docs/data-format.md) |
| `backup`, `backups`, `restore FILE\|--latest` | Recovery (backups go to `data/backups/`) |

## Rules and assumptions

- **Priorities:** `critical > high > normal > low`. **Estimates:** whole minutes, entered as `2h`, `90m`, `1h30m` or `1.5` (hours). **Due dates:** plain local calendar dates.
- **Completion:** a task is *blocked* while any prerequisite is open, and `done` is refused. A done task can only be reopened after the done tasks that depend on it are reopened. Done tasks cannot get new open prerequisites.
- **Cycles,** including self-dependencies, are rejected when you add or edit a dependency and when you import or restore data.
- **Deletion** never leaves broken references. Deleting a task or project that other tasks depend on is refused unless you pass `--detach`, which removes those dependencies and lists them. Deleting a project that has tasks needs `--yes` and writes a backup first.
- **`next`** only suggests *ready* tasks (open, all prerequisites done). Each one inherits the highest priority and earliest due date of the open work it unblocks. That way, prerequisites of urgent work come first. Ordering:
  1. Urgent tasks (overdue or due within 2 days), by due date, then priority.
  2. All other tasks, by priority, then due date.
  3. Ties go to the task that unblocks more work, then the smaller estimate, then the lower id.

  Each suggestion shows its reasons.
- **Import** is all-or-nothing. An invalid file is fully reported and changes nothing. Import, restore and project deletion back up the previous state automatically. If the state file itself is corrupt, commands stop without overwriting it. `restore` recovers it and keeps a raw copy of the corrupt file.
- **Every command** locks the data file, validates the whole state and writes atomically (temp file + fsync + rename).

## Test and demo

```sh
python3 -m unittest discover -s tests -v   # behavior tests (mostly real CLI subprocesses)
sh examples/demo.sh                        # synthetic end-to-end demo in .scratch/demo/
```

`examples/sample-project.json` is a synthetic fixture: 2 projects and 8 tasks, with a dependency chain, a completed task and blocked tasks.

## Limitations

- Single-user local tool. Backups are never pruned automatically, so delete old files in `data/backups/` yourself.
- No undo apart from backups.
- The whole state is rewritten on each change. That is fine for hundreds or thousands of tasks, but it is not designed for very large data.
- There is no schema migration yet (`schema_version` 1 only).
- Backups sit on the same disk as the state. Copy them elsewhere if you need protection against losing the disk.
- Timestamps (`created`, `done_at`) are informational UTC values. Planning uses only calendar dates.
