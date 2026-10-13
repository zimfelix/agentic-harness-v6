"""Read-side logic: next-work ranking and project overview."""
from datetime import date, timedelta

from .model import PRIORITIES

DUE_SOON_DAYS = 2


def unblocks(plan, task_id):
    """Number of open tasks that directly or transitively wait for task_id."""
    seen, stack = set(), [task_id]
    while stack:
        for dep in plan.dependents(stack.pop()):
            if dep not in seen and not plan.tasks[dep].is_done:
                seen.add(dep)
                stack.append(dep)
    return len(seen)


def rank_key(plan, task, today):
    due = date.fromisoformat(task.due) if task.due else None
    pressing = due is not None and due <= today + timedelta(days=DUE_SOON_DAYS)
    return (0 if pressing else 1,
            PRIORITIES.index(task.priority),
            due or date.max,
            -unblocks(plan, task.id),
            task.estimate_minutes if task.estimate_minutes is not None else float("inf"),
            task.id)


def reason(plan, task, today):
    parts = []
    if task.due:
        delta = (date.fromisoformat(task.due) - today).days
        parts.append(f"overdue by {-delta}d" if delta < 0 else
                     "due today" if delta == 0 else f"due in {delta}d")
    parts.append(f"{task.priority} priority")
    n = unblocks(plan, task.id)
    if n:
        parts.append(f"unblocks {n} task{'s' if n > 1 else ''}")
    return ", ".join(parts)


def suggest(plan, today, project=None):
    """Ready tasks only (open, all prerequisites done), best first."""
    candidates = [t for t in plan.tasks.values()
                  if plan.state(t) == "ready" and (project is None or t.project == project)]
    return sorted(candidates, key=lambda t: rank_key(plan, t, today))


def overview(plan, key, today):
    tasks = sorted((t for t in plan.tasks.values() if t.project == key), key=lambda t: t.id)
    counts = {s: 0 for s in ("ready", "blocked", "done")}
    for t in tasks:
        counts[plan.state(t)] += 1
    open_tasks = [t for t in tasks if not t.is_done]
    return {
        "tasks": tasks,
        "counts": counts,
        "remaining_minutes": sum(t.estimate_minutes or 0 for t in open_tasks),
        "unestimated": sum(1 for t in open_tasks if t.estimate_minutes is None),
        "overdue": [t for t in open_tasks if t.due and date.fromisoformat(t.due) < today],
    }
