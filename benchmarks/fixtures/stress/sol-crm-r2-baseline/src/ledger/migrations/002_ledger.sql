ALTER TABLE deals RENAME TO deals_v1;
-- No type affinity on IDs: preserve legacy integer IDs, allow opaque new text IDs.
CREATE TABLE deals (
    id PRIMARY KEY NOT NULL,
    tenant TEXT NOT NULL,
    title TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0),
    UNIQUE(tenant, id)
);
INSERT INTO deals(id, tenant, title, amount_cents, currency, status, version)
    SELECT id, tenant, title, amount_cents, currency, status, 1 FROM deals_v1;
DROP TABLE deals_v1;
CREATE TABLE invoices (
    id TEXT PRIMARY KEY NOT NULL,
    tenant TEXT NOT NULL,
    deal_id NOT NULL,
    request_id TEXT NOT NULL,
    tax_bps INTEGER NOT NULL CHECK(tax_bps BETWEEN 0 AND 10000),
    net_cents INTEGER NOT NULL,
    tax_cents INTEGER NOT NULL,
    total_cents INTEGER NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('issued', 'void')),
    void_reason TEXT,
    UNIQUE(tenant, request_id),
    UNIQUE(tenant, deal_id),
    FOREIGN KEY(tenant, deal_id) REFERENCES deals(tenant, id)
);
CREATE TABLE audit (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN (
        'deal.created', 'deal.transitioned', 'invoice.issued', 'invoice.voided'
    )),
    resource_id NOT NULL
);
CREATE INDEX audit_tenant_sequence ON audit(tenant, sequence);
