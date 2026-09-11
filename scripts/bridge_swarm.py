"""Detection-to-response bridge: swarm-boards alerts through the replay adapter. Design frozen in docs/bridge-design.md.

Reuses agent_delegate.harness.replay unchanged; never writes data/incident_events.json.
Writes <out>/{external_events.json,replay.json,summary.csv,summary.md,latency.json,manifest.json}. No network, no randomness.
"""
import argparse,csv,hashlib,json,platform,statistics,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_delegate.harness import ROOT,replay

EPISODE='external';STAGE='external_detection';DELAYS=(0,2,6)
OPERATING_POINTS=('high_priority','candidate')
LEVEL_ALIASES={'probable':'high_priority','high_priority':'high_priority','candidate':'candidate'}
RECORD_KEYS=['id','episode','event_time','time_precision','source_id','source_locator','summary','stage','severity',
             'evidence_status','observation_status','public_available_at','annotation_status']
SUMMARY_COLUMNS=['condition','delay','n_alert_events','completed_before_containment','first_alert_ts','first_containment_ts',
                 'detection_latency_seconds_median','detection_latency_seconds_max']
INCIDENT_EVENTS=ROOT/'data/incident_events.json'

def sha256_file(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def sha256_text(text):return hashlib.sha256(text.encode()).hexdigest()
def parse_ts(s):return datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(timezone.utc)
def seconds_between(earlier,later):return int((parse_ts(later)-parse_ts(earlier)).total_seconds())
def iso_utc(epoch):return datetime.fromtimestamp(int(epoch),tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def human_duration(seconds):
    seconds=int(round(seconds));d,rem=divmod(seconds,86400);h,rem=divmod(rem,3600);m,s=divmod(rem,60)
    parts=[f'{d}d' if d else '',f'{h}h' if h else '',f'{m}m' if m else '',f'{s}s' if s or not (d or h or m) else '']
    return ' '.join(p for p in parts if p)

def surface_label(index):
    """0 -> 'public wiki A', 25 -> 'public wiki Z', 26 -> 'public wiki AA' (bijective base 26)."""
    n=index+1;s=''
    while n:n,r=divmod(n-1,26);s=chr(65+r)+s
    return 'public wiki '+s

def severity_map(incident_events):
    """high_priority -> the harness's highest nonzero severity class, candidate -> the lowest nonzero."""
    used=sorted({e['severity'] for e in incident_events if e['severity']>0})
    return {'high_priority':used[-1],'candidate':used[0]}

def read_alerts(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]

def operating_point(alert):
    op=alert.get('operating_point') or LEVEL_ALIASES.get(alert.get('level'))
    if op not in OPERATING_POINTS:raise ValueError(f"alert {alert.get('alert_id')}: unknown operating point {op!r}")
    return op

def select(alerts,level):
    """Keep the first record per alert_id, filter by operating point, and under 'both' keep one alert per window (high_priority wins).
    Returns (kept, duplicate_ids, superseded_ids)."""
    seen=set();unique=[];duplicates=[]
    for a in alerts:
        if a['alert_id'] in seen:duplicates.append(a['alert_id'])
        else:unique.append(a);seen.add(a['alert_id'])
    wanted=OPERATING_POINTS if level=='both' else (level,)
    kept=[a for a in unique if operating_point(a) in wanted];superseded=[]
    if level=='both':
        high={a['window_id'] for a in kept if operating_point(a)=='high_priority'}
        superseded=[a['alert_id'] for a in kept if operating_point(a)=='candidate' and a['window_id'] in high]
        kept=[a for a in kept if a['alert_id'] not in set(superseded)]
    return kept,duplicates,superseded

def surface_labels(alerts):
    """Alphabetical over every surface in the file, so letters do not depend on the level filter."""
    return {sid:surface_label(i) for i,sid in enumerate(sorted({a['surface_id'] for a in alerts}))}

def to_event(alert,labels,source_id,severities):
    op=operating_point(alert);label=labels[alert['surface_id']];latency=seconds_between(alert['ts_event_first'],alert['emitted_at'])
    window_start=alert['window_id'].rsplit('@',1)[-1]
    window=iso_utc(window_start) if window_start.isdigit() else 'unknown'
    first=alert['ts_event_first'][11:16];last=alert['ts_event_last'][11:16]
    signals=', '.join(alert.get('fired_signals') or [])or 'none'
    return dict(id=alert['alert_id'],episode=EPISODE,event_time=alert['ts_event_first'],
                time_precision='minute' if alert['ts_event_first'].endswith(':00Z') else 'second',
                source_id=source_id,
                source_locator=f"alert {alert['alert_id']}; {label}; window starting {window}; snapshot sha256 {alert['snapshot_sha256']}",
                summary=(f"External detector alert ({op}) on {label}: {alert['n_events']} listed change{'s' if alert['n_events']!=1 else ''} "
                         f"between {first} and {last} UTC; "
                         f"fired {signals}; score {alert['score']} against threshold {alert['threshold']}."),
                stage=STAGE,severity=severities[op],
                evidence_status='detector_alert; not a confirmed harmful act',
                observation_status=f"prospective; emitted by the external detector at {alert['emitted_at']}; listing-to-alert latency {latency} s",
                public_available_at=alert['emitted_at'],
                annotation_status='stage and severity assigned by this project from the alert operating point')

def build_events(alerts,labels,source_id,severities):
    events=[to_event(a,labels,source_id,severities) for a in alerts]
    return sorted(events,key=lambda e:(parse_ts(e['event_time']),e['id']))

def latency_seconds(events):return [seconds_between(e['event_time'],e['public_available_at']) for e in events]

def listed_before_first_emission(events):
    """Events whose listed change precedes the earliest emission in the timeline: complete before any control could act."""
    if not events:return 0,None
    earliest=min(events,key=lambda e:(parse_ts(e['public_available_at']),e['id']))['public_available_at']
    return sum(parse_ts(e['event_time'])<parse_ts(earliest) for e in events),earliest

def containment_ts(events,result):
    """Timestamp of the first event the modeled containment blocks; None when containment falls after the last event."""
    stop=len(result['trace'])
    return events[stop]['event_time'] if stop<len(events) else None

def run_replays(events,conditions,delays=DELAYS):
    lat=latency_seconds(events);rows=[];results=[]
    med=statistics.median(lat) if lat else None;mx=max(lat) if lat else None
    for c in conditions:
        for d in delays:
            if events:
                r=replay(events,c,d);results.append(r)
                completed=r['harmful_observed_before_containment'];first=r['first_alert_time'];cont=containment_ts(events,r)
            else:completed=0;first=cont=None
            rows.append(dict(condition=c,delay=d,n_alert_events=len(events),completed_before_containment=completed,
                             first_alert_ts=first,first_containment_ts=cont,
                             detection_latency_seconds_median=med,detection_latency_seconds_max=mx))
    return rows,results

def check_first_event_never_prevented(rows):
    return [(r['condition'],r['delay']) for r in rows if r['n_alert_events']>0 and r['completed_before_containment']<1]

def check_non_decreasing(rows):
    violations=[];by={}
    for r in rows:by.setdefault(r['condition'],[]).append(r)
    for c,members in by.items():
        members=sorted(members,key=lambda r:r['delay'])
        for a,b in zip(members,members[1:]):
            if b['completed_before_containment']<a['completed_before_containment']:violations.append((c,a['delay'],b['delay']))
    return violations

def check_latency_blind(events,conditions):
    """The adapter reads no availability column: with every latency set to zero the completed counts are identical."""
    zero=[dict(e,public_available_at=e['event_time']) for e in events]
    a,_=run_replays(events,conditions);b,_=run_replays(zero,conditions)
    return [(x['condition'],x['delay']) for x,y in zip(a,b) if x['completed_before_containment']!=y['completed_before_containment']]

def quantiles(values):
    if not values:return {}
    s=sorted(values);q=lambda p:s[min(len(s)-1,int(round(p*(len(s)-1))))]
    return dict(n=len(s),min=s[0],p25=q(0.25),median=statistics.median(s),p75=q(0.75),max=s[-1])

def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=SUMMARY_COLUMNS,lineterminator='\n');w.writeheader()
        w.writerows([{k:('' if v is None else v) for k,v in r.items()} for r in rows])

def fmt(v):return '' if v is None else str(v)

def summary_md(rows,events,alerts_kept,labels,checks,args,input_sha,severities,n_parsed,duplicates,superseded,conditions):
    first_claim,monotone,blind=checks;q=quantiles(latency_seconds(events));k,earliest=listed_before_first_emission(events)
    verdict=lambda v:'**held**' if not v else f'**FAILED** ({len(v)} cells: {v})'
    by_surface={};by_op={}
    for a in alerts_kept:
        by_surface[labels[a['surface_id']]]=by_surface.get(labels[a['surface_id']],0)+1
        by_op[operating_point(a)]=by_op.get(operating_point(a),0)+1
    lines=['# Bridge summary: swarm-boards alerts through the replay adapter','']
    if args.provisional:
        lines+=['**Provisional run.** The alerts file was produced with provisional detector thresholds, not the frozen configuration. '
                'Counts and latencies below describe this input and will be superseded by the run on the frozen file.','']
    lines+=[f'Design: `docs/bridge-design.md`, frozen before the run. Input `alerts.jsonl` sha256 `{input_sha}`: {n_parsed} records parsed, '
            f'{len(duplicates)} duplicate alert ids dropped, level filter `{args.level}`, {len(superseded)} candidate alerts superseded by a '
            f'high_priority alert on the same window, {len(events)} external events.',
            'Operating points: '+(', '.join(f'{op} {n}' for op,n in sorted(by_op.items())) or 'none')+
            f'. Severity map from `data/incident_events.json`: high_priority -> {severities["high_priority"]}, candidate -> {severities["candidate"]}.',
            'Surfaces: '+(', '.join(f'{s} {n}' for s,n in sorted(by_surface.items())) or 'none')+'.','',
            '## Completed events before modeled containment (event-index replay, contemporaneous telemetry assumed)','',
            '| condition | '+' | '.join(f'delay {d}' for d in DELAYS)+' |','|---|'+'---|'*len(DELAYS)]
    for c in conditions:
        cells=[next(r for r in rows if r['condition']==c and r['delay']==d) for d in DELAYS]
        lines.append(f'| {c} | '+' | '.join(str(r['completed_before_containment']) for r in cells)+' |')
    lines+=['',f'Every condition except `layered` is the same code path in `replay` (`stop = first + max(1, delay)`); `layered` restricts at `first + 1` '
            'regardless of delay. `gates_only` is not treated as gated by `replay`, so its row equals `monitor`. Delay 0 and delay 1 coincide by construction.','']
    if events:
        r0=rows[0];lines+=[f"First alert event (earliest listed change): `{r0['first_alert_ts']}`, emitted at `{events[0]['public_available_at']}`, "
                            f"listing-to-alert latency {latency_seconds(events)[0]} s ({human_duration(latency_seconds(events)[0])}).",
                            'Modeled containment timestamp per cell (first blocked event; empty when containment falls after the last event):','',
                            '| condition | '+' | '.join(f'delay {d}' for d in DELAYS)+' |','|---|'+'---|'*len(DELAYS)]
        for c in conditions:
            cells=[next(r for r in rows if r['condition']==c and r['delay']==d) for d in DELAYS]
            lines.append(f'| {c} | '+' | '.join(fmt(r['first_containment_ts']) or 'after last event' for r in cells)+' |')
        lines+=['','## Observed listing-to-alert latency (emitted_at - ts_event_first, seconds)','',
                '| n | min | p25 | median | p75 | max |','|---|---|---|---|---|---|',
                f"| {q['n']} | {q['min']} ({human_duration(q['min'])}) | {q['p25']} ({human_duration(q['p25'])}) | {q['median']} ({human_duration(q['median'])}) | "
                f"{q['p75']} ({human_duration(q['p75'])}) | {q['max']} ({human_duration(q['max'])}) |",'',
                f'Earliest emission in the timeline: `{earliest}`. Events whose listed change precedes it: {k} of {len(events)}. '
                'No control can act on an alert before it is emitted, so under real availability at least that many events are complete '
                'before any containment, for every condition and delay'+
                (' (more than every count in the table above).' if k>max(r['completed_before_containment'] for r in rows) else '.'),'']
    lines+=['## Predeclared claims','',
            f'- External detection alone never prevents the first event (completed >= 1 in every cell): {verdict(first_claim)}.',
            f'- Completed events non-decreasing in human delay, per condition: {verdict(monotone)}.',
            f'- The adapter is latency-blind (identical counts with every latency set to zero), so detection latency adds to the human delay in full: {verdict(blind)}.','',
            '## What this run cannot claim','',
            'An alert is a detector decision on a public listing, not a confirmed harmful act; the severity is our annotation from the operating point. '
            'Nothing here attributes the listed changes to any actor or laboratory. Latency is that of the captured listing relative to the '
            'listed change, which for batch captures is backfill time, not the response time of a live monitor.','']
    return '\n'.join(lines)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--alerts',type=Path,required=True,help='swarm-boards alerts.jsonl')
    p.add_argument('--out',type=Path,default=ROOT/'results'/'bridge')
    p.add_argument('--level',choices=('high_priority','candidate','both'),default='both')
    p.add_argument('--provisional',action='store_true',help='mark the summary as produced from unfrozen thresholds')
    p.add_argument('--incident-events',type=Path,default=INCIDENT_EVENTS,help='harness timeline used only to read the severity classes')
    args=p.parse_args(argv)
    cfg=json.loads((ROOT/'configs/experiment.json').read_text());conditions=list(cfg['conditions'])
    incident=json.loads(Path(args.incident_events).read_text());severities=severity_map(incident)
    alerts=read_alerts(args.alerts);input_sha=sha256_file(args.alerts);source_id=f'swarm-boards alerts.jsonl {input_sha}'
    kept,duplicates,superseded=select(alerts,args.level);labels=surface_labels(alerts)
    events=build_events(kept,labels,source_id,severities)
    rows,results=run_replays(events,conditions)
    checks=(check_first_event_never_prevented(rows),check_non_decreasing(rows),check_latency_blind(events,conditions))
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'external_events.json').write_text(json.dumps(events,indent=2)+'\n')
    (args.out/'replay.json').write_text(json.dumps(results,indent=2)+'\n')
    write_csv(args.out/'summary.csv',rows)
    k,earliest=listed_before_first_emission(events)
    (args.out/'latency.json').write_text(json.dumps(dict(unit='seconds',definition='emitted_at - ts_event_first per alert event',
        distribution=quantiles(latency_seconds(events)),per_event={e['id']:l for e,l in zip(events,latency_seconds(events))},
        earliest_emission=earliest,events_listed_before_earliest_emission=k),indent=2)+'\n')
    (args.out/'summary.md').write_text(summary_md(rows,events,kept,labels,checks,args,input_sha,severities,len(alerts),duplicates,superseded,conditions))
    manifest=dict(design='docs/bridge-design.md',status='provisional; thresholds not frozen' if args.provisional else 'as run',
        input=dict(path=str(args.alerts),sha256=input_sha,bytes=args.alerts.stat().st_size,records=len(alerts),
                   duplicate_alert_ids=duplicates,superseded_candidate_ids=superseded,level=args.level),
        events=len(events),conditions=conditions,delays=list(DELAYS),severity_map=severities,
        surfaces={label:sha256_text(sid) for sid,label in labels.items()},
        claims=dict(first_event_never_prevented=not checks[0],non_decreasing_in_delay=not checks[1],latency_blind_adapter=not checks[2]),
        code={str(f.relative_to(ROOT)):sha256_file(f) for f in [ROOT/'agent_delegate/harness.py',Path(__file__).resolve(),Path(args.incident_events).resolve()] if f.exists()},
        python=platform.python_version(),network='none',randomness='none')
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(events=len(events),level=args.level,out=str(args.out),
                          claims=manifest['claims'],latency_median=rows[0]['detection_latency_seconds_median'] if rows else None)))
    return rows
if __name__=='__main__':main()
