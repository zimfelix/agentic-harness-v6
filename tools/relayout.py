#!/usr/bin/env python3
"""Move a flat v6 project's harness files into harness/ once, keeping every reference valid.

Moves PROJECT.md, specs/, ideas/, docs/, learnings.md and harness-update.md into
harness/ (git mv for tracked files). In every tracked text file, relative Markdown
links are recomputed and root-relative path mentions (`docs/x.md`) get the harness/
prefix; `../docs/x.md` style mentions become root-relative. The harness part of
AGENTS.md above the marker and the learnings.md header are left for tools/update.py,
which replaces them afterwards. Requires a clean tracked working tree. Default is a
dry run that prints moves and a diff; --apply writes. Run tools/update.py next.
"""
import argparse
import difflib
import importlib.util
import os
from pathlib import Path
import posixpath
import re
import subprocess

_spec = importlib.util.spec_from_file_location('updater', Path(__file__).with_name('update.py'))
updater = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(updater)
MEMORY = updater.exporter.MEMORY

MOVED = ['PROJECT.md', 'specs', 'ideas', 'docs', 'learnings.md', 'harness-update.md']
SKIP_FILES = {'uv.lock', 'package-lock.json', 'poetry.lock', 'Cargo.lock', 'pnpm-lock.yaml', 'yarn.lock'}
LINK = re.compile(r'(\]\()([^)\s]+)(\))')
TOKEN = re.compile(r'(?<![\w./@-])((?:\.\./)*)(PROJECT\.md|specs/|ideas/|docs/|learnings\.md|harness-update\.md)')


def moved(rel):
    """Old project-relative path -> new one."""
    return f'{MEMORY}/{rel}' if rel.split('/', 1)[0] in MOVED else rel


def git(project, *args):
    return subprocess.run(['git', '-C', str(project), *args], capture_output=True, text=True, check=True).stdout


def _link(target, old_rel, new_rel):
    if '://' in target or target.startswith(('#', '/', 'mailto:')):
        return target
    path, hash_, anchor = target.partition('#')
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(old_rel), path))
    if resolved.startswith('..') or resolved == '.':
        return target
    if posixpath.normpath(posixpath.join(posixpath.dirname(new_rel), path)) == moved(resolved):
        return target  # still points to the same file after the move
    new = posixpath.relpath(moved(resolved), posixpath.dirname(new_rel) or '.') + ('/' if path.endswith('/') else '')
    return new + hash_ + anchor


def _tokens(text, old_rel):
    def sub(match):
        ups, name = match.groups()
        if not ups:
            return f'{MEMORY}/{name}'
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(old_rel), ups + name))
        if moved(resolved) == resolved:  # outside the project or not a moved entry
            return match.group(0)
        return moved(resolved) + ('/' if name.endswith('/') else '')
    return TOKEN.sub(sub, text)


def rewrite(text, old_rel, new_rel):
    """Rewrite links and path mentions in one file's text."""
    out, last = [], 0
    for match in LINK.finditer(text):
        out.append(_tokens(text[last:match.start()], old_rel))
        out.append(match.group(1) + _link(match.group(2), old_rel, new_rel) + match.group(3))
        last = match.end()
    out.append(_tokens(text[last:], old_rel))
    return ''.join(out)


def _split(rel, text):
    """(fixed part left for update.py, rewritable part)."""
    if rel == 'AGENTS.md':
        match = updater.MARKER_RE.search(text)
        return (text[:match.end()], text[match.end():]) if match else ('', text)
    if rel == 'learnings.md' and updater.ENTRIES in text:
        head, entries = text.split(updater.ENTRIES, 1)
        return head + updater.ENTRIES, entries
    return '', text


def broken_links(project, files):
    """Relative Markdown links in the given files whose target does not exist."""
    broken = set()
    for rel in files:
        if not rel.endswith('.md') or not (project / rel).is_file():
            continue
        for target in LINK.findall((project / rel).read_text(errors='ignore')):
            path = target[1].partition('#')[0]
            if path and '://' not in path and not path.startswith(('/', 'mailto:')) and \
                    not (project / posixpath.dirname(rel) / path).exists():
                broken.add((rel, target[1]))
    return broken


def plan(project):
    """Return {'moves': [(old, new)], 'writes': {old_rel: (new_rel, text)}, 'diff': str, 'notes': [str]}."""
    project = Path(project).resolve()
    agents = project / 'AGENTS.md'
    if not agents.is_file() or not updater.MARKER_RE.search(agents.read_text()):
        raise ValueError('No harness-v6 marker in AGENTS.md; this tool only moves v6 projects.')
    if not (project / 'PROJECT.md').is_file():
        raise ValueError('No PROJECT.md in the root; nothing to move.')
    if (project / MEMORY).exists():
        raise ValueError(f'{MEMORY}/ already exists; resolve that by hand first.')
    if git(project, 'status', '--porcelain', '--untracked-files=no').strip():
        raise ValueError('Tracked files have uncommitted changes; commit or stash them first.')
    moves = [(name, f'{MEMORY}/{name}') for name in MOVED if (project / name).exists()]
    files = [f for f in git(project, 'ls-files').splitlines() if Path(f).name not in SKIP_FILES]
    writes, diffs, code = {}, [], []
    for rel in files:
        path = project / rel
        if not path.is_file() or path.is_symlink():
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        fixed, body = _split(rel, text)
        new_text = fixed + rewrite(body, rel, moved(rel))
        if new_text != text:
            writes[rel] = (moved(rel), new_text)
            diffs.append(''.join(difflib.unified_diff(text.splitlines(True), new_text.splitlines(True),
                                                      f'a/{rel}', f'b/{moved(rel)}')))
            if not rel.endswith('.md'):
                code.append(rel)
    notes = [f'outside Markdown (review): {rel}' for rel in code]
    notes += [f'link already broken before the move: {rel} -> {target}'
              for rel, target in sorted(broken_links(project, files))]
    return {'moves': moves, 'writes': writes, 'diff': ''.join(diffs), 'notes': notes, 'files': files}


def apply(project, result):
    project = Path(project).resolve()
    before = broken_links(project, result['files'])
    for rel, (_, text) in result['writes'].items():
        (project / rel).write_text(text)
    (project / MEMORY).mkdir()
    for old, new in result['moves']:
        if git(project, 'ls-files', '--', old).strip():
            git(project, 'mv', old, new)
        else:
            os.rename(project / old, project / new)
    after_files = [moved(rel) for rel in result['files']]
    known = {(moved(rel), t) for rel, t in before}
    broken = broken_links(project, after_files) - known
    if broken:
        raise RuntimeError('Links broken by the move: ' + ', '.join(f'{r} -> {t}' for r, t in sorted(broken)))
    return broken


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('project', type=Path)
    parser.add_argument('--apply', action='store_true', help='write changes (default: dry run)')
    parser.add_argument('--diff', action='store_true', help='print the full text diff')
    args = parser.parse_args()
    try:
        result = plan(args.project)
    except (ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{args.project}: {error}\n')
    print(f'{args.project}: {len(result["moves"])} moves, {len(result["writes"])} files rewritten')
    for old, new in result['moves']:
        print(f'  move  {old} -> {new}')
    for note in result['notes']:
        print(f'  note  {note}')
    if args.diff:
        print(result['diff'])
    if args.apply:
        apply(args.project, result)
        print('  done; next: python3 tools/update.py <project> --apply')
