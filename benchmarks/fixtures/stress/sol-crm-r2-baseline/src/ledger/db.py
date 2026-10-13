"""SQLite connection lifetime, atomic transactions and versioned migrations."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3


MIGRATIONS = ("001_legacy.sql", "002_ledger.sql")


def connect(path):
    db = sqlite3.connect(path, timeout=30, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


@contextmanager
def transaction(path, write=False):
    db = connect(path)
    try:
        db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


def migrate(path):
    with transaction(path, write=True) as db:
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version < 0 or version > len(MIGRATIONS):
            raise RuntimeError("Unsupported database version")
        for index in range(version, len(MIGRATIONS)):
            source = Path(__file__).parent / "migrations" / MIGRATIONS[index]
            # These migrations contain only simple SQL statements. Avoid
            # executescript(), whose implicit commit would break atomic migration.
            for statement in source.read_text(encoding="utf-8").split(";"):
                if statement.strip():
                    db.execute(statement)
            db.execute(f"PRAGMA user_version={index + 1}")
