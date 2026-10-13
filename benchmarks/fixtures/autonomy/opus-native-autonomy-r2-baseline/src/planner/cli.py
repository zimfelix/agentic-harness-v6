"""Command-line interface: argument parsing and text output."""
import argparse
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from . import operations as ops
from .model import (PRIORITIES, STATES, PlannerError, format_minutes, parse_date,
                    parse_estimate, parse_priority)
from .planning import overview, reason, suggest
from .store import Store
from .transfer import document_to_plan, merge, read_document, to_document, write_json_atomic

ROOT = Path(__file__).resolve().parents[2]


def task_line(plan, t):
    state = plan.state(t)
    extra = [t.priority, f"est {format_minutes(t.estimate_minutes)}"]
    if t.due:
        extra.append(f"due {t.due}")
    if state == "blocked":
        extra.append("waits for " + ", ".join(f"#{p}" for p in plan.open_prerequisites(t)))
    return f"  #{t.id:<4} [{state:<7}] {t.title}  ({'; '.join(extra)})"


def _today(args):
    return date.fromisoformat(parse_date(args.today)) if args.today else date.today()


def _task_fields(args):
    fields = {}
    if args.priority:
        fields["priority"] = parse_priority(args.priority)
    if args.estimate is not None:
        fields["estimate_minutes"] = parse_estimate(args.estimate)
    if args.due is not None:
        fields["due"] = parse_date(args.due)
    if args.note is not None:
        fields["note"] = args.note
    return fields


def cmd_project(args, store):
    if args.action == "list":
        plan = store.load()
        for p in sorted(plan.projects.values(), key=lambda p: p.key):
            n = sum(1 for t in plan.tasks.values() if t.project == p.key)
            print(f"{p.key:<20} {p.name}  ({n} tasks)")
        return
    with store.transaction() as plan:
        if args.action == "add":
            ops.add_project(plan, args.key, args.name)
            print(f"created project '{args.key}'")
        elif args.action == "rename":
            plan.project(args.key).name = args.name
            print(f"renamed project '{args.key}'")
        elif args.action == "delete":
            tasks = sorted(t.id for t in plan.tasks.values() if t.project == args.key)
            plan.project(args.key)
            if tasks and not args.yes:
                print(f"would delete project '{args.key}' with {len(tasks)} task(s): "
                      + ", ".join(f"#{t}" for t in tasks) + ". Re-run with --yes to delete.")
                return
            deleted, links = ops.delete_project(plan, args.key, args.detach)
            _report_detached(links)
            print(f"deleted project '{args.key}' and {len(deleted)} task(s)")


def _report_detached(links):
    for t, p in links:
        print(f"removed dependency: #{t} no longer waits for #{p}")


def cmd_task(args, store):
    if args.action == "show":
        plan = store.load()
        t = plan.task(args.id)
        print(task_line(plan, t).strip())
        print(f"project: {t.project}\ncreated: {t.created_at}\ndone: {t.done_at or '-'}")
        print("depends on: " + (", ".join(f"#{p}" for p in sorted(t.depends_on)) or "-"))
        print("needed by: " + (", ".join(f"#{d}" for d in plan.dependents(t.id)) or "-"))
        if t.note:
            print(f"note: {t.note}")
        return
    with store.transaction() as plan:
        if args.action == "add":
            t = ops.add_task(plan, args.project, args.title, depends_on=args.after or (),
                             **_task_fields(args))
            print(f"created task #{t.id} in '{t.project}' [{plan.state(t)}]")
        elif args.action == "edit":
            fields = _task_fields(args)
            if args.title:
                fields["title"] = args.title
            if args.clear_due:
                fields["due"] = None
            if args.clear_estimate:
                fields["estimate_minutes"] = None
            ops.edit_task(plan, args.id, **fields)
            print(f"updated task #{args.id}")
        elif args.action == "done":
            ops.complete(plan, args.id)
            print(f"completed task #{args.id}")
        elif args.action == "reopen":
            ops.reopen(plan, args.id)
            print(f"reopened task #{args.id}")
        elif args.action == "delete":
            _report_detached(ops.delete_task(plan, args.id, args.detach))
            print(f"deleted task #{args.id}")


