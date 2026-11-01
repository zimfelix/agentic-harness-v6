#!/usr/bin/env python3
"""Bring exported projects to the current harness without touching project content.

Universal parts: AGENTS.md above the harness marker, the learnings.md header above
its entries marker, specs/README.md and ideas/README.md. Docs under docs/ that
nothing routes to are reported. PROJECT.md, other
specs/ideas, learnings entries, README.md and code are never written. Where a safe automatic update is
impossible, a note goes to harness-update.md for review at the next task.
Default is a dry run; --apply writes.
"""
import argparse
from datetime import date
import difflib
import importlib.util
from pathlib import Path
import re
import subprocess

_spec = importlib.util.spec_from_file_location('exporter', Path(__file__).with_name('export.py'))
exporter = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exporter)

MARKER_RE = re.compile(r'^<!-- harness-v6@([0-9a-f]+|local)\b.*-->$', re.M)
UNIVERSAL = ['specs/README.md', 'ideas/README.md']
NOTE = 'harness-update.md'
ENTRIES = '<!-- learnings:entries'


def template_at(source, version, rel):
    if version == 'local':
        return None
    result = subprocess.run(['git', '-C', str(source), 'show', f'{version}:./{rel}'], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else None


def plan(project, source=exporter.SOURCE):
    """Return {'status', 'old', 'new', 'writes': {rel: text}, 'hints': [str]} without writing."""
    project, source = Path(project).resolve(), Path(source).resolve()
    agents_path = project / 'AGENTS.md'
    text = agents_path.read_text() if agents_path.is_file() else ''
    match = MARKER_RE.search(text)
    if not match:
        return {'status': 'no-marker', 'old': None, 'new': None, 'writes': {}, 'hints': []}
    old, new = match.group(1), exporter.source_version(source)
    top, rest = text[:match.start()].rstrip('\n'), text[match.end():]
    current = (source / 'AGENTS.md').read_text()
    previous = template_at(source, old, 'AGENTS.md')
    result = {'old': old, 'new': new, 'writes': {}, 'hints': []}
    if top not in (current.rstrip('\n'), (previous or '').rstrip('\n')):
        result['status'] = 'conflict'
        result['hints'].append('AGENTS.md: the part above the marker differs from the harness. Move project rules '
                               'below the marker or bring the change to the harness repository, then update again.')
        return result
    updated = exporter.agents_with_marker(current, new, rest)
    if updated != text:
        result['writes']['AGENTS.md'] = updated
    for rel in UNIVERSAL:
        target, wanted = project / rel, (source / rel).read_text()
        have = target.read_text() if target.is_file() else None
        if have == wanted:
            continue
        if have is None or have == template_at(source, old, rel):
            result['writes'][rel] = wanted
        else:
            result['hints'].append(f'{rel}: changed locally, so it was not replaced. Compare with the harness '
                                   f'version and keep what is project-specific elsewhere.')
    learnings, wanted = project / 'learnings.md', (source / 'learnings.md').read_text()
    if learnings.is_file() and ENTRIES in learnings.read_text():
        have = learnings.read_text()
        head, entries = have.split(ENTRIES, 1)
        new_head = wanted.split(ENTRIES, 1)[0]
        old_head = (template_at(source, old, 'learnings.md') or '').split(ENTRIES, 1)[0]
        if head != new_head and head == old_head:
            result['writes']['learnings.md'] = new_head + ENTRIES + entries
        elif head != new_head:
            result['hints'].append('learnings.md: the header differs from the harness and was not replaced. Move '
                                   'project notes below the entries marker, then update again.')
    elif learnings.is_file() or (project / 'learning-state.md').is_file():
        result['hints'].append('learnings.md: no entries marker yet. Put the current harness header on top and move '
                               'existing notes (also from learning-state.md) below the marker in the new format.')
    else:
        result['writes']['learnings.md'] = wanted
    routing = text + ((project / 'PROJECT.md').read_text() if (project / 'PROJECT.md').is_file() else '')
    for doc in sorted((project / 'docs').rglob('*.md')) if (project / 'docs').is_dir() else []:
        rel = doc.relative_to(project).as_posix()
        if rel not in routing:
            result['hints'].append(f'{rel}: neither AGENTS.md nor PROJECT.md routes to it. Add a project rule saying '
                                   f'when to read it, or merge it into PROJECT.md or a neighbouring doc.')
    before, after = template_at(source, old, 'PROJECT.md'), (source / 'PROJECT.md').read_text()
    if before is None and old != new:
        result['hints'].append('PROJECT.md: previous template unknown; compare the project file with the current '
                               'harness template by hand.')
    elif before is not None and before != after:
        diff = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                            f'PROJECT template {old}', f'PROJECT template {new}'))
        result['hints'].append('PROJECT.md: the template changed. The project file was not touched; decide which '
                               'changes it should adopt.\n\n```diff\n' + diff + '```')
    result['status'] = 'update' if result['writes'] or result['hints'] else 'current'
    return result


def apply(project, result):
    project = Path(project).resolve()
    for rel, text in result['writes'].items():
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(text)
    if result['hints']:
        note = project / NOTE
        header = '' if note.exists() else ('# Harness update – review at the next task\n\n'
                                           'Discuss each point briefly, agree the step, apply it, then delete this file.\n')
        entry = f'\n## {date.today()} · {result["old"]} → {result["new"]}\n\n' + '\n\n'.join(
            f'- {hint}' for hint in result['hints']) + '\n'
        with note.open('a') as handle:
            handle.write(header + entry)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('projects', nargs='+', type=Path)
    parser.add_argument('--apply', action='store_true', help='write changes (default: dry run)')
    args = parser.parse_args()
    if args.apply and exporter.source_version() == 'local':
        parser.exit(1, 'Commit the harness repository first, so projects record a real version.\n')
    for project in args.projects:
        result = plan(project)
        print(f"{project}: {result['status']} ({result['old']} → {result['new']})")
        for rel in result['writes']:
            print(f'  write {rel}')
        for hint in result['hints']:
            print('  note  ' + hint.splitlines()[0])
        if args.apply and result['status'] == 'update':
            apply(project, result)
