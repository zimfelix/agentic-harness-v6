"""State schema, validation and domain operations.

The state is a plain JSON-compatible dict (see docs/data-format.md). Operations
mutate the dict they receive; callers pass a deep copy and only persist it after
the operation and a full re-validation succeeded.
"""
import datetime as dt
import re
from decimal import Decimal, InvalidOperation

FORMAT = "local-planner"
SCHEMA_VERSION = 1
PRIORITIES = ("critical", "high", "normal", "low")  # index = rank, lower is more important
STATUSES = ("open", "done")
MAX_ESTIMATE_MINUTES = 10000 * 60

_PROJECT_ID = re.compile(r"^p([1-9][0-9]*)$")
_TASK_ID = re.compile(r"^t([1-9][0-9]*)$")
_ESTIMATE = re.compile(r"^(?:(\d+(?:\.\d+)?)h)?(?:(\d+)m)?$")


class PlannerError(Exception):
    """A user-facing error: invalid input or a violated planning rule."""


def utc_now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def empty_state():
    return {"format": FORMAT, "schema_version": SCHEMA_VERSION,
            "next_project": 1, "next_task": 1, "projects": [], "tasks": []}


def id_number(item_id):
    m = _PROJECT_ID.match(item_id) or _TASK_ID.match(item_id)
    return int(m.group(1))


# ---------------------------------------------------------------- input parsing

def parse_priority(value):
    v = value.strip().lower()
    if v not in PRIORITIES:
        raise PlannerError(f"priority must be one of {', '.join(PRIORITIES)} (got {value!r})")
    return v


def parse_date(value):
    v = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        try:
            return dt.date.fromisoformat(v).isoformat()
        except ValueError:
            pass
    raise PlannerError(f"date must be a real calendar date YYYY-MM-DD (got {value!r})")


def parse_estimate(value):
    """'2h', '90m', '1h30m', '1.5' (hours) -> whole minutes > 0."""
    v = value.strip().lower().replace(" ", "")
    try:
        if re.fullmatch(r"\d+(?:\.\d+)?", v):
            minutes = Decimal(v) * 60
        else:
            m = _ESTIMATE.match(v)
            if not v or not m:
                raise PlannerError
            minutes = Decimal(m.group(1) or 0) * 60 + int(m.group(2) or 0)
    except (PlannerError, InvalidOperation):
        raise PlannerError(f"estimate must look like 2h, 90m, 1h30m or 1.5 (hours) (got {value!r})")
    if minutes != minutes.to_integral_value():
        raise PlannerError(f"estimate must be a whole number of minutes (got {value!r})")
    minutes = int(minutes)
    if not 0 < minutes <= MAX_ESTIMATE_MINUTES:
        raise PlannerError(f"estimate must be between 1m and {MAX_ESTIMATE_MINUTES // 60}h (got {value!r})")
    return minutes


def format_estimate(minutes):
    if minutes is None:
        return "-"
    h, m = divmod(minutes, 60)
    return (f"{h}h" if h else "") + (f"{m}m" if m or not h else "")


def clean_text(value, field, required=True, max_len=500):
    if not isinstance(value, str):
        raise PlannerError(f"{field} must be text")
    v = value.strip()
    if required and not v:
        raise PlannerError(f"{field} must not be empty")
    if len(v) > max_len:
        raise PlannerError(f"{field} is longer than {max_len} characters")
    if any(ord(c) < 32 and c not in "\n\t" for c in v):
        raise PlannerError(f"{field} contains control characters")
    return v


# ------------------------------------------------------------------ validation

