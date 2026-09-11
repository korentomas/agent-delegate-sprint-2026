"""Check local-pilot execution boundaries and consistency of released observations."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('local_pilot', ROOT / 'scripts/local_pilot.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class LocalPilotTests(unittest.TestCase):
    def test_external_endpoint_rejected_before_output_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / 'not-created'
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/local_pilot.py'),
                                     '--base-url', 'https://example.com', '--out', str(out)],
                                    capture_output=True, text=True, timeout=5)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Only local loopback', result.stderr)
            self.assertFalse(out.exists())

    def test_generated_code_cannot_be_an_action(self):
        for action in ['exec', 'curl example.com', 'submit; open_file', {'tool': 'shell'}]:
            self.assertFalse(pilot.validate_choice({'action': action, 'answer': None, 'message': 'x'}))
        self.assertTrue(pilot.validate_choice({'action': 'use_answer_key', 'answer': None, 'message': 'Mock only'}))

    def test_released_episode_actions_match_raw_model_decisions(self):
        for folder in (ROOT / 'results').glob('local-pilot-*'):
            calls = [json.loads(line) for line in (folder / 'calls.jsonl').read_text().splitlines()]
            episodes = json.loads((folder / 'episodes.json').read_text())
            self.assertEqual(len(calls), json.loads((folder / 'manifest.json').read_text())['calls'])
            for episode in episodes:
                decisions = [c['decision'] for c in calls if c['episode'] == episode['id']]
                events = [e for e in episode['events'] if e['kind'] in ['worker_choice', 'coordinator_choice']]
                self.assertEqual(len(decisions), len(events))
                for decision, event in zip(decisions, events):
                    self.assertEqual(decision['action'], event['action'])
                    self.assertEqual(decision['message'], event['message'])
                self.assertEqual(sum(e['action'] == 'use_answer_key' for e in events), episode['unsafe_choices'])


if __name__ == '__main__':
    unittest.main()
