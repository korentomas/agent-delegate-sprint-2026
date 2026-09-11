import copy,json,tempfile,unittest
from pathlib import Path
from agent_delegate.harness import ROOT,Audit,run_case,verify,semantic_audit,replay,due_tick
CFG=json.loads((ROOT/'configs/experiment.json').read_text())
CASES={s['id']:s for s in json.loads((ROOT/'data/scenarios.json').read_text())}
class HarnessTests(unittest.TestCase):
    def run_one(self,name='minority_warning',condition='delegate',latency=6,capture=False,bypass=True,coverage='complete'):
        return run_case(CASES[name],condition,latency,capture,bypass,coverage,CFG)
    def test_hash_mutation_and_truncation(self):
        _,rows=self.run_one();head=rows[-1]['hash']
        self.assertEqual(verify(rows,head,len(rows)),[])
        changed=copy.deepcopy(rows);changed[1]['delegate_id']='attacker'
        self.assertTrue(verify(changed,head,len(rows)))
        self.assertTrue(verify(rows[:-1],head,len(rows)))
        self.assertEqual(verify(rows[:-1]),[]) # A chain alone cannot detect suffix truncation.
    def test_full_gates(self):
        for name in CASES:
            for condition in ['layered','gates_only']:
                row,_=self.run_one(name,condition,capture=True,bypass=False)
                self.assertEqual(row['executed_harm'],0)
    def test_minority_bypass(self):
        lost,_=self.run_one(capture=True,bypass=False)
        saved,_=self.run_one(capture=True,bypass=True)
        self.assertEqual(lost['minority_delivered'],0)
        self.assertEqual(saved['minority_delivered'],1)
        self.assertGreater(lost['executed_harm'],saved['executed_harm'])
    def test_pause_expiry_does_not_authorize(self):
        row,rows=self.run_one()
        after=[r for r in rows if r['kind']=='action' and 2<=r['simulation_tick']<6 and r['action']!='authorized_work']
        self.assertTrue(after)
        self.assertTrue(all(r['frozen'] and not r['executed'] for r in after))
    def test_hidden_gate_failure(self):
        row,_=self.run_one('hidden_violation','gates_only',coverage='missing_hidden')
        self.assertGreater(row['hidden_harm'],0)
    def test_benign_negative_control(self):
        row,_=self.run_one('feasible','delegate')
        self.assertEqual(row['correct_answers'],3);self.assertEqual(row['false_pause'],0)
    def test_false_report_is_not_oracle_filtered(self):
        row,_=self.run_one('false_alarm')
        self.assertEqual(row['false_pause'],1)
    def test_latency_and_safe_tools(self):
        fast,_=self.run_one('impossible_task',latency=0)
        slow,_=self.run_one('impossible_task',latency=6)
        self.assertGreater(fast['correct_answers'],slow['correct_answers'])
        self.assertEqual(due_tick(1,2,2),4)
    def test_matched_observation_null(self):
        for name in CASES:
            d,_=self.run_one(name,'delegate');m,_=self.run_one(name,'matched_monitor')
            for field in ['executed_harm','correct_answers','minority_delivered']:
                self.assertEqual(d[field],m[field])
    def test_future_suffix_does_not_change_decisions(self):
        s=copy.deepcopy(CASES['minority_warning']);_,r1=run_case(s,'delegate',2,False,True,'complete',CFG)
        s['actions'][-1]=[5,'authorized_work',0,True]
        _,r2=run_case(s,'delegate',2,False,True,'complete',CFG)
        def prefix(rows):return [{k:v for k,v in r.items() if k not in ['hash','previous_hash','scenario_hash']} for r in rows if r['simulation_tick']<5]
        self.assertEqual(prefix(r1),prefix(r2))
    def test_semantic_checker_detects_bad_executor(self):
        _,rows=self.run_one();rows=copy.deepcopy(rows)
        r=next(r for r in rows if r['kind']=='action' and r['frozen'] and r['action']!='authorized_work');r['executed']=True
        self.assertIn('unauthorized mediated execution',semantic_audit(rows))
    def test_replay_no_retroactive_prevention(self):
        es=json.loads((ROOT/'data/incident_events.json').read_text());es=[e for e in es if e['episode']=='hf']
        for c in CFG['conditions'][:4]:
            self.assertEqual(replay(es,c,0)['harmful_observed_before_containment'],1)
    def test_replay_restriction_does_not_wait_for_human(self):
        es=json.loads((ROOT/'data/incident_events.json').read_text());es=[e for e in es if e['episode']=='hf']
        self.assertEqual(replay(es,'layered',2)['harmful_observed_before_containment'],1)
        self.assertEqual(replay(es,'monitor',2)['harmful_observed_before_containment'],2)
    def test_unsafe_request_is_denied(self):
        row,rows=self.run_one('unsafe_resource_request',latency=0)
        responses=[r for r in rows if r['kind']=='human_response']
        self.assertEqual(responses[0]['response'],'deny_unsafe_request')
        self.assertIsNone(responses[0]['approved_change'])
        self.assertEqual(row['executed_harm'],0)
    def test_exclusive_log_creation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'log.jsonl';a=Audit(p,'test');a.add(0,'start');a.save()
            with self.assertRaises(FileExistsError):a.save()
    def test_source_integrity(self):
        events=json.loads((ROOT/'data/incident_events.json').read_text());sources=json.loads((ROOT/'data/sources.json').read_text())
        self.assertEqual(len({e['id'] for e in events}),len(events))
        for e in events:self.assertIn(e['source_id'],sources);self.assertTrue(e['source_locator'])
if __name__=='__main__':unittest.main()
