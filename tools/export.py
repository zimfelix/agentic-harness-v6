#!/usr/bin/env python3
"""Copy only the pristine template into a new/empty project; never overwrite a project."""
import argparse
from pathlib import Path
import shutil
import tempfile

SOURCE = Path(__file__).resolve().parents[1] / 'harness'


def export(destination, source=SOURCE, *, claude=False):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Source and destination must not overlap')
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError('Destination must be new or empty; no project upgrades/overwrites')
    required = ['AGENTS.md', 'PROJECT.md', 'specs/README.md', '.agents/skills/business-software/SKILL.md',
                '.agents/skills/website-tools/SKILL.md']
    if any(not (source / path).is_file() for path in required):
        raise ValueError('Incomplete template')
    if any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('Template must not contain symlinks')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.v6-export-', dir=destination.parent) as temp:
        staged = Path(temp) / 'project'
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns('__pycache__', '.DS_Store', '.idea'))
        if claude:
            aliases = staged / '.claude/skills'
            aliases.mkdir(parents=True)
            for skill in sorted((staged / '.agents/skills').iterdir()):
                if skill.is_dir() and (skill / 'SKILL.md').is_file():
                    (aliases / skill.name).symlink_to(Path('../../.agents/skills') / skill.name, target_is_directory=True)
        # Staging avoids a half-written destination if copying fails.
        if destination.exists():
            destination.rmdir()  # still must be empty; race fails closed
        staged.rename(destination)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--claude', action='store_true', help='Add project-local skill symlinks for Claude; no duplicated content')
    args = parser.parse_args()
    try:
        print(export(args.destination, claude=args.claude))
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')
