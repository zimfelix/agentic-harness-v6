"""Self-tests use deliberately broken entrypoints, never reference products."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

import oracle


class tempfile:
    # All self-test fixtures must remain within the QA workspace.
    @staticmethod
    def TemporaryDirectory():
        return TemporaryDirectory(dir=Path(__file__).resolve().parent)


class AssertionTests(unittest.TestCase):
    def test_require_and_equal(self):
        oracle.require(True, 'ok')
        oracle.equal({'a': [1]}, {'a': [1]})
        with self.assertRaisesRegex(AssertionError, 'synthetic failure'):
            oracle.require(False, 'synthetic failure')
        with self.assertRaisesRegex(AssertionError, 'expected 2, got 1'):
            oracle.equal(1, 2, 'synthetic')

    def test_report_rejects_wrong_counts_and_missing_reason(self):
        good = dict(run_id='r', status='completed', applied_groups=1,
                    rejected_groups=0, applied_rows=1, replayed=False, errors=[])
        oracle.report(good)
        with self.assertRaises(AssertionError):
            oracle.report({**good, 'applied_rows': 2})
        with self.assertRaises(AssertionError):
            oracle.report({**good, 'errors': [{'group_id': 'g', 'reason': ''}],
                           'rejected_groups': 1}, rejected=1)


class ProcessTests(unittest.TestCase):
    def test_capture_stdout_stderr_and_exit(self):
        rc, out, err = oracle.invoke([sys.executable, '-c',
            'import sys; print("synthetic stdout"); print("synthetic stderr",file=sys.stderr); sys.exit(7)'])
        self.assertEqual(rc, 7)
        self.assertIn('synthetic stdout', out)
        self.assertIn('synthetic stderr', err)

    def test_json_single_value_and_exit_enforcement(self):
        app = [sys.executable, '-c']
        self.assertEqual(oracle.json_command(app + ['print("{\\"x\\":1}")']), {'x': 1})
        with self.assertRaisesRegex(AssertionError, 'not one JSON'):
            oracle.json_command(app + ['print("{}\\n{}")'])
        with self.assertRaisesRegex(AssertionError, 'exited zero'):
            oracle.json_command(app + ['print("{}")'], success=False)
        with self.assertRaisesRegex(AssertionError, 'synthetic-error'):
            oracle.json_command(app + ['import sys; print("synthetic-error",file=sys.stderr); sys.exit(2)'])

    def test_timeout_reaps_child_and_closes_pipes(self):
        children = []
        real = subprocess.Popen
        def record(*a, **kw):
            child = real(*a, **kw)
            children.append(child)
            return child
        start = time.monotonic()
        with patch.object(oracle.subprocess, 'Popen', side_effect=record):
            with self.assertRaisesRegex(AssertionError, 'timed out'):
                oracle.invoke([sys.executable, '-c', 'import time; time.sleep(60)'], timeout=.15)
        self.assertLess(time.monotonic() - start, 4)
        self.assertIsNotNone(children[0].poll())
        self.assertTrue(children[0].stdout.closed)
        self.assertTrue(children[0].stderr.closed)

    def test_stop_kills_group_and_is_repeatable(self):
        p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'],
                             start_new_session=True)
        try:
            oracle.stop(p)
            oracle.stop(p)
            self.assertIsNotNone(p.poll())
            with self.assertRaises(ProcessLookupError):
                os.killpg(p.pid, 0)
        finally:
            oracle.stop(p)

    def test_startup_error_includes_stderr(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root)
            (p/'app.py').write_text('import sys\nprint("synthetic-startup-error",file=sys.stderr)\nsys.exit(3)\n')
            server = oracle.Server(p, p/'db')
            with self.assertRaisesRegex(AssertionError, 'startup stderr=.*synthetic-startup-error'):
                with server:
                    self.fail('broken server started')
            self.assertTrue(server.out.closed)
            self.assertTrue(server.err.closed)
            self.assertIsNotNone(server.p.poll())

    def test_startup_deadline_is_bounded(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root)
            (p/'app.py').write_text('import time\ntime.sleep(60)\n')
            server = oracle.Server(p, p/'db')
            start = time.monotonic()
            with patch.object(oracle, 'START_TIMEOUT', .15):
                with self.assertRaisesRegex(AssertionError, 'deadline'):
                    with server:
                        self.fail('silent server started')
            self.assertLess(time.monotonic() - start, 4)
            self.assertIsNotNone(server.p.poll())

    def test_output_budgets(self):
        for script in ['import os\nwhile True: os.write(1,b"x"*65536)',
                       'import os\nos.write(2,b"x"*2000000)']:
            with self.assertRaisesRegex(oracle.HarnessError,'byte budget'):
                oracle.invoke([sys.executable,'-c',script],timeout=2)
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)
            (p/'app.py').write_text('import os,time\nos.write(1,b"x"*20000)\ntime.sleep(60)')
            server=oracle.Server(p,p/'db')
            with self.assertRaisesRegex(oracle.HarnessError,'byte budget'):
                with server: self.fail('oversized startup accepted')
            self.assertTrue(server.out.closed);self.assertTrue(server.err.closed)

    def test_exceptional_setup_cleanup(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root);server=oracle.Server(p,p/'db')
            real=oracle.tempfile.TemporaryFile;opened=[]
            def allocate(*a,**kw):
                if opened: raise OSError('synthetic allocation failure')
                f=real(*a,**kw);opened.append(f);return f
            with patch.object(oracle.tempfile,'TemporaryFile',side_effect=allocate):
                with self.assertRaises(oracle.HarnessError): server.__enter__()
            self.assertTrue(opened[0].closed)
        import socket
        left,right=socket.socketpair()
        server=oracle.Server(Path('.'),Path('db'));server.base='http://127.0.0.1:1'
        try:
            with patch.object(oracle.socket,'create_connection',return_value=left), patch.object(oracle.threading.Timer,'start',side_effect=RuntimeError('timer setup')):
                with self.assertRaisesRegex(RuntimeError,'timer setup'): server.request('GET','/deals')
            self.assertEqual(left.fileno(),-1)
        finally: left.close();right.close()

    def test_race_really_uses_six_workers(self):
        self.assertEqual(sorted(oracle.race(lambda i: i)), list(range(6)))
        with self.assertRaisesRegex(RuntimeError, 'synthetic'):
            oracle.race(lambda i: (_ for _ in ()).throw(RuntimeError('synthetic')))


class EvaluationTests(unittest.TestCase):
    def test_independent_groups_continue_with_fresh_stores_and_seed(self):
        seen = []
        def failing(p, t, rng):
            rc, out, err = oracle.invoke([sys.executable, '-c', 'print("synthetic")'])
            oracle.equal(rc, 0)
            seen.append((t, rng.randrange(100000)))
            (t/'marker').write_text('synthetic')
            raise AssertionError('synthetic group failure')
        def later(p, t, rng):
            oracle.invoke([sys.executable, '-c', 'print("synthetic")'])
            oracle.require(not (t/'marker').exists(), 'not isolated')
            seen.append((t, rng.randrange(100000)))
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            with patch.dict(oracle.FACTORIES, {'selftest': lambda: [('first', failing), ('second', later)]}):
                results = oracle.evaluate('selftest', root, root/'artifacts', 14)
                self.assertEqual([r['passed'] for r in results], [False, True])
                self.assertEqual([r['outcome'] for r in results], ['fail','pass'])
                self.assertIn('synthetic group failure', results[0]['error'])
                first = [n for _, n in seen]
                seen.clear()
                oracle.evaluate('selftest', root, root/'artifacts', 14)
                self.assertEqual(first, [n for _, n in seen])
                self.assertNotEqual(seen[0][0], seen[1][0])
                self.assertTrue(all(not t.exists() for t, _ in seen))

    def test_broken_dummy_entrypoints_fail_every_real_group(self):
        # These are intentional error-only programs, not mock implementations.
        # Each command invocation appends to a marker, proving groups reached the entrypoint.
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            project = root/'project'
            project.mkdir()
            marker = project/'calls.txt'
            py = ('from pathlib import Path\nimport sys\n'
                  f'with Path({str(marker)!r}).open("a") as f: f.write("python synthetic\\n")\n'
                  'print("synthetic-dummy-error",file=sys.stderr)\n'
                  'print("{\\"error\\":\\"deliberately broken\\"}")\nsys.exit(2)\n')
            (project/'app.py').write_text(py)
            # No packages, network, or provider. Uses only Node's built-in filesystem.
            (project/'app.mjs').write_text(
                "import {appendFileSync} from 'node:fs';\n"
                f'appendFileSync({json.dumps(str(marker))}, "node synthetic\\n");\n'
                'console.error("synthetic-dummy-error");\n'
                'console.log(JSON.stringify({error:"deliberately broken"}));\nprocess.exit(2);\n')
            for case in ['crm', 'import', 'dispatch']:
                before = len(marker.read_text().splitlines()) if marker.exists() else 0
                reached=[]
                def checked(name, fn):
                    def run(p,t,rng):
                        n=len(marker.read_text().splitlines()) if marker.exists() else 0
                        try: fn(p,t,rng)
                        finally:
                            m=len(marker.read_text().splitlines()) if marker.exists() else 0
                            reached.append((name,m>n))
                    return name,run
                groups=[checked(name,fn) for name,fn in oracle.FACTORIES[case]()]
                with patch.dict(oracle.FACTORIES,{case:lambda:groups}):
                    results = oracle.evaluate(case, project, root/'artifacts', 27)
                self.assertTrue(all(hit for _,hit in reached),reached)
                self.assertEqual(len(reached),len(groups))
                self.assertTrue(all(r['outcome']=='fail' for r in results),results)
                self.assertGreaterEqual(len(results), 15)
                self.assertEqual(len(results), len(oracle.FACTORIES[case]()))
                self.assertTrue(all(r['passed'] is False and r.get('error') for r in results), results)
                after = len(marker.read_text().splitlines())
                self.assertGreaterEqual(after - before, len(results))
                self.assertEqual(len({r['name'] for r in results}), len(results))
            self.assertTrue(all('startup stderr' in r['error'] for r in oracle.evaluate('crm', project, root/'artifacts')))

    def test_unknown_case_is_reported(self):
        results = oracle.evaluate('bad', Path('.'), Path('.'))
        self.assertFalse(results[0]['passed'])
        self.assertEqual(results[0]['outcome'],'harness_error')
        self.assertIn('unknown case', results[0]['error'])

    def test_outcomes_and_new_groups(self):
        def raising(exc):
            def run(*args): raise exc
            return run
        groups=[('pass',lambda *args:None)]+[(name,raising(exc)) for name,exc in [
            ('fail',AssertionError('business')),('inconclusive',oracle.Inconclusive('window')),
            ('timeout',oracle.DeadlineExceeded('deadline')),('harness_error',oracle.HarnessError('budget'))]]
        with tempfile.TemporaryDirectory() as root:
            with patch.dict(oracle.FACTORIES,{'selftest':lambda:groups}):
                results=oracle.evaluate('selftest',Path(root),Path(root)/'artifacts')
        self.assertEqual([r['outcome'] for r in results],[n for n,_ in groups])
        self.assertEqual([r['passed'] for r in results],[True,False,False,False,False])
        self.assertIn('six-distinct-invoice-requests-one-deal',dict(oracle.crm_groups()))
        self.assertIn('six-concurrent-voids-once-only',dict(oracle.crm_groups()))
        self.assertIn('provider-conflicting-payload-two-local-stores',dict(oracle.dispatch_groups()))

    def test_cli_unknown_case_is_structured(self):
        rc,out,_=oracle.invoke([sys.executable,str(Path(oracle.__file__).resolve()),'unknown','.','.'])
        self.assertEqual(rc,1)
        self.assertEqual(json.loads(out)[0]['outcome'],'harness_error')

    def test_cli_prints_json_and_returns_failure(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            (root/'app.py').write_text('import sys; print("synthetic-cli-dummy",file=sys.stderr); sys.exit(1)')
            rc, out, err = oracle.invoke([sys.executable, str(Path(oracle.__file__).resolve()),
                'crm', str(root), str(root/'artifacts'), '--seed', '4'], timeout=15)
            self.assertEqual(rc, 1)
            results = json.loads(out)
            self.assertEqual(len(results), len(oracle.crm_groups()))
            self.assertTrue(all(not r['passed'] for r in results))


if __name__ == '__main__':
    unittest.main()
