#!/usr/bin/env python3
"""Opt-in matched runs. No model calls in ordinary tests. Raw logs remain local."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from agent import invoke

REPO = Path(__file__).resolve().parents[1]
FRAME = '''Implement the complete confirmed product task below. Work in shipping mode.
Read and follow this project's AGENTS.md. The stated product decisions are confirmed;
routine reversible architecture/layout/implementation/testing choices are delegated.
Do not ask for another approval for those choices. Persist enough context for another
session and explain the architecture briefly. Build and execute your own meaningful tests.
Do not modify the harness rules or deferred work. No git operations, packages, external
network requests, real data/providers or writes outside this project. Use only the stated
runtime's standard library. Be honest about missing evidence and any production limitations.
Public entrypoint names specify an interface, not an internal architecture. Complete all
requested behavior; do not substitute a smaller easier task.
'''


def digest_tree(root):
    digest = hashlib.sha256()
    for path in sorted(Path(root).rglob('*')):
        if path.is_file():
            digest.update(str(path.relative_to(root)).encode() + b'\0' + path.read_bytes() + b'\0')
    return digest.hexdigest()


def quota(provider='codex'):
    result = subprocess.run(['codexbar', 'usage', '--provider', provider, '--format', 'json', '--no-credits'],
                            capture_output=True, text=True, timeout=45)
    result.check_returncode()
    record = json.loads(result.stdout)[0]
    usage = record['usage']
    windows = {name: 100 - usage[name]['usedPercent'] for name in ('primary', 'secondary') if usage.get(name)}
    if not windows:
        raise RuntimeError('Usage unavailable; no unbounded paid run')
    return {'remaining': windows, 'reset_count': usage.get('codexResetCredits', {}).get('availableCount')}


def prepare(workspace, baseline):
    workspace = Path(workspace).resolve()
    if (workspace / 'manifest.json').exists():
        raise ValueError('Already frozen; use the existing snapshot or a new workspace')
    snapshots = workspace / 'snapshots'
    snapshots.mkdir(parents=True)
    subprocess.run(['sh', str(Path(baseline).resolve() / 'agentic-harness/tools/export-harness.sh'), str(snapshots / 'baseline')], check=True)
    shutil.copytree(REPO / 'template', snapshots / 'lean')
    shutil.copytree(REPO / 'benchmarks/tasks', snapshots / 'tasks')
    meta = {'baseline_commit': subprocess.check_output(['git', '-C', str(baseline), 'rev-parse', 'HEAD'], text=True).strip(),
            'snapshots': {name: digest_tree(snapshots / name) for name in ('baseline', 'lean', 'tasks')},
            'pi_version': subprocess.check_output(['pi', '--version'], text=True).strip(),
            'python': subprocess.check_output(['python3', '--version'], text=True).strip(),
            'node': subprocess.check_output(['node', '--version'], text=True).strip(),
            'created_unix': time.time(), 'baseline_path': str(Path(baseline).resolve())}
    (workspace / 'manifest.json').write_text(json.dumps(meta, indent=2))
    return meta


def run_pair(workspace, case, repetition=1, model='gpt-6.1-sol', provider='openai-codex', timeout=900, engine='pi'):
    workspace = Path(workspace).resolve()
    meta = json.loads((workspace / 'manifest.json').read_text())
    for name, digest in meta['snapshots'].items():
        if digest_tree(workspace / 'snapshots' / name) != digest:
            raise RuntimeError(f'Frozen source changed: {name}')
    usage_provider = 'claude' if provider == 'anthropic' else 'codex'
    before = quota(usage_provider)
    # Anthropic low-quota trial is explicit and recorded, never a reason to bypass Codex gate.
    if usage_provider == 'codex' and min(before['remaining'].values()) < 10:
        raise RuntimeError('Quota below 10%; user-authorized reset required before another pair')
    family = ('opus-native' if engine == 'claude' else 'opus') if provider == 'anthropic' else 'sol'
    order = ['baseline', 'lean'] if repetition % 2 else ['lean', 'baseline']
    runs = workspace / 'trials'
    runs.mkdir(exist_ok=True)
    directories = {}
    for version in order:
        name = f'{family}-{case}-r{repetition}-{version}'
        directory = runs / name
        if directory.exists():
            raise ValueError(f'Refusing to overwrite trial {name}')
        project = directory / 'project'
        shutil.copytree(workspace / 'snapshots' / version, project)
        directories[version] = directory
    def one(version):
        directory = directories[version]
        forbidden = [REPO, Path(meta['baseline_path']), workspace / 'snapshots', workspace / 'qa', workspace / 'qa-run']
        forbidden += [p for p in runs.iterdir() if p != directory]
        prompt = FRAME + '\n' + (workspace / 'snapshots/tasks' / (case + '.md')).read_text()
        result = invoke(directory / 'project', directory / 'initial', prompt, model=model, provider=provider,
                        timeout=timeout, forbidden=forbidden, engine=engine)
        result.update(case=case, variant=version, repetition=repetition, quota_before=before,
                      snapshot=meta['snapshots'][version], task_hash=hashlib.sha256(prompt.encode()).hexdigest())
        # No raw reasoning or credentials in this structured summary.
        (directory / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps({'trial': directory.name, 'exit': result['exit'], 'seconds': result['seconds'], 'usage': result['usage'], 'errors': result['errors']}), flush=True)
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(one, order))
    (workspace / f'{family}-{case}-r{repetition}.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('prepare'); init.add_argument('--baseline', type=Path, required=True)
    pair = sub.add_parser('pair'); pair.add_argument('case'); pair.add_argument('--run-agents', action='store_true', required=True)
    pair.add_argument('--repetition', type=int, default=1); pair.add_argument('--model', default='gpt-6.1-sol')
    pair.add_argument('--provider', default='openai-codex'); pair.add_argument('--timeout', type=int, default=900)
    pair.add_argument('--engine', choices=['pi', 'claude'], default='pi')
    args = parser.parse_args()
    if args.command == 'prepare':
        print(json.dumps(prepare(args.workspace, args.baseline), indent=2))
    else:
        run_pair(args.workspace, args.case, args.repetition, args.model, args.provider, args.timeout, args.engine)


if __name__ == '__main__':
    main()
