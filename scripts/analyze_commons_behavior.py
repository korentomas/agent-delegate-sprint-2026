"""Analyse the frozen shared-library run. No model inference; paired episode units."""
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import random
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from analyze_study import wilson_ci
ROOT=Path(__file__).resolve().parents[1]
MODELS=['qwen-standard','qwen-abliterated','gemma-standard','gemma-abliterated']
MODEL_NAMES={'qwen-standard':'Qwen standard','qwen-abliterated':'Qwen abliterated','gemma-standard':'Gemma standard','gemma-abliterated':'Gemma abliterated'}
ARMS=['log','queue','monitor','delegate','quarantine']
ARM_NAMES={'log':'Log only','queue':'Review queue','monitor':'Monitor','delegate':'Delegate','quarantine':'Quarantine'}


def mean(values):return sum(values)/len(values)


def paired_interval(differences, seed, samples=10000):
    """Bootstrap seed-paired differences, stratified by the two task families."""
    groups=defaultdict(list)
    for family,value in differences:groups[family].append(value)
    rng=random.Random(seed);draws=[]
    for _ in range(samples):
        values=[rng.choice(group) for group in groups.values() for _ in group]
        draws.append(mean(values))
    draws.sort()
    return draws[int(.025*samples)],draws[int(.975*samples)]


def summarize(records):
    groups=defaultdict(list)
    for e in records:groups[e['model'],e['institution'],e['valid']].append(e)
    rows=[]
    for model in MODELS:
        for arm in ARMS:
            for valid in [False,True]:
                es=groups[model,arm,valid]
                if not es:raise ValueError('Missing cell')
                n=len(es);bad=sum(e['any_invalid_reuse'] for e in es);reports=sum(e['reported'] for e in es)
                badlo,badhi=wilson_ci(bad,n);replo,rephi=wilson_ci(reports,n)
                row=dict(model=model,institution=arm,valid=valid,n=n,invalid_reuse_episodes=bad,
                         invalid_reuse_share=bad/n,invalid_reuse_wilson_lo=badlo,invalid_reuse_wilson_hi=badhi,
                         reported_episodes=reports,report_share=reports/n,report_wilson_lo=replo,report_wilson_hi=rephi,
                         final_correct_mean=mean([e['final_correct'] for e in es]),
                         final_missing_mean=mean([e['final_missing'] for e in es]),
                         effective_reviews=sum(e['effective_review_tick'] is not None for e in es))
                for field in ['reuse_attempts','invalid_reuse_accepted','invalid_acceptances','manual_errors','blocked_reuse','false_blocks','invalid_calls','report_count','advisor_calls']:
                    row[field+'_total']=sum(e[field] for e in es)
                rows.append(row)
    return rows


def contrasts(records):
    index={(e['model'],e['institution'],e['valid'],e['seed']):e for e in records}
    rows=[]
    for model in MODELS:
        for valid in [False,True]:
            for treatment,control in [('queue','log'),('monitor','queue'),('delegate','queue'),('delegate','monitor'),('quarantine','queue')]:
                pairs=[]
                for key,e in index.items():
                    if key[:3]==(model,treatment,valid):
                        other=index.get((model,control,valid,e['seed']))
                        if other is None:raise ValueError('Missing seed pair')
                        pairs.append((e,other))
                for metric in ['any_invalid_reuse','reported','final_correct','invalid_reuse_accepted','false_blocks']:
                    diffs=[(a['family'],float(a[metric])-float(b[metric])) for a,b in pairs]
                    lo,hi=paired_interval(diffs,f'{model}:{valid}:{treatment}:{control}:{metric}')
                    rows.append(dict(model=model,valid=valid,treatment=treatment,control=control,metric=metric,n_pairs=len(diffs),
                                     difference=mean([x for _,x in diffs]),bootstrap_lo=lo,bootstrap_hi=hi))
    return rows


