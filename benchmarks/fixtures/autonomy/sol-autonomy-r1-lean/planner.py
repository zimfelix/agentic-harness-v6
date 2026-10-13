#!/usr/bin/env python3
"""Local project and task planner. Run --help for the CLI."""
import argparse
from datetime import date
import json
import re
import sqlite3
import sys
from uuid import uuid4

from storage import PlannerError, Store, read_json


PROJECT_KEYS = {"id", "name"}
TASK_KEYS = {"id", "project_id", "title", "estimate_minutes", "priority", "due", "done", "dependencies"}


def require(condition, message):
    if not condition:
        raise PlannerError(message)


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be nonempty text")


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value), "IDs must be 1–64 letters, digits, underscores or hyphens, starting alphanumeric")


def validate(state):
    require(type(state) is dict and set(state) == {"version", "projects", "tasks"}, "expected version, projects and tasks")
    require(type(state["version"]) is int and state["version"] == 1, "unsupported schema version")
    for collection, keys in (("projects", PROJECT_KEYS), ("tasks", TASK_KEYS)):
        require(type(state[collection]) is list, f"{collection} must be an array")
        seen = set()
        for item in state[collection]:
            require(type(item) is dict and set(item) == keys, f"invalid {collection} fields")
            identifier(item["id"])
            require(item["id"] not in seen, f"duplicate {collection} ID: {item['id']}")
            seen.add(item["id"])
    projects = {p["id"] for p in state["projects"]}
    for p in state["projects"]:
        text(p["name"], "project name")
    tasks = {t["id"]: t for t in state["tasks"]}
    for t in tasks.values():
        text(t["title"], "task title")
        require(isinstance(t["project_id"], str) and t["project_id"] in projects, f"unknown project for {t['id']}")
        require(type(t["estimate_minutes"]) is int and t["estimate_minutes"] >= 0, "estimate must be a nonnegative integer")
        require(type(t["priority"]) is int and 1 <= t["priority"] <= 5, "priority must be 1–5")
        require(type(t["done"]) is bool, "done must be boolean")
        if t["due"] is not None:
            require(isinstance(t["due"], str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", t["due"]), "due must be YYYY-MM-DD or null")
            try:
                date.fromisoformat(t["due"])
            except ValueError as exc:
                raise PlannerError("due is not a real calendar date") from exc
        deps = t["dependencies"]
        require(type(deps) is list and all(isinstance(d, str) for d in deps), "dependencies must be an array of IDs")
        require(len(set(deps)) == len(deps), "duplicate dependency")
        for dep in deps:
            require(dep in tasks, f"unknown dependency: {dep}")
            require(dep != t["id"], "task cannot depend on itself")
            require(not t["done"] or tasks[dep]["done"], f"completed task {t['id']} has unfinished prerequisite {dep}")
    # Iterative topological traversal handles long chains without recursion limits.
    pending = {key: len(t["dependencies"]) for key, t in tasks.items()}
    dependents = {key: [] for key in tasks}
    for key, t in tasks.items():
        for dep in t["dependencies"]:
            dependents[dep].append(key)
    ready = [key for key in tasks if pending[key] == 0]
    visited = 0
    while ready:
        key = ready.pop()
        visited += 1
        for child in dependents[key]:
            pending[child] -= 1
            if pending[child] == 0:
                ready.append(child)
    require(visited == len(tasks), "dependency cycle detected")


def find(state, collection, key):
    for item in state[collection]:
        if item["id"] == key:
            return item
    raise PlannerError(f"unknown {collection} ID: {key}")


def decorated(state, task):
    tasks = {t["id"]: t for t in state["tasks"]}
    blockers = sorted(d for d in task["dependencies"] if not tasks[d]["done"])
    return {**task, "status": "done" if task["done"] else "blocked" if blockers else "ready", "blockers": blockers}


def overview(state, project=None):
    if project:
        find(state, "projects", project)
    result = []
    for p in sorted(state["projects"], key=lambda p: p["id"]):
        if project and project != p["id"]:
            continue
        tasks = [decorated(state, t) for t in state["tasks"] if t["project_id"] == p["id"]]
        tasks.sort(key=lambda t: t["id"])
        result.append({**p, "counts": {status: sum(t["status"] == status for t in tasks) for status in ("ready", "blocked", "done")}, "estimate_minutes": sum(t["estimate_minutes"] for t in tasks), "remaining_minutes": sum(t["estimate_minutes"] for t in tasks if not t["done"]), "tasks": tasks})
    return {"projects": result}


def suggest(state, project=None):
    if project:
        find(state, "projects", project)
    ready = [decorated(state, t) for t in state["tasks"] if not project or t["project_id"] == project]
    ready = [t for t in ready if t["status"] == "ready"]
    ready.sort(key=lambda t: (-t["priority"], t["due"] or "9999-99-99", t["estimate_minutes"], t["id"]))
    return {"task": ready[0] if ready else None, "reason": "priority descending, due ascending (undated last), effort ascending, ID" if ready else "no ready unfinished tasks"}


def mutate(state, args):
    cmd = args.command
    if cmd == "project-add":
        item = {"id": args.id or "p-" + uuid4().hex, "name": args.name}
        state["projects"].append(item)
    elif cmd == "project-edit":
        item = find(state, "projects", args.id)
        item["name"] = args.name
    elif cmd == "project-delete":
        item = find(state, "projects", args.id)
        require(not any(t["project_id"] == args.id for t in state["tasks"]), "project must be empty before deletion")
        state["projects"].remove(item)
    elif cmd == "task-add":
        item = {"id": args.id or "t-" + uuid4().hex, "project_id": args.project, "title": args.title, "estimate_minutes": args.estimate, "priority": args.priority, "due": args.due, "done": False, "dependencies": args.depends or []}
        state["tasks"].append(item)
    else:
        item = find(state, "tasks", args.id)
        if cmd == "task-edit":
            for attribute, field in (("title", "title"), ("project", "project_id"), ("estimate", "estimate_minutes"), ("priority", "priority"), ("due", "due")):
                value = getattr(args, attribute)
                if value is not None:
                    item[field] = value
            if args.clear_due:
                item["due"] = None
        elif cmd in ("done", "reopen"):
            item["done"] = cmd == "done"
        elif cmd == "task-delete":
            require(not any(args.id in t["dependencies"] for t in state["tasks"]), "task is referenced by dependencies; explicitly remove them first")
            state["tasks"].remove(item)
        elif cmd == "depend":
            require(args.prerequisite not in item["dependencies"], "dependency already exists")
            item["dependencies"].append(args.prerequisite)
        elif cmd == "undepend":
            require(args.prerequisite in item["dependencies"], "dependency does not exist")
            item["dependencies"].remove(args.prerequisite)
    return {"ok": True, "item": item}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", default=".planner/planner.sqlite3", help="SQLite state path (default: %(default)s)")
    sub = p.add_subparsers(dest="command", required=True)
    for cmd in ("project-add", "project-edit", "project-delete"):
        s = sub.add_parser(cmd)
        if cmd == "project-add":
            s.add_argument("name")
            s.add_argument("--id")
        else:
            s.add_argument("id")
            if cmd == "project-edit":
                s.add_argument("name")
    for cmd in ("task-add", "task-edit"):
        s = sub.add_parser(cmd)
        if cmd == "task-add":
            s.add_argument("project")
            s.add_argument("title")
            s.add_argument("--id")
            s.add_argument("--depends", action="append", help="repeat for each prerequisite ID")
        else:
            s.add_argument("id")
            s.add_argument("--project")
            s.add_argument("--title")
        s.add_argument("--estimate", type=int, default=0 if cmd == "task-add" else None, help="integer minutes")
        s.add_argument("--priority", type=int, default=3 if cmd == "task-add" else None, help="1 lowest to 5 highest")
        due = s.add_mutually_exclusive_group()
        due.add_argument("--due", help="YYYY-MM-DD")
        if cmd == "task-edit":
            due.add_argument("--clear-due", action="store_true")
    for cmd in ("done", "reopen", "task-delete", "depend", "undepend"):
        s = sub.add_parser(cmd)
        s.add_argument("id", help="task ID")
        if cmd in ("depend", "undepend"):
            s.add_argument("prerequisite")
    for cmd in ("overview", "next"):
        s = sub.add_parser(cmd)
        s.add_argument("--project", help="optional project ID filter")
    for cmd in ("import", "restore", "export", "backup"):
        s = sub.add_parser(cmd)
        s.add_argument("file")
        if cmd in ("import", "restore"):
            s.add_argument("--replace", action="store_true", required=True, help="acknowledge whole-state replacement")
        else:
            s.add_argument("--overwrite", action="store_true")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    store = Store(args.db)
    try:
        if args.command in ("import", "restore"):
            state = read_json(args.file)
            validate(state)
            store.run(validate, replacement=state)
            result = {"ok": True, "mode": "whole-state replacement", "projects": len(state["projects"]), "tasks": len(state["tasks"])}
        elif args.command in ("export", "backup"):
            state = store.run(validate)
            store.output(args.file, state, args.overwrite)
            result = {"ok": True, "file": args.file}
        elif args.command in ("overview", "next"):
            state = store.run(validate)
            result = overview(state, args.project) if args.command == "overview" else suggest(state, args.project)
        else:
            result = store.run(validate, action=lambda state: mutate(state, args))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (PlannerError, OSError, sqlite3.Error, UnicodeError, RecursionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
