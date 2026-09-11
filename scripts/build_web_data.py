"""Export the committed experiment for the visual app; never invent new results."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results/final'
OUT=ROOT/'web/data'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    checkpoints=json.loads((RESULTS/'checkpoints.json').read_text())
    scenarios=json.loads((ROOT/'data/scenarios.json').read_text())
    totals={r['run_id']:r for r in csv.DictReader((RESULTS/'runs.csv').open())}
    for scenario in scenarios:
        runs={}
        for path in sorted((RESULTS/'traces').glob(scenario['id']+'-*.jsonl')):
            records=[json.loads(x) for x in path.read_text().splitlines()]
            assert records[-1]['hash']==checkpoints[path.stem]['head']
            runs[path.stem]={'records':[{k:v for k,v in r.items() if k not in ['previous_hash','hash','run_id','clock']} for r in records],
                             'head':records[-1]['hash'],'summary':totals[path.stem]}
        assert len(runs)==144
        (OUT/(scenario['id']+'.json')).write_text(json.dumps(runs,ensure_ascii=False,separators=(',',':'))+'\n')
    index={'scenarios':scenarios,'config':json.loads((ROOT/'configs/experiment.json').read_text()),
           'events':json.loads((ROOT/'data/incident_events.json').read_text()),
           'sources':json.loads((ROOT/'data/sources.json').read_text()),
           'results_sha256':hashlib.sha256((RESULTS/'runs.csv').read_bytes()).hexdigest(),
           'trace_commit':'5bf7772','run_count':len(totals),'dialogue':'Authored English dramatization of trace events; not recorded model reasoning.'}
    (OUT/'index.json').write_text(json.dumps(index,ensure_ascii=False,separators=(',',':'))+'\n')
    print(f'Web data: {len(totals)} existing traces, {len(scenarios)} scenario bundles.')
if __name__=='__main__':main()
