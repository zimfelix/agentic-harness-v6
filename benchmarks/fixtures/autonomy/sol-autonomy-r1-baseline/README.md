# Local work planner

A Python-standard-library CLI for a solo freelancer. No install, account, server or network. Python **3.10+** required. All data paths must stay inside this repository (including resolved symlinks). Commands print JSON; errors go to stderr with exit code 2, success uses 0.

## Start and test

From the project root:

```sh
python3 planner.py --help
python3 planner.py overview
python3 -m unittest discover -s tests -v
python3 examples/demo.py
```

The default saved state is `data/planner.json`, created on the first successful mutation. Use `--state path` **before** the command to choose an isolated planner file. No package installation is needed. Each command is a fresh process reading the saved state.

## Everyday use

```sh
python3 planner.py project add studio "Synthetic studio work"
python3 planner.py task add draft --project studio --title "Draft sample" --estimate 90 --priority 1 --due 2026-08-01
python3 planner.py task add review --project studio --title "Review sample" --estimate 30 --depends-on draft
python3 planner.py overview --project studio
python3 planner.py task show review
python3 planner.py next
python3 planner.py task done draft
python3 planner.py task done review
python3 planner.py task reopen review
python3 planner.py task update draft --title "Revise sample" --estimate 60 --priority 2 --due none
python3 planner.py task update review --depends-on
python3 planner.py project update studio "Renamed synthetic project"
```

`task update` changes only supplied fields. `--depends-on a b` replaces the entire prerequisite list; the flag alone clears it. `--due none` clears the date. `--project` can move a task; IDs cannot be renamed. Projects and tasks have separate ID namespaces; IDs are 1–64 letters/digits/underscore/hyphen, starting with a letter or digit. Names/titles must be nonblank and at most 500 characters. Estimates are positive integer **minutes**, not tracked time. Priority: **1 high, 2 normal, 3 low** (default 2).

Dates are optional `YYYY-MM-DD` calendar dates, not instants, and may be in the past. They are advisory: never an automatic completion gate. No timezone or scheduling/reminder logic. Next-work selection excludes done and blocked tasks, then sorts by **earliest due date (undated last), priority, shortest estimate, ID**. Thus even a low-priority dated task precedes undated high-priority work. This is deterministic, not an optimized schedule. `next --project ID` scopes the suggestion; no eligible work returns `{"next": null}`.

Dependencies may cross projects. A task is blocked if **any direct prerequisite** is unfinished; the acyclic graph and completion rule ensure the whole chain is respected. A completed task cannot acquire an unfinished prerequisite. Reopening a prerequisite is refused if a completed dependent would become inconsistent; reopen dependents first. Cycles, unknown references, duplicate IDs/prerequisites and invalid dates are rejected without saving.

Overview contains tasks with `ready`, `blocked` or `done` status, blocker IDs, status counts, total estimated minutes and remaining minutes. All tasks count toward total estimates, including completed ones.

### Deleting work

Inspect `overview` and make a backup first. Destructive commands require `--yes`:

```sh
python3 planner.py task delete review --yes
python3 planner.py project delete studio --cascade --yes
```

Task deletion refuses **all** dependents, even completed ones. Remove their dependency first if appropriate. Project deletion refuses contained tasks unless `--cascade` is supplied, and still refuses any reference from outside that project. There is no automatic reference detachment or undo; restore a backup for recovery. An empty project can be deleted without `--cascade`.

## Synthetic import/export and backup recovery

`fixtures/demo.json` is a complete example interchange document: two projects, six tasks, `a1 → a2 → a3` chain, completed `a1`, blocked `a3`/`b2`, and ready `a2`/`b1`/`b3`. All names and work are invented.

```sh
python3 planner.py --state data/example.json import fixtures/demo.json --dry-run
python3 planner.py --state data/example.json import fixtures/demo.json --yes
python3 planner.py --state data/example.json overview
python3 planner.py --state data/example.json next
python3 planner.py --state data/example.json export data/example-export.json
python3 planner.py --state data/example.json backup data/example-backup.json
python3 planner.py --state data/example.json task done a2
python3 planner.py --state data/example.json restore data/example-backup.json --dry-run
python3 planner.py --state data/example.json restore data/example-backup.json --yes
```

Import/restore are **whole-state replacements**, not merges. First use dry-run to inspect new/changed/removed/unchanged IDs, and back up existing work. `--yes` explicitly confirms replacement; without it only dry-run is allowed. Validation applies to the whole file before saving. A malformed import or invalid graph leaves current bytes intact; repeating the same valid import produces no duplicates. No file instructions are executed.

Export and backup use the **same portable schema** and refuse to overwrite any existing destination. Parent directories for outputs must already exist. Input/output must differ from the state and lock files. Backup is a validated logical snapshot, not an archive of CLI code. Restore can also replace a corrupted state file (dry-run reports the unreadable state); ordinary commands and import will not silently erase corruption. Keep a copy of corrupt files if forensic recovery matters.

### Schema v1

All keys below are required; unknown keys, duplicate JSON object keys and unsupported versions are rejected. Arrays may be empty. IDs are stable identities, not display names. `done` must be a JSON boolean, `due` either a valid date string or `null`, estimates/priorities integers (not booleans). See the full [fixture](fixtures/demo.json).

```json
{
  "version": 1,
  "projects": [{"id": "sample", "name": "Synthetic example"}],
  "tasks": [{
    "id": "first", "project": "sample", "title": "Draft synthetic sample",
    "estimate": 30, "priority": 2, "due": null,
    "done": false, "depends_on": []
  }]
}
```

## Executed demonstration

`python3 examples/demo.py` uses a temporary directory **inside this project**, starts a new interpreter for every CLI command, and asserts restart visibility, six-task/two-project structure, exclusion of blocked/completed work, malformed-import byte equality, cycle rejection, blocked-completion rejection, and identical bytes/overview after backup restoration. It cleans up synthetic state and intentionally refreshes only [examples/demo-results.json](examples/demo-results.json). The report includes commands, actual output, exit codes and a before/after state hash. The selected initial next task is **a2**, not the earlier-due blocked a3 nor completed a1.

## Architecture and limits

`planner.py` loads `src/workplanner/cli.py`. Pure rules and graph validation are in `domain.py`; `storage.py` manages strict JSON, exclusive lock files and atomic replacement. This avoids a framework/database platform while separating testable rules from IO. Architecture and handoff context: [docs/architecture.md](docs/architecture.md), [specs/S001-planner.md](specs/S001-planner.md).

Every CLI access holds an exclusive fail-fast `STATE.lock` file, serializing cooperating commands. A process crash may leave it behind. Verify no planner is running before manually removing that **lock only**; never remove the state file to clear a lock. Do not edit state files while commands run. Writes flush/fsync the temporary file then atomically replace the state; tested write failures preserve the old file. This is not a guarantee against disk corruption/power loss (directory metadata is not fsynced), hostile local filesystem changes, or network filesystems. Outputs/backups interrupted by process termination may require removal and retry; inspect them before restoring.

This is a local MVP, not a production multiuser service: no access control, encryption, audit history, scheduling, automatic backup rotation or older-schema migrations. Whole-state validation and overview are intended for modest local workloads; no large-data benchmarks or hardware-loss tests were performed. Backup frequency determines potential loss; the operator owns backup storage and recovery. Tests/demo use synthetic data only. Future recurring work, accounts, dashboard, reminders and cloud remain out of scope.
