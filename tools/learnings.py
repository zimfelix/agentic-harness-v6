#!/usr/bin/env python3
"""Show open learnings from all projects on this harness, plus this repository's own.

Projects are found automatically: an AGENTS.md with a `harness-v6@` marker below
~/Code or ~/PycharmProjects (depth 3). Only entries with status `offen` are shown;
`--all` shows every entry. Read-only.
"""
import argparse
from pathlib import Path
import re

REPO = Path(__file__).resolve().parents[1]
ROOTS = [Path.home() / 'Code', Path.home() / 'PycharmProjects']
ENTRIES = '<!-- learnings:entries'
CORE_REVIEW = 6000  # review signal, not a limit
SKIP = {'node_modules', '.venv', '.git', 'dist', 'build'}


def projects(roots=ROOTS, depth=3):
    found = []

    def walk(folder, level):
        if level > depth or folder.name in SKIP:
            return
        agents = folder / 'AGENTS.md'
        if agents.is_file() and 'harness-v6@' in agents.read_text(errors='ignore'):
            found.append(folder)
            return
        for child in sorted(p for p in folder.iterdir() if p.is_dir() and not p.is_symlink()) if folder.is_dir() else []:
            walk(child, level + 1)

    for root in roots:
        if root.is_dir():
            walk(root, 0)
    return found


def entries(learnings, include_all=False):
    text = learnings.read_text() if learnings.is_file() else ''
    if ENTRIES not in text:
        return []
    body = text.split(ENTRIES, 1)[1].split('\n', 1)[-1]
    blocks = re.split(r'(?m)^(?=## )', body)
    return [b.strip() for b in blocks if b.startswith('## ') and (include_all or b.split('\n', 1)[0].rstrip().endswith('offen'))]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--all', action='store_true', help='show entries of every status')
    args = parser.parse_args()
    total = 0
    for folder in [REPO] + projects():
        found = entries(folder / 'learnings.md', args.all)
        total += len(found)
        label = 'agentic-harness-v6 (eigene)' if folder == REPO else str(folder).replace(str(Path.home()), '~')
        print(f'\n### {label}: {len(found)}')
        for block in found:
            print(block + '\n')
    print(f'\n{total} Einträge' + ('' if args.all else ' offen'))
    core = sum(len((REPO / 'harness' / name).read_text()) for name in ('AGENTS.md', 'PROJECT.md'))
    print(f'Core (harness/AGENTS.md + PROJECT.md): {core} Zeichen'
          + (' – Qualitätsprüfung fällig: Wiederholungen, Zeilen für einen Skill, ungenaue Formulierungen.' if core > CORE_REVIEW else ''))
