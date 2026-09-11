"""Detection-to-response bridge: synthetic alerts build a well-formed external timeline, the replay runs, and the preregistered claims hold."""
import csv,importlib.util,io,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bridge_swarm',ROOT/'scripts/bridge_swarm.py');bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
INCIDENT=json.loads((ROOT/'data/incident_events.json').read_text())
HOSTS=('wiki.example.test/alpha','wiki.example.test/beta')
COMMON=dict(availability={'burst':True},baseline_fired=False,baseline_value=1,event_ids=['deadbeef00000001'],features={'burst':0.5},
            first_seen='2026-01-01T00:20:00Z',n_events=2,score=0.5,snapshot_path='snapshots/wiki.example.test/alpha.html',
            snapshot_sha256='ab'*32,threshold=0.25,updates=[])

def alert(aid,surface,op,level,first,last,emitted,window='1767225600',signals=('burst',)):
    return dict(COMMON,alert_id=aid,surface_id=surface,operating_point=op,level=level,ts_event_first=first,ts_event_last=last,
                emitted_at=emitted,window_id=f'{surface}@{window}',fired_signals=list(signals))

# Three alerts, deliberately out of event-time order in the file: the second listed change is the first emitted.
ALERTS=[alert('a2','wiki.example.test/beta','high_priority','probable','2026-01-01T00:15:00Z','2026-01-01T00:16:00Z','2026-01-01T00:20:00Z',window='1767226500'),
        alert('a1','wiki.example.test/alpha','candidate','candidate','2026-01-01T00:00:00Z','2026-01-01T00:05:00Z','2026-01-01T00:20:00Z'),
        alert('a3','wiki.example.test/alpha','candidate','candidate','2026-01-01T01:00:00Z','2026-01-01T01:02:00Z','2026-01-01T01:05:00Z',window='1767229200')]

