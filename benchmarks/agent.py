"""Isolated opt-in Pi process calls. Secrets/logs stay outside the repository."""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time


def summarize(log):
    usage = {k: 0 for k in ('input', 'output', 'cacheRead', 'cacheWrite', 'totalTokens')}
    messages, tools, errors, compactions = [], [], [], 0
    settled = False
    for line in Path(log).read_text(errors='replace').split('\n'):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        kind = event.get('type')
        if kind == 'message_end' and event.get('message', {}).get('role') == 'assistant':
            msg = event['message']
            messages.append(msg)
            for key in usage:
                usage[key] += msg.get('usage', {}).get(key, 0)
            if msg.get('stopReason') in ('error', 'aborted'):
                errors.append(msg.get('errorMessage', msg.get('stopReason')))
        elif kind == 'tool_execution_start':
            tools.append(event)
        elif kind == 'agent_settled':
            settled = not event.get('aborted', False)
        elif kind == 'compaction_end' and event.get('result'):
            compactions += 1
            for key in usage:
                usage[key] += event['result'].get('usage', {}).get(key, 0)
    final = '\n'.join(c.get('text', '') for c in (messages[-1].get('content', []) if messages else []) if c.get('type') == 'text')
    return dict(usage=usage, tool_calls=len(tools), errors=errors, settled=settled,
                compactions=compactions, read_paths=[t.get('args', {}).get('path') for t in tools if t['toolName'] == 'read'], final=final)


def summarize_claude(log):
    result, tools = {}, []
    for line in Path(log).read_text(errors='replace').split('\n'):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('type') == 'result':
            result = event
        if event.get('type') == 'assistant':
            tools.extend(c for c in event.get('message', {}).get('content', []) if c.get('type') == 'tool_use')
    u = result.get('usage', {})
    usage = dict(input=u.get('input_tokens', 0), output=u.get('output_tokens', 0),
                 cacheRead=u.get('cache_read_input_tokens', 0), cacheWrite=u.get('cache_creation_input_tokens', 0))
    usage['totalTokens'] = sum(usage.values())
    errors = [] if result.get('subtype') == 'success' and not result.get('is_error') else [result.get('result', result.get('subtype', 'no terminal result'))]
    return dict(usage=usage, tool_calls=len(tools), errors=errors, settled=bool(result), compactions=None,
                read_paths=[t.get('input', {}).get('file_path') for t in tools if t.get('name') == 'Read'],
                final=result.get('result', ''), estimated_usd=result.get('total_cost_usd'))


def invoke(project, output, prompt, *, model='gpt-6.1-sol', provider='openai-codex',
           timeout=900, forbidden=(), write_extra=(), thinking='medium', engine='pi'):
    project, output = Path(project).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / 'prompt.md').write_text(prompt)
    source_config = Path(os.environ.get('PI_CODING_AGENT_DIR', Path.home() / '.pi/agent'))
    config = Path(tempfile.mkdtemp(prefix='v6-agent-config-', dir=output))
    config.chmod(0o700)
    temp = output / 'tmp'
    temp.mkdir(exist_ok=True)
    policy = output / 'sandbox.sb'
    # Each trial is unreadable from other trials. Model transport still has network access.
    quote = lambda p: json.dumps(str(Path(p).resolve()))
    policy.write_text('(version 1)\n(allow default)\n(deny file-write*)\n' +
                      ''.join(f'(allow file-write* (subpath {quote(p)}))\n' for p in [project, output, *write_extra]) +
                      '(allow file-write* (literal "/dev/null"))\n' +
                      ''.join(f'(deny file-read* (subpath {quote(p)}))\n' for p in forbidden))
    try:
        auth = json.loads((source_config / 'auth.json').read_text())
        if provider not in auth:
            raise RuntimeError(f'No configured authentication for {provider}')
        private = config / 'auth.json'
        private.write_text(json.dumps({provider: auth[provider]}))
        private.chmod(0o600)
        # Built-in models only: no copied global instructions, hooks, providers or packages.
        (config / 'settings.json').write_text(json.dumps({'telemetry': False, 'compaction': {'enabled': True}}))
        env = {k: v for k, v in os.environ.items() if not (k.startswith('PI_') or any(s in k.upper() for s in ('TOKEN', 'SECRET', 'API_KEY', 'PASSWORD')))}
        env.update(PI_CODING_AGENT_DIR=str(config), PI_OFFLINE='1', PI_SKIP_VERSION_CHECK='1',
                   PI_TELEMETRY='0', PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(temp),
                   PI_MODEL=model, PI_PROVIDER=provider)
        args = ['pi', '--offline', '--no-extensions', '--no-skills', '--no-mcp', '--no-prompt-templates',
                '--no-session', '--no-approve', '--model', model, '--provider', provider,
                '--thinking', thinking, '--tools', 'read,bash,edit,write', '--mode', 'json', prompt]
        if engine == 'claude':
            env['CLAUDE_CODE_TMPDIR'] = str(temp)
            # Native first-party subscription transport. No paid-usage setting is enabled.
            # --safe-mode disables global/project customizations; both variants get only their AGENTS.
            args = ['claude', '--safe-mode', '--no-chrome', '--no-session-persistence', '--setting-sources', '',
                    '--model', model, '--effort', thinking, '--tools', 'Bash,Read,Edit,Write',
                    '--allowedTools', 'Bash,Read,Edit,Write', '--permission-mode', 'dontAsk',
                    '--strict-mcp-config', '--append-system-prompt', (project / 'AGENTS.md').read_text(),
                    '--output-format', 'stream-json', '--verbose', '--max-budget-usd', '2', '--print', prompt]
        elif engine != 'pi':
            raise ValueError('Unknown engine')
        if not shutil.which('sandbox-exec'):
            raise RuntimeError('This runner requires macOS sandbox-exec; do not silently drop isolation')
        args = ['sandbox-exec', '-f', str(policy), *args]
        started = time.monotonic()
        with (output / 'events.jsonl').open('w') as out, (output / 'stderr.log').open('w') as err:
            process = subprocess.Popen(args, cwd=project, env=env, stdin=subprocess.DEVNULL,
                                       stdout=out, stderr=err, start_new_session=True)
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=5)
                code = 'timeout'
            finally:
                # A completed agent may leave a server descendant: clean its process group.
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        summary = summarize_claude if engine == 'claude' else summarize
        result = dict(exit=code, seconds=round(time.monotonic() - started, 2), model=model,
                      provider=provider, thinking=thinking, engine=engine, **summary(output / 'events.jsonl'))
        (output / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    finally:
        shutil.rmtree(config)
