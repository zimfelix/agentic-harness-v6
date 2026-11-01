#!/usr/bin/env python3
"""Count how often each globally linked skill was actually loaded by Claude Code and Pi.

A load is a Claude `Skill` call, or a Claude/Pi read (tool or shell) of a `<skill>/SKILL.md`.
Counts loads, not usefulness; a listed-but-never-loaded skill shows 0.
Sources: ~/.claude/projects/**/*.jsonl and ~/.pi/agent/sessions/**/*.jsonl (local only;
older sessions may already be pruned by the clients). --readme rewrites the table between
the markers in this repository's README.md.
"""
import argparse
from collections import defaultdict
from datetime import date
import json
import re
from pathlib import Path

HOME = Path.home()
REPO = Path(__file__).resolve().parents[1]
OWN = REPO / 'harness/.agents/skills'
LINK_DIRS = [HOME / '.claude/skills', HOME / '.pi/agent/skills']
LOGS = {'Claude': HOME / '.claude/projects', 'Pi': HOME / '.pi/agent/sessions'}
START, END = '<!-- skills:start -->', '<!-- skills:end -->'


def linked_skills():
    """name -> resolved source directory, for every skill linked in a global skill folder."""
    skills = {}
    for folder in LINK_DIRS:
        for entry in sorted(folder.glob('*')) if folder.is_dir() else []:
            if (entry / 'SKILL.md').is_file():
                skills.setdefault(entry.name, entry.resolve())
    for entry in sorted(OWN.glob('*')):
        if (entry / 'SKILL.md').is_file():
            skills.setdefault(entry.name, entry.resolve())
    return skills


def loads_in(record):
    """Yield skill names loaded by one transcript line (Claude or Pi format)."""
    message = record.get('message') if isinstance(record.get('message'), dict) else record
    content = message.get('content') if isinstance(message, dict) else None
    for block in content if isinstance(content, list) else []:
        if not isinstance(block, dict):
            continue
        name = block.get('name')
        args = block.get('input') or block.get('arguments') or {}
        if not isinstance(args, dict):
            continue
        if block.get('type') == 'tool_use' and name == 'Skill' and args.get('skill'):
            yield args['skill'].split(':')[-1]
        path = args.get('file_path') or args.get('path') or ''
        if name in ('Read', 'read') and isinstance(path, str) and path.endswith('/SKILL.md'):
            yield Path(path).parent.name
        command = args.get('command') or ''
        if name in ('Bash', 'bash') and isinstance(command, str):
            yield from set(re.findall(r'([\w.-]+)/SKILL\.md', command))


def collect():
    stats = defaultdict(lambda: {'Claude': 0, 'Pi': 0, 'sessions': set(), 'last': ''})
    for client, root in LOGS.items():
        for log in root.rglob('*.jsonl') if root.is_dir() else []:
            try:
                lines = log.read_text(errors='ignore').splitlines()
            except OSError:
                continue
            for line in lines:
                if 'SKILL.md' not in line and '"Skill"' not in line:
                    continue
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                for skill in loads_in(record):
                    entry = stats[skill]
                    entry[client] += 1
                    entry['sessions'].add(log.stem)
                    entry['last'] = max(entry['last'], str(record.get('timestamp', ''))[:10])
    return stats


def table():
    skills, stats = linked_skills(), collect()
    rows = []
    for name, source in skills.items():
        own = source.is_relative_to(OWN.resolve())
        origin = 'eigen (v6)' if own else 'importiert: ' + str(source.parent).replace(str(HOME), '~')
        s = stats.get(name, {'Claude': 0, 'Pi': 0, 'sessions': set(), 'last': ''})
        rows.append((not own, -(s['Claude'] + s['Pi']), name, origin, s))
    lines = [f'Stand {date.today()}, aus lokalen Claude-Code- und Pi-Protokollen (`python3 tools/skill_usage.py --readme`).',
             '', '| Skill | Herkunft | Ladungen Claude | Ladungen Pi | Sitzungen | zuletzt |', '|---|---|---:|---:|---:|---|']
    for _, _, name, origin, s in sorted(rows):
        lines.append(f"| `{name}` | {origin} | {s['Claude']} | {s['Pi']} | {len(s['sessions'])} | {s['last'] or '–'} |")
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--readme', action='store_true', help='write the table into README.md between the markers')
    args = parser.parse_args()
    text = table()
    if args.readme:
        readme = REPO / 'README.md'
        content = readme.read_text()
        start, end = content.index(START) + len(START), content.index(END)
        readme.write_text(content[:start] + '\n' + text + '\n' + content[end:])
    print(text)
