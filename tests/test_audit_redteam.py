"""Audit red team: tamper classes are deterministic, the committed matrix reproduces, and the preregistered claims of
docs/audit-redteam-design.md hold (a failed claim would be asserted as failed here and named in matrix.md)."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audit_redteam',ROOT/'scripts/audit_redteam.py');rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
CFG=json.loads((ROOT/'configs/experiment.json').read_text())
FINAL=ROOT/'results/final';COMMITTED=ROOT/'results/audit-redteam/matrix.csv';MD=(ROOT/'results/audit-redteam/matrix.md').read_text()

class AuditRedTeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=rt.read_rows(COMMITTED);cls.run_id=rt.sample(CFG)[0]
        cls.clean=rt.load(FINAL/'traces'/f'{cls.run_id}.jsonl');cls.partner=rt.load(FINAL/'traces'/f'{rt.partner_id(cls.run_id)}.jsonl')
    def test_sample_covers_every_condition_and_reads_only_final(self):
        ids=rt.sample(CFG);self.assertEqual(len(ids),24);self.assertEqual({i.split('-')[1] for i in ids},set(CFG['conditions']))
        for i in ids:self.assertTrue((FINAL/'traces'/f'{i}.jsonl').exists());self.assertTrue((FINAL/'traces'/f'{rt.partner_id(i)}.jsonl').exists())
    def test_tampers_are_deterministic_and_control_is_identical(self):
        original=(FINAL/'traces'/f'{self.run_id}.jsonl').read_bytes()
        for name in rt.TAMPERS:
            a=rt.tamper(name,self.clean,self.partner);b=rt.tamper(name,self.clean,self.partner)
            self.assertEqual(rt.dump(a[0]),rt.dump(b[0]),name);self.assertEqual(a[1:],b[1:],name)
            if name=='T0':self.assertEqual(rt.dump(a[0]).encode(),original)
            else:self.assertNotEqual(rt.dump(a[0]).encode(),original,name)
        self.assertEqual(rt.dump(self.clean).encode(),original)   # tampering never mutates the loaded original
    def test_insider_classes_rechain_and_naive_classes_do_not(self):
        for name in ['T5a','T5b','T5c','T6','T7','T8a','T8b']:
            rows,cp,_,_=rt.tamper(name,self.clean,self.partner);self.assertEqual(rt.verify(rows,cp['head'],cp['records']),[],name)
        for name in ['T1','T2','T4']:self.assertTrue(rt.verify(rt.tamper(name,self.clean,self.partner)[0]),name)
        self.assertEqual(rt.verify(rt.tamper('T3',self.clean,self.partner)[0]),[])   # a chain alone cannot see suffix truncation
    def test_matrix_reproduces_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as d:
            rt.main(['--out',str(Path(d)/'out'),'--scratch',str(Path(d)/'scratch')])
            self.assertEqual((Path(d)/'out'/'matrix.csv').read_bytes(),COMMITTED.read_bytes())
            self.assertFalse(list(Path(d).glob('**/results')))   # tampered copies stay in the scratch directory
    def test_matrix_shape(self):
        self.assertEqual(len(self.rows),24*len(rt.TAMPERS)*len(rt.VERIFIERS))
        self.assertEqual(sum(r['applicable']=='0' for r in self.rows),3*len(rt.VERIFIERS))   # T5b has nothing to forge in 3 runs
    def test_predeclared_claims_hold(self):
        outcomes=rt.claim_outcomes(self.rows)
        for claim,text in [('C1','undetectable by V1 and V2: **held**'),('C2','detects T5a: **held**'),('C3','T8a: **held**'),('C4','untouched control: **held**')]:
            self.assertEqual(outcomes[claim],[],claim);self.assertIn(text,MD)
        self.assertEqual(rt.mismatches(self.rows),[]);self.assertIn('0 of 1710 applicable cells differ',MD)
    def test_partial_anchor_only_covers_its_prefix(self):
        cond=[r for r in self.rows if r['tamper']=='T5b' and r['verifier']=='V3p' and r['applicable']=='1']
        self.assertTrue(cond)
        for r in cond:self.assertEqual(r['detected']=='1',int(r['target_index'])<int(r['m']))
        for t in ['T3','T5c','T6','T8a']:
            self.assertTrue(all(r['detected']=='0' for r in self.rows if r['tamper']==t and r['verifier'] in ('V3p','V4p')),t)
            self.assertTrue(all(r['detected']=='1' for r in self.rows if r['tamper']==t and r['verifier'] in ('V3','V4')),t)
if __name__=='__main__':unittest.main()
