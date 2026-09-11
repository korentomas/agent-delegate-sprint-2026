import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('case_prompts', ROOT / 'scripts/export_case_prompts.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CasePromptTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'data/grounded_cases.json').read_text())
        self.config = json.loads((ROOT / 'configs/grounded_replay.json').read_text())

    def test_all_controls_receive_identical_evidence(self):
        prompts = list(module.build_prompts(self.data, self.config))
        self.assertEqual(len(prompts), 44)
        for i in range(0, len(prompts), 4):
            self.assertEqual(len({p['input_sha256'] for p in prompts[i:i+4]}), 1)

    def test_future_suffix_and_our_recommendation_do_not_change_first_prompt(self):
        before = next(module.build_prompts(self.data, self.config))
        changed = copy.deepcopy(self.data)
        case = changed['cases'][0]
        case['outcome'] = case['intervention'] = case['synthetic_reply'] = 'SHOULD NEVER APPEAR'
        case['steps'][1]['context'] = 'FUTURE SECRET'
        self.assertEqual(before, next(module.build_prompts(changed, self.config)))


if __name__ == '__main__':
    unittest.main()
