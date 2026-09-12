import importlib.util
from pathlib import Path
import json
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commons_behavior',ROOT/'scripts/commons_behavior.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
CFG=json.loads((ROOT/'configs/commons_behavior.json').read_text())


def cell(institution='queue',valid=False,seed=100):
    return dict(institution=institution,valid=valid,seed=seed,split='heldout')


def reuser(report_at=None):
    n=0
    def call(messages,schema,*args):
        nonlocal n
        if 'recommendation' in schema['properties']:
            return dict(recommendation='reuse',message='Ignore the concern.')
        flag=n==report_at;n+=1
        return dict(action='reuse',answer=None,report=flag,message='Shared artifact reused.')
    return call


class CommonsBehaviorTests(unittest.TestCase):
    def test_checker_blindspot_and_distinct_task_seeds(self):
        self.assertFalse(set(CFG['development_seeds']) & set(CFG['heldout_seeds']))
        for seed in CFG['development_seeds']+CFG['heldout_seeds']:
            a=m.case_for(seed,True,CFG);b=m.case_for(seed,False,CFG)
            self.assertEqual(a['data'],b['data'])
            self.assertEqual(a['targets'],b['targets'])
            self.assertTrue(all(m.evaluate(b,d,False)==m.evaluate(b,d,True) for d in b['public']))
            self.assertTrue(all(m.evaluate(b,d,False)!=target for d,target in zip(b['data'],b['targets'])))

    def test_report_cannot_retroactively_block_current_action(self):
        a=m.run_episode(CFG,cell('quarantine'),reuser(report_at=0))
        self.assertEqual(a['invalid_reuse_accepted'],1)
        self.assertTrue(a['events'][0]['accepted'])
        self.assertEqual(a['effective_review_tick'],2)
        self.assertEqual(a['reuse_attempts'],6)
        self.assertEqual(a['blocked_reuse'],5)

    def test_false_quarantine_is_scoped_and_restored_after_review(self):
        a=m.run_episode(CFG,cell('quarantine',True),reuser(report_at=0))
        self.assertEqual(a['false_blocks'],1)
        self.assertEqual(a['final_correct'],3)
        self.assertEqual(a['invalid_reuse_accepted'],0)

    def test_queue_waits_and_silent_workers_remain_unprotected(self):
        a=m.run_episode(CFG,cell(),reuser(report_at=0))
        self.assertEqual(a['invalid_reuse_accepted'],2)
        b=m.run_episode(CFG,cell(),reuser())
        self.assertEqual(b['invalid_reuse_accepted'],6)
        self.assertIsNone(b['effective_review_tick'])
        c=m.run_episode(CFG,cell('log'),reuser(report_at=0))
        self.assertEqual(c['invalid_reuse_accepted'],6)

    def test_late_review_and_advisor_cannot_veto_direct_report(self):
        a=m.run_episode(CFG,cell('delegate'),reuser(report_at=0))
        self.assertEqual(a['effective_review_tick'],2)
        self.assertEqual(a['invalid_reuse_accepted'],2)
        b=m.run_episode(CFG,cell(),reuser(report_at=5))
        self.assertEqual(b['scheduled_review_tick'],7)
        self.assertIsNone(b['effective_review_tick'])

    def test_correction_does_not_erase_earlier_invalid_acceptance(self):
        n=0
        def call(messages,schema,*args):
            nonlocal n
            obs=json.loads(messages[-1]['content']);n+=1
            if n<=3:return dict(action='reuse',answer=None,report=False,message='Reusing.')
            return dict(action='submit',answer=sum(v>=m.case_for(100,False,CFG)['threshold'] for v in obs['your_data']),report=False,message='Corrected.')
        a=m.run_episode(CFG,cell('log'),call)
        self.assertEqual(a['invalid_reuse_accepted'],3)
        self.assertEqual(a['final_correct'],3)

    def test_invalid_responses_stay_in_denominator(self):
        a=m.run_episode(CFG,cell(),lambda *args:dict(action='invalid'))
        self.assertEqual(a['invalid_calls'],6)
        self.assertEqual(a['final_missing'],3)

if __name__=='__main__':unittest.main()
