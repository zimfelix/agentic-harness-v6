# Local tenant-safe sales ledger

Python 3 standard library and SQLite only. No install step.

```sh
python3 app.py serve --db ledger.sqlite --port 0
python3 -m unittest discover -s tests -v
```

The service binds only to `127.0.0.1`, prints one JSON readiness line containing the actual port, then handles JSON HTTP requests. Stop with Ctrl-C. Relative database paths resolve from the working directory; the containing directory must exist. Do not use `:memory:` (connections are per request).

## TEST authentication
Send `Authorization: Bearer owner-a` (or `editor-a`, `viewer-a`, `owner-b`, `editor-b`, `viewer-b`). These hardcoded identities are **not production authentication**. Tenant comes only from the token; a client `tenant` field is rejected. Readers read; editors/owners mutate deals; only owners issue/void invoices.

## API
- `POST /deals`: `{title,amount_cents,currency}` (EUR/USD); `GET /deals`, `GET /deals/{id}`.
- `PATCH /deals/{id}`: `{version,status}`; new → qualified → won/lost. Conflict =409.
- `POST /invoices`: `{deal_id,request_id,tax_bps}`; won deals only, one invoice ever per deal. First issuance =201; identical tenant-scoped replay =200. Tax uses integer HALF_UP cents.
- `GET /invoices`, `GET /invoices/{id}`.
- `POST /invoices/{id}/void`: `{reason}`; retains amounts and prevents reissuance.
- `GET /audit`: causal successful mutations, not failed attempts or replays.

Use returned opaque IDs. New IDs are UUID strings; migrated legacy IDs remain integers and work in URL paths. `request_id` must be nonblank text; exact text is significant. `deal_id` accepts nonblank text or legacy integer IDs. Bodies require exactly the documented fields. Missing/unknown auth =401, forbidden role =403, missing/foreign resource =404, malformed body =400. JSON bodies are limited to 1 MiB.

## Persistence and migration
SQL migrations live in `migrations/`; empty files migrate through v1 to v2. Existing specified v1 files retain every deal/ID and get version 1. Migration is one startup transaction, so errors roll back and prevent readiness. Repeated startup at v2 is a no-op. Back up an existing file before upgrading: reverting the schema/application requires restoring that backup; no downgrade tool is included. Successful mutation, uniqueness/version checks and audit insert share one SQLite transaction. Same-process and cross-process writes serialize through SQLite BEGIN IMMEDIATE.

## Scope and limitations
For local synthetic use only. The standard-library HTTP server is not a hardened production server: no TLS, rate limits or bounded worker pool; no production identity or operational monitoring. Tests use real loopback HTTP and local synthetic SQLite files, including concurrent callers and process restarts. They do not establish performance under sustained load, power-loss durability, backup recovery or production security.
Before production: real authentication/authorization review, secure deployment/transport, resource limits and monitoring, validated backup/restore, audit retention/access and privacy policies, and confirmed legal/accounting/tax requirements. No payment, customer email or provider integration exists or is authorized.

Architecture and scope: `PROJECT.md`. Acceptance/evidence and continuation: `specs/ledger.md`.
