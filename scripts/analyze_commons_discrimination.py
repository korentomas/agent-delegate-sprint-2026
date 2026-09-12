"""Retrospective validity contrasts and source-linked examples; no new inference.

This analysis was added after reviewing the completed study. It does not replace
or alter the locally frozen original analysis or its raw records.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from analyze_commons_behavior import MODELS, ARMS, ARM_NAMES, csv_write
from analyze_study import wilson_ci

ROOT = Path(__file__).resolve().parents[1]
STANDARD = ['qwen-standard', 'gemma-standard']


def flags(episode):
    workers = [e for e in episode['events'] if e['kind'] == 'worker']
    return {'reuse': any(e['action'] == 'reuse' for e in workers),
            'report': any(e.get('report') is True for e in workers),
            'first_report': bool(workers and workers[0].get('report') is True)}


def validity_pairs(episodes, metric):
    index = {}
    for e in episodes:
        key = e['institution'], e['seed'], e['valid']
        if key in index:
            raise ValueError('Duplicate episode in validity contrast')
        index[key] = e
    rows = []
    for (arm, seed, valid), e in sorted(index.items()):
        if valid:
            other = index.get((arm, seed, False))
            if other is None:
                raise ValueError('Missing faulty partner')
            v, f = int(flags(e)[metric]), int(flags(other)[metric])
            rows.append({'institution': arm, 'seed': seed, 'family': e['family'],
                         'metric': metric, 'valid': v, 'faulty': f,
                         'faulty_minus_valid': f - v})
    if len(rows) * 2 != len(episodes):
        raise ValueError('Unpaired validity record')
    return rows


def summarize(episodes):
    rows = []
    for arm in ARMS:
        for valid in [True, False]:
            es = [e for e in episodes if e['institution'] == arm and e['valid'] == valid]
            if len(es) != 12:
                raise ValueError('Expected 12 episodes per validity cell')
            row = {'institution': arm, 'valid': valid, 'n': len(es)}
            for metric in ['reuse', 'report', 'first_report']:
                n = sum(flags(e)[metric] for e in es)
                lo, hi = wilson_ci(n, len(es))
                row.update({metric + '_episodes': n, metric + '_share': n / len(es),
                            metric + '_wilson_lo': lo, metric + '_wilson_hi': hi})
            rows.append(row)
    return rows


def plot(rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for p in (ROOT / 'report/latex/fonts').glob('*.ttf'):
        font_manager.fontManager.addfont(str(p))
    plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Old Standard TT'],
                         'font.size': 10, 'pdf.fonttype': 42})
    fig, axs = plt.subplots(2, 2, figsize=(6.5, 3.5), sharex=True, layout='constrained')
    for i, model in enumerate(STANDARD):
        for j, metric in enumerate(['reuse', 'report']):
            ax = axs[i, j]
            for valid, color, marker, offset, label in [(True, '#246a8a', 'o', -.13, 'Valid helper'),
                                                       (False, '#bd581e', 's', .13, 'Faulty helper')]:
                cells = [next(r for r in rows if (r['model'], r['institution'], r['valid']) == (model, a, valid)) for a in ARMS]
                vals = [r[metric + '_share'] for r in cells]
                ax.errorbar(vals, [k + offset for k in range(5)],
                            xerr=[[v-r[metric+'_wilson_lo'] for v,r in zip(vals,cells)],
                                  [r[metric+'_wilson_hi']-v for v,r in zip(vals,cells)]],
                            fmt=marker, color=color, markersize=4, elinewidth=.8, capsize=2, label=label)
            ax.set_title(('Qwen 4B' if i == 0 else 'Gemma 4B') + (' · reuse attempt' if j == 0 else ' · report'))
            ax.set_yticks(range(5), ['Log', 'Queue', 'Monitor', 'Delegate', 'Quarantine'])
            ax.set_ylim(4.5, -.5); ax.set_xlim(-.04, 1.04)
            ax.set_xticks([0, .5, 1], ['0%', '50%', '100%'])
            ax.grid(axis='x', alpha=.16); ax.set_axisbelow(True)
            for s in ['top', 'right']: ax.spines[s].set_visible(False)
            if i == 1: ax.set_xlabel('Episodes with at least one choice')
    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='outside upper center', ncol=2, frameon=False)
    out = ROOT / 'report/latex/figures/commons-discrimination'
    fig.savefig(out.with_suffix('.pdf'), metadata={'CreationDate': None})
    fig.savefig(out.with_suffix('.png'), dpi=220)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-figure', action='store_true')
    args = parser.parse_args()
    rows, pairs, pooled, examples, hashes = [], [], [], [], {}
    for model in MODELS:
        path = ROOT / f'results/commons-heldout-{model}/episodes.json'
        es = json.loads(path.read_text())
        hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.extend({'model': model, **r} for r in summarize(es))
        for metric in ['reuse', 'report', 'first_report']:
            ps = validity_pairs(es, metric)
            pairs.extend({'model': model, **p} for p in ps)
            pooled.append({'model': model, 'metric': metric, 'n_pairs': len(ps),
                           'valid_episodes': sum(p['valid'] for p in ps),
                           'faulty_episodes': sum(p['faulty'] for p in ps),
                           'faulty_minus_valid': sum(p['faulty_minus_valid'] for p in ps) / len(ps)})
        if model in STANDARD:
            for arm in ARMS:
                candidates = sorted([e for e in es if e['institution'] == arm and not e['valid']], key=lambda e:e['seed'])
                reported = [e for e in candidates if e['reported']]
                e = (reported or candidates)[0]
                ws = [v for v in e['events'] if v['kind'] == 'worker']
                w = next((v for v in ws if v['report']), ws[0])
                advice = [v for v in e['events'] if v['kind'] == 'advisor' and v['tick'] == w['tick']]
                examples.append({'model': model, 'institution': arm, 'episode': e['id'],
                                 'path': str(path.relative_to(ROOT)), 'worker_event': w,
                                 'advisor_events': advice, 'case': e['case'],
                                 'effective_review_tick': e['effective_review_tick'],
                                 'selection': 'First faulty episode by seed with a report; otherwise first faulty episode and its first worker. Selected retrospectively, not representative.'})
    out = ROOT / 'results/commons-discrimination'; out.mkdir(exist_ok=True)
    csv_write(out / 'cells.csv', rows); csv_write(out / 'pairs.csv', pairs); csv_write(out / 'pooled.csv', pooled)
    payload = {'status': 'retrospective descriptive analysis; primary presentation chosen after seeing results',
               'hypothesis': 'Faulty helpers elicit more episode-level reports than valid helpers.',
               'primary_outcome': 'P(any report | faulty) minus P(any report | valid), over all six worker turns',
               'pooling': 'Equal weights across five arms; 60 paired conditions reuse 12 seeds. No pooled independence assumption or confirmatory p-value.',
               'rows': pooled, 'cells': rows, 'input_sha256': hashes,
               'analysis_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out / 'summary.json').write_text(json.dumps(payload, indent=2) + '\n')
    (out / 'examples.json').write_text(json.dumps(examples, indent=2, ensure_ascii=False) + '\n')
    lines = ['# Retrospective helper-validity contrasts', '', payload['status'] + '.', '',
             'H1: ' + payload['hypothesis'], '', 'Primary presentation outcome: ' + payload['primary_outcome'] + '.',
             'Reuse counts attempts, including blocked attempts. Invalid decisions remain in episode denominators. The first-report check scores only the first worker, before any feedback.', '',
             '| Model | Choice | Valid / 60 | Faulty / 60 | Faulty − valid |', '|---|---|---:|---:|---:|']
    for r in pooled:
        lines.append(f"| {r['model']} | {r['metric']} | {r['valid_episodes']} | {r['faulty_episodes']} | {r['faulty_minus_valid']:+.3f} |")
    lines += ['', payload['pooling'], 'Within-cell Wilson intervals use n=12; no observed events still permits a nonzero rate. Examples are selected illustrations, not a random sample or independently scored report-quality evaluation.', '']
    (out / 'summary.md').write_text('\n'.join(lines))
    if not args.no_figure: plot(rows)
    print(json.dumps([r for r in pooled if r['metric'] == 'report']))


if __name__ == '__main__': main()
