#!/usr/bin/env python3
"""Install the reusable harness into a project without overwriting project files."""

import argparse
from pathlib import Path
import sys

SOURCE = Path(__file__).resolve().parent.parent

# Explicit allowlist: never distribute this repository's .git, image, main.py or own tests.
FILES = (
    "AGENTS.md",
    "harness/core.md",
    "harness/init.md",
    "harness/project.md",
    "harness/verification/gate.md",
    "harness/verification/requirements.md",
    "harness/verification/implementation.md",
    "harness/verification/fail.md",
    "harness/templates/idea.md",
    "harness/templates/spec.md",
    "docs/README.md",
    "docs/architecture.md",
    "docs/code.md",
    "docs/testing.md",
    "ideas/README.md",
    "specs/README.md",
    "src/README.md",
    "tests/README.md",
)
# The starter-kit README describes this repository, not the target product.
# Project Init creates a product README later; never copy or create one here.


def install(target: Path, *, keep_agents: bool = False, dry_run: bool = False) -> list[str]:
    """Preflight all collisions, then copy missing files; return actions taken/planned."""
    target = target.absolute()
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise ValueError(f"Target is not a normal directory: {target}")

    planned = [(relative, relative) for relative in FILES]
    actions = []
    conflicts = []
    for source_name, destination_name in planned:
        source = SOURCE / source_name
        if not source.is_file():
            raise ValueError(f"Missing installer source: {source}")
        destination = target / destination_name
        # Refuse links INSIDE the target; macOS /var itself is commonly a symlink.
        parts = Path(destination_name).parts
        inside = [target, *(target.joinpath(*parts[:i]) for i in range(1, len(parts) + 1))]
        if any(path.is_symlink() for path in inside):
            raise ValueError(f"Symlink in target path: {destination}")
        if any(path.exists() and not path.is_dir() for path in inside[:-1]):
            raise ValueError(f"Parent is not a directory: {destination}")
        if destination.exists() and not destination.is_file():
            conflicts.append(destination_name)
            continue
        if destination_name == "AGENTS.md" and destination.exists() and keep_agents:
            actions.append(f"KEEP {destination_name} (manual integration required)")
        elif destination.exists():
            if destination.is_file() and destination.read_bytes() == source.read_bytes():
                actions.append(f"SAME {destination_name}")
            else:
                conflicts.append(destination_name)
        else:
            actions.append(f"ADD  {destination_name}")
    if conflicts:
        raise ValueError(
            "Existing files differ; nothing installed: " + ", ".join(conflicts)
            + ". Merge them manually; for an existing AGENTS.md use --keep-agents "
            "and add a link to harness/core.md yourself."
        )

    if not dry_run:
        for source_name, destination_name in planned:
            destination = target / destination_name
            if destination.exists():
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation: even if the target changes after preflight, do not overwrite it.
            with destination.open("xb") as output:
                output.write((SOURCE / source_name).read_bytes())
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="New or existing project directory")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without writing")
    parser.add_argument(
        "--keep-agents", action="store_true",
        help="Keep an existing AGENTS.md; manually add a reference to harness/core.md afterwards",
    )
    args = parser.parse_args()
    existing_agents = (args.target / "AGENTS.md").exists()
    try:
        actions = install(args.target, keep_agents=args.keep_agents, dry_run=args.dry_run)
    except (ValueError, OSError) as error:
        print(f"Installation stopped: {error}", file=sys.stderr)
        return 1
    print("\n".join(actions))
    if args.keep_agents and existing_agents:
        print("ACTION REQUIRED: Update the existing AGENTS.md to load harness/core.md "
              "and, while Pending Project Init, harness/init.md.")
    print("Next: complete harness/init.md, including the product README; "
          "installation is NOT Project Init or a passing gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
