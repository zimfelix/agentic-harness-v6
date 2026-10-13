"""Tenant-scoped ledger operations. Each mutation and audit event commit together."""
from uuid import uuid4

from .db import transaction
from .rules import Problem, integer, reference, shape, tax_cents, text, transition


DEAL_FIELDS = ("id", "title", "amount_cents", "currency", "status", "version")
INVOICE_FIELDS = ("id", "deal_id", "request_id", "net_cents", "tax_cents",
                  "total_cents", "currency", "status")


def public(row, fields):
    return {key: row[key] for key in fields}


def find(db, table, tenant, identifier):
    # Table comes only from internal route dispatch, never from client input.
    row = db.execute(
        f"SELECT * FROM {table} WHERE tenant=? AND CAST(id AS TEXT)=?",
        (tenant, reference(identifier)),
    ).fetchone()
    if row is None:
        raise Problem(404, "Resource not found")
    return row


def audit(db, tenant, action, identifier):
    db.execute("INSERT INTO audit(tenant,action,resource_id) VALUES(?,?,?)",
               (tenant, action, identifier))


class Ledger:
    def __init__(self, path):
        self.path = path

    def list_resources(self, tenant, table):
        with transaction(self.path) as db:
            if table == "audit":
                rows = db.execute(
                    "SELECT action,resource_id FROM audit WHERE tenant=? ORDER BY sequence",
                    (tenant,),
                )
                return [dict(row) for row in rows]
            fields = DEAL_FIELDS if table == "deals" else INVOICE_FIELDS
            rows = db.execute(f"SELECT * FROM {table} WHERE tenant=? ORDER BY rowid", (tenant,))
            return [public(row, fields) for row in rows]

    def get_resource(self, tenant, table, identifier):
        with transaction(self.path) as db:
            fields = DEAL_FIELDS if table == "deals" else INVOICE_FIELDS
            return public(find(db, table, tenant, identifier), fields)

    def create_deal(self, tenant, body):
        shape(body, ("title", "amount_cents", "currency"))
        title = text(body["title"])
        amount = integer(body["amount_cents"], 0, 100000000)
        if type(body["currency"]) is not str or body["currency"] not in ("EUR", "USD"):
            raise Problem(400, "Invalid currency")
        identifier = uuid4().hex
        with transaction(self.path, write=True) as db:
            db.execute(
                "INSERT INTO deals(id,tenant,title,amount_cents,currency,status,version) "
                "VALUES(?,?,?,?,?,'new',1)",
                (identifier, tenant, title, amount, body["currency"]),
            )
            audit(db, tenant, "deal.created", identifier)
            return public(find(db, "deals", tenant, identifier), DEAL_FIELDS)

    def transition_deal(self, tenant, identifier, body):
        shape(body, ("version", "status"))
        version = integer(body["version"], 1)
        if type(body["status"]) is not str:
            raise Problem(400, "Expected status text")
        with transaction(self.path, write=True) as db:
            deal = find(db, "deals", tenant, identifier)
            if deal["version"] != version:
                raise Problem(409, "Stale version")
            transition(deal["status"], body["status"])
            db.execute("UPDATE deals SET status=?,version=version+1 WHERE tenant=? AND id=?",
                       (body["status"], tenant, deal["id"]))
            audit(db, tenant, "deal.transitioned", deal["id"])
            return public(find(db, "deals", tenant, identifier), DEAL_FIELDS)

    def issue_invoice(self, tenant, body):
        shape(body, ("deal_id", "request_id", "tax_bps"))
        deal_id = reference(body["deal_id"])
        request_id = text(body["request_id"])
        bps = integer(body["tax_bps"], 0, 10000)
        with transaction(self.path, write=True) as db:
            # Resolve the reference in this tenant, including canonical legacy IDs.
            deal = find(db, "deals", tenant, deal_id)
            replay = db.execute("SELECT * FROM invoices WHERE tenant=? AND request_id=?",
                                (tenant, request_id)).fetchone()
            if replay is not None:
                if replay["deal_id"] != deal["id"] or replay["tax_bps"] != bps:
                    raise Problem(409, "Request payload conflict")
                return 200, public(replay, INVOICE_FIELDS)
            if deal["status"] != "won":
                raise Problem(409, "Deal must be won")
            if db.execute("SELECT 1 FROM invoices WHERE tenant=? AND deal_id=?",
                          (tenant, deal["id"])).fetchone():
                raise Problem(409, "Deal already invoiced")
            identifier = uuid4().hex
            tax = tax_cents(deal["amount_cents"], bps)
            db.execute(
                "INSERT INTO invoices(id,tenant,deal_id,request_id,tax_bps,net_cents,"
                "tax_cents,total_cents,currency,status) VALUES(?,?,?,?,?,?,?,?,?,'issued')",
                (identifier, tenant, deal["id"], request_id, bps, deal["amount_cents"],
                 tax, deal["amount_cents"] + tax, deal["currency"]),
            )
            audit(db, tenant, "invoice.issued", identifier)
            return 201, public(find(db, "invoices", tenant, identifier), INVOICE_FIELDS)

    def void_invoice(self, tenant, identifier, body):
        shape(body, ("reason",))
        reason = text(body["reason"])
        with transaction(self.path, write=True) as db:
            invoice = find(db, "invoices", tenant, identifier)
            if invoice["status"] != "issued":
                raise Problem(409, "Invoice already void")
            db.execute("UPDATE invoices SET status='void',void_reason=? WHERE tenant=? AND id=?",
                       (reason, tenant, invoice["id"]))
            audit(db, tenant, "invoice.voided", invoice["id"])
            return public(find(db, "invoices", tenant, identifier), INVOICE_FIELDS)
