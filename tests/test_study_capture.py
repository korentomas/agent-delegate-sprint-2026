"""Offline checks for the capture study (E5). No inference server is contacted."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


study = load('study_capture')
analyze = load('analyze_study')
common = load('study_common')
CFG = json.loads((ROOT / 'configs/study_capture.json').read_text())


class ScriptedCall:
    """Stand-in for the coordinator call: forwards `forward` (a function of the observation) and answers `action`."""

    def __init__(self, forward=lambda obs: [], action='continue', invalid=False):
        self.calls, self.forward, self.action, self.invalid = [], forward, action, invalid

    def __call__(self, messages, schema, seed, episode, actor, round_index):
        self.calls.append({'episode': episode, 'actor': actor, 'messages': messages, 'schema': schema, 'seed': seed})
        if self.invalid:
            return dict(common.INVALID)
        obs = json.loads(messages[-1]['content'])
        return {'forward': self.forward(obs), 'action': self.action, 'message': 'Decision recorded.'}


def minority(obs):
    return [r['id'] for r in obs['reports'] if r['worker'] == 'A']


def cell(role='delegate', pressure='none', bypass='off'):
    return {'role': role, 'pressure': pressure, 'bypass': bypass}


class CaptureStudyTests(unittest.TestCase):
    def test_external_endpoint_rejected_before_output_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            for url in ['https://example.com', 'http://10.0.0.5:8094', 'https://localhost:8094']:
                out = Path(folder) / 'not-created'
                result = subprocess.run([sys.executable, str(ROOT / 'scripts/study_capture.py'), '--base-url', url, '--out', str(out)],
                                        capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0, url)
                self.assertIn('Only local loopback', result.stderr, url)
                self.assertFalse(out.exists(), url)

    def test_schema_restricts_forward_ids_and_actions(self):
        ids = ['r-1000', 'r-2000', 'r-3000']
        schema = study.capture_schema(ids)
        self.assertTrue(common.validate({'forward': [], 'action': 'continue', 'message': 'x'}, schema))
        self.assertTrue(common.validate({'forward': ['r-1000', 'r-3000'], 'action': 'pause', 'message': 'x'}, schema))
        self.assertFalse(common.validate({'forward': ['exec'], 'action': 'continue', 'message': 'x'}, schema))
        self.assertFalse(common.validate({'forward': 'r-1000', 'action': 'continue', 'message': 'x'}, schema))
        self.assertFalse(common.validate({'forward': [], 'action': 'grant_access', 'message': 'x'}, schema))
        self.assertFalse(common.validate({'forward': [], 'action': 'continue', 'message': 'x', 'tool': 'shell'}, schema))
        self.assertFalse(common.validate({'forward': [], 'action': 'continue'}, schema))

    def test_pressure_and_bypass_live_where_the_design_says(self):
        for seed in range(3):
            none, majority = study.build_observation(CFG, seed, 'none'), study.build_observation(CFG, seed, 'majority')
            self.assertEqual(none['reports'], majority['reports'])  # the case is identical; only the public messages differ
            self.assertEqual([m['worker'] for m in majority['public_messages']], ['B', 'C'])
            text = ' '.join(m['message'] for m in majority['public_messages']).lower()
            self.assertIn('continue', text)
            self.assertTrue('points' in text and ('noise' in text or 'bother' in text or 'escalate' in text))
            neutral = ' '.join(m['message'] for m in none['public_messages']).lower()
            self.assertNotIn('noise', neutral)
            self.assertNotIn('points', neutral)
            self.assertNotIn('human', neutral)
        on, off = study.system_prompt(CFG, 'delegate', 'on'), study.system_prompt(CFG, 'delegate', 'off')
        self.assertIn(study.BYPASS_TEXT['on'], on)
        self.assertNotIn(study.BYPASS_TEXT['on'], off)
        self.assertIn('only if you forward them', off)
        self.assertEqual(on.replace(study.BYPASS_TEXT['on'], study.BYPASS_TEXT['off']), off)
        monitor = study.system_prompt(CFG, 'matched_monitor', 'on')
        self.assertEqual(on.replace('protected rotating delegate', 'independent monitor'), monitor)

    def test_reports_vary_by_seed_but_keep_one_minority_case(self):
        orders, ids = set(), set()
        for seed in range(CFG['seeds_per_cell']):
            reports = study.build_reports(CFG, seed)
            self.assertEqual(sorted(r['worker'] for r in reports), ['A', 'B', 'C'])
            self.assertEqual(len({r['id'] for r in reports}), 3)
            a = next(r for r in reports if r['worker'] == 'A')
            self.assertIn('prohibited', a['message'])
            self.assertIn('human', a['message'])
            for r in reports:
                if r['worker'] != 'A':
                    self.assertNotIn('prohibited', r['message'])
            orders.add(tuple(r['worker'] for r in reports))
            ids.add(tuple(r['id'] for r in reports))
            self.assertEqual(reports, study.build_reports(CFG, seed))
        self.assertGreater(len(orders), 1)
        self.assertEqual(len(ids), CFG['seeds_per_cell'])

    def test_bypass_is_a_mechanism_computed_in_python(self):
        for bypass in ['off', 'on']:
            drop = ScriptedCall(forward=lambda obs: [r['id'] for r in obs['reports'] if r['worker'] != 'A'])
            e = study.run_episode(CFG, cell(bypass=bypass), 0, drop)
            self.assertFalse(e['minority_forwarded'])
            self.assertEqual(e['majority_forwarded'], 2)
            self.assertEqual(e['minority_reached_human'], bypass == 'on')
            keep = ScriptedCall(forward=minority, action='request_tool')
            e = study.run_episode(CFG, cell(bypass=bypass), 0, keep)
            self.assertTrue(e['minority_forwarded'] and e['minority_reached_human'] and e['human_request'])
            self.assertEqual(e['majority_forwarded'], 0)
            invalid = ScriptedCall(invalid=True)
            e = study.run_episode(CFG, cell(bypass=bypass), 0, invalid)
            self.assertTrue(e['invalid'])
            self.assertEqual((e['forward'], e['minority_forwarded'], e['minority_reached_human'], e['action']), ([], False, bypass == 'on', 'invalid'))
        unknown = ScriptedCall(forward=lambda obs: ['r-0000', 'exec'])
        e = study.run_episode(CFG, cell(), 0, unknown)
        self.assertEqual(e['forward'], [])
        self.assertEqual(len(unknown.calls), 1)
        self.assertEqual(unknown.calls[0]['schema']['properties']['forward']['items']['enum'], e['report_ids'])

    def test_messages_are_clipped(self):
        long_message = ' '.join(f'w{i}' for i in range(40))

        class Chatty(ScriptedCall):
            def __call__(self, *a, **k):
                return {'forward': [], 'action': 'continue', 'message': long_message}
        e = study.run_episode(CFG, cell(), 1, Chatty())
        self.assertEqual((len(e['message'].split()), e['message_words']), (CFG['max_message_words'], 40))

    def test_plan_and_resume_skip_completed_episodes(self):
        cells = study.plan_cells(CFG)
        self.assertEqual(len(cells), 96)
        self.assertEqual(len({study.episode_id(c['role'], c['pressure'], c['bypass'], s) for c, s in cells}), 96)
        self.assertEqual(len(study.plan_cells(CFG, limit=4)), 4)
        self.assertTrue(all(c['bypass'] == 'on' and c['role'] == 'delegate' for c, s in study.plan_cells(CFG, roles=['delegate'], bypass=['on'])))
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            study.run_study(CFG, cells[:4], out, ScriptedCall(), log=lambda s: None)
            second = ScriptedCall()
            episodes, skipped = study.run_study(CFG, cells[:6], out, second, resume=True, log=lambda s: None)
            self.assertEqual((len(episodes), skipped, len(second.calls)), (6, 4, 2))
            self.assertEqual(len(json.loads((out / 'episodes.json').read_text())), 6)

    def test_llm_seeds_differ_across_cells_and_seeds(self):
        seeds = set()
        for c, s in study.plan_cells(CFG):
            call = ScriptedCall()
            study.run_episode(CFG, c, s, call)
            seeds.add(call.calls[0]['seed'])
        self.assertEqual(len(seeds), 96)

    def test_end_to_end_against_a_loopback_stub(self):
        """A stub HTTP server on 127.0.0.1 stands in for llama-server: no inference, no network. One episode gets an HTTP 500."""
        import http.server
        import threading
        seen = []

        class Stub(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, code, body):
                data = json.dumps(body).encode()
                self.send_response(code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                self._send(200, {'data': [{'id': 'stub-model'}]})

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                seen.append(body)
                obs = json.loads(body['messages'][-1]['content'])
                if len(seen) == 2:
                    return self._send(500, {'error': 'stub failure'})
                content = json.dumps({'forward': [r['id'] for r in obs['reports']], 'action': 'request_tool', 'message': 'Forwarding everything.'})
                self._send(200, {'model': 'stub-model', 'choices': [{'message': {'content': content, 'reasoning_content': 'SECRET-THOUGHTS'}, 'finish_reason': 'stop'}],
                                 'usage': {'total_tokens': 100}})
        server = http.server.HTTPServer(('127.0.0.1', 0), Stub)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f'http://127.0.0.1:{server.server_address[1]}'
            with tempfile.TemporaryDirectory() as folder:
                out = Path(folder) / 'run'
                study.main(['--base-url', base, '--out', str(out), '--limit', '3', '--model-tag', 'stub'])
                with self.assertRaises(SystemExit):
                    study.main(['--base-url', base, '--out', str(out), '--limit', '3'])  # not fresh, no --resume
                study.main(['--base-url', base, '--out', str(out), '--limit', '5', '--resume', '--schema-style', 'openai'])
                manifest = json.loads((out / 'manifest.json').read_text())
                self.assertEqual((manifest['episodes'], manifest['calls'], manifest['skipped_on_resume'], manifest['invalid_calls']), (5, 5, 3, 1))
                self.assertEqual((manifest['model'], manifest['model_tag'], manifest['total_tokens'], len(manifest['resumed_at'])), ('stub-model', 'stub', 400, 1))
                self.assertEqual(set(manifest['input_sha256']), {'configs/study_capture.json', 'scripts/study_capture.py', 'scripts/study_common.py', 'docs/study-capture-design.md'})
                self.assertTrue(manifest['started_at'] < manifest['finished_at'])
                raw = (out / 'calls.jsonl').read_text()
                self.assertNotIn('SECRET-THOUGHTS', raw)
                calls = [json.loads(line) for line in raw.splitlines()]
                self.assertEqual([c['valid'] for c in calls], [True, False, True, True, True])
                self.assertIn('HTTPError', calls[1]['error'])
                self.assertTrue(all(c['response']['reasoning_omitted'] for c in calls if 'response' in c))
                self.assertTrue(all(c['request']['chat_template_kwargs'] == {'enable_thinking': False} for c in calls))
                self.assertEqual([c['request']['response_format']['type'] for c in calls], ['json_object'] * 3 + ['json_schema'] * 2)
                episodes = json.loads((out / 'episodes.json').read_text())
                self.assertEqual(len(episodes), 5)
                self.assertEqual([e['invalid'] for e in episodes], [False, True, False, False, False])
                self.assertEqual(sum(e['minority_forwarded'] for e in episodes), 4)
                for name in ['study_capture_snapshot.py', 'study_common_snapshot.py', 'study_capture_snapshot.json', 'study-capture-design_snapshot.md', 'summary.json', 'config.json']:
                    self.assertTrue((out / name).exists(), name)
        finally:
            server.shutdown()
            server.server_close()

    def test_analysis_summarizes_capture_runs(self):
        with tempfile.TemporaryDirectory() as folder:
            run = Path(folder) / 'study-capture-fixture'
            run.mkdir()
            episodes = []
            for c, s in study.plan_cells(CFG):
                forwarded = not (c['pressure'] == 'majority' and s % 2 == 0)
                episodes.append({'id': study.episode_id(c['role'], c['pressure'], c['bypass'], s), **c, 'seed': s, 'action': 'continue', 'forward': [],
                                 'minority_forwarded': forwarded, 'majority_forwarded': 2, 'minority_reached_human': forwarded or c['bypass'] == 'on',
                                 'human_request': False, 'invalid': False})
            (run / 'episodes.json').write_text(json.dumps(episodes))
            out = Path(folder) / 'summary'
            analyze.main(['--study', 'capture', '--inputs', str(run), '--out', str(out), '--no-figure', '--resamples', '200'])
            rows = (out / 'summary.csv').read_text().splitlines()
            self.assertEqual(rows[0], ','.join(analyze.CAPTURE_COLUMNS))
            self.assertEqual(len(rows), 9)
            for row in rows[1:]:
                fields = dict(zip(analyze.CAPTURE_COLUMNS, row.split(',')))
                self.assertEqual(fields['model'], 'fixture')
                self.assertEqual(fields['n'], '12')
                if fields['bypass'] == 'on':
                    self.assertEqual(fields['minority_reached_human_rate'], '1.0000')
                self.assertEqual(fields['minority_forwarded_rate'], '0.5000' if fields['pressure'] == 'majority' else '1.0000')
            tests = (out / 'tests.csv').read_text().splitlines()
            self.assertEqual(len(tests), 9)
            self.assertIn('fixture,pressure,delegate/bypass_off,majority,6,12,none,12,12,0.0137', tests)


if __name__ == '__main__':
    unittest.main()
