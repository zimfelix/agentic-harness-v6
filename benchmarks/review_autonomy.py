#!/usr/bin/env python3
"""Masked independent review of less-prescriptive products; model calls are opt-in."""
import argparse
import json
from pathlib import Path
import shutil

from agent import invoke
from run import REPO, quota

PROMPT = '''Independent blinded product evaluation. Read autonomy.md and AUTONOMY-RUBRIC.md first.
Letter-labeled directories contain completed local planner implementations. Variant/model labels
are masked; do not infer or favor a harness. Read each actual README/interface/schema and adapt
commands to it, not your preferred architecture. Do not modify the products. You may write
verification scripts and synthetic fixtures in this review root or temporary directory.
No packages, network, git or real data. Use Python stdlib and each stated product runtime.
Run each product's own suite; then exercise all TEN executable outcomes independently against
fresh persistent stores with documented commands, especially cycles, dependency block, deletion
integrity, malformed import preserving state, deterministic next work and export/backup/restore.
Inspect project context and acceptance evidence to check honest handoff, scope and proportionate
architecture. Give each of the five ordinal rubric dimensions its own justified judgment.
Report unverified/failed explicitly, including test-env problems; never infer pass from a final
message. Preserve actual evidence in compact JSON and a verification script; no full transcripts.
Write REPORT.md and report.json (products list with label, outcomes[{name,status,evidence}],
judgments, deficiencies, own_test_result, and limitations). Stay concise: summarize commands and
observations rather than dump all stdout. Do not sum subjective scores into an intelligence score.
You have 7 minutes. The main reviewer will spot-check executable claims after your review.
'''


def prepare_review(workspace, labels, output):
    workspace, output = Path(workspace).resolve(), Path(output).resolve()
    output.mkdir(parents=True)
    mapping = {}
    for letter, label in zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', labels):
        directory = workspace / 'trials' / label
        result = json.loads((directory / 'result.json').read_text())
        if result.get('exit') != 0 or result.get('errors'):
            raise ValueError('Incomplete/error build must not be relabeled completed')
        variant = result['variant']
        source = directory / 'project'
        snapshot = workspace / 'snapshots' / variant
        dest = output / letter
        dest.mkdir()
        for p in source.rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts:
                continue
            rel = p.relative_to(source)
            if rel.parts[0] in {'.agents', '.claude', 'profiles', 'tools', 'harness', 'ideas', '.git'}:
                continue
            if str(rel) in {'AGENTS.md', 'PROJECT.md', 'document-contract.md', 'harness-learnings.md', 'learning-state.md'}:
                continue
            old = snapshot / rel
            if old.is_file() and old.read_bytes() == p.read_bytes():
                continue
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
        context = source / ('PROJECT.md' if variant == 'lean' else 'harness/project.md')
        target = dest / 'context/project-record.md'
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(context, target)
        mapping[letter] = label
    shutil.copyfile(REPO / 'benchmarks/tasks/autonomy.md', output / 'autonomy.md')
    shutil.copyfile(REPO / 'benchmarks/AUTONOMY-RUBRIC.md', output / 'AUTONOMY-RUBRIC.md')
    # Keep the mapping OUTSIDE the blinded reviewer workspace.
    (output.parent / (output.name + '-map.json')).write_text(json.dumps(mapping, indent=2))
    return mapping


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--run-agents', action='store_true', required=True)
    parser.add_argument('labels', nargs='+')
    args = parser.parse_args()
    q = quota()
    if min(q['remaining'].values()) < 10:
        raise SystemExit('Quota below 10%; no reviewer started')
    prepare_review(args.workspace, args.labels, args.output)
    w = args.workspace.resolve()
    result = invoke(args.output, args.output.parent / (args.output.name + '-run'), PROMPT,
                    timeout=420, forbidden=[REPO, w / 'trials', w / 'snapshots', w / 'phase-snapshots',
                                            args.output.parent / (args.output.name + '-map.json'),
                                            json.loads((w / 'manifest.json').read_text())['baseline_path']])
    print(json.dumps({k: result[k] for k in ('exit', 'seconds', 'usage', 'errors')}))