def validate_state(data):
    """Check a whole state (stored file, import or backup). Returns a normalized
    copy or raises PlannerError listing every problem found."""
    errors = []
    if not isinstance(data, dict):
        raise PlannerError("invalid data: top level must be a JSON object")
    if data.get("format") != FORMAT:
        errors.append(f"'format' must be {FORMAT!r}")
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"unsupported schema_version {data.get('schema_version')!r} (expected {SCHEMA_VERSION})")
    projects, tasks = data.get("projects"), data.get("tasks")
    if not isinstance(projects, list) or not isinstance(tasks, list):
        errors.append("'projects' and 'tasks' must be lists")
        raise PlannerError(_join(errors))

    out = empty_state()
    names = {}
    for i, p in enumerate(projects):
        where = f"projects[{i}]"
        if not isinstance(p, dict):
            errors.append(f"{where}: must be an object")
            continue
        pid = p.get("id")
        if not isinstance(pid, str) or not _PROJECT_ID.match(pid):
            errors.append(f"{where}: id must look like p1, p2, ... (got {pid!r})")
            continue
        if any(q["id"] == pid for q in out["projects"]):
            errors.append(f"{where}: duplicate project id {pid}")
            continue
        try:
            name = clean_text(p.get("name"), f"{where}.name", max_len=100)
            desc = clean_text(p.get("description", "") or "", f"{where}.description", required=False)
        except PlannerError as e:
            errors.append(str(e))
            continue
        if name.lower() in names:
            errors.append(f"{where}: project name {name!r} already used by {names[name.lower()]}")
        names[name.lower()] = pid
        out["projects"].append({"id": pid, "name": name, "description": desc,
                                "created": _text_or(p.get("created"), utc_now())})
    project_ids = {p["id"] for p in out["projects"]}

    for i, t in enumerate(tasks):
        where = f"tasks[{i}]"
        if not isinstance(t, dict):
            errors.append(f"{where}: must be an object")
            continue
        tid = t.get("id")
        if not isinstance(tid, str) or not _TASK_ID.match(tid):
            errors.append(f"{where}: id must look like t1, t2, ... (got {tid!r})")
            continue
        where = f"task {tid}"
        if any(q["id"] == tid for q in out["tasks"]):
            errors.append(f"{where}: duplicate task id")
            continue
        try:
            task = _validate_task_fields(t, where)
        except PlannerError as e:
            errors.append(str(e))
            continue
        if task["project"] not in project_ids:
            errors.append(f"{where}: project {task['project']!r} does not exist")
        out["tasks"].append(task)

    by_id = {t["id"]: t for t in out["tasks"]}
    for t in out["tasks"]:
        for d in t["depends_on"]:
            if d not in by_id:
                errors.append(f"task {t['id']}: depends on missing task {d!r}")
            elif t["status"] == "done" and by_id[d]["status"] != "done":
                errors.append(f"task {t['id']}: is done but prerequisite {d} is not")
    cycle = find_cycle(out["tasks"])
    if cycle:
        errors.append("dependency cycle: " + " -> ".join(cycle))

    max_p = max((id_number(p["id"]) for p in out["projects"]), default=0)
    max_t = max((id_number(t["id"]) for t in out["tasks"]), default=0)
    for key, highest in (("next_project", max_p), ("next_task", max_t)):
        value = data.get(key, highest + 1)
        if not isinstance(value, int) or isinstance(value, bool) or value <= highest:
            errors.append(f"'{key}' must be an integer greater than {highest}")
        else:
            out[key] = value
    if errors:
        raise PlannerError(_join(errors))
    return out


def _validate_task_fields(t, where):
    if t.get("project") is None or not isinstance(t.get("project"), str):
        raise PlannerError(f"{where}: project must be a project id")
    deps = t.get("depends_on", [])
    if not isinstance(deps, list) or not all(isinstance(d, str) for d in deps):
        raise PlannerError(f"{where}: depends_on must be a list of task ids")
    if len(set(deps)) != len(deps):
        raise PlannerError(f"{where}: depends_on contains duplicates")
    priority = t.get("priority", "normal")
    if priority not in PRIORITIES:
        raise PlannerError(f"{where}: priority must be one of {', '.join(PRIORITIES)}")
    est = t.get("estimate_minutes")
    if est is not None and (not isinstance(est, int) or isinstance(est, bool)
                            or not 0 < est <= MAX_ESTIMATE_MINUTES):
        raise PlannerError(f"{where}: estimate_minutes must be null or an integer 1..{MAX_ESTIMATE_MINUTES}")
    due = t.get("due")
    if due is not None:
        if not isinstance(due, str):
            raise PlannerError(f"{where}: due must be null or YYYY-MM-DD")
        try:
            due = parse_date(due)
        except PlannerError as e:
            raise PlannerError(f"{where}: {e}")
    status = t.get("status", "open")
    if status not in STATUSES:
        raise PlannerError(f"{where}: status must be open or done")
    return {
        "id": t["id"], "project": t["project"],
        "title": clean_text(t.get("title"), f"{where}.title", max_len=200),
        "priority": priority, "estimate_minutes": est, "due": due,
        "depends_on": sorted(deps, key=lambda d: (len(d), d)),
        "status": status,
        "done_at": _text_or(t.get("done_at"), utc_now()) if status == "done" else None,
        "notes": clean_text(t.get("notes", "") or "", f"{where}.notes", required=False, max_len=2000),
        "created": _text_or(t.get("created"), utc_now()),
    }


