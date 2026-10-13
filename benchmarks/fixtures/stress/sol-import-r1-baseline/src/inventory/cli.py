"""Public JSON-only CLI boundary."""
import argparse
import json
import os
import sqlite3
import sys

from . import parsing, service, storage


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise parsing.Problem('invalid_input', message)

    def print_help(self, file=None):
        raise Help(self.format_help())


class Help(Exception):
    pass


def positive_number(value):
    if not value.isascii() or not value.isdecimal() or int(value) < 1:
        raise argparse.ArgumentTypeError('must be an integer >=1')
    return int(value)


def arguments(argv):
    parser = Parser(description='Tenant-scoped recoverable inventory transfers')
    commands = parser.add_subparsers(dest='command', required=True, parser_class=Parser)
    for command in ('seed', 'apply', 'stock', 'runs'):
        sub = commands.add_parser(command)
        sub.add_argument('--db', required=True)
        sub.add_argument('--tenant', required=True)
        if command == 'seed':
            sub.add_argument('--stock', required=True)
        if command == 'apply':
            sub.add_argument('--csv', required=True)
            sub.add_argument('--run-id', required=True)
            sub.add_argument('--fail-after-groups', type=positive_number)
    return parser.parse_args(argv)


def emit(value):
    print(json.dumps(value, ensure_ascii=True, separators=(',', ':')), flush=True)


def main(argv=None):
    db = None
    try:
        args = arguments(argv)
        parsing.nonblank(args.tenant, 'tenant')
        accounts = groups = data = None
        if args.command == 'seed':
            _, rows = parsing.read_csv(args.stock, parsing.SEED_HEADER)
            accounts = parsing.seed_rows(rows)
        elif args.command == 'apply':
            parsing.nonblank(args.run_id, 'run-id')
            data, rows = parsing.read_csv(args.csv, parsing.APPLY_HEADER)
            groups = parsing.group_rows(rows)
        db = storage.connect(args.db)
        if args.command == 'seed':
            result = service.seed(db, args.tenant, accounts)
        elif args.command == 'apply':
            result, interrupted = service.apply(db, args.tenant, args.run_id, data,
                                              groups, args.fail_after_groups)
            if interrupted:
                emit(result)
                # Real process termination, no cleanup; group transaction already committed.
                os._exit(3)
        elif args.command == 'stock':
            result = storage.stock(db, args.tenant)
        else:
            result = storage.runs(db, args.tenant)
        emit(result)
        return 0
    except Help as exc:
        emit({'status': 'help', 'help': str(exc)})
        return 0
    except parsing.Problem as exc:
        emit({'status': exc.status, 'reason': str(exc)})
        return 2
    except (OSError, sqlite3.Error, ValueError) as exc:
        emit({'status': 'execution_error', 'reason': str(exc) or type(exc).__name__})
        return 4
    finally:
        if db is not None:
            db.close()


if __name__ == '__main__':
    sys.exit(main())
