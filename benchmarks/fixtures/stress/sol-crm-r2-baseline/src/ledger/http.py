"""Loopback-only HTTP transport and explicitly TEST-only authentication."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sys
from urllib.parse import unquote, urlsplit

from .rules import Problem
from .service import Ledger


TEST_IDENTITIES = {
    f"{role}-{tenant}": (tenant, role)
    for tenant in ("a", "b") for role in ("owner", "editor", "viewer")
}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("Nonstandard JSON constant")


class Handler(BaseHTTPRequestHandler):
    # Close each connection, avoiding unread request bodies on early failures.
    protocol_version = "HTTP/1.0"

    def log_message(self, *args):
        pass

    def body(self):
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1 or self.headers.get("Transfer-Encoding"):
            raise Problem(400, "Invalid body framing")
        try:
            length = int(lengths[0])
            if length < 0:
                raise ValueError("Invalid length")
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError("Incomplete body")
            return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                              parse_constant=invalid_constant)
        except (ValueError, UnicodeError, RecursionError):
            raise Problem(400, "Invalid JSON body") from None

    def dispatch(self):
        parts = [unquote(part) for part in urlsplit(self.path).path.split("/")[1:]]
        if not parts or parts[0] not in ("deals", "invoices", "audit"):
            raise Problem(404, "Route not found")
        auth = self.headers.get_all("Authorization", [])
        identity = TEST_IDENTITIES.get(auth[0][7:]) if (
            len(auth) == 1 and auth[0].startswith("Bearer ")
        ) else None
        if identity is None:
            raise Problem(401, "TEST bearer identity required")
        tenant, role = identity
        table = parts[0]
        ledger = self.server.ledger
        if self.command == "GET":
            if len(parts) == 1:
                return 200, ledger.list_resources(tenant, table)
            if len(parts) == 2 and table != "audit" and parts[1]:
                return 200, ledger.get_resource(tenant, table, parts[1])
        elif self.command in ("POST", "PATCH", "PUT", "DELETE"):
            permitted = ("owner", "editor") if table == "deals" else ("owner",)
            if role not in permitted:
                raise Problem(403, "Role cannot perform this write")
            if self.command == "POST" and parts == ["deals"]:
                return 201, ledger.create_deal(tenant, self.body())
            if self.command == "PATCH" and len(parts) == 2 and table == "deals" and parts[1]:
                return 200, ledger.transition_deal(tenant, parts[1], self.body())
            if self.command == "POST" and parts == ["invoices"]:
                return ledger.issue_invoice(tenant, self.body())
            if (self.command == "POST" and len(parts) == 3 and table == "invoices"
                    and parts[1] and parts[2] == "void"):
                return 200, ledger.void_invoice(tenant, parts[1], self.body())
        raise Problem(404, "Route not found")

    def respond(self, status, data):
        payload = json.dumps(data, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        if status == 401:
            self.send_header("WWW-Authenticate", 'Bearer realm="TEST adapter"')
        self.end_headers()
        self.wfile.write(payload)

    def handle_request(self):
        self.connection.settimeout(10)
        try:
            status, data = self.dispatch()
        except Problem as error:
            status, data = error.status, {"error": error.message}
        except (TimeoutError, ConnectionError):
            status, data = 400, {"error": "Incomplete request"}
        except Exception:
            # No request payload, token or database details in logs/responses.
            print("Ledger request failed", file=sys.stderr, flush=True)
            status, data = 500, {"error": "Internal server error"}
        try:
            self.respond(status, data)
        except (ConnectionError, TimeoutError):
            pass  # The committed result can be recovered through reads/replay.

    do_GET = do_POST = do_PATCH = do_PUT = do_DELETE = do_OPTIONS = do_HEAD = handle_request

    def send_error(self, code, message=None, explain=None):
        # BaseHTTPRequestHandler's parser errors must also be JSON, not HTML.
        self.respond(code, {"error": "Invalid HTTP request"})


class LocalServer(ThreadingHTTPServer):
    # The stdlib default backlog of five can drop a modest simultaneous burst.
    request_queue_size = 64


def serve(path, port):
    from .db import migrate
    migrate(path)
    with LocalServer(("127.0.0.1", port), Handler) as server:
        server.ledger = Ledger(path)
        print(json.dumps({"port": server.server_address[1]}), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
