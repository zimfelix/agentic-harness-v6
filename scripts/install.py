#!/usr/bin/env python3
"""Copy the bundled agentic-harness directory into a project and connect AGENTS.md."""

import argparse
from pathlib import Path
import shutil
import sys
import tempfile

SOURCE = Path(__file__).resolve().parent.parent / "agentic-harness"
BUNDLE_NAME = "agentic-harness"
AGENTS_NAME = "AGENTS.md"
START = "<!-- BEGIN AGENTIC HARNESS -->"
END = "<!-- END AGENTIC HARNESS -->"
BLOCK = f"{START}\nFor project work, follow `{BUNDLE_NAME}/AGENTS.md`. Existing project instructions remain in force; resolve conflicts before acting.\n{END}"


def _bundle_matches(destination: Path) -> bool:
    """Return whether an existing bundle has exactly the source files and contents."""
    if not destination.is_dir() or destination.is_symlink():
        return False
    if any(path.is_symlink() for path in destination.rglob("*")):
        return False
    source_files = {p.relative_to(SOURCE) for p in SOURCE.rglob("*") if p.is_file()}
    destination_files = {p.relative_to(destination) for p in destination.rglob("*") if p.is_file()}
    if source_files != destination_files:
        return False
    return all((SOURCE / rel).read_bytes() == (destination / rel).read_bytes()
               for rel in source_files)


def _agents_result(path: Path) -> tuple[str, str | None]:
    """Return action and replacement content for the target AGENTS.md."""
    if path.is_symlink():
        raise ValueError(f"Refusing symlink: {path}")
    if not path.exists():
        return "ADD", BLOCK + "\n"
    if not path.is_file():
        raise ValueError(f"AGENTS.md is not a regular file: {path}")
    current = path.read_text(encoding="utf-8")
    has_start, has_end = START in current, END in current
    if (current.count(START) > 1 or current.count(END) > 1
            or has_start != has_end or (has_start and current.index(START) > current.index(END))):
        raise ValueError("Malformed Agentic Harness markers in AGENTS.md; repair them manually.")
    if has_start:
        section = current[current.index(START):current.index(END) + len(END)]
        if section != BLOCK:
            raise ValueError("AGENTS.md contains a different managed Harness section; "
                             "review and update it manually.")
        return "SAME", None
    separator = "" if not current or current.endswith("\n\n") else "\n"
    return "UPDATE", current + separator + BLOCK + "\n"


def install(target: Path, *, dry_run: bool = False) -> list[str]:
    """Preflight, then install one bundle directory and append an idempotent AGENTS entry."""
    if not SOURCE.is_dir():
        raise ValueError(f"Harness bundle missing from source: {SOURCE}")
    target = target.expanduser().absolute()
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise ValueError(f"Target is not a normal directory: {target}")

    bundle = target / BUNDLE_NAME
    if bundle.is_symlink():
        raise ValueError(f"Refusing symlink: {bundle}")
    if bundle.exists() and not _bundle_matches(bundle):
        raise ValueError(f"{BUNDLE_NAME}/ already exists and differs; nothing installed. "
                         "Review or back it up before installing the bundle.")
    bundle_action = "SAME" if bundle.exists() else "ADD"
    agents = target / AGENTS_NAME
    agents_action, agents_content = _agents_result(agents)
    actions = [f"{bundle_action}  {BUNDLE_NAME}/", f"{agents_action}  {AGENTS_NAME}"]
    if dry_run:
        return actions

    target.mkdir(parents=True, exist_ok=True)
    if not bundle.exists():
        # Stage in the destination filesystem and rename only after the complete copy succeeds.
        with tempfile.TemporaryDirectory(prefix=".agentic-harness-", dir=target) as temporary:
            staged = Path(temporary) / BUNDLE_NAME
            shutil.copytree(SOURCE, staged)
            staged.rename(bundle)
    if agents_content is not None:
        if agents_action == "ADD":
            # Exclusive create protects an AGENTS.md created after preflight.
            with agents.open("x", encoding="utf-8") as output:
                output.write(agents_content)
        else:
            # Atomic replacement; preserve existing file permissions.
            mode = agents.stat().st_mode
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target,
                                             prefix=".AGENTS.", delete=False) as output:
                temporary = Path(output.name)
                output.write(agents_content)
            temporary.chmod(mode)
            temporary.replace(agents)
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="New or existing project directory")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    args = parser.parse_args()
    try:
        actions = install(args.target, dry_run=args.dry_run)
    except (ValueError, OSError) as error:
        print(f"Installation stopped: {error}", file=sys.stderr)
        return 1
    print("\n".join(actions))
    if not args.dry_run:
        print("Next: initialize agentic-harness/harness/project.md; installation is not Project Init.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
