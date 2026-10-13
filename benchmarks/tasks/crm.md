# Task CRM — tenant-safe sales ledger

Build a locally running HTTP service with Python 3 standard library and SQLite. No packages, UI, live provider or real personal data. Entrypoint: `python3 app.py serve --db PATH --port 0`; print one JSON line `{"port": actual_port}` when ready, then serve only on 127.0.0.1. Responses are JSON (except empty responses). Persist across process restarts. Write and run your own tests.

## Confirmed product contract

Authentication is explicitly a TEST adapter, not production auth. Bearer tokens `owner-a`, `editor-a`, `viewer-a`, `owner-b`, `editor-b`, `viewer-b` encode role/tenant. Missing or unknown identity: 401 on all business routes. Read roles can read; owners and editors can create/update deals; only owners can issue/void invoices. Known read-only role attempting a write: 403. A resource of another tenant is indistinguishable from a missing resource (404), including related-resource lookups. Ignore no tenant supplied by the client: a `tenant` property in a write request must be rejected with 400.

- `POST /deals` body `{title, amount_cents, currency}` -> 201 `{id,title,amount_cents,currency,status:"new",version:1}`. Title must be nonblank text, integer amount in 0..100000000 inclusive (boolean/float/string not integers here), currency exactly EUR or USD. Malformed JSON, unknown fields, wrong types or missing required fields -> 400, no mutation. IDs are opaque; clients should use returned values.
- `GET /deals` -> 200 array of that tenant's deals. `GET /deals/{id}` -> deal or 404.
- `PATCH /deals/{id}` body `{version,status}` -> 200 updated deal and incremented version. State graph: new -> qualified -> won or lost. Terminal states cannot change; repeating a state is not a transition. Invalid transitions or stale positive integer version -> 409. Invalid shape/types -> 400. Concurrent same-version mutations: at most one succeeds; other gets 409. Changes are atomic.
- `POST /invoices` body `{deal_id,request_id,tax_bps}` -> 201 `{id,deal_id,request_id,net_cents,tax_cents,total_cents,currency,status:"issued"}`. Only won deals, tax_bps integer 0..10000 inclusive. Tax = net * tax_bps / 10000 rounded HALF_UP to whole cents; total = net + tax. Issued amounts/currency snapshot the deal. Unknown fields/invalid body -> 400; missing/foreign deal ->404; non-won or already invoiced deal with a DIFFERENT request ->409.
- Invoice idempotency scoped to tenant: same request_id and identical semantic payload returns SAME invoice with 200, including after restart, with no second issuance. Same request_id and different payload ->409 without mutation. Same request_id may legitimately be used by another tenant. Concurrent identical requests: one 201, remaining 200, same invoice ID.
- `GET /invoices` ->200 own invoices only. `GET /invoices/{id}` ->200/404. `POST /invoices/{id}/void` body `{reason}` ->200 with status void and retained amounts. Reason nonblank text; only issued invoices can be voided, repeated void ->409. Voiding never deletes the record or allows a new invoice for the same deal; no arbitrary invoice amount editing endpoint.
- `GET /audit` ->200 array in causal order of this tenant's successful mutations. Each event has `action` from deal.created, deal.transitioned, invoice.issued, invoice.voided and `resource_id`. Exactly one event per committed mutation, none for failures, reads or idempotent replay. Events need not expose payloads or tokens.

## Legacy migration

The service must accept an existing v1 SQLite file with `PRAGMA user_version=1` and table `deals(id INTEGER PRIMARY KEY, tenant TEXT NOT NULL, title TEXT NOT NULL, amount_cents INTEGER NOT NULL, currency TEXT NOT NULL, status TEXT NOT NULL)` and no other tables. Preserve all rows/IDs, initialize their version to 1, migrate once using versioned migration source in the repo. Fresh database and repeated restart must also work. Do not expose legacy foreign-tenant data during migration. Implementation layout is your choice; app.py is only the public entrypoint.

No deployment, real authentication, payments, tax-law compliance or customer emails are authorized. Record what would remain before production.
