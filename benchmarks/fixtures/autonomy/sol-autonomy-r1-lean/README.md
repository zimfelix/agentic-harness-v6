# Local work planner

An offline, single-person project/task planner. Python **3.10+**, standard library only; no installation, server or network. Run commands from this repository. Output is readable JSON; failures go to stderr with nonzero exit status. `--help` works at both command levels.

## Start

```sh
python3 planner.py --help
python3 planner.py project-add 'Sample work' --id sample
python3 planner.py task-add sample 'Draft concept' --id draft --estimate 90 --priority 4 --due 2030-04-03
python3 planner.py task-add sample 'Review concept' --id review --estimate 30 --depends draft
python3 planner.py overview
python3 planner.py next
python3 planner.py done draft
python3 planner.py next
```

The default database is `.planner/planner.sqlite3`, relative to your current directory. Use `python3 planner.py --db path/to/state.sqlite3 COMMAND ...` to select a different database; keep the flag before the command. Parent directories are created. Use the same path on later invocations. Empty databases start automatically. IDs can be supplied or are generated and returned by add commands.

## Commands

| Command | Arguments/options |
|---|---|
| `project-add` | `NAME [--id ID]` |
| `project-edit` | `ID NAME` |
| `project-delete` | `ID` (must be empty) |
| `task-add` | `PROJECT_ID TITLE [--id ID] [--estimate MINUTES] [--priority 1..5] [--due YYYY-MM-DD] [--depends TASK_ID]` (repeat `--depends`) |
| `task-edit` | `ID [--title TITLE] [--project PROJECT_ID] [--estimate MINUTES] [--priority 1..5] [--due YYYY-MM-DD \| --clear-due]` |
| `depend` / `undepend` | `TASK_ID PREREQUISITE_ID` (add/remove an edge explicitly) |
| `done` / `reopen` | `TASK_ID` |
| `task-delete` | `ID` (must not be referenced, even by done tasks) |
| `overview` / `next` | `[--project PROJECT_ID]` |
| `export` / `backup` | `FILE [--overwrite]` |
| `import` / `restore` | `FILE --replace` |

## Rules and practical suggestions

- Effort is nonnegative integer **minutes** (default 0 = unspecified/no estimate); remaining effort is a sum of unfinished task estimates, not a calendar forecast.
- Priority ranges from 1 (low) to 5 (high), default 3. Dates are optional date-only calendar deadlines, not timestamps; there is no timezone/reminder behavior.
- A task is **done**, **blocked** by any unfinished direct prerequisite, or **ready**. Dependencies can cross projects. Chains are enforced by validating every completed task's prerequisites. Missing references, duplicate edges, self-edges and cycles are rejected.
- Completing blocked work fails. Reopening work that a completed task relies on also fails: reopen the dependents first. Dependency edits cannot invalidate completed work.
- Deletion never cascades. Remove edges explicitly before deleting referenced tasks, and delete/move tasks before deleting a project.
- `next` considers only ready unfinished tasks: highest priority first, then earliest due date (undated last), shortest effort, finally lexicographic ID. This is deterministic, with no hidden current-date weighting. An overdue lower-priority task does not outrank a higher-priority one. A project filter narrows candidates, not prerequisite evaluation. No candidate produces `"task": null`.
- Overview includes blockers, status counts, total/remaining estimated minutes and all task fields per project. There is no scheduling, time tracking or automatic dependency completion.

## Portable format, import and recovery

`examples/synthetic.json` is the full example fixture (two projects, seven tasks). Minimal schema example:

```json
{
  "version": 1,
  "projects": [{"id": "practice", "name": "Synthetic practice"}],
  "tasks": [{
    "id": "draft", "project_id": "practice", "title": "Draft sample",
    "estimate_minutes": 60, "priority": 3, "due": null,
    "done": false, "dependencies": []
  }]
}
```

All fields shown are mandatory; no unknown fields. Version must be integer 1, `done` a JSON boolean; IDs are 1–64 ASCII letters/digits/underscores/hyphens, beginning alphanumeric. Project IDs are unique among projects and task IDs among tasks; names need not be unique. Titles/names must contain non-whitespace text. Duplicate JSON keys, IDs or dependency edges fail. Dates must be real, zero-padded `YYYY-MM-DD` dates. Dependencies refer to task IDs anywhere in the document; array order has no semantic effect.

**Import and restore replace the entire saved state, never merge.** `--replace` acknowledges this destructive scope. Invalid input commits nothing. Replaying the same document yields the same state without duplicates. Success reports project/task totals; failure reports a reason and no partial work is saved. Back up first if you want to retain current work:

```sh
python3 planner.py backup examples/my-backup.json
python3 planner.py import examples/synthetic.json --replace
python3 planner.py export examples/my-export.json
python3 planner.py restore examples/my-backup.json --replace
```

Backup and export share the same versioned portable JSON format. Output uses a flushed temporary file followed by atomic publication; existing files require `--overwrite`. The database and SQLite sidecars are protected from export overwrite. Keep backups under a different filename from imports you wish to retain.

Recovery: restore a valid backup into the original path, or, if the SQLite file itself is corrupt/unreadable, use a **new path**:

```sh
python3 planner.py --db .planner/recovered.sqlite3 restore examples/my-backup.json --replace
python3 planner.py --db .planner/recovered.sqlite3 overview
```

A malformed stored JSON document can be restored in place. A physically corrupt SQLite file cannot; keep it for diagnosis and recover into a new database. Backup loss window is all changes since the last backup; there are no automatic backups or history. Backup JSON has no cryptographic authenticity guarantee. SQLite transactions serialize local writers (10-second wait, then explicit failure) and roll back interrupted mutations. No schema migration beyond version 1 is implemented: retain a portable backup before future upgrades.

## Executed behavior checks and demonstration

```sh
python3 -m unittest discover -s tests -v
python3 examples/demo.py
```

Tests launch the actual CLI in fresh processes and check persistence, CRUD, invalid inputs, atomic rejection, ranking, cross-project edges, concurrent writers, exception/killed-process rollback, long chains, export safety and exact backup restore. The demo prints both projects and all statuses, next-work `a2`, malformed-import preservation, cycle/blocked-completion rejection and exact restore. Both use only synthetic data and project-local temporary directories, cleaned afterward. Current evidence is in `specs/S001-planner.md`.

## Architecture and limits

`planner.py`: argument parsing, domain invariants, queries and mutations. `storage.py`: one versioned state document in a SQLite row, transactional read/validate/mutate/validate/commit, plus atomic JSON output. Whole-state validation favors understandable small local workloads over large-dataset performance. The file format is the backup/recovery boundary, not an internal SQLite copy.

This is a local tool, not a hardened multiuser service: no authentication, encryption, audit log, cloud sync, reminders or malicious-file resource limits. Use a local disk with normal filesystem permissions; network filesystems are untested. Hard-kill rollback and local concurrency are tested; physical power-loss/filesystem durability, Windows portability and very large datasets are not verified. Backup publication flushes file content, but does not promise survival of directory metadata through power loss. Keep backups and verify restores before relying on important saved work.
