import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('commons', Path(__file__).resolve().parents[1] / 'scripts/commons_response.py')
commons = importlib.util.module_from_spec(spec)
spec.loader.exec_module(commons)


class CommonsResponseTests(unittest.TestCase):
    def case(self, control, delay=2, visible=True, suppressed=False, bypass=True, invalid=True):
        return commons.run_case(control, delay, visible, suppressed, bypass, invalid)

    def test_receipt_is_not_enforcement(self):
        log = self.case('log_only')
        self.assertEqual(log['delivery_tick'], 1)
        self.assertIsNone(log['effective_decision_tick'])
        self.assertEqual(log['invalid_accepted'], 6)
        self.assertEqual(self.case('review_queue')['invalid_accepted'], 3)

    def test_delayed_review_does_not_erase_history(self):
        r = self.case('review_queue', delay=6)
        self.assertEqual(r['decision_tick'], 7)
        self.assertIsNone(r['effective_decision_tick'])
        self.assertEqual(r['invalid_accepted'], 6)
        self.assertEqual(self.case('review_queue', delay=0)['invalid_accepted'], 1)

    def test_quarantine_cost_and_release(self):
        self.assertEqual(self.case('quarantine')['invalid_accepted'], 1)
        good = self.case('quarantine', invalid=False)
        self.assertEqual((good['false_blocks'], good['valid_completed']), (2, 4))
        self.assertEqual(self.case('quarantine', delay=0, invalid=False)['false_blocks'], 0)

    def test_bypass_cannot_recover_an_unobserved_report(self):
        self.assertEqual(self.case('quarantine', suppressed=True, bypass=False)['invalid_accepted'], 6)
        self.assertEqual(self.case('quarantine', suppressed=True)['invalid_accepted'], 1)
        self.assertEqual(self.case('quarantine', visible=False)['invalid_accepted'], 6)

    def test_gate_independent_of_reporting_and_institution_match(self):
        for delay in (0, 2, 6):
            for visible in (False, True):
                gate = self.case('verified_gate', delay, visible, suppressed=True, bypass=False)
                self.assertEqual(gate['invalid_accepted'], 0)
                self.assertEqual(self.case('verified_gate', delay, visible, invalid=False)['valid_completed'], 6)
                rows = [self.case(c, delay, visible) for c in ('review_queue', 'delegate', 'matched_monitor')]
                for row in rows:
                    row.pop('control')
                self.assertEqual(rows[0], rows[1])
                self.assertEqual(rows[1], rows[2])
