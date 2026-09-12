import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('analyze_commons',Path(__file__).resolve().parents[1]/'scripts/analyze_commons_behavior.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class PairedAnalysisTests(unittest.TestCase):
    def test_stratified_bootstrap_preserves_family_weights(self):
        lo,hi=a.paired_interval([('threshold',1)]*6+[('distinct',-1)]*6,'fixed',100)
        self.assertEqual((lo,hi),(0,0))

    def test_pairing_is_by_seed_not_row_order(self):
        records=[]
        for model in a.MODELS:
            for valid in [False,True]:
                for arm in a.ARMS:
                    for seed in [0,1]:
                        records.append(dict(model=model,valid=valid,institution=arm,seed=seed,family='threshold' if seed==0 else 'distinct',any_invalid_reuse=seed,reported=seed,final_correct=seed,invalid_reuse_accepted=seed,false_blocks=0))
        out=a.contrasts(list(reversed(records)))
        self.assertTrue(all(x['difference']==0 and x['bootstrap_lo']==0 and x['bootstrap_hi']==0 for x in out))
        with self.assertRaises(ValueError):a.contrasts(records[1:])

if __name__=='__main__':unittest.main()
