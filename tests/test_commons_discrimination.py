import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from analyze_commons_discrimination import flags, validity_pairs


def episode(valid, events, seed=100):
    return {'institution': 'quarantine', 'seed': seed, 'valid': valid,
            'family': 'threshold', 'events': events}


class DiscriminationTests(unittest.TestCase):
    def test_blocked_reuse_remains_an_attempt(self):
        e = episode(False, [{'kind': 'worker', 'action': 'reuse', 'accepted': False, 'report': False}])
        self.assertEqual(flags(e), {'reuse': True, 'report': False, 'first_report': False})

    def test_later_report_does_not_become_first_contact(self):
        e = episode(False, [{'kind': 'worker', 'action': 'invalid', 'report': False},
                            {'kind': 'advisor', 'action': 'reuse'},
                            {'kind': 'worker', 'action': 'inspect', 'report': True}])
        self.assertEqual(flags(e), {'reuse': False, 'report': True, 'first_report': False})

    def test_validity_pair_direction_and_denominator(self):
        valid = episode(True, [{'kind': 'worker', 'action': 'invalid', 'report': False}])
        faulty = episode(False, [{'kind': 'worker', 'action': 'inspect', 'report': True}])
        self.assertEqual(validity_pairs([faulty, valid], 'report')[0]['faulty_minus_valid'], 1)
        with self.assertRaises(ValueError): validity_pairs([valid], 'report')
        with self.assertRaises(ValueError): validity_pairs([valid, valid, faulty], 'report')


if __name__ == '__main__': unittest.main()
