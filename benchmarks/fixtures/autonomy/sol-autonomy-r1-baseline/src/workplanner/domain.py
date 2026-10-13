"""Pure planner rules. Every accepted state satisfies the same invariants."""
import copy
import re
from datetime import date


ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")


def empty():
    return {"version": 1, "projects": [], "tasks": []}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identifier(value):
    require(isinstance(value, str) and ID.fullmatch(value), f"Invalid ID: {value!r}")


def text(value, field):
    require(isinstance(value, str) and value.strip() and len(value) <= 500,
            f"{field} must be nonblank text, at most 500 characters")


def keys(obj, expected, label):
    require(isinstance(obj, dict) and set(obj) == set(expected),
            f"{label}: expected exactly {', '.join(expected)}")


def validate(state):
    keys(state, ("version", "projects", "tasks"), "state")
    require(type(state["version"]) is int and state["version"] == 1, "Unsupported schema version")
    require(isinstance(state["projects"], list) and isinstance(state["tasks"], list),
            "projects and tasks must be arrays")
    projects, tasks = {}, {}
    for project in state["projects"]:
        keys(project, ("id", "name"), "project")
        identifier(project["id"])
        text(project["name"], "name")
        require(project["id"] not in projects, "Duplicate project ID")
        projects[project["id"]] = project
    for task in state["tasks"]:
        keys(task, ("id", "project", "title", "estimate", "priority", "due", "done", "depends_on"), "task")
        identifier(task["id"])
        identifier(task["project"])
        text(task["title"], "title")
        require(task["id"] not in tasks, "Duplicate task ID")
        require(task["project"] in projects, f"{task['id']}: unknown project")
        require(type(task["estimate"]) is int and task["estimate"] > 0, "estimate must be positive integer minutes")
        require(type(task["priority"]) is int and task["priority"] in (1, 2, 3), "priority must be 1, 2 or 3")
        require(type(task["done"]) is bool, "done must be boolean")
        if task["due"] is not None:
            due = task["due"]
            require(isinstance(due, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", due), "due must be YYYY-MM-DD or null")
            try:
                date.fromisoformat(due)
            except ValueError:
                raise ValueError(f"Invalid due date: {due}") from None
        deps = task["depends_on"]
        require(isinstance(deps, list), "depends_on must be an array")
        for dep in deps:
            identifier(dep)
        require(len(deps) == len(set(deps)), "Duplicate prerequisite")
        tasks[task["id"]] = task
    # Kahn traversal avoids recursion limits on valid long chains.
    indegree = {tid: len(t["depends_on"]) for tid, t in tasks.items()}
    outgoing = {tid: [] for tid in tasks}
    for tid, task in tasks.items():
        for dep in task["depends_on"]:
            require(dep in tasks, f"{tid}: unknown prerequisite {dep}")
            require(dep != tid, f"{tid}: self dependency is a cycle")
            require(not task["done"] or tasks[dep]["done"], f"{tid}: completed task has unfinished prerequisite {dep}")
            outgoing[dep].append(tid)
    queue = [tid for tid, degree in indegree.items() if degree == 0]
    visited = 0
    while queue:
        tid = queue.pop()
        visited += 1
        for child in outgoing[tid]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    require(visited == len(tasks), "Dependency cycle detected")
    return state


def find(state, collection, identity):
    for item in state[collection]:
        if item["id"] == identity:
            return item
    raise ValueError(f"Unknown {collection[:-1]}: {identity}")


def mutate(state, action, identity, **values):
    """Return a validated copy, never partially mutate the caller's state."""
    result = copy.deepcopy(state)
    if action == "project-add":
        result["projects"].append({"id": identity, "name": values["name"]})
    elif action == "project-update":
        find(result, "projects", identity)["name"] = values["name"]
    elif action == "project-delete":
        find(result, "projects", identity)
        removed = {t["id"] for t in result["tasks"] if t["project"] == identity}
        require(not removed or values.get("cascade"), "Project has tasks; use --cascade after reviewing overview")
        for task in result["tasks"]:
            require(task["id"] in removed or not removed.intersection(task["depends_on"]),
                    f"Cannot delete project: referenced by {task['id']}")
        result["tasks"] = [t for t in result["tasks"] if t["id"] not in removed]
        result["projects"] = [p for p in result["projects"] if p["id"] != identity]
    elif action == "task-add":
        result["tasks"].append({"id": identity, "done": False, **values})
    elif action == "task-update":
        require(bool(values), "No changes supplied")
        find(result, "tasks", identity).update(values)
    elif action in ("done", "reopen"):
        find(result, "tasks", identity)["done"] = action == "done"
    elif action == "task-delete":
        find(result, "tasks", identity)
        for task in result["tasks"]:
            require(identity not in task["depends_on"], f"Cannot delete: referenced by {task['id']}")
        result["tasks"] = [t for t in result["tasks"] if t["id"] != identity]
    else:
        raise ValueError(f"Unknown action: {action}")
    return validate(result)


def task_view(state, task):
    tasks = {t["id"]: t for t in state["tasks"]}
    blockers = sorted(dep for dep in task["depends_on"] if not tasks[dep]["done"])
    return {**task, "status": "done" if task["done"] else "blocked" if blockers else "ready", "blockers": blockers}


def next_task(state, project=None):
    if project is not None:
        find(state, "projects", project)
    ready = [t for t in state["tasks"] if (project is None or t["project"] == project)
             and task_view(state, t)["status"] == "ready"]
    if not ready:
        return None
    selected = min(ready, key=lambda t: (t["due"] is None, t["due"] or "", t["priority"], t["estimate"], t["id"]))
    return task_view(state, selected)


def overview(state, project=None):
    if project is not None:
        find(state, "projects", project)
    rows = []
    for p in sorted(state["projects"], key=lambda p: p["id"]):
        if project is not None and p["id"] != project:
            continue
        tasks = [task_view(state, t) for t in sorted(state["tasks"], key=lambda t: t["id"]) if t["project"] == p["id"]]
        rows.append({**p, "tasks": tasks, "counts": {status: sum(t["status"] == status for t in tasks)
                    for status in ("ready", "blocked", "done")},
                    "estimate_minutes": sum(t["estimate"] for t in tasks),
                    "remaining_minutes": sum(t["estimate"] for t in tasks if not t["done"])})
    return {"projects": rows, "next": next_task(state, project)}
