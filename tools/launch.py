#!/usr/bin/env python3
"""Start Pi or Claude on an exported project with ONE AGENTS.md source."""
import argparse
import json
from pathlib import Path
import subprocess


def command(project, client, extra=()):
    project = Path(project).resolve()
    agents = project / 'AGENTS.md'
    if not project.is_dir() or not agents.is_file():
        raise ValueError('Select an exported project containing AGENTS.md')
    if client == 'pi':
        # Pi discovers AGENTS and .agents/skills natively.
        return ['pi', *extra]
    if client == 'claude':
        # Native Claude does not load AGENTS automatically. No CLAUDE.md copy.
        return ['claude', '--append-system-prompt', agents.read_text(), *extra]
    raise ValueError('Client must be pi or claude')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--client', choices=['pi', 'claude'], required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('extra', nargs=argparse.REMAINDER, help='Client arguments after --')
    args = parser.parse_args()
    extra = args.extra[1:] if args.extra[:1] == ['--'] else args.extra
    try:
        cmd = command(args.project, args.client, extra)
        if args.dry_run:
            preview = cmd[:]
            if args.client == 'claude':
                preview[2] = f'<contents of {args.project.resolve() / "AGENTS.md"}>'
            print(json.dumps({'cwd': str(args.project.resolve()), 'argv': preview}))
        else:
            raise SystemExit(subprocess.call(cmd, cwd=args.project.resolve()))
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')
