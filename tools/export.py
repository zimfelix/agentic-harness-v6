#!/usr/bin/env python3
"""Copy only the pristine template into a new/empty project; never overwrite a project.

Skills stay in this repository and reach projects through global links
(~/.claude/skills, ~/.pi/agent/skills). --with-skills bundles a copy for
self-contained projects (cloud, other machines); that copy is not synced back."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

SOURCE = Path(__file__).resolve().parents[1] / 'harness'
MARKER = '<!-- harness-v6@{version} · project rules below; tools/update.py never changes them -->'
PROJECT_PART = '\n\n## Project rules\n\nNone yet.\n'


def source_version(source=SOURCE):
    """Short commit of a clean, versioned template; 'local' if uncommitted or unversioned."""
    source = Path(source)
    try:
        dirty = subprocess.run(['git', '-C', str(source), 'status', '--porcelain', '--', '.'],
                               capture_output=True, text=True, check=True).stdout.strip()
        head = subprocess.run(['git', '-C', str(source), 'rev-parse', '--short', 'HEAD'],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return 'local'
    return 'local' if dirty or not head else head


def agents_with_marker(template_text, version, project_part=PROJECT_PART):
    return template_text.rstrip('\n') + '\n\n' + MARKER.format(version=version) + project_part


def export(destination, source=SOURCE, *, with_skills=False):
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
        patterns = shutil.ignore_patterns('__pycache__', '.DS_Store', '.idea')

        def ignore(directory, names):
            skipped = set(patterns(directory, names))
            if not with_skills and Path(directory) == source:
                skipped.add('.agents')
            return skipped

        shutil.copytree(source, staged, ignore=ignore)
        agents = staged / 'AGENTS.md'
        agents.write_text(agents_with_marker(agents.read_text(), source_version(source)))
        if with_skills:
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
    parser.add_argument('--with-skills', action='store_true',
                        help='Bundle a skill copy plus Claude aliases (self-contained project); default relies on global skill links')
    args = parser.parse_args()
    try:
        print(export(args.destination, with_skills=args.with_skills))
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')
