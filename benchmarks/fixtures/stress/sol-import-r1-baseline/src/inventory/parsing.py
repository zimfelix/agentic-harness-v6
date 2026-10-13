"""CSV boundary validation; opaque cells are data, never instructions."""
import csv
import io
import re
from collections import Counter
from pathlib import Path

SEED_HEADER = ['sku', 'warehouse', 'quantity']
APPLY_HEADER = ['group_id', 'transfer_id', 'sku', 'from_warehouse',
                'to_warehouse', 'quantity']


class Problem(Exception):
    def __init__(self, status, reason):
        super().__init__(reason)
        self.status = status


def nonblank(value, label):
    if not value.strip():
        raise Problem('invalid_input', f'{label} must be nonblank')
    return value


def quantity(value, positive=False):
    if not re.fullmatch(r'[0-9]+', value):
        raise Problem('invalid_input', 'quantity must be an ASCII base-10 integer')
    significant = value.lstrip('0') or '0'
    if len(significant) > 7 or int(significant) > 1000000:
        raise Problem('invalid_input', 'quantity must be <=1000000')
    number = int(significant)
    if positive and number == 0:
        raise Problem('invalid_input', 'transfer quantity must be positive')
    return number


def read_csv(path, header):
    data = Path(path).read_bytes()
    try:
        rows = list(csv.reader(io.StringIO(data.decode('utf-8'), newline=''), strict=True))
    except (UnicodeError, csv.Error) as exc:
        raise Problem('invalid_input', f'invalid UTF-8 CSV: {exc}') from exc
    if not rows or rows[0] != header:
        raise Problem('invalid_input', f'header must be {",".join(header)}')
    return data, rows[1:]


def seed_rows(rows):
    result = []
    seen = set()
    for row in rows:
        if len(row) != 3:
            raise Problem('invalid_input', 'seed row must have exactly 3 cells')
        sku, warehouse, value = row
        nonblank(sku, 'sku')
        nonblank(warehouse, 'warehouse')
        key = (sku, warehouse)
        if key in seen:
            raise Problem('invalid_input', 'duplicate sku/warehouse in seed')
        seen.add(key)
        result.append((sku, warehouse, quantity(value)))
    return result


def group_rows(rows):
    """Preflight all duplicate IDs, including rows with other validation errors."""
    ids = Counter(row[1] for row in rows if len(row) >= 2)
    groups = {}
    for row in rows:
        group_id = row[0] if row else ''
        groups.setdefault(group_id, []).append(row)
    result = []
    for group_id, members in groups.items():
        transfers = []
        reason = None
        try:
            nonblank(group_id, 'group_id')
            for row in members:
                if len(row) >= 2 and ids[row[1]] > 1:
                    raise Problem('invalid_input', f'duplicate transfer_id: {row[1]}')
                if len(row) != 6:
                    raise Problem('invalid_input', 'transfer row must have exactly 6 cells')
                _, transfer_id, sku, source, destination, value = row
                for cell, name in [(transfer_id, 'transfer_id'), (sku, 'sku'),
                                   (source, 'from_warehouse'), (destination, 'to_warehouse')]:
                    nonblank(cell, name)
                if source == destination:
                    raise Problem('invalid_input', 'source and destination must differ')
                transfers.append((transfer_id, sku, source, destination, quantity(value, True)))
        except Problem as exc:
            reason = str(exc)
        result.append((group_id, transfers, reason))
    return result
