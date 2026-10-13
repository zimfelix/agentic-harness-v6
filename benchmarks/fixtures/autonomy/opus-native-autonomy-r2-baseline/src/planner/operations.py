"""Domain mutations on a Plan. Callers validate and persist the result."""
from .model import (PlannerError, Project, Task, describe_cycle, find_cycle, now_utc,
                    parse_key, parse_title)


def add_project(plan, key, name):
    parse_key(key)
    if key in plan.projects:
        raise PlannerError(f"project '{key}' already exists")
    plan.projects[key] = Project(key, parse_title(name, "project name"), now_utc())


def add_task(plan, project, title, **fields):
    plan.project(project)
    task = Task(plan.next_task_id, project, parse_title(title), now_utc())
    plan.next_task_id += 1
    plan.tasks[task.id] = task
    edit_task(plan, task.id, **fields)
    return task


def edit_task(plan, task_id, depends_on=(), **fields):
    task = plan.task(task_id)
    for name, value in fields.items():
        setattr(task, name, value)
    for pre in depends_on:
        add_dependency(plan, task_id, pre)
    return task


def add_dependency(plan, task_id, prereq_id):
    task, prereq = plan.task(task_id), plan.task(prereq_id)
    if task_id == prereq_id:
        raise PlannerError(f"task #{task_id} cannot depend on itself")
    if task.is_done and not prereq.is_done:
        raise PlannerError(f"task #{task_id} is already done; reopen it before adding open "
                           f"prerequisite #{prereq_id}")
    task.depends_on.add(prereq_id)
    cycle = find_cycle(plan)
    if cycle:
        task.depends_on.discard(prereq_id)
        raise PlannerError(f"rejected: #{task_id} after #{prereq_id} would create the cycle "
                           f"{describe_cycle(cycle)}")


def remove_dependency(plan, task_id, prereq_id):
    task = plan.task(task_id)
    if prereq_id not in task.depends_on:
        raise PlannerError(f"task #{task_id} does not depend on #{prereq_id}")
    task.depends_on.discard(prereq_id)


def complete(plan, task_id):
    task = plan.task(task_id)
    if task.is_done:
        raise PlannerError(f"task #{task_id} is already done")
    blocking = plan.open_prerequisites(task)
    if blocking:
        raise PlannerError(f"task #{task_id} is blocked by unfinished "
                           + ", ".join(f"#{p} {plan.tasks[p].title!r}" for p in blocking))
    task.done_at = now_utc()


def reopen(plan, task_id):
    task = plan.task(task_id)
    if not task.is_done:
        raise PlannerError(f"task #{task_id} is not done")
    done_dependents = [d for d in plan.dependents(task_id) if plan.tasks[d].is_done]
    if done_dependents:
        raise PlannerError(f"cannot reopen #{task_id}: done tasks depend on it ("
                           + ", ".join(f"#{d}" for d in done_dependents) + "); reopen them first")
    task.done_at = None


def _detach_or_refuse(plan, doomed, detach, what):
    """Handle tasks outside `doomed` that depend on a task inside it. Returns removed links."""
    links = [(t.id, p) for t in plan.tasks.values() if t.id not in doomed
             for p in sorted(t.depends_on) if p in doomed]
    if links and not detach:
        raise PlannerError(f"cannot delete {what}: still required by "
                           + ", ".join(f"#{t} (needs #{p})" for t, p in links)
                           + "; use --detach to remove these dependencies")
    for t, p in links:
        plan.tasks[t].depends_on.discard(p)
    return links


def delete_task(plan, task_id, detach=False):
    plan.task(task_id)
    links = _detach_or_refuse(plan, {task_id}, detach, f"task #{task_id}")
    del plan.tasks[task_id]
    return links


def delete_project(plan, key, detach=False):
    plan.project(key)
    doomed = {t.id for t in plan.tasks.values() if t.project == key}
    links = _detach_or_refuse(plan, doomed, detach, f"project '{key}'")
    for tid in doomed:
        del plan.tasks[tid]
    del plan.projects[key]
    return sorted(doomed), links
