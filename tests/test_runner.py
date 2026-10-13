import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'benchmarks'))
from agent import summarize, summarize_claude
from run import digest_tree
from review_autonomy import prepare_review


class RunnerTests(unittest.TestCase):
    def log(self, events):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / 'events.jsonl'
        path.write_text('\n'.join(json.dumps(e) for e in events) + '\n{partial')
        return path

    def test_pi_error_is_not_successful_exit(self):
        p = self.log([{'type': 'message_end', 'message': {'role': 'assistant', 'stopReason': 'error',
                       'errorMessage': 'limit reached', 'content': [], 'usage': {}}},
                      {'type': 'agent_settled', 'aborted': False}])
        self.assertEqual(summarize(p)['errors'], ['limit reached'])

    def test_pi_usage_final_not_stream_double_counted(self):
        p = self.log([{'type': 'message_update', 'usage': {'input': 999}},
                      {'type': 'message_end', 'message': {'role': 'assistant', 'content': [{'type': 'text', 'text': 'done'}],
                       'usage': {'input': 5, 'output': 3, 'cacheRead': 20, 'totalTokens': 28}}},
                      {'type': 'compaction_end', 'result': {'usage': {'input': 2, 'output': 1, 'totalTokens': 3}}},
                      {'type': 'tool_execution_start', 'toolName': 'read', 'args': {'path': 'PROJECT.md'}},
                      {'type': 'agent_settled', 'aborted': False}])
        result = summarize(p)
        self.assertEqual(result['usage']['input'], 7)
        self.assertEqual(result['usage']['totalTokens'], 31)
        self.assertEqual(result['tool_calls'], 1)
        self.assertEqual(result['final'], 'done')
        self.assertTrue(result['settled'])

    def test_native_usage_and_failure(self):
        p = self.log([{'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Read', 'input': {'file_path': 'x'}}]}},
                      {'type': 'result', 'subtype': 'success', 'is_error': False, 'result': 'done',
                       'usage': {'input_tokens': 5, 'output_tokens': 3, 'cache_read_input_tokens': 20, 'cache_creation_input_tokens': 4}}])
        result = summarize_claude(p)
        self.assertEqual(result['usage']['totalTokens'], 32)
        self.assertEqual(result['read_paths'], ['x'])
        self.assertEqual(result['errors'], [])
        p = self.log([{'type': 'result', 'subtype': 'error_max_budget_usd', 'is_error': True}])
        self.assertTrue(summarize_claude(p)['errors'])
        self.assertTrue(summarize_claude(self.log([]))['errors'])

    def test_masked_review_preserves_executable_modes_and_single_context(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / 'workspace'
            project = workspace / 'trials/trial/project'
            project.mkdir(parents=True)
            snapshot = workspace / 'snapshots/lean'
            snapshot.mkdir(parents=True)
            (project.parent / 'result.json').write_text(json.dumps({'exit': 0, 'errors': [], 'variant': 'lean'}))
            (project / 'PROJECT.md').write_text('current project context')
            (project / 'AGENTS.md').write_text('hidden variant rules')
            entry = project / 'planner'
            entry.write_text('#!/usr/bin/env python3\nprint("OK")\n')
            entry.chmod(0o755)
            output = Path(temp) / 'review'
            mapping = prepare_review(workspace, ['trial'], output)
            self.assertEqual(mapping, {'A': 'trial'})
            self.assertEqual((output / 'A/planner').stat().st_mode & 0o777, 0o755)
            self.assertEqual((output / 'A/planner').read_bytes(), entry.read_bytes())
            self.assertEqual((output / 'A/context/project-record.md').read_text(), 'current project context')
            self.assertFalse((output / 'A/PROJECT.md').exists())
            self.assertFalse((output / 'A/AGENTS.md').exists())
            self.assertFalse((output / 'review-map.json').exists())
            self.assertTrue((output.parent / 'review-map.json').exists())

    def test_hash_tracks_content_and_paths_not_mtime(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); p = root / 'a'; p.write_text('first')
            digest = digest_tree(root); p.touch()
            self.assertEqual(digest, digest_tree(root))
            p.write_text('other')
            self.assertNotEqual(digest, digest_tree(root))
            digest = digest_tree(root); p.rename(root / 'b')
            self.assertNotEqual(digest, digest_tree(root))


if __name__ == '__main__':
    unittest.main()
