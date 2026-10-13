"""Public standard-library CLI entrypoint for the local TEST ledger."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from ledger.http import serve


def main():
    parser = argparse.ArgumentParser(description="Local sales ledger (TEST auth only)")
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("serve")
    command.add_argument("--db", required=True)
    command.add_argument("--port", required=True, type=int)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be between 0 and 65535")
    serve(args.db, args.port)


if __name__ == "__main__":
    main()
