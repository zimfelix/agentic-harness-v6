#!/usr/bin/env python3
"""Run held-out checks after a completed build/phase; never repairs products."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tempfile

import oracle
from run import digest_tree


def accept(workspace, label, phase='initial', seeds=(1, 17)):
    base = Path(workspace).resolve() / 'trials' / label
    run = json.loads((base / ('result.json' if phase == 'initial' else phase + '/result.json')).read_text())
    if run.get('errors') or run.get('exit') != 0:
        raise ValueError('Infrastructure/timeout run is not a completed-build quality comparison')
    case = run.get('case') or json.loads((base / 'result.json').read_text())['case']
    destination = base / f'acceptance-{phase}.json'
    if destination.exists():
        raise ValueError('Refusing to overwrite acceptance; use a labeled re-evaluation')
    project = base / 'project'
    record = {'label': label, 'phase': phase, 'case': case, 'product_hash_before': digest_tree(project),
              'oracle_sha256': hashlib.sha256(Path(oracle.__file__).read_bytes()).hexdigest(), 'seeds': []}
    with tempfile.TemporaryDirectory(prefix='v6-acceptance-') as temp:
        for seed in seeds:
            groups = oracle.evaluate(case, project, Path(temp) / f'seed-{seed}', seed)
            if phase in ('change', 'change-recovery'):
                from change_oracle import evaluate
                groups += evaluate(project, Path(temp) / f'change-{seed}')
            record['seeds'].append({'seed': seed, 'groups': groups,
                                    'counts': dict(Counter(g.get('outcome', 'pass' if g['passed'] else 'fail') for g in groups))})
    record['product_hash_after'] = digest_tree(project)
    destination.write_text(json.dumps(record, ensure_ascii=False, indent=2))
    print(json.dumps({'label': label, 'phase': phase, 'results': [s['counts'] for s in record['seeds']]}), flush=True)
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--phase', default='initial', choices=['initial', 'resume', 'change', 'change-recovery', 'blocker'])
    parser.add_argument('labels', nargs='+')
    args = parser.parse_args()
    for label in args.labels:
        accept(args.workspace, label, args.phase)
