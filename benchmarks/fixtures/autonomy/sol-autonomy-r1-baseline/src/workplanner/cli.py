"""Documented command-line boundary; all output data is JSON."""
import argparse
import json
from pathlib import Path
import sys

from .domain import find, mutate, next_task, overview, task_view
from .storage import Store, read_json, replacement_report, write_new

ROOT = Path(__file__).resolve().parents[2]


def local_path(value):
    path = Path(value).resolve()
    if path == ROOT or ROOT not in path.parents:
        raise ValueError("All data paths must be inside this project directory")
    return path


def parser():
    p = argparse.ArgumentParser(description="Local work planner; JSON output, no network. See README.md for examples.")
    p.add_argument("--state", default=str(ROOT / "data/planner.json"), help="state file inside this project (default: data/planner.json)")
    commands = p.add_subparsers(dest="command", required=True)
    project = commands.add_parser("project", help="create, rename or delete projects").add_subparsers(dest="operation", required=True)
    for operation in ("add", "update", "delete"):
        sub = project.add_parser(operation)
        sub.add_argument("id")
        if operation != "delete":
            sub.add_argument("name")
        else:
            sub.add_argument("--cascade", action="store_true", help="also delete contained tasks; external references still prevent deletion")
            sub.add_argument("--yes", action="store_true")
    task = commands.add_parser("task", help="manage work and prerequisites").add_subparsers(dest="operation", required=True)
    for operation in ("add", "update", "show", "delete", "done", "reopen"):
        sub = task.add_parser(operation)
        sub.add_argument("id")
        if operation in ("add", "update"):
            required = operation == "add"
            sub.add_argument("--project", required=required)
            sub.add_argument("--title", required=required)
            sub.add_argument("--estimate", type=int, required=required, help="positive integer minutes")
            sub.add_argument("--priority", type=int, default=2 if required else None, help="1 high, 2 normal, 3 low")
            sub.add_argument("--due", help="YYYY-MM-DD; use 'none' to clear")
            sub.add_argument("--depends-on", nargs="*", default=[] if required else None,
                             help="replace prerequisite IDs; flag alone clears them")
        if operation == "delete":
            sub.add_argument("--yes", action="store_true")
    for command in ("overview", "next"):
        sub = commands.add_parser(command)
        sub.add_argument("--project", help="optional project scope")
    for command in ("export", "backup", "import", "restore"):
        sub = commands.add_parser(command, help="validated portable JSON " + command)
        sub.add_argument("file", help="path inside project; outputs must not exist")
        if command in ("import", "restore"):
            sub.add_argument("--dry-run", action="store_true", help="validate and report without changing saved work")
            sub.add_argument("--yes", action="store_true", help="confirm entire-state replacement")
    return p


def execute(args):
    state_path = local_path(args.state)
    store = Store(state_path)
    file = local_path(args.file) if hasattr(args, "file") else None
    if file is not None and file in (store.path, store.lock):
        raise ValueError("Interchange file must differ from state and its lock")
    with store.session():
        damaged = None
        try:
            state = store.load()
        except (ValueError, OSError) as error:
            if args.command != "restore":
                raise
            state = None
            damaged = str(error)
        if args.command in ("import", "restore"):
            new = read_json(file)
            report = replacement_report(state, new) if state is not None else {"unreadable_current_state": damaged}
            if not args.dry_run and not args.yes:
                raise ValueError("Replacement requires --yes; first review with --dry-run and make a backup")
            if not args.dry_run:
                store.save(new)
            return {"operation": args.command, "saved": not args.dry_run, "changes": report,
                    "errors": 0, "projects": len(new["projects"]), "tasks": len(new["tasks"])}
        if args.command in ("export", "backup"):
            write_new(file, state)
            return {"operation": args.command, "file": str(file), "projects": len(state["projects"]), "tasks": len(state["tasks"])}
        if args.command == "overview":
            return overview(state, args.project)
        if args.command == "next":
            return {"next": next_task(state, args.project)}
        if args.command == "task" and args.operation == "show":
            return task_view(state, find(state, "tasks", args.id))
        if args.operation == "delete" and not args.yes:
            raise ValueError("Deletion requires --yes; inspect overview and make a backup first")
        action = args.operation if args.operation in ("done", "reopen") else f"{args.command}-{args.operation}"
        values = {}
        if args.command == "project":
            if args.operation == "delete":
                values["cascade"] = args.cascade
            else:
                values["name"] = args.name
        elif args.operation in ("add", "update"):
            for field in ("project", "title", "estimate", "priority", "due", "depends_on"):
                value = getattr(args, field)
                if value is not None:
                    values[field] = None if field == "due" and value == "none" else value
            if args.operation == "add":
                values.setdefault("due", None)
        new = mutate(state, action, args.id, **values)
        store.save(new)
        return {"saved": True, "action": action, "id": args.id}


def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    try:
        result = execute(args)
    except (ValueError, OSError, RecursionError) as error:
        print(f"error: {error}; operation not completed", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
