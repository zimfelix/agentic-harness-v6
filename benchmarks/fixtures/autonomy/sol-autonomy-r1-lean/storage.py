"""Transactional local snapshots and safe portable JSON files."""
import json
import os
from pathlib import Path
import sqlite3
import tempfile


class PlannerError(ValueError):
    pass


def empty_state():
    return {"version": 1, "projects": [], "tasks": []}


def parse_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise PlannerError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    try:
        return json.loads(text, object_pairs_hook=unique)
    except (ValueError, RecursionError) as exc:
        raise PlannerError(f"invalid JSON: {exc}") from exc


def read_json(path):
    return parse_json(Path(path).read_text(encoding="utf-8"))


class Store:
    def __init__(self, path):
        self.path = Path(path)

    def run(self, validate, action=None, replacement=None):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=10)
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), document TEXT NOT NULL)")
            row = connection.execute("SELECT document FROM state WHERE id=1").fetchone()
            state = replacement if replacement is not None else (parse_json(row[0]) if row else empty_state())
            validate(state)
            result = action(state) if action else state
            validate(state)
            if action is not None or replacement is not None or row is None:
                connection.execute("INSERT OR REPLACE INTO state VALUES (1, ?)", (json.dumps(state),))
            connection.commit()
            return result
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def output(self, path, state, overwrite=False):
        target = Path(path).resolve()
        database = self.path.resolve()
        reserved = {database, Path(str(database) + "-journal"), Path(str(database) + "-wal"), Path(str(database) + "-shm")}
        if target in reserved or (target.exists() and self.path.exists() and os.path.samefile(target, self.path)):
            raise PlannerError("output cannot overwrite the database or its sidecars")
        # Temp file on the same filesystem; no partial backup/export is published.
        descriptor, temporary = tempfile.mkstemp(prefix=".planner-", dir=target.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(state, stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            if overwrite:
                os.replace(temporary, target)
            else:
                try:
                    os.link(temporary, target)
                except FileExistsError as exc:
                    raise PlannerError("output exists; use --overwrite") from exc
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
