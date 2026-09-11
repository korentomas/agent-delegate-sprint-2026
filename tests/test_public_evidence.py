"""Verify attribution safeguards and the public evidence inventory offline."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('public_evidence', ROOT / 'scripts/verify_public_evidence.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PublicEvidenceTests(unittest.TestCase):
    def test_inherited_messages_are_not_attributed_to_latest_editor(self):
        previous = 'Earlier author: I disagree.\n'
        current = previous + 'Later author: noted.\n'
        added = module.added_text(current, previous)
        self.assertNotIn('I disagree', added)
        self.assertIn('Later author: noted.', added)

    def test_every_excerpt_has_a_matching_verification_record(self):
        data = json.loads((ROOT / 'data/grounded_cases.json').read_text())
        checked = json.loads((ROOT / 'data/verified-excerpts.json').read_text())['excerpts']
        actual = []
        for case in data['cases']:
            self.assertIn(case['source_id'], data['sources'])
            self.assertTrue(case['not_established'] and case['alternative'] and case['observation_assumption'])
            for i, step in enumerate(case['steps']):
                self.assertIn(step['kind'], ['public_message', 'published_cot', 'investigator_reconstruction'])
                if step['kind'] == 'investigator_reconstruction':
                    self.assertEqual(step['quotes'], [])
                for quote in step['quotes']:
                    actual.append((case['id'], i, hashlib.sha256(quote.encode()).hexdigest()))
        self.assertCountEqual(actual, [(r['case_id'], r['step'], r['excerpt_sha256']) for r in checked])

    def test_brief_quotes_and_uncertain_times_are_explicit(self):
        data = json.loads((ROOT / 'data/grounded_cases.json').read_text())
        counts = {s: 0 for s in data['sources']}
        for case in data['cases']:
            self.assertTrue(case['time_note'])
            if case['source_id'] != 'wiki':
                self.assertIsNone(case['time'])
            for step in case['steps']:
                counts[case['source_id']] += sum(len(q.split()) for q in step['quotes'])
        self.assertTrue(all(n <= 25 for n in counts.values()), counts)

    def test_every_casebook_source_is_registered(self):
        data = json.loads((ROOT / 'data/grounded_cases.json').read_text())
        registry = json.loads((ROOT / 'data/sources.json').read_text())
        urls = {entry['url'] for entry in registry.values()}
        for key, source in data['sources'].items():
            self.assertTrue(key in registry or source['url'] in urls, key)
        self.assertIn('metr', registry)


if __name__ == '__main__':
    unittest.main()
