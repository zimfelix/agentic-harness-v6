"""Domain types, input parsing, derived task state and plan invariants."""
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

PRIORITIES = ("urgent", "high", "normal", "low")  # index = rank, lower first
STATES = ("ready", "blocked", "done")
KEY_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")


class PlannerError(Exception):
    """Expected, user-facing failure. Nothing is written when raised."""


@dataclass
class Project:
    key: str
    name: str
    created_at: str


@dataclass
class Task:
    id: int
    project: str
    title: str
    created_at: str
    priority: str = "normal"
    estimate_minutes: int | None = None
    due: str | None = None  # plain calendar date YYYY-MM-DD
    note: str = ""
    done_at: str | None = None  # UTC instant
    depends_on: set[int] = field(default_factory=set)

    @property
    def is_done(self):
        return self.done_at is not None


@dataclass
class Plan:
    projects: dict[str, Project] = field(default_factory=dict)
    tasks: dict[int, Task] = field(default_factory=dict)
    next_task_id: int = 1

    def project(self, key):
        if key not in self.projects:
            raise PlannerError(f"unknown project '{key}'")
        return self.projects[key]

    def task(self, task_id):
        if task_id not in self.tasks:
            raise PlannerError(f"unknown task #{task_id}")
        return self.tasks[task_id]

    def open_prerequisites(self, task):
        return sorted(p for p in task.depends_on if not self.tasks[p].is_done)

    def dependents(self, task_id):
        return sorted(t.id for t in self.tasks.values() if task_id in t.depends_on)

    def state(self, task):
        if task.is_done:
            return "done"
        return "blocked" if self.open_prerequisites(task) else "ready"


def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_key(value):
    if not KEY_RE.match(value or ""):
        raise PlannerError(
            f"invalid project key '{value}': use lowercase letters, digits and '-', max 40 chars")
    return value


def parse_title(value, what="title"):
    value = (value or "").strip()
    if not value:
        raise PlannerError(f"{what} must not be empty")
    return value


def parse_priority(value):
    if value not in PRIORITIES:
        raise PlannerError(f"invalid priority '{value}': choose one of {', '.join(PRIORITIES)}")
    return value


def parse_date(value):
    try:
        return date.fromisoformat(value).isoformat() if len(value) == 10 else _bad_date(value)
    except (TypeError, ValueError):
        return _bad_date(value)


def _bad_date(value):
    raise PlannerError(f"invalid date '{value}': use YYYY-MM-DD")


def parse_estimate(value):
    """'90m', '1.5h', '2h30m' or a bare number of hours -> minutes."""
    text = str(value).strip().lower()
    match = re.fullmatch(r"(?:(\d+(?:\.\d+)?)h)?\s*(?:(\d+)m)?", text)
    if re.fullmatch(r"\d+(?:\.\d+)?", text):
        hours, minutes = text, None
    elif match and text:
        hours, minutes = match.groups()
    else:
        raise PlannerError(f"invalid estimate '{value}': use e.g. 90m, 1.5h, 2h30m")
    total = round(float(hours or 0) * 60) + int(minutes or 0)
    if total > 100000:
        raise PlannerError(f"estimate '{value}' is unrealistically large")
    return total


def format_minutes(minutes):
    if minutes is None:
        return "-"
    h, m = divmod(minutes, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m"


def find_cycle(plan):
    """Return a list of task ids forming a cycle, or None."""
    color = {}  # 1 = on stack, 2 = finished

    def visit(tid, path):
        color[tid] = 1
        path.append(tid)
        for pre in sorted(plan.tasks[tid].depends_on):
            if pre not in plan.tasks:
                continue
            if color.get(pre) == 1:
                return path[path.index(pre):] + [pre]
            if pre not in color:
                found = visit(pre, path)
                if found:
                    return found
        path.pop()
        color[tid] = 2
        return None

    for tid in sorted(plan.tasks):
        if tid not in color:
            found = visit(tid, [])
            if found:
                return found
    return None


def describe_cycle(cycle):
    return " -> ".join(f"#{t}" for t in cycle)


def validate_plan(plan):
    """Raise PlannerError on the first violated invariant. Runs before every commit."""
    for key, project in plan.projects.items():
        parse_key(key)
        parse_title(project.name, "project name")
    for tid, task in plan.tasks.items():
        if not isinstance(tid, int) or tid < 1 or tid >= plan.next_task_id:
            raise PlannerError(f"invalid task id {tid!r}")
        if task.project not in plan.projects:
            raise PlannerError(f"task #{tid} refers to unknown project '{task.project}'")
        parse_title(task.title)
        parse_priority(task.priority)
        if task.estimate_minutes is not None and (
                not isinstance(task.estimate_minutes, int) or task.estimate_minutes < 0):
            raise PlannerError(f"task #{tid} has an invalid estimate")
        if task.due is not None:
            parse_date(task.due)
        for pre in task.depends_on:
            if pre == tid:
                raise PlannerError(f"task #{tid} cannot depend on itself")
            if pre not in plan.tasks:
                raise PlannerError(f"task #{tid} depends on missing task #{pre}")
            if task.is_done and not plan.tasks[pre].is_done:
                raise PlannerError(f"task #{tid} is done but its prerequisite #{pre} is open")
    cycle = find_cycle(plan)
    if cycle:
        raise PlannerError(f"dependency cycle: {describe_cycle(cycle)}")
