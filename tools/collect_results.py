#!/usr/bin/env python3
"""Collect bounded, sanitized experiment metrics; never copy raw sessions/configs."""
import argparse
import json
from pathlib import Path
import shutil

REPO = Path(__file__).resolve().parents[1]


def collect(workspace, brief_workspace, destination):
    workspace, brief_workspace, destination = map(lambda p: Path(p).resolve(), (workspace, brief_workspace, destination))
    destination.mkdir(parents=True, exist_ok=True)
    trials, phases, acceptance = [], [], []
    for root in (workspace, brief_workspace):
        for path in sorted((root / 'trials').glob('*/result.json')):
            raw = json.loads(path.read_text())
            fields = ('case', 'variant', 'repetition', 'exit', 'seconds', 'model', 'provider', 'engine', 'thinking',
                      'usage', 'tool_calls', 'snapshot', 'task_hash')
            item = {k: raw[k] for k in fields if k in raw}
            item['label'] = path.parent.name
            item['model_errors'] = len(raw.get('errors', []))
            item['completed_transport'] = raw.get('exit') == 0 and not raw.get('errors')
            item['native_bash_unavailable'] = item['label'].startswith('opus-native-autonomy-r1-')
            item['comparison_eligible'] = item['completed_transport'] and not item['native_bash_unavailable']
            item['read_calls'] = len(raw.get('read_paths', []))
            item['unique_read_paths'] = len(set(raw.get('read_paths', [])))
            trials.append(item)
        for path in sorted((root / 'trials').glob('*/*/result.json')):
            if path.parent.name == 'initial':
                continue
            raw = json.loads(path.read_text())
            fields = ('phase', 'exit', 'seconds', 'usage', 'tool_calls', 'deferred_unchanged', 'code_unchanged')
            item = {k: raw[k] for k in fields if k in raw}
            item.update(label=path.parent.parent.name, model_errors=len(raw.get('errors', [])))
            phases.append(item)
        for path in sorted((root / 'trials').glob('*/acceptance-*.json')):
            raw = json.loads(path.read_text())
            acceptance.append({k: raw[k] for k in ('label', 'phase', 'case', 'oracle_sha256', 'seeds',
                                                  'product_hash_before', 'product_hash_after')})
    shape = {}
    for variant in ('baseline', 'lean'):
        source = workspace / 'snapshots' / variant
        docs = list(source.rglob('*.md'))
        entry = ['AGENTS.md', 'harness/core.md', 'harness/project.md'] if variant == 'baseline' else ['AGENTS.md', 'PROJECT.md']
        shape[variant] = {'markdown_files': len(docs), 'markdown_characters': sum(len(p.read_text()) for p in docs),
                          'entry_characters': sum(len((source / p).read_text()) for p in entry)}
    manifest = json.loads((workspace / 'manifest.json').read_text())
    manifest.pop('baseline_path', None)
    brief_manifest = json.loads((brief_workspace / 'manifest.json').read_text())
    brief_manifest.pop('baseline_path', None)
    result = dict(manifest=manifest, supplementary_brief_manifest=brief_manifest, template_shape=shape,
                  trials=trials, phases=phases, acceptance=acceptance)
    (destination / 'metrics.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def copy_sample(project, snapshot, destination):
    """Synthetic generated product files only; retain executable modes, exclude harness/data/logs."""
    project, snapshot, destination = map(Path, (project, snapshot, destination))
    if destination.exists():
        raise ValueError('Refusing to overwrite sample')
    destination.mkdir(parents=True)
    ignored = {'.agents', '.claude', '.git', '.idea', 'profiles', 'tools', 'harness', 'ideas',
               '.data', 'data', '__pycache__', '.scratch', '.runs'}
    suffixes = {'.py', '.mjs', '.js', '.sql', '.md', '.json', '.csv', '.sh'}
    for p in project.rglob('*'):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(project)
        if any(part in ignored for part in rel.parts):
            continue
        if str(rel) in {'AGENTS.md', 'PROJECT.md', 'document-contract.md', 'harness-learnings.md', 'learning-state.md'}:
            continue
        if p.suffix not in suffixes and p.name not in {'planner', '.gitignore'}:
            continue
        old = snapshot / rel
        if old.is_file() and old.read_bytes() == p.read_bytes():
            continue
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--brief-workspace', type=Path, required=True)
    args = parser.parse_args()
    collect(args.workspace, args.brief_workspace, REPO / 'reports')