def cmd_dep(args, store):
    with store.transaction() as plan:
        if args.action == "add":
            ops.add_dependency(plan, args.task, args.prereq)
            print(f"#{args.task} now waits for #{args.prereq}")
        else:
            ops.remove_dependency(plan, args.task, args.prereq)
            print(f"#{args.task} no longer waits for #{args.prereq}")


def cmd_list(args, store):
    plan = store.load()
    if args.project:
        plan.project(args.project)
    wanted = {"open": {"ready", "blocked"}, "all": set(STATES)}.get(args.state, {args.state})
    rows = [t for t in sorted(plan.tasks.values(), key=lambda t: t.id)
            if plan.state(t) in wanted and (not args.project or t.project == args.project)]
    for t in rows:
        print(task_line(plan, t))
    if not rows:
        print("no matching tasks")


def cmd_next(args, store):
    plan = store.load()
    if args.project:
        plan.project(args.project)
    today = _today(args)
    ranked = suggest(plan, today, args.project)[:args.limit]
    if not ranked:
        print("nothing ready: every open task is blocked, or all work is done")
    for i, t in enumerate(ranked, 1):
        print(f"{i}. #{t.id} {t.title} [{t.project}] - {reason(plan, t, today)}")


def cmd_overview(args, store):
    plan = store.load()
    keys = [plan.project(args.project).key] if args.project else sorted(plan.projects)
    today = _today(args)
    for key in keys:
        o = overview(plan, key, today)
        c, total = o["counts"], len(o["tasks"])
        pct = round(100 * c["done"] / total) if total else 0
        print(f"== {key}: {plan.projects[key].name} ==")
        print(f"  {total} tasks: {c['done']} done ({pct}%), {c['ready']} ready, "
              f"{c['blocked']} blocked; remaining estimate {format_minutes(o['remaining_minutes'])}"
              + (f" (+{o['unestimated']} unestimated)" if o["unestimated"] else ""))
        if o["overdue"]:
            print("  overdue: " + ", ".join(f"#{t.id} (due {t.due})" for t in o["overdue"]))
        for t in o["tasks"]:
            print(task_line(plan, t))
    if not keys:
        print("no projects yet - start with: planner project add KEY NAME")


def cmd_export(args, store):
    doc = to_document(store.load(), args.project)
    if args.file == "-":
        import json
        print(json.dumps(doc, indent=2, ensure_ascii=False))
    else:
        write_json_atomic(args.file, doc)
        print(f"exported {len(doc['projects'])} project(s), {len(doc['tasks'])} task(s) "
              f"to {args.file}")


def cmd_import(args, store):
    incoming = document_to_plan(read_document(args.file))
    with store.transaction() as plan:
        mapping = merge(plan, incoming)
        verb = "would import" if args.dry_run else "imported"
        print(f"{verb} {len(incoming.projects)} project(s) ("
              f"{', '.join(sorted(incoming.projects)) or '-'}), {len(mapping)} task(s), "
              f"{sum(len(t.depends_on) for t in incoming.tasks.values())} dependencies")
        print("task ids: " + (", ".join(f"{o}->#{n}" for o, n in sorted(mapping.items())) or "-"))
        if args.dry_run:
            raise _DryRun()


class _DryRun(Exception):
    pass


def default_backup_path(store):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return store.path.parent / "backups" / f"planner-{stamp}.json"


def cmd_backup(args, store):
    path = args.file or default_backup_path(store)
    doc = to_document(store.load())
    write_json_atomic(path, doc)
    print(f"backup written: {path} ({len(doc['projects'])} projects, {len(doc['tasks'])} tasks)")


def cmd_restore(args, store):
    restored = document_to_plan(read_document(args.file))
    summary = f"{len(restored.projects)} project(s), {len(restored.tasks)} task(s)"
    if not args.yes:
        print(f"{args.file} is valid ({summary}). Restoring REPLACES the current state; "
              "re-run with --yes.")
        return
    with store.transaction() as plan:
        safety = default_backup_path(store)
        write_json_atomic(safety, to_document(plan))
        plan.projects, plan.tasks = restored.projects, restored.tasks
        plan.next_task_id = restored.next_task_id
    print(f"safety backup of previous state: {safety}")
    print(f"restored {summary} from {args.file}")


