"""Robustness sweeps: the committed CSV reproduces and the preregistered claims of docs/sweeps-design.md hold."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sweeps',ROOT/'scripts/sweeps.py');sweeps=importlib.util.module_from_spec(spec);spec.loader.exec_module(sweeps)
CFG=json.loads((ROOT/'configs/experiment.json').read_text())
SCENARIOS=json.loads((ROOT/'data/scenarios.json').read_text())
COMMITTED=ROOT/'results/sweeps/sweeps.csv'
SUMMARY=(ROOT/'results/sweeps/summary.md').read_text()

class SweepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rows=sweeps.read_rows(COMMITTED)
    def test_csv_reproduces_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as d:
            sweeps.main(['--out',d,'--no-figure'])
            self.assertEqual((Path(d)/'sweeps.csv').read_bytes(),COMMITTED.read_bytes())
    def test_grid_shape(self):
        kinds=sweeps.hidden_kinds(SCENARIOS);self.assertEqual(kinds,('concealment','escalation','shadow_channel'))
        levels=sweeps.coverage_levels(kinds);self.assertEqual(len(levels),2**len(kinds)+2)
        self.assertEqual(len(self.rows),8*6*11*4*len(levels)+8*6*11*4)
        self.assertTrue(all(not r['capture'] and r['bypass'] for r in self.rows))
    def test_claim_a_gates_hold_at_every_latency(self):
        self.assertEqual(sweeps.check_a(self.rows),[]);self.assertIn('every latency 0-10, pause length and rotation period: **held**',SUMMARY)
    def test_claim_b_delegate_equals_matched_monitor(self):
        self.assertEqual(sweeps.check_b(self.rows),[]);self.assertIn('except audit_records, all 3,872 matched cells: **held**',SUMMARY)
        # The exemption is real: the delegate logs rotation records that the matched monitor does not.
        d=next(r for r in self.rows if r['condition']=='delegate');m=next(r for r in self.rows if r['condition']=='matched_monitor' and sweeps.key(r)==sweeps.key(d))
        self.assertGreater(d['audit_records'],m['audit_records'])
    def test_claim_c_latency_monotone_and_false_pauses_flat(self):
        self.assertEqual(sweeps.check_c(self.rows),[]);self.assertIn('false pauses constant in latency, per stratum: **held**',SUMMARY)
    def test_legacy_labels_equal_subset_twins(self):
        self.assertEqual(sweeps.check_equivalences(self.rows,sweeps.hidden_kinds(SCENARIOS)),[])
    def test_main_slice_reproduces_frozen_results(self):
        n,violations=sweeps.check_main_slice(self.rows,ROOT/'results/final/runs.csv',CFG)
        self.assertEqual((n,violations),(288,[]))
    def test_rotation_period_is_cosmetic(self):
        rot=[r for r in self.rows if r['grid']=='latency_rotation'];groups={}
        for r in rot:groups.setdefault((r['scenario'],r['condition'],r['latency']),set()).add(tuple(r[k] for k in sweeps.OUTCOMES if k!='audit_records'))
        self.assertEqual(len(groups),8*6*11);self.assertTrue(all(len(v)==1 for v in groups.values()))
    def test_coverage_key_default_is_inert(self):
        """Without gate_coverage_sets an unknown label behaves as missing_hidden, as before the key existed."""
        s=next(x for x in SCENARIOS if x['id']=='hidden_violation')
        a,_=sweeps.run_case(s,'gates_only',2,False,True,'missing_hidden',CFG);b,_=sweeps.run_case(s,'gates_only',2,False,True,'hidden:none',CFG)
        for k in sweeps.OUTCOMES:self.assertEqual(a[k],b[k])
        c,_=sweeps.run_case(s,'gates_only',2,False,True,'hidden:none',dict(CFG,gate_coverage_sets={'hidden:none':['shadow_channel','concealment','escalation']}))
        self.assertEqual(c['executed_harm'],0)
if __name__=='__main__':unittest.main()
