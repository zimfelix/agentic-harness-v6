# 0001 – Portable validated JSON for a local planner

**Gilt bei:** storage or domain architecture changes.

- **Status:** entschieden
- **Datum:** 2026-07-16
- **Entschieden von:** Agent als reversible Annahme

## Kontext
Single local operator, standard library only, portable synthetic import/export and backup required.

## Entscheidung
Pure domain functions plus locked whole-state JSON writes using atomic replacement. Strict whole-graph validation; import is an explicit whole-state replacement, never a partial merge.

## Alternativen
SQLite offers richer transactions but requires separate interchange mapping. Unlocked JSON risks lost updates. A server/framework is outside scope.

## Folgen
Readable portable backups and simple testing. Whole-state validation fits intermediate local workloads, not large datasets. Fail-fast locks require manual cleanup after a crash; no multiuser or network-filesystem guarantee.