def write_alerts(path,alerts):path.write_text(''.join(json.dumps(a)+'\n' for a in alerts))

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.dir=Path(self.tmp.name);self.alerts=self.dir/'alerts.jsonl';write_alerts(self.alerts,ALERTS)
    def tearDown(self):self.tmp.cleanup()
    def run_bridge(self,*extra):
        out=self.dir/'out';bridge.main(['--alerts',str(self.alerts),'--out',str(out),*extra])
        rows=list(csv.DictReader(io.StringIO((out/'summary.csv').read_text())));events=json.loads((out/'external_events.json').read_text())
        return out,rows,events
    def test_external_events_are_well_formed(self):
        out,rows,events=self.run_bridge();sev=bridge.severity_map(INCIDENT)
        self.assertEqual([e['id'] for e in events],['a1','a2','a3'])   # ordered by ts_event_first, not by file order
        self.assertEqual(list(events[0]),list(INCIDENT[0]))               # exact incident_events.json record shape, same key order
        for e in events:
            self.assertEqual(e['episode'],'external');self.assertEqual(e['stage'],'external_detection')
            self.assertTrue(e['source_id'].startswith('swarm-boards alerts.jsonl '+bridge.sha256_file(self.alerts)))
            self.assertIn(e['severity'],(sev['high_priority'],sev['candidate']));self.assertGreater(e['severity'],0)
            for host in HOSTS:self.assertNotIn(host.split('/')[0],json.dumps(e))
            self.assertIn('public wiki ',e['summary'])
        by={e['id']:e for e in events}
        self.assertEqual(by['a2']['severity'],sev['high_priority']);self.assertEqual(by['a1']['severity'],sev['candidate'])
        self.assertEqual(by['a1']['event_time'],'2026-01-01T00:00:00Z');self.assertEqual(by['a1']['public_available_at'],'2026-01-01T00:20:00Z')
        self.assertEqual(sev,{'high_priority':max(e['severity'] for e in INCIDENT),'candidate':min(e['severity'] for e in INCIDENT if e['severity']>0)})
        self.assertEqual(json.loads((ROOT/'data/incident_events.json').read_text()),INCIDENT)
    def test_replay_runs_for_every_condition_and_delay(self):
        out,rows,events=self.run_bridge();cfg=json.loads((ROOT/'configs/experiment.json').read_text())
        self.assertEqual(len(rows),len(cfg['conditions'])*len(bridge.DELAYS))
        self.assertEqual(list(rows[0]),bridge.SUMMARY_COLUMNS)
        self.assertTrue(all(r['n_alert_events']=='3' and r['first_alert_ts']=='2026-01-01T00:00:00Z' for r in rows))
        self.assertEqual(len(json.loads((out/'replay.json').read_text())),len(rows))
        self.assertEqual(int(rows[0]['detection_latency_seconds_max']),1200);self.assertEqual(float(rows[0]['detection_latency_seconds_median']),300)
    def test_completed_harm_non_decreasing_in_delay(self):
        out,rows,events=self.run_bridge();self.assertEqual(bridge.check_non_decreasing([dict(r,delay=int(r['delay']),completed_before_containment=int(r['completed_before_containment'])) for r in rows]),[])
        monitor={int(r['delay']):int(r['completed_before_containment']) for r in rows if r['condition']=='monitor'}
        self.assertEqual(monitor,{0:1,2:2,6:3})
        layered={int(r['delay']):int(r['completed_before_containment']) for r in rows if r['condition']=='layered'}
        self.assertEqual(layered,{0:1,2:1,6:1})
    def test_first_event_is_never_prevented(self):
        out,rows,events=self.run_bridge()
        self.assertTrue(all(int(r['completed_before_containment'])>=1 for r in rows))
        # Wall clock: the earliest emission postdates the first listed change, so nothing could have acted on it.
        k,earliest=bridge.listed_before_first_emission(events);self.assertEqual((k,earliest),(2,'2026-01-01T00:20:00Z'))
        self.assertEqual(bridge.check_latency_blind(events,['monitor','layered']),[])
        self.assertIn('never prevents the first event (completed >= 1 in every cell): **held**',(out/'summary.md').read_text())
    def test_deterministic_and_hashed(self):
        out,_,_=self.run_bridge();first={f.name:f.read_bytes() for f in out.iterdir()}
        out,_,_=self.run_bridge();self.assertEqual({f.name:f.read_bytes() for f in out.iterdir()},first)
        manifest=json.loads((out/'manifest.json').read_text())
        self.assertEqual(manifest['input']['sha256'],bridge.sha256_file(self.alerts));self.assertIn('agent_delegate/harness.py',manifest['code'])
        self.assertTrue(all(v.startswith('public wiki ') for v in manifest['surfaces']))
    def test_level_filter_and_window_supersession(self):
        _,rows,events=self.run_bridge('--level','high_priority');self.assertEqual([e['id'] for e in events],['a2'])
        _,rows,events=self.run_bridge('--level','candidate');self.assertEqual([e['id'] for e in events],['a1','a3'])
        # A window that fired at both operating points enters once, as the high_priority alert.
        twin=alert('a1h','wiki.example.test/alpha','high_priority','probable','2026-01-01T00:00:00Z','2026-01-01T00:05:00Z','2026-01-01T00:30:00Z')
        write_alerts(self.alerts,ALERTS+[twin,ALERTS[0]]);_,rows,events=self.run_bridge()
        self.assertEqual([e['id'] for e in events],['a1h','a2','a3'])
        manifest=json.loads((self.dir/'out'/'manifest.json').read_text())
        self.assertEqual(manifest['input']['superseded_candidate_ids'],['a1']);self.assertEqual(manifest['input']['duplicate_alert_ids'],['a2'])
    def test_empty_selection_writes_a_summary(self):
        write_alerts(self.alerts,[a for a in ALERTS if a['operating_point']=='candidate'])
        out,rows,events=self.run_bridge('--level','high_priority')
        self.assertEqual(events,[]);self.assertTrue(all(r['completed_before_containment']=='0' and r['first_alert_ts']=='' for r in rows))
if __name__=='__main__':unittest.main()
