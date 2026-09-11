"""Optional local human incident-replay tabletop; never executes action strings."""
import argparse,json,time
from pathlib import Path
from .harness import ROOT,Audit
ACTIONS=['continue','request_clarification','request_resources','restrict_capabilities','alert_human','temporarily_pause','declare_incident']
def main():
    p=argparse.ArgumentParser();p.add_argument('--episode',choices=['collective','hf','wiki'],default='wiki');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    events=[e for e in json.loads((ROOT/'data/incident_events.json').read_text()) if e['episode']==a.episode]
    audit=Audit(a.out,'human-'+a.episode)
    print('Retrospective tabletop. Source event dates are NOT proven defender-availability dates.')
    print('No future events will be shown. Enter q to end; choices only record decisions.')
    for i,e in enumerate(events):
        print('\n'+e['event_time']+' | '+e['summary'])
        print('  '.join(f'{j}: {x}' for j,x in enumerate(ACTIONS)))
        start=time.perf_counter()
        while True:
            response=input('Decision: ').strip()
            if response=='q':break
            if response.isdigit() and int(response)<len(ACTIONS):break
            print('Choose 0–6 or q.')
        if response=='q':break
        audit.add(i,'human_playtest_decision',event_id=e['id'],source_event_time=e['event_time'],action=ACTIONS[int(response)],response_seconds=time.perf_counter()-start)
    head=audit.save();print('Saved',a.out,'checkpoint',head)
if __name__=='__main__':main()
