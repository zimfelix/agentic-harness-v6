#!/usr/bin/env python3
"""Separately recorded fresh-session recovery of a transport-failed change phase."""
import argparse
import json
from pathlib import Path
from agent import invoke
from run import REPO, quota


def recover(workspace, label):
    workspace = Path(workspace).resolve()
    directory = workspace / 'trials' / label
    previous = json.loads((directory / 'change/result.json').read_text())
    if not previous.get('errors'):
        raise ValueError('No infrastructure error in the preceding change phase')
    output = directory / 'change-recovery'
    if output.exists():
        raise ValueError('Refusing to overwrite a recovery')
    q = quota()
    if min(q['remaining'].values()) < 10:
        raise RuntimeError('Quota below 10%; no recovery started')
    prompt = ('The previous change phase ended with a transport error, not a product decision. '
              'Fresh session: finish the existing authorized amendment and verification from persisted files. '
              'Do not make unrelated changes. This recovery is reported separately, not a new first build.\n' +
              (REPO / 'benchmarks/changes/crm-title.md').read_text())
    forbidden = [REPO, workspace / 'snapshots', workspace / 'phase-snapshots', workspace / 'qa', workspace / 'oracle-review',
                 Path(json.loads((workspace / 'manifest.json').read_text())['baseline_path'])]
    forbidden += [p for p in (workspace / 'trials').iterdir() if p != directory]
    result = invoke(directory / 'project', output, prompt, timeout=300, forbidden=forbidden)
    result.update(label=label, phase='change-recovery', quota_before=q)
    (output / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({k: result[k] for k in ('exit', 'seconds', 'usage', 'errors')}), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--run-agents', action='store_true', required=True)
    parser.add_argument('label')
    args = parser.parse_args()
    recover(args.workspace, args.label)
