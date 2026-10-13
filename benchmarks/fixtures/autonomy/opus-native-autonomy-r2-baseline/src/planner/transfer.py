"""JSON document format for export, import and backup (format 'local-work-planner' v1)."""
import json
import os
from pathlib import Path

from .model import Plan, PlannerError, Project, Task, now_utc, validate_plan

FORMAT, VERSION = "local-work-planner", 1
TOP_KEYS = {"format", "version", "exported_at", "next_task_id", "projects", "tasks"}
PROJECT_KEYS = {"key", "name", "created_at"}
TASK_KEYS = {"id", "project", "title", "priority", "estimate_minutes", "due", "note",
             "done_at", "created_at", "depends_on"}


def to_document(plan, project=None):
    tasks = [t for t in plan.tasks.values() if project is None or t.project == project]
    ids = {t.id for t in tasks}
    crossing = [(t.id, p) for t in tasks for p in sorted(t.depends_on) if p not in ids]
    if crossing:
        raise PlannerError("cannot export project subset: dependencies leave it ("
                           + ", ".join(f"#{t} needs #{p}" for t, p in crossing) + ")")
    doc = {"format": FORMAT, "version": VERSION, "exported_at": now_utc()}
    if project is None:
        doc["next_task_id"] = plan.next_task_id
    doc["projects"] = [vars(p).copy() for k, p in sorted(plan.projects.items())
                       if project is None or k == project]
    doc["tasks"] = [{**vars(t), "depends_on": sorted(t.depends_on)}
                    for t in sorted(tasks, key=lambda t: t.id)]
    return doc


def write_json_atomic(path, doc):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def read_document(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise PlannerError(f"file not found: {path}")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PlannerError(f"{path} is not valid JSON: {exc}")


def _check(cond, msg):
    if not cond:
        raise PlannerError(f"invalid document: {msg}")


def _typed(obj, name, types, where, optional=True):
    value = obj.get(name)
    _check((optional and value is None) or (isinstance(value, types) and not isinstance(value, bool)),
           f"{where}: field '{name}' has wrong type")
    return value


def document_to_plan(doc):
    """Strictly parse a document into a validated Plan with the document's ids."""
    _check(isinstance(doc, dict), "top level must be an object")
    _check(doc.get("format") == FORMAT, f"'format' must be '{FORMAT}'")
    _check(doc.get("version") == VERSION, f"unsupported version {doc.get('version')!r}")
    _check(not set(doc) - TOP_KEYS, f"unknown fields {sorted(set(doc) - TOP_KEYS)}")
    _check(isinstance(doc.get("projects"), list) and isinstance(doc.get("tasks"), list),
           "'projects' and 'tasks' must be lists")
    plan = Plan()
    for i, p in enumerate(doc["projects"]):
        where = f"projects[{i}]"
        _check(isinstance(p, dict) and not set(p) - PROJECT_KEYS, f"{where}: unknown fields")
        key = _typed(p, "key", str, where, optional=False)
        _check(key not in plan.projects, f"{where}: duplicate project key '{key}'")
        plan.projects[key] = Project(key, _typed(p, "name", str, where, optional=False),
                                     _typed(p, "created_at", str, where) or now_utc())
    for i, t in enumerate(doc["tasks"]):
        where = f"tasks[{i}]"
        _check(isinstance(t, dict) and not set(t) - TASK_KEYS, f"{where}: unknown fields")
        tid = _typed(t, "id", int, where, optional=False)
        _check(tid not in plan.tasks, f"{where}: duplicate task id {tid}")
        deps = t.get("depends_on", [])
        _check(isinstance(deps, list) and all(isinstance(d, int) and not isinstance(d, bool)
                                              for d in deps), f"{where}: 'depends_on' must list ids")
        plan.tasks[tid] = Task(
            id=tid, project=_typed(t, "project", str, where, optional=False),
            title=_typed(t, "title", str, where, optional=False),
            created_at=_typed(t, "created_at", str, where) or now_utc(),
            priority=_typed(t, "priority", str, where) or "normal",
            estimate_minutes=_typed(t, "estimate_minutes", int, where),
            due=_typed(t, "due", str, where), note=_typed(t, "note", str, where) or "",
            done_at=_typed(t, "done_at", str, where), depends_on=set(deps))
    highest = max(plan.tasks, default=0)
    plan.next_task_id = _typed(doc, "next_task_id", int, "document") or highest + 1
    _check(plan.next_task_id > highest, "'next_task_id' must exceed every task id")
    try:
        validate_plan(plan)
    except PlannerError as exc:
        raise PlannerError(f"invalid document: {exc}")
    return plan


def merge(plan, incoming):
    """Add all projects/tasks of `incoming` with fresh ids. Returns {old_id: new_id}."""
    clash = sorted(set(incoming.projects) & set(plan.projects))
    if clash:
        raise PlannerError(f"import rejected: project(s) already exist: {', '.join(clash)} "
                           "(import only adds new projects; nothing was changed)")
    plan.projects.update(incoming.projects)
    mapping = {}
    for old in sorted(incoming.tasks):
        mapping[old] = plan.next_task_id
        plan.next_task_id += 1
    for old, task in incoming.tasks.items():
        task.id = mapping[old]
        task.depends_on = {mapping[d] for d in task.depends_on}
        plan.tasks[task.id] = task
    return mapping
