"""Inventory rules and durable, resumable group execution."""
from .parsing import Problem
from .storage import report, transaction


def seed(db, tenant, accounts):
    with transaction(db):
        if db.execute('SELECT 1 FROM tenants WHERE tenant=?', (tenant,)).fetchone():
            raise Problem('conflict', 'tenant has already been seeded')
        db.execute('INSERT INTO tenants VALUES (?)', (tenant,))
        db.executemany('INSERT INTO stock VALUES (?,?,?,?)',
                       [(tenant, *account) for account in accounts])
    return {'status': 'seeded', 'tenant': tenant, 'accounts': len(accounts)}


def balances_for_group(db, tenant, transfers):
    """Simulate in file order; rejection never creates destination accounts."""
    balances = {}

    def get(sku, warehouse):
        key = (sku, warehouse)
        if key not in balances:
            row = db.execute('SELECT quantity FROM stock WHERE tenant=? AND sku=? AND warehouse=?',
                             (tenant, sku, warehouse)).fetchone()
            balances[key] = row[0] if row else 0
        return balances[key]

    for _, sku, source, destination, quantity in transfers:
        available = get(sku, source)
        if available < quantity:
            raise Problem('invalid_input', f'insufficient stock for sku {sku} at {source}')
        target = get(sku, destination) + quantity
        if target > 9223372036854775807:
            raise Problem('invalid_input', 'destination exceeds SQLite integer capacity')
        balances[(sku, source)] = available - quantity
        balances[(sku, destination)] = target
    return balances


def apply(db, tenant, run_id, data, groups, fail_after=None):
    # Registration determines replay status for this invocation, under the same
    # writer lock as identity checking. No ownership lease survives a crash.
    with transaction(db):
        existing = db.execute('SELECT input,status FROM runs WHERE tenant=? AND run_id=?',
                              (tenant, run_id)).fetchone()
        if existing:
            if bytes(existing['input']) != data:
                raise Problem('conflict', 'run-id already exists with different input bytes')
            if existing['status'] == 'completed':
                return report(db, tenant, run_id, True), False
        else:
            if not db.execute('SELECT 1 FROM tenants WHERE tenant=?', (tenant,)).fetchone():
                raise Problem('conflict', 'tenant must be seeded before apply')
            db.execute('INSERT INTO runs(tenant,run_id,input,status) VALUES (?,?,?,?)',
                       (tenant, run_id, data, 'interrupted'))

    decided_here = 0
    while True:
        with transaction(db):
            row = db.execute('SELECT status,next_group FROM runs WHERE tenant=? AND run_id=?',
                             (tenant, run_id)).fetchone()
            ordinal = row['next_group']
            if row['status'] == 'completed':
                return report(db, tenant, run_id), False
            if ordinal == len(groups):
                db.execute("UPDATE runs SET status='completed' WHERE tenant=? AND run_id=?",
                           (tenant, run_id))
                return report(db, tenant, run_id), False
            group_id, transfers, reason = groups[ordinal]
            balances = {}
            if reason is None:
                try:
                    balances = balances_for_group(db, tenant, transfers)
                except Problem as exc:
                    reason = str(exc)
            db.execute('INSERT INTO decisions VALUES (?,?,?,?,?)',
                       (tenant, run_id, ordinal, group_id, reason))
            if reason is None:
                db.executemany('''INSERT INTO stock VALUES (?,?,?,?)
                    ON CONFLICT(tenant,sku,warehouse) DO UPDATE SET quantity=excluded.quantity''',
                               [(tenant, sku, warehouse, quantity)
                                for (sku, warehouse), quantity in balances.items()])
                db.executemany('INSERT INTO transfers VALUES (?,?,?,?,?,?,?,?,?)',
                               [(tenant, run_id, transfer_id, ordinal, index, sku, source,
                                 destination, quantity)
                                for index, (transfer_id, sku, source, destination, quantity)
                                in enumerate(transfers)])
            db.execute('''UPDATE runs SET next_group=next_group+1,
                applied_groups=applied_groups+?, rejected_groups=rejected_groups+?,
                applied_rows=applied_rows+? WHERE tenant=? AND run_id=?''',
                       (int(reason is None), int(reason is not None),
                        len(transfers) if reason is None else 0, tenant, run_id))
            progress = report(db, tenant, run_id)
        decided_here += 1
        if fail_after is not None and decided_here == fail_after:
            return progress, True
