"""Command line interface. Run `python3 planner.py --help`."""
import argparse
import copy
import datetime as dt
import os
import sys

from . import model, suggest
from .model import PlannerError, format_estimate
from .store import DEFAULT_PATH, Store, dump, read_json_file, write_atomic

EPILOG = """examples:
  planner.py project add "Website relaunch"
  planner.py task add "Website relaunch" "Write copy" --estimate 3h --priority high --due 2026-10-20
  planner.py task add p1 "Publish" --after t1,t2
  planner.py next
  planner.py overview p1
data file: --data PATH, else $PLANNER_DATA, else data/planner.json in the program directory."""


def _ids(value):
    return [v for v in (x.strip() for x in value.split(",")) if v]


def build_parser():
    ap = argparse.ArgumentParser(prog="planner.py", description="Local project and work planner.",
                                 epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", help="state file (default: $PLANNER_DATA or data/planner.json)")
    ap.add_argument("--today", help="treat this date (YYYY-MM-DD) as today (default: local date)")
    sub = ap.add_subparsers(dest="cmd", required=True, metavar="COMMAND")

    pr = sub.add_parser("project", help="add, list, edit or delete projects")
    ps = pr.add_subparsers(dest="action", required=True)
    a = ps.add_parser("add", help="create a project")
    a.add_argument("name")
    a.add_argument("--description", default="")
    ps.add_parser("list", help="list projects")
    a = ps.add_parser("edit", help="rename or describe a project")
    a.add_argument("project")
    a.add_argument("--name")
    a.add_argument("--description")
    a = ps.add_parser("delete", help="delete a project and its tasks (backup is written first)")
    a.add_argument("project")
    a.add_argument("--yes", action="store_true", help="confirm deleting the project's tasks")
    a.add_argument("--detach", action="store_true", help="remove dependencies other tasks have on it")

    tk = sub.add_parser("task", help="add, edit, complete, delete or inspect tasks")
    ts = tk.add_subparsers(dest="action", required=True)
    a = ts.add_parser("add", help="create a task")
    a.add_argument("project", help="project id or name")
    a.add_argument("title")
    a.add_argument("--priority", default="normal", help="critical, high, normal (default), low")
    a.add_argument("--estimate", help="effort, e.g. 2h, 90m, 1h30m, 1.5")
    a.add_argument("--due", help="due date YYYY-MM-DD")
    a.add_argument("--after", type=_ids, default=[], help="prerequisite task ids, comma separated")
    a.add_argument("--notes", default="")
    a = ts.add_parser("edit", help="change task fields")
    a.add_argument("task")
    a.add_argument("--title")
    a.add_argument("--priority")
    a.add_argument("--estimate")
    a.add_argument("--no-estimate", action="store_true")
    a.add_argument("--due")
    a.add_argument("--no-due", action="store_true")
    a.add_argument("--project", help="move to another project")
    a.add_argument("--notes")
    a = ts.add_parser("depend", help="add prerequisites: TASK cannot be done before them")
    a.add_argument("task")
    a.add_argument("prereqs", type=_ids, help="comma separated task ids")
    a = ts.add_parser("undepend", help="remove prerequisites")
    a.add_argument("task")
    a.add_argument("prereqs", type=_ids)
    a = ts.add_parser("done", help="mark a task done (refused while prerequisites are open)")
    a.add_argument("task")
    a = ts.add_parser("reopen", help="mark a done task open again")
    a.add_argument("task")
    a = ts.add_parser("delete", help="delete a task")
    a.add_argument("task")
    a.add_argument("--detach", action="store_true", help="remove dependencies other tasks have on it")
    a = ts.add_parser("show", help="show one task")
    a.add_argument("task")
    a = ts.add_parser("list", help="list tasks")
    a.add_argument("--project")
    a.add_argument("--status", choices=("ready", "blocked", "done", "open"))

    a = sub.add_parser("blocked", help="list blocked tasks and what blocks them")
    a.add_argument("--project")
    a = sub.add_parser("next", help="suggest what to work on next")
    a.add_argument("--project")
    a.add_argument("--limit", type=int, default=5)
    a = sub.add_parser("overview", help="summary of all projects, or details of one")
    a.add_argument("project", nargs="?")

    a = sub.add_parser("export", help="write the state as JSON (stdout or file)")
    a.add_argument("--out", help="file to write (default: stdout)")
    a.add_argument("--force", action="store_true", help="overwrite an existing file")
    a = sub.add_parser("import", help="import a JSON file (all-or-nothing)")
    a.add_argument("file")
    mode = a.add_mutually_exclusive_group(required=True)
    mode.add_argument("--replace", action="store_true", help="replace the whole current state")
    mode.add_argument("--merge", action="store_true", help="add the file's projects/tasks with new ids")
    a.add_argument("--dry-run", action="store_true", help="validate and report only")
    sub.add_parser("backup", help="write a timestamped backup of the current state")
    sub.add_parser("backups", help="list backup files")
    a = sub.add_parser("restore", help="replace the current state with a backup/export file")
    src = a.add_mutually_exclusive_group(required=True)
    src.add_argument("file", nargs="?")
    src.add_argument("--latest", action="store_true", help="newest valid backup")
    return ap


# ------------------------------------------------------------------ output

def _table(rows, headers):
    rows = [[str(c) for c in r] for r in rows]
    widths = [max(len(h), *(len(r[i]) for r in rows)) if rows else len(h) for i, h in enumerate(headers)]
    lines = ["  ".join(h.ljust(w) for h, w in zip(headers, widths)).rstrip()]
    lines += ["  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip() for r in rows]
    return "\n".join(lines)


def _task_rows(state, tasks):
    st = suggest.statuses(state)
    return _table([[t["id"], st[t["id"]], t["priority"], format_estimate(t["estimate_minutes"]),
                    t["due"] or "-", ",".join(t["depends_on"]) or "-", t["title"]] for t in tasks],
                  ["ID", "STATUS", "PRIORITY", "EST", "DUE", "AFTER", "TITLE"])


def _show_task(state, t):
    st = suggest.statuses(state)[t["id"]]
    p = model.get_project(state, t["project"])
    lines = [f"{t['id']}  {t['title']}",
             f"  project:   {p['id']} {p['name']}",
             f"  status:    {st}" + (f" ({t['done_at']})" if t["done_at"] else ""),
             f"  priority:  {t['priority']}",
             f"  estimate:  {format_estimate(t['estimate_minutes'])}",
             f"  due:       {t['due'] or '-'}",
             f"  after:     {', '.join(t['depends_on']) or '-'}",
             f"  needed by: {', '.join(x['id'] for x in model.dependents(state, t['id'])) or '-'}"]
    if st == "blocked":
        lines.append(f"  blocked by: {', '.join(model.unfinished_prereqs(state, t))}")
    if t["notes"]:
        lines.append(f"  notes:     {t['notes']}")
    return "\n".join(lines)


def _summary(state):
    return f"{len(state['projects'])} project(s), {len(state['tasks'])} task(s)"


# ------------------------------------------------------------------ commands

class App:
    def __init__(self, args):
        self.args = args
        self.store = Store(args.data or os.environ.get("PLANNER_DATA") or DEFAULT_PATH)
        today = args.today or os.environ.get("PLANNER_TODAY")
        self.today = dt.date.fromisoformat(model.parse_date(today)) if today else dt.date.today()

    def run(self):
        a = self.args
        handler = getattr(self, f"cmd_{a.cmd}_{a.action}" if hasattr(a, "action") else f"cmd_{a.cmd}")
        return handler(a)

    def mutate(self, fn, backup_label=None):
        """Lock, load, apply fn on a copy, validate and save atomically."""
        with self.store.locked():
            state = self.store.load()
            work = copy.deepcopy(state)
            result = fn(work)
            model.validate_state(work)
            if backup_label:
                print(f"backup of previous state: {self.store.backup(state, backup_label)}")
            self.store.save(work)
            return work, result

    def read(self):
        with self.store.locked():
            return self.store.load()

    # projects
    def cmd_project_add(self, a):
        _, p = self.mutate(lambda s: model.add_project(s, a.name, a.description))
        print(f"created project {p['id']}: {p['name']}")

    def cmd_project_list(self, a):
        s = self.read()
        print(_table([[p["id"], p["name"], sum(t["project"] == p["id"] for t in s["tasks"]), p["description"]]
                      for p in s["projects"]], ["ID", "NAME", "TASKS", "DESCRIPTION"]))

    def cmd_project_edit(self, a):
        _, p = self.mutate(lambda s: model.edit_project(s, a.project, a.name, a.description))
        print(f"updated project {p['id']}: {p['name']}")

    def cmd_project_delete(self, a):
        _, (p, ids, edges) = self.mutate(lambda s: model.delete_project(s, a.project, a.detach, a.yes),
                                         backup_label="pre-delete")
        print(f"deleted project {p['id']} ({p['name']}) with {len(ids)} task(s){': ' + ', '.join(ids) if ids else ''}")
        for dep, pre in edges:
            print(f"removed dependency: {dep} no longer depends on {pre}")

    # tasks
    def cmd_task_add(self, a):
        _, t = self.mutate(lambda s: model.add_task(s, a.project, a.title, a.priority, a.estimate,
                                                     a.due, a.after, a.notes))
        print(f"created task {t['id']} in {t['project']}: {t['title']}")

    def cmd_task_edit(self, a):
        s, t = self.mutate(lambda s: model.edit_task(
            s, a.task, a.title, a.priority, a.estimate, a.no_estimate, a.due, a.no_due, a.project, a.notes))
        print(_show_task(s, t))

    def cmd_task_depend(self, a):
        _, t = self.mutate(lambda s: model.add_dependencies(s, a.task, a.prereqs))
        print(f"{t['id']} now depends on: {', '.join(t['depends_on'])}")

    def cmd_task_undepend(self, a):
        _, t = self.mutate(lambda s: model.remove_dependencies(s, a.task, a.prereqs))
        print(f"{t['id']} now depends on: {', '.join(t['depends_on']) or '-'}")

    def cmd_task_done(self, a):
        s, t = self.mutate(lambda s: model.complete_task(s, a.task))
        print(f"done: {t['id']} {t['title']}")
        unblocked = [x["id"] for x in model.dependents(s, t["id"])
                     if suggest.statuses(s)[x["id"]] == "ready"]
        if unblocked:
            print(f"now ready: {', '.join(unblocked)}")

    def cmd_task_reopen(self, a):
        _, t = self.mutate(lambda s: model.reopen_task(s, a.task))
        print(f"reopened: {t['id']} {t['title']}")

    def cmd_task_delete(self, a):
        _, (t, edges) = self.mutate(lambda s: model.delete_task(s, a.task, a.detach))
        print(f"deleted task {t['id']}: {t['title']}")
        for dep, pre in edges:
            print(f"removed dependency: {dep} no longer depends on {pre}")

    def cmd_task_show(self, a):
        s = self.read()
        print(_show_task(s, model.get_task(s, a.task)))

    def cmd_task_list(self, a):
        s = self.read()
        pid = model.get_project(s, a.project)["id"] if a.project else None
        st = suggest.statuses(s)
        tasks = [t for t in s["tasks"] if pid in (None, t["project"])
                 and (a.status is None or st[t["id"]] == a.status or (a.status == "open" and st[t["id"]] != "done"))]
        print(_task_rows(s, tasks) if tasks else "no tasks")

    def cmd_blocked(self, a):
        s = self.read()
        pid = model.get_project(s, a.project)["id"] if a.project else None
        rows = suggest.blocked_report(s, pid)
        if not rows:
            print("nothing is blocked")
        for t, blockers in rows:
            print(f"{t['id']} [{t['project']}] {t['title']} -- waiting for: "
                  + ", ".join(f"{b} ({model.get_task(s, b)['title']})" for b in blockers))

    def cmd_next(self, a):
        s = self.read()
        pid = model.get_project(s, a.project)["id"] if a.project else None
        picks = suggest.next_work(s, self.today, pid, max(a.limit, 1))
        if not picks:
            print("nothing is ready to work on")
        for i, (t, reasons) in enumerate(picks, 1):
            print(f"{i}. {t['id']} [{t['project']}] {t['title']}\n   " + "; ".join(reasons))

    def cmd_overview(self, a):
        s = self.read()
        rows = suggest.overview(s, self.today)
        if a.project:
            pid = model.get_project(s, a.project)["id"]
            rows = [r for r in rows if r["project"]["id"] == pid]
        if not rows:
            print("no projects yet")
        for r in rows:
            p = r["project"]
            print(f"{p['id']}  {p['name']}" + (f" -- {p['description']}" if p["description"] else ""))
            print(f"  tasks {r['total']}: {r['done']} done, {r['ready']} ready, {r['blocked']} blocked"
                  f" | remaining estimate {format_estimate(r['remaining_minutes'])}"
                  + (f" (+{r['unestimated']} unestimated)" if r["unestimated"] else "")
                  + f" | next due {r['next_due'] or '-'}")
            if r["overdue"]:
                print("  OVERDUE: " + ", ".join(f"{t['id']} (due {t['due']})" for t in r["overdue"]))
            if a.project and r["tasks"]:
                print("\n".join("  " + line for line in _task_rows(s, r["tasks"]).splitlines()))
        print(f"today: {self.today.isoformat()}")

    # data exchange and recovery
    def cmd_export(self, a):
        text = dump(self.read())
        if a.out:
            write_atomic(a.out, text, overwrite=a.force)
            print(f"exported to {a.out}")
        else:
            sys.stdout.write(text)

    def cmd_import(self, a):
        incoming = read_json_file(a.file)  # raises before any state is touched

        def apply(s):
            if a.replace:
                s.clear()
                s.update(copy.deepcopy(incoming))
                return None
            return model.merge_states(s, incoming)

        if a.dry_run:
            work = copy.deepcopy(self.read())
            mapping = apply(work)
            model.validate_state(work)
            print(f"dry run OK: file has {_summary(incoming)}; result would have {_summary(work)}; nothing changed")
            return
        s, mapping = self.mutate(apply, backup_label="pre-import")
        mode = "replaced state with" if a.replace else "merged"
        print(f"imported ({mode}) {_summary(incoming)} from {a.file}; state now has {_summary(s)}")
        if mapping:
            print("new ids: " + ", ".join(f"{k}->{v}" for k, v in mapping.items()))

    def cmd_backup(self, a):
        print(f"backup written: {self.store.backup(self.read())}")

    def cmd_backups(self, a):
        files = self.store.backups()
        print("\n".join(str(f) for f in files) if files else f"no backups in {self.store.backup_dir}")

    def cmd_restore(self, a):
        source = a.file
        if a.latest:
            for f in reversed(self.store.backups()):
                if "-corrupt" in f.name:
                    continue
                try:
                    read_json_file(f)
                    source = f
                    break
                except PlannerError:
                    continue
            if source is None:
                raise PlannerError(f"no valid backup found in {self.store.backup_dir}")
        incoming = read_json_file(source)
        with self.store.locked():
            if self.store.path.exists():
                try:
                    current = self.store.load()
                    print(f"backup of previous state: {self.store.backup(current, 'pre-restore')}")
                except PlannerError:
                    print(f"previous state was unreadable; raw copy kept at {self.store.backup_raw('corrupt')}")
            self.store.save(incoming)
        print(f"restored {_summary(incoming)} from {source}")


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return App(args).run() or 0
    except PlannerError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
