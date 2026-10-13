# Data format (state file, export, import, backup)

One JSON format is used everywhere: the saved state (`data/planner.json`), `export`, `import` and the files in `backups/`. Example: [`examples/sample-project.json`](../examples/sample-project.json). The authoritative rules are in `validate_state` in `planner/model.py`.

```json
{
  "format": "local-planner",
  "schema_version": 1,
  "next_project": 3,
  "next_task": 9,
  "projects": [{"id": "p1", "name": "Example Bakery Website", "description": "", "created": "2026-10-01T09:00:00Z"}],
  "tasks": [{"id": "t2", "project": "p1", "title": "Wireframes", "priority": "normal",
             "estimate_minutes": 240, "due": null, "depends_on": ["t1"],
             "status": "open", "done_at": null, "notes": "", "created": "2026-10-01T09:11:00Z"}]
}
```

| Field | Rule |
|---|---|
| `format`, `schema_version` | must be `"local-planner"` and `1` |
| `next_project`, `next_task` | optional on import; must exceed the highest used id number (ids are never reused) |
| project `id` | `p1`, `p2`, ... unique; `name` required, unique ignoring case, ≤100 chars |
| task `id` | `t1`, `t2`, ... unique; `project` must exist; `title` required, ≤200 chars |
| `priority` | `critical`, `high`, `normal` (default), `low` |
| `estimate_minutes` | `null` or integer 1..600000 |
| `due` | `null` or a calendar date `YYYY-MM-DD` |
| `depends_on` | ids of existing tasks (any project), no duplicates, no self-reference, no cycles |
| `status` | `open` or `done`; a done task may only depend on done tasks |
| `created`, `done_at`, `description`, `notes` | optional on import (timestamps are UTC ISO strings) |

Import is all-or-nothing. Every problem in a file is listed, and the current state stays unchanged:
- `import FILE --replace` replaces the whole state.
- `import FILE --merge` adds the file's projects and tasks under new ids. References must stay inside the file, and project names must not clash with existing ones.
- `--dry-run` validates the file and reports what would happen without saving anything.