def build_parser():
    p = argparse.ArgumentParser(prog="planner", description="Local project/work planner.")
    p.add_argument("--db", help="SQLite file (default: $PLANNER_DB or data/planner.db)")
    sub = p.add_subparsers(dest="command", required=True)

    pr = sub.add_parser("project", help="manage projects").add_subparsers(dest="action", required=True)
    a = pr.add_parser("add", help="create a project")
    a.add_argument("key", help="short id, e.g. acme-site")
    a.add_argument("name")
    pr.add_parser("list", help="list projects")
    a = pr.add_parser("rename")
    a.add_argument("key")
    a.add_argument("name")
    a = pr.add_parser("delete", help="delete a project and its tasks")
    a.add_argument("key")
    a.add_argument("--yes", action="store_true", help="really delete")
    a.add_argument("--detach", action="store_true", help="drop dependencies of other projects on it")

    tk = sub.add_parser("task", help="manage tasks").add_subparsers(dest="action", required=True)

    def task_opts(a):
        a.add_argument("--priority", help="/".join(PRIORITIES) + " (default normal)")
        a.add_argument("--estimate", help="effort, e.g. 90m, 1.5h, 2h30m")
        a.add_argument("--due", help="due date YYYY-MM-DD")
        a.add_argument("--note")

    a = tk.add_parser("add", help="create a task")
    a.add_argument("project")
    a.add_argument("title")
    task_opts(a)
    a.add_argument("--after", type=int, nargs="+", metavar="ID", help="prerequisite task ids")
    a = tk.add_parser("edit", help="change task fields")
    a.add_argument("id", type=int)
    a.add_argument("--title")
    task_opts(a)
    a.add_argument("--clear-due", action="store_true")
    a.add_argument("--clear-estimate", action="store_true")
    for name in ("show", "done", "reopen"):
        tk.add_parser(name).add_argument("id", type=int)
    a = tk.add_parser("delete")
    a.add_argument("id", type=int)
    a.add_argument("--detach", action="store_true", help="drop dependencies of other tasks on it")

    dp = sub.add_parser("dep", help="task dependencies").add_subparsers(dest="action", required=True)
    for name in ("add", "remove"):
        a = dp.add_parser(name, help=f"{name}: TASK waits for PREREQ")
        a.add_argument("task", type=int)
        a.add_argument("prereq", type=int)

    a = sub.add_parser("list", help="list tasks")
    a.add_argument("--project")
    a.add_argument("--state", default="open", choices=["open", "all", *STATES])
    a = sub.add_parser("blocked", help="list blocked tasks and what blocks them")
    a.add_argument("--project")
    a = sub.add_parser("next", help="suggest what to work on next")
    a.add_argument("--project")
    a.add_argument("--limit", type=int, default=3)
    a.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    a = sub.add_parser("overview", help="project overview")
    a.add_argument("project", nargs="?")
    a.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    a = sub.add_parser("export", help="write JSON document")
    a.add_argument("file", help="path or - for stdout")
    a.add_argument("--project")
    a = sub.add_parser("import", help="add projects from a JSON document (all or nothing)")
    a.add_argument("file")
    a.add_argument("--dry-run", action="store_true")
    a = sub.add_parser("backup", help="write a full backup")
    a.add_argument("file", nargs="?")
    a = sub.add_parser("restore", help="replace current state with a backup")
    a.add_argument("file")
    a.add_argument("--yes", action="store_true")
    return p


COMMANDS = {"project": cmd_project, "task": cmd_task, "dep": cmd_dep, "list": cmd_list,
            "next": cmd_next, "overview": cmd_overview, "export": cmd_export,
            "import": cmd_import, "backup": cmd_backup, "restore": cmd_restore,
            "blocked": lambda args, store: cmd_list(
                argparse.Namespace(project=args.project, state="blocked"), store)}


def main(argv=None):
    args = build_parser().parse_args(argv)
    db = args.db or os.environ.get("PLANNER_DB") or ROOT / "data" / "planner.db"
    try:
        store = Store(db)
        try:
            COMMANDS[args.command](args, store)
        finally:
            store.close()
    except _DryRun:
        print("dry run: nothing was changed")
    except PlannerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0
