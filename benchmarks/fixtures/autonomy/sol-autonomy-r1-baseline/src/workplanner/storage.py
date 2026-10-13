"""Strict JSON interchange and atomic local persistence."""
import json
import os
from pathlib import Path
import tempfile
from contextlib import contextmanager

from .domain import empty, validate


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    with Path(path).open(encoding="utf-8") as stream:
        state = json.load(stream, object_pairs_hook=unique_object)
    return validate(state)


def encoded(state):
    return json.dumps(validate(state), indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def write_new(path, state):
    """Create export/backup exclusively; remove incomplete output on failure."""
    path = Path(path)
    content = encoded(state)
    with path.open("x", encoding="utf-8") as stream:
        try:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            path.unlink()
            raise


class Store:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.lock = self.path.with_name(self.path.name + ".lock")

    @contextmanager
    def session(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(self.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            raise ValueError(f"State is locked: {self.lock}; remove only after verifying no planner process is running") from None
        try:
            with os.fdopen(descriptor, "w") as stream:
                stream.write(str(os.getpid()))
            yield self
        finally:
            self.lock.unlink()

    def load(self):
        if not self.path.exists():
            return empty()
        return read_json(self.path)

    def save(self, state):
        content = encoded(state)
        name = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".planner-", delete=False) as stream:
                name = stream.name
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.path)
        finally:
            if name is not None and Path(name).exists():
                Path(name).unlink()


def replacement_report(old, new):
    report = {}
    for collection in ("projects", "tasks"):
        before = {item["id"]: item for item in old[collection]}
        after = {item["id"]: item for item in new[collection]}
        report[collection] = {
            "new": sorted(after.keys() - before.keys()),
            "removed": sorted(before.keys() - after.keys()),
            "changed": sorted(k for k in before.keys() & after.keys() if before[k] != after[k]),
            "unchanged": sorted(k for k in before.keys() & after.keys() if before[k] == after[k]),
        }
    return report
