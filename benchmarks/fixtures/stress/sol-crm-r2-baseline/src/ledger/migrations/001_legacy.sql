CREATE TABLE deals (
    id INTEGER PRIMARY KEY,
    tenant TEXT NOT NULL,
    title TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL
);
