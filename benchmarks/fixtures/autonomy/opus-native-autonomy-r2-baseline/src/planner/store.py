"""SQLite persistence: schema migrations and atomic whole-plan load/save."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .model import Plan, PlannerError, Project, Task, validate_plan

MIGRATIONS = [
    """
    CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE TABLE projects (key TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY,
        project_key TEXT NOT NULL REFERENCES projects(key) ON DELETE RESTRICT,
        title TEXT NOT NULL,
        priority TEXT NOT NULL CHECK (priority IN ('urgent','high','normal','low')),
        estimate_minutes INTEGER CHECK (estimate_minutes IS NULL OR estimate_minutes >= 0),
        due TEXT, note TEXT NOT NULL DEFAULT '', done_at TEXT, created_at TEXT NOT NULL);
    CREATE TABLE dependencies (
        task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE RESTRICT,
        prereq_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE RESTRICT,
        PRIMARY KEY (task_id, prereq_id), CHECK (task_id <> prereq_id));
    INSERT INTO meta VALUES ('next_task_id', '1');
    """,
]


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._migrate()

    def _migrate(self):
        version = self.conn.execute("PRAGMA user_version").fetchone()[0]
        if version > len(MIGRATIONS):
            raise PlannerError(f"database {self.path} has schema version {version}, newer than "
                               f"this planner supports ({len(MIGRATIONS)}); refusing to touch it")
        for number in range(version, len(MIGRATIONS)):
            self.conn.execute("BEGIN IMMEDIATE")
            try:
                if self.conn.execute("PRAGMA user_version").fetchone()[0] == number:
                    for statement in MIGRATIONS[number].split(";"):
                        if statement.strip():
                            self.conn.execute(statement)
                    self.conn.execute(f"PRAGMA user_version = {number + 1}")
                self.conn.execute("COMMIT")
            except BaseException:
                self.conn.execute("ROLLBACK")
                raise

    def load(self):
        c = self.conn
        plan = Plan(next_task_id=int(c.execute(
            "SELECT value FROM meta WHERE key='next_task_id'").fetchone()[0]))
        for key, name, created in c.execute("SELECT key, name, created_at FROM projects"):
            plan.projects[key] = Project(key, name, created)
        for row in c.execute("SELECT id, project_key, title, created_at, priority, "
                             "estimate_minutes, due, note, done_at FROM tasks"):
            plan.tasks[row[0]] = Task(*row)
        for task_id, prereq in c.execute("SELECT task_id, prereq_id FROM dependencies"):
            plan.tasks[task_id].depends_on.add(prereq)
        return plan

    def _save(self, plan):
        validate_plan(plan)
        c = self.conn
        c.execute("DELETE FROM dependencies")
        c.execute("DELETE FROM tasks")
        c.execute("DELETE FROM projects")
        c.executemany("INSERT INTO projects VALUES (?, ?, ?)",
                      [(p.key, p.name, p.created_at) for p in plan.projects.values()])
        c.executemany("INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      [(t.id, t.project, t.title, t.priority, t.estimate_minutes, t.due, t.note,
                        t.done_at, t.created_at) for t in plan.tasks.values()])
        c.executemany("INSERT INTO dependencies VALUES (?, ?)",
                      [(t.id, p) for t in plan.tasks.values() for p in t.depends_on])
        c.execute("UPDATE meta SET value=? WHERE key='next_task_id'", (str(plan.next_task_id),))

    @contextmanager
    def transaction(self):
        """Yield the current plan under a write lock; save it if the block succeeds."""
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            plan = self.load()
            yield plan
            self._save(plan)
            self.conn.execute("COMMIT")
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise

    def close(self):
        self.conn.close()
