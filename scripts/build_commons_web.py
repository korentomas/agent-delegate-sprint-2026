"""Export the completed behavioral study for a read-only browser replay."""
from pathlib import Path
import csv
import json
ROOT=Path(__file__).resolve().parents[1]
MODELS=['qwen-standard','qwen-abliterated','gemma-standard','gemma-abliterated']


def main():
    base=ROOT/'results/commons-behavior-summary'
    manifest=json.loads((base/'manifest.json').read_text())
    with (base/'summary.csv').open() as f:summary=list(csv.DictReader(f))
    models=[]
    for model in MODELS:
        es=json.loads((ROOT/f'results/commons-heldout-{model}/episodes.json').read_text())
        if len(es)!=120:raise ValueError('Only complete study exports are published')
        models.append({'id':model,'episodes':es})
    result={'totals':manifest['totals_descriptive_only'],'summary':summary,'models':models,
            'discrimination':json.loads((ROOT/'results/commons-discrimination/summary.json').read_text()),
            'stronger_screen':json.loads((ROOT/'results/commons-stronger-summary/summary.json').read_text()),
            'diagnostic':json.loads((ROOT/'results/commons-capability-summary/summary.json').read_text()),
            'scope':'Seeded shared artifacts; real model decisions; scripted independent review; no inference in the browser.'}
    (ROOT/'web/data/commons-behavior.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
    print('Exported 480 held-out shared-library episodes from four models.')

if __name__=='__main__':main()
