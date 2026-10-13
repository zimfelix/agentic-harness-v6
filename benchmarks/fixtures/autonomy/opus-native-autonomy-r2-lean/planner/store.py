"""JSON file storage with a per-command lock, atomic writes and backups."""
import contextlib
import datetime as dt
import fcntl
import json
import os
import tempfile
from pathlib import Path

from .model import PlannerError, empty_state, validate_state

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "planner.json"


def read_json_file(path):
    """Parse and validate a state/import/backup file; never modifies anything."""
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise PlannerError(f"cannot read {path}: {e.strerror}")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise PlannerError(f"{path} is not valid JSON (line {e.lineno}, column {e.colno}: {e.msg})")
    return validate_state(data)


def dump(state):
    return json.dumps(state, indent=2, ensure_ascii=False) + "\n"


def write_atomic(path, text, overwrite=True):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not overwrite and path.exists():
        raise PlannerError(f"{path} already exists (use --force to overwrite)")
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise
    dir_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.backup_dir = self.path.parent / "backups"

    @contextlib.contextmanager
    def locked(self):
        """Serialize read-modify-write cycles between concurrent invocations."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path.parent / f".{self.path.name}.lock", "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def load(self):
        if not self.path.exists():
            return empty_state()
        try:
            return read_json_file(self.path)
        except PlannerError as e:
            raise PlannerError(f"saved state is unreadable, nothing was changed.\n{e}\n"
                               "Recover with: restore --latest  (or restore <backup file>)")

    def save(self, state):
        write_atomic(self.path, dump(validate_state(state)))

    def backup(self, state, label="manual"):
        return self._write_backup(dump(state), label)

    def backup_raw(self, label):
        """Copy the current file byte-for-byte (used when it does not validate)."""
        return self._write_backup(self.path.read_text(encoding="utf-8", errors="replace"), label)

    def _write_backup(self, text, label):
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        target = self.backup_dir / f"planner-{stamp}-{label}.json"
        n = 1
        while target.exists():
            n += 1
            target = self.backup_dir / f"planner-{stamp}-{label}-{n}.json"
        write_atomic(target, text, overwrite=False)
        return target

    def backups(self):
        """Backup files, oldest first (timestamped names sort chronologically)."""
        if not self.backup_dir.is_dir():
            return []
        return sorted(p for p in self.backup_dir.glob("planner-*.json"))