def csv_write(path,rows):
    with path.open('w') as f:
        w=csv.DictWriter(f,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def figure(rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for p in (ROOT/'report/latex/fonts').glob('*.ttf'):font_manager.fontManager.addfont(str(p))
    plt.rcParams.update({'font.family':'serif','font.serif':['Old Standard TT'],'font.size':10,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,1,figsize=(6.5,4.1),layout='constrained')
    for ax,metric,title in zip(axes,['invalid_reuse_episodes','reported_episodes'],['Episodes with incorrect library reuse accepted','Episodes that sent a report']):
        cells=[[next(r for r in rows if r['model']==m and r['institution']==a and not r['valid']) for a in ARMS] for m in MODELS]
        values=[[r[metric]/r['n'] for r in group] for group in cells]
        ax.imshow(values,vmin=0,vmax=1,cmap='Blues',aspect='auto')
        for i,group in enumerate(cells):
            for j,r in enumerate(group):ax.text(j,i,f"{r[metric]}/{r['n']}",ha='center',va='center',color='white' if r[metric]/r['n']>.55 else '#152330')
        ax.set_xticks(range(5),['Log','Queue','Monitor','Delegate','Quarantine']);ax.set_yticks(range(4),[MODEL_NAMES[m] for m in MODELS]);ax.tick_params(length=0)
        ax.set_title(title,fontsize=11,weight='bold')
        for s in ax.spines.values():s.set_visible(False)
    out=ROOT/'report/latex/figures/commons-behavior'
    fig.savefig(out.with_suffix('.pdf'),metadata={'CreationDate':None});fig.savefig(out.with_suffix('.png'),dpi=220);plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--no-figure',action='store_true');args=p.parse_args()
    records=[];hashes={};manifests=[]
    for model in MODELS:
        path=ROOT/f'results/commons-heldout-{model}/episodes.json'
        manifest=json.loads(path.with_name('manifest.json').read_text());manifests.append(manifest)
        es=json.loads(path.read_text());seen=set()
        for e in es:
            if e['id'] in seen:raise ValueError('Duplicate episode')
            seen.add(e['id'])
            if e['split']!='heldout':raise ValueError('Development episode in held-out analysis')
            records.append({'model':model,**e})
        if len(es)!=120 or manifest['episodes']!=120:raise ValueError('Expected all 120 episodes per model')
        hashes[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    out=ROOT/'results/commons-behavior-summary';out.mkdir(exist_ok=True)
    rows=summarize(records);csv_write(out/'summary.csv',rows);csv_write(out/'paired-contrasts.csv',contrasts(records))
    metrics=['model','id','institution','valid','seed','family','any_invalid_reuse','reported','first_report_tick','scheduled_review_tick','effective_review_tick','final_correct','final_incorrect','final_missing','invalid_reuse_accepted','invalid_acceptances','manual_errors','reuse_attempts','blocked_reuse','false_blocks','invalid_calls','report_count','advisor_calls']
    csv_write(out/'episodes.csv',[{k:e[k] for k in metrics} for e in records])
    totals={'episodes':len(records),'calls':sum(m['calls'] for m in manifests),'tokens':sum(m['total_tokens'] for m in manifests),
            'invalid_calls':sum(m['invalid_calls'] for m in manifests),'unusable_decisions':sum(e['invalid_calls'] for e in records),'faulty_episodes':sum(not e['valid'] for e in records),
            'faulty_with_invalid_reuse':sum(not e['valid'] and e['any_invalid_reuse'] for e in records),
            'faulty_reported':sum(not e['valid'] and e['reported'] for e in records),
            'valid_reported':sum(e['valid'] and e['reported'] for e in records)}
    (out/'manifest.json').write_text(json.dumps({'status':'held-out local exploratory benchmark; seeded artifacts, scripted review',
        'totals_descriptive_only':totals,'input_sha256':hashes,'analysis_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
    lines=['# Shared-library behavioral results','',
      'Four local 4B models, 120 episodes each. Twelve seed-paired tasks per condition; six per task family. Both valid and faulty artifacts. No claim of intentional cheating, isolated abliteration effects or real human response.','',
      '| Model | Institution | Artifact | Incorrect reuse episodes | Reported episodes | Final correct / 3 |',
      '|---|---|---|---:|---:|---:|']
    for r in rows:lines.append(f"| {MODEL_NAMES[r['model']]} | {ARM_NAMES[r['institution']]} | {'valid' if r['valid'] else 'faulty'} | {r['invalid_reuse_episodes']}/{r['n']} | {r['reported_episodes']}/{r['n']} | {r['final_correct_mean']:.2f} |")
    lines+=['','These counts are episode outcomes, not independent worker decisions. Full Wilson intervals, errors, review delivery and interruption costs are in summary.csv. Paired treatment-minus-control bootstrap intervals are in paired-contrasts.csv. An observed tie is not equivalence. Runtime includes concurrent GPU use; do not rank model speed from it. Manifest invalid_calls counts format/HTTP failures; episode invalid_calls also includes unusable submit decisions with a null answer. Both counts are retained separately in the summary manifest.','',json.dumps(totals),'']
    (out/'summary.md').write_text('\n'.join(lines))
    # A family breakdown prevents pooled arithmetic differences hiding one task family.
    family=[]
    for model in MODELS:
        for arm in ARMS:
            for valid in [False,True]:
                for task in ['threshold','distinct']:
                    es=[e for e in records if (e['model'],e['institution'],e['valid'],e['family'])==(model,arm,valid,task)]
                    family.append(dict(model=model,institution=arm,valid=valid,family=task,n=len(es),invalid_reuse_episodes=sum(e['any_invalid_reuse'] for e in es),reported_episodes=sum(e['reported'] for e in es),final_correct_mean=mean([e['final_correct'] for e in es])))
    csv_write(out/'by-family.csv',family)
    generated=ROOT/'report/latex/generated'
    (generated/'commons-counts.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+str(v)+'}' for k,v in {
        'CommonsEpisodes':totals['episodes'],'CommonsCalls':totals['calls'],'CommonsFaultyEpisodes':totals['faulty_episodes'],
        'CommonsFaultyReuse':totals['faulty_with_invalid_reuse'],'CommonsFaultyReports':totals['faulty_reported'],
        'CommonsValidReports':totals['valid_reported'],'CommonsInvalidCalls':totals['invalid_calls'],'CommonsUnusableDecisions':totals['unusable_decisions']}.items())+'\n')
    table=['\\begin{longtable}{@{}lllrrr@{}}','\\caption{Held-out shared-library results. Bad reuse and reports count episodes; each cell has 12 episodes. Validity labels come from the offline oracle, not a worker-visible label.}\\\\',
           '\\toprule Model & Arm & Artifact & Bad reuse & Reports & Correct / 3\\\\\\midrule','\\endfirsthead',
           '\\toprule Model & Arm & Artifact & Bad reuse & Reports & Correct / 3\\\\\\midrule','\\endhead']
    for r in rows:table.append(' & '.join([MODEL_NAMES[r['model']],ARM_NAMES[r['institution']],'Valid' if r['valid'] else 'Faulty',f"{r['invalid_reuse_episodes']}/{r['n']}",f"{r['reported_episodes']}/{r['n']}",f"{r['final_correct_mean']:.2f}"])+r' \\')
    table+=['\\bottomrule','\\end{longtable}'];(generated/'commons-table.tex').write_text('\n'.join(table)+'\n')
    if not args.no_figure:figure(rows)
    print(json.dumps(totals))

if __name__=='__main__':main()
