"""Derived views: task status, next-work ranking and project overview."""
import datetime as dt

from .model import PRIORITIES, format_estimate, id_number

URGENT_DAYS = 2  # due within this many days (or overdue) counts as urgent
NO_DUE = "9999-12-31"


def statuses(state):
    """task id -> 'done' | 'blocked' | 'ready'."""
    done = {t["id"] for t in state["tasks"] if t["status"] == "done"}
    return {t["id"]: "done" if t["id"] in done
            else "blocked" if any(d not in done for d in t["depends_on"]) else "ready"
            for t in state["tasks"]}


def blocked_report(state, project_id=None):
    """[(task, [unfinished prerequisite ids])] for blocked tasks."""
    st = statuses(state)
    return [(t, [d for d in t["depends_on"] if st[d] != "done"])
            for t in state["tasks"]
            if st[t["id"]] == "blocked" and project_id in (None, t["project"])]


def _open_dependents(state):
    """task id -> set of open tasks that (transitively) depend on it."""
    direct = {t["id"]: [] for t in state["tasks"]}
    for t in state["tasks"]:
        if t["status"] != "done":
            for d in t["depends_on"]:
                direct[d].append(t["id"])
    result = {}
    for tid in direct:
        seen, stack = set(), list(direct[tid])
        while stack:
            x = stack.pop()
            if x not in seen:
                seen.add(x)
                stack.extend(direct[x])
        result[tid] = seen
    return result


def next_work(state, today, project_id=None, limit=5):
    """Rank ready tasks. Returns [(task, reasons)] best first.

    Each candidate inherits the highest priority and earliest due date of the
    open tasks it unblocks, so prerequisites of urgent work surface early.
    """
    st = statuses(state)
    by_id = {t["id"]: t for t in state["tasks"]}
    downstream = _open_dependents(state)
    urgent_until = (today + dt.timedelta(days=URGENT_DAYS)).isoformat()
    ranked = []
    for t in state["tasks"]:
        if st[t["id"]] != "ready" or project_id not in (None, t["project"]):
            continue
        group = [t] + [by_id[x] for x in downstream[t["id"]]]
        prio_src = min(group, key=lambda x: (PRIORITIES.index(x["priority"]), id_number(x["id"])))
        due_src = min((x for x in group if x["due"]), key=lambda x: (x["due"], id_number(x["id"])), default=None)
        rank = PRIORITIES.index(prio_src["priority"])
        due = due_src["due"] if due_src else NO_DUE
        urgent = due <= urgent_until
        est = t["estimate_minutes"]
        key = ((0, due, rank) if urgent else (1, "", rank)) + (
            due, -len(downstream[t["id"]]), est if est is not None else float("inf"), id_number(t["id"]))
        ranked.append((key, t, _reasons(t, today, prio_src, due_src, downstream[t["id"]])))
    ranked.sort(key=lambda r: r[0])
    return [(t, reasons) for _, t, reasons in ranked[:limit]]


def _reasons(t, today, prio_src, due_src, downstream):
    reasons = []
    if due_src:
        days = (dt.date.fromisoformat(due_src["due"]) - today).days
        when = (f"overdue by {-days} day(s)" if days < 0 else "due today" if days == 0
                else f"due in {days} day(s)") + f" ({due_src['due']})"
        reasons.append(when if due_src is t else f"{when} via {due_src['id']}")
    reasons.append(f"priority {prio_src['priority']}"
                   + ("" if prio_src is t or prio_src["priority"] == t["priority"] else f" via {prio_src['id']}"))
    if downstream:
        reasons.append(f"unblocks {len(downstream)} task(s)")
    reasons.append(f"estimate {format_estimate(t['estimate_minutes'])}")
    return reasons


def overview(state, today):
    """Per-project summary rows."""
    st = statuses(state)
    rows = []
    for p in state["projects"]:
        tasks = [t for t in state["tasks"] if t["project"] == p["id"]]
        open_tasks = [t for t in tasks if t["status"] != "done"]
        dues = sorted(t["due"] for t in open_tasks if t["due"])
        rows.append({
            "project": p, "tasks": tasks, "total": len(tasks),
            "done": sum(st[t["id"]] == "done" for t in tasks),
            "ready": sum(st[t["id"]] == "ready" for t in tasks),
            "blocked": sum(st[t["id"]] == "blocked" for t in tasks),
            "remaining_minutes": sum(t["estimate_minutes"] or 0 for t in open_tasks),
            "unestimated": sum(t["estimate_minutes"] is None for t in open_tasks),
            "overdue": [t for t in open_tasks if t["due"] and t["due"] < today.isoformat()],
            "next_due": dues[0] if dues else None,
        })
    return rows
