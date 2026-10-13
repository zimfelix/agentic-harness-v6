# Local tenant-safe sales ledger

A Python 3 standard-library HTTP service backed by SQLite. Synthetic/test data only; no packages, UI or external providers.

## Run

From this directory:

```sh
python3 app.py serve --db local.sqlite --port 0
```

The first stdout line is `{"port": actual_port}`. The service binds only to `127.0.0.1`; use that port for HTTP requests. SQLite persists across restarts. Stop with Ctrl-C.

Every business request needs `Authorization: Bearer TOKEN`. **This is a TEST adapter, not secure authentication.** Tokens: `owner-a`, `editor-a`, `viewer-a`, and equivalent `-b` tokens. Viewers can read; owners/editors write deals; only owners issue or void invoices. Tenants are derived from tokens, never request bodies.

## API

All responses are JSON. Use IDs returned by the service; do not assume their format.

| Method/path | Body / result |
|---|---|
| `POST /deals` | `{title,amount_cents,currency}` → 201, new deal/version 1 |
| `GET /deals`, `GET /deals/{id}` | Own list/detail |
| `PATCH /deals/{id}` | `{version,status}` → updated version; new → qualified → won/lost |
| `POST /invoices` | `{deal_id,request_id,tax_bps}` → 201, or 200 on identical replay |
| `GET /invoices`, `GET /invoices/{id}` | Own list/detail |
| `POST /invoices/{id}/void` | `{reason}` → retained snapshot with status void |
| `GET /audit` | Own successful mutations in causal order |

Titles/reasons/request IDs are nonblank strings. Amounts are integer cents 0..100000000, currency exactly EUR/USD; tax basis points are integers 0..10000. Booleans/floats/strings do not count as integers. Tax rounds HALF_UP. Invoice amounts are snapshots of won deals. A deal can be invoiced only once, even after voiding. Request keys are tenant-scoped and persist; identical payload replay returns the same record, conflicting reuse returns 409.

Unknown fields, client `tenant` fields and malformed bodies return 400; missing/unknown identity 401, forbidden role 403, missing/foreign resource 404, state/version/idempotency conflicts 409. Failed requests and replays create no audit event.

## Tests and migration

```sh
python3 -m unittest discover -s tests -v
```

Tests launch real CLI subprocesses, use loopback HTTP and isolated project-local SQLite fixtures, and cover validation, roles, tenants, exact rounding, races, restarts, atomic rollback and migration. No real data or providers.

A specified `user_version=1` legacy deals database migrates automatically and transactionally on startup. IDs/rows are preserved, versions become 1; existing rows receive no fabricated historical audit. SQL migration sources are in `src/ledger/migrations/`. For important data, stop the service and make an offline copy first. Recover after a successful migration by restoring that copy; do not run old code against the new schema.

## Architecture and limits

`app.py` is the entrypoint; `src/ledger/http.py` handles transport/TEST identity, `service.py` owns tenant-scoped transactions, `rules.py` holds pure state/money rules, and `db.py` runs versioned migrations. SQLite write locking serializes checks, mutation and audit; unique constraints protect issuance/request keys.

This is not production-ready authentication, legally compliant invoicing, or a deployment. No load/DoS or power-loss durability evidence is claimed. Before real use: replace TEST auth, establish TLS/access controls, request/connection limits and operational monitoring, test backup/restore with agreed recovery targets, and confirm privacy, numbering, retention and tax-law requirements with qualified owners. See `docs/architecture.md` and `specs/S001-ledger.md` for continuation context.