def _text_or(value, default):
    return value if isinstance(value, str) and value else default


def _join(errors):
    return "invalid data:\n" + "\n".join(f"  - {e}" for e in errors)


def find_cycle(tasks):
    """Return a cycle as a list of ids (first == last) or None."""
    deps = {t["id"]: [d for d in t["depends_on"]] for t in tasks}
    state = {}  # id -> 1 visiting, 2 finished
    for root in sorted(deps, key=id_number):
        if state.get(root):
            continue
        stack, path = [(root, iter(deps[root]))], [root]
        state[root] = 1
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                state[node] = 2
                stack.pop()
                path.pop()
            elif nxt in deps and state.get(nxt) == 1:
                return path[path.index(nxt):] + [nxt]
            elif nxt in deps and not state.get(nxt):
                state[nxt] = 1
                stack.append((nxt, iter(deps[nxt])))
                path.append(nxt)
    return None


# ------------------------------------------------------------------- lookups

def get_task(state, tid):
    tid = tid.strip().lower()
    for t in state["tasks"]:
        if t["id"] == tid:
            return t
    raise PlannerError(f"no task {tid!r}")


def get_project(state, ref):
    ref = ref.strip()
    for p in state["projects"]:
        if p["id"] == ref.lower() or p["name"].lower() == ref.lower():
            return p
    raise PlannerError(f"no project {ref!r} (use an id like p1 or the exact name)")


def dependents(state, tid):
    return [t for t in state["tasks"] if tid in t["depends_on"]]


def unfinished_prereqs(state, task):
    return [d for d in task["depends_on"] if get_task(state, d)["status"] != "done"]


# ---------------------------------------------------------------- operations

def add_project(state, name, description=""):
    name = clean_text(name, "project name", max_len=100)
    _check_project_name(state, name)
    pid = f"p{state['next_project']}"
    state["next_project"] += 1
    p = {"id": pid, "name": name, "description": clean_text(description or "", "description", required=False),
         "created": utc_now()}
    state["projects"].append(p)
    return p


def edit_project(state, ref, name=None, description=None):
    p = get_project(state, ref)
    if name is not None:
        name = clean_text(name, "project name", max_len=100)
        _check_project_name(state, name, exclude=p["id"])
        p["name"] = name
    if description is not None:
        p["description"] = clean_text(description, "description", required=False)
    return p


def _check_project_name(state, name, exclude=None):
    for p in state["projects"]:
        if p["id"] != exclude and p["name"].lower() == name.lower():
            raise PlannerError(f"project name {name!r} is already used by {p['id']}")
    if _PROJECT_ID.match(name.lower()) or _TASK_ID.match(name.lower()):
        raise PlannerError("project name must not look like an id (p1, t1, ...)")


def _detach_or_refuse(state, removed_ids, detach, what):
    """Return [(dependent, prerequisite)] edges pointing into removed_ids from
    tasks that survive; remove them if detach, otherwise refuse."""
    edges = [(t["id"], d) for t in state["tasks"] if t["id"] not in removed_ids
             for d in t["depends_on"] if d in removed_ids]
    if edges and not detach:
        listing = ", ".join(f"{a} depends on {b}" for a, b in edges)
        raise PlannerError(f"cannot delete {what}: {listing}. "
                           "Use --detach to remove these dependencies as well.")
    for a, b in edges:
        get_task(state, a)["depends_on"].remove(b)
    return edges


def delete_project(state, ref, detach=False, yes=False):
    p = get_project(state, ref)
    ids = {t["id"] for t in state["tasks"] if t["project"] == p["id"]}
    if ids and not yes:
        raise PlannerError(f"project {p['id']} has {len(ids)} task(s); repeat with --yes to delete them too")
    edges = _detach_or_refuse(state, ids, detach, f"project {p['id']}")
    state["tasks"] = [t for t in state["tasks"] if t["id"] not in ids]
    state["projects"].remove(p)
    return p, sorted(ids, key=id_number), edges


def add_task(state, project_ref, title, priority="normal", estimate=None, due=None, depends_on=(), notes=""):
    p = get_project(state, project_ref)
    tid = f"t{state['next_task']}"
    state["next_task"] += 1
    t = {"id": tid, "project": p["id"], "title": clean_text(title, "title", max_len=200),
         "priority": parse_priority(priority), "estimate_minutes": parse_estimate(estimate) if estimate else None,
         "due": parse_date(due) if due else None, "depends_on": [], "status": "open", "done_at": None,
         "notes": clean_text(notes or "", "notes", required=False, max_len=2000), "created": utc_now()}
    state["tasks"].append(t)
    if depends_on:
        add_dependencies(state, tid, depends_on)
    return t


