ALTER TABLE deals RENAME TO legacy_deals;
CREATE TABLE deals (
 id PRIMARY KEY NOT NULL,
 tenant TEXT NOT NULL,
 title TEXT NOT NULL,
 amount_cents INTEGER NOT NULL,
 currency TEXT NOT NULL,
 status TEXT NOT NULL,
 version INTEGER NOT NULL DEFAULT 1,
 UNIQUE(tenant,id)
);
INSERT INTO deals SELECT id,tenant,title,amount_cents,currency,status,1 FROM legacy_deals;
DROP TABLE legacy_deals;
CREATE TABLE invoices (
 id TEXT PRIMARY KEY,
 tenant TEXT NOT NULL,
 deal_id NOT NULL,
 request_id TEXT NOT NULL,
 tax_bps INTEGER NOT NULL,
 net_cents INTEGER NOT NULL,
 tax_cents INTEGER NOT NULL,
 total_cents INTEGER NOT NULL,
 currency TEXT NOT NULL,
 status TEXT NOT NULL,
 void_reason TEXT,
 UNIQUE(tenant,request_id),
 UNIQUE(tenant,deal_id),
 FOREIGN KEY(tenant,deal_id) REFERENCES deals(tenant,id)
);
CREATE TABLE audit (
 seq INTEGER PRIMARY KEY AUTOINCREMENT,
 tenant TEXT NOT NULL,
 action TEXT NOT NULL,
 resource_id NOT NULL
);
PRAGMA user_version=2;
