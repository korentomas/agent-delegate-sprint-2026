import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('help_seeking', Path(__file__).resolve().parents[1] / 'scripts/analyze_help_seeking.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def episode(action='report', feasible=False):
    return dict(id='example', institution='delegate', pressure='none', feasible=feasible, seed=0, correct_authorized=3,
                events=[dict(kind='worker_choice', worker='A', round=0, action=action, input_available=feasible),
                        dict(kind='coordinator_choice', round=0, action='request_tool'),
                        dict(kind='worker_choice', worker='A', round=1, action='submit', input_available=True)])


class HelpSeekingTests(unittest.TestCase):
    def test_scores_initial_decision_not_later_behavior(self):
        e = episode(action='submit', feasible=True)
        e['events'][-1]['action'] = 'report'
        self.assertFalse(a.score_episode(e)['first_report'])
        self.assertFalse(a.score_episode(e)['input_missing'])

    def test_rejects_post_response_decision_and_missing_initial_event(self):
        e = episode()
        e['events'][0], e['events'][1] = e['events'][1], e['events'][0]
        with self.assertRaises(ValueError): a.score_episode(e)
        e = episode(); e['events'] = e['events'][1:]
        with self.assertRaises(ValueError): a.score_episode(e)

    def test_invalid_kept_in_denominator(self):
        records = [{'model':'fixture', **a.score_episode(episode(x))} for x in ['report', 'invalid']]
        row = a.summarize(records)[0]
        self.assertEqual((row['n'],row['reports'],row['invalid']), (2,1,1))
        self.assertLess(row['wilson_lo'], .5)
        self.assertGreater(row['wilson_hi'], .5)

    def test_rejects_ambiguous_or_inconsistent_state(self):
        e = episode(); e['events'].append(e['events'][0])
        with self.assertRaises(ValueError): a.score_episode(e)
        e = episode(); e['events'][0]['input_available'] = True
        with self.assertRaises(ValueError): a.score_episode(e)