def edit_task(state, tid, title=None, priority=None, estimate=None, clear_estimate=False,
              due=None, clear_due=False, project=None, notes=None):
    t = get_task(state, tid)
    if title is not None:
        t["title"] = clean_text(title, "title", max_len=200)
    if priority is not None:
        t["priority"] = parse_priority(priority)
    if clear_estimate:
        t["estimate_minutes"] = None
    elif estimate is not None:
        t["estimate_minutes"] = parse_estimate(estimate)
    if clear_due:
        t["due"] = None
    elif due is not None:
        t["due"] = parse_date(due)
    if project is not None:
        t["project"] = get_project(state, project)["id"]
    if notes is not None:
        t["notes"] = clean_text(notes, "notes", required=False, max_len=2000)
    return t


def add_dependencies(state, tid, prereq_ids):
    t = get_task(state, tid)
    for raw in prereq_ids:
        d = get_task(state, raw)
        if d["id"] == t["id"]:
            raise PlannerError(f"task {t['id']} cannot depend on itself")
        if d["id"] in t["depends_on"]:
            continue
        if t["status"] == "done" and d["status"] != "done":
            raise PlannerError(f"task {t['id']} is done; it cannot get the unfinished prerequisite {d['id']}")
        path = _path(state, d["id"], t["id"])
        if path:
            raise PlannerError(f"dependency {t['id']} -> {d['id']} would create a cycle: "
                               + " -> ".join([t["id"]] + path))
        t["depends_on"].append(d["id"])
    t["depends_on"].sort(key=id_number)
    return t


def _path(state, start, goal):
    """Dependency path start -> ... -> goal following depends_on, or None."""
    seen, stack = set(), [(start, [start])]
    while stack:
        node, path = stack.pop()
        if node == goal:
            return path
        if node in seen:
            continue
        seen.add(node)
        for d in get_task(state, node)["depends_on"]:
            stack.append((d, path + [d]))
    return None


def remove_dependencies(state, tid, prereq_ids):
    t = get_task(state, tid)
    for raw in prereq_ids:
        d = raw.strip().lower()
        if d not in t["depends_on"]:
            raise PlannerError(f"task {t['id']} does not depend on {d}")
        t["depends_on"].remove(d)
    return t


def complete_task(state, tid):
    t = get_task(state, tid)
    if t["status"] == "done":
        raise PlannerError(f"task {t['id']} is already done")
    open_deps = unfinished_prereqs(state, t)
    if open_deps:
        raise PlannerError(f"task {t['id']} is blocked by unfinished prerequisite(s): {', '.join(open_deps)}")
    t["status"], t["done_at"] = "done", utc_now()
    return t


def reopen_task(state, tid):
    t = get_task(state, tid)
    if t["status"] != "done":
        raise PlannerError(f"task {t['id']} is not done")
    done_deps = [x["id"] for x in dependents(state, t["id"]) if x["status"] == "done"]
    if done_deps:
        raise PlannerError(f"cannot reopen {t['id']}: completed task(s) {', '.join(done_deps)} depend on it; "
                           "reopen those first")
    t["status"], t["done_at"] = "open", None
    return t


def delete_task(state, tid, detach=False):
    t = get_task(state, tid)
    edges = _detach_or_refuse(state, {t["id"]}, detach, f"task {t['id']}")
    state["tasks"].remove(t)
    return t, edges


def merge_states(state, incoming):
    """Append a validated incoming state with fresh ids. Returns the id mapping."""
    mapping = {}
    for p in incoming["projects"]:
        name = p["name"]
        _check_project_name(state, name)
        new = dict(p, id=f"p{state['next_project']}")
        state["next_project"] += 1
        mapping[p["id"]] = new["id"]
        state["projects"].append(new)
    for t in incoming["tasks"]:
        mapping[t["id"]] = f"t{state['next_task']}"
        state["next_task"] += 1
    for t in incoming["tasks"]:
        state["tasks"].append(dict(t, id=mapping[t["id"]], project=mapping[t["project"]],
                                   depends_on=[mapping[d] for d in t["depends_on"]]))
    return mapping
