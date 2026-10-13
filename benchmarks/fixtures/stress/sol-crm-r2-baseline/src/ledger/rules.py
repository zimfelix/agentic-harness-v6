"""Pure validation and ledger rules; no HTTP or database dependencies."""


class Problem(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def shape(body, fields):
    if type(body) is not dict or set(body) != set(fields):
        raise Problem(400, "Invalid request fields")


def text(value):
    if type(value) is not str or not value.strip():
        raise Problem(400, "Expected nonblank text")
    return value


def integer(value, low, high=None):
    if type(value) is not int or value < low or (high is not None and value > high):
        raise Problem(400, "Integer out of range")
    return value


def reference(value):
    if type(value) is int:
        return str(value)
    return text(value)


def transition(current, target):
    edges = {"new": {"qualified"}, "qualified": {"won", "lost"}}
    if target not in edges.get(current, set()):
        raise Problem(409, "Invalid state transition")


def tax_cents(net, bps):
    # Nonnegative integer arithmetic: exact HALF_UP, including half-cent ties.
    return (net * bps + 5000) // 10000
