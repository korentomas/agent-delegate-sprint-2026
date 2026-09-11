"""Offline, deterministic whistleblowing-to-enforcement ablation; no model calls.

Inspired by arXiv:2609.04170, not a reproduction. The initial artifact and
subsequent reuse attempts are scripted. All effects are in-memory records.
"""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLS = ('log_only', 'review_queue', 'delegate', 'matched_monitor', 'quarantine', 'verified_gate')


def run_case(control, delay, visible, suppressed, bypass, invalid):
    if control not in CONTROLS or delay < 0:
        raise ValueError('Unknown control or negative delay')
    report_tick = 1 if visible else None
    delivery_tick = 1 if visible and (not suppressed or bypass) else None
    actionable = control in ('review_queue', 'delegate', 'matched_monitor', 'quarantine')
    decision_tick = delivery_tick + delay if actionable and delivery_tick is not None else None
    quarantined = False
    removed = False
    accepted = []
    trace = []
    false_blocks = exposures = post_report = rejected = 0
    # Six different workers/tasks; each tries the same library technique once.
    # Decisions happen before that tick's action. Tick 0 cannot be undone.
    for tick in range(6):
        if tick == report_tick:
            trace.append({'tick': tick, 'event': 'report', 'claim': 'artifact_invalid', 'correct': invalid})
        if tick == delivery_tick:
            trace.append({'tick': tick, 'event': 'delivered'})
            if control == 'quarantine':
                quarantined = True
                trace.append({'tick': tick, 'event': 'quarantine'})
        if tick == decision_tick:
            quarantined = False
            removed = invalid
            trace.append({'tick': tick, 'event': 'review', 'verdict': 'remove' if invalid else 'release',
                          'reopened_tasks': len(accepted) if invalid else 0})
        if removed or quarantined:
            if not invalid:
                false_blocks += 1
            trace.append({'tick': tick, 'event': 'reuse_blocked', 'valid_work': not invalid})
            continue
        exposures += 1
        if control == 'verified_gate' and invalid:
            rejected += 1
            trace.append({'tick': tick, 'event': 'rejected_by_validator'})
            continue
        accepted.append(tick)
        if invalid and report_tick is not None and tick >= report_tick:
            post_report += 1
        trace.append({'tick': tick, 'event': 'accepted', 'valid': not invalid, 'task': tick})
    return {'control': control, 'delay': delay, 'visible': visible, 'suppressed': suppressed,
            'bypass': bypass, 'invalid_artifact': invalid, 'report_tick': report_tick,
            'delivery_tick': delivery_tick, 'decision_tick': decision_tick,
            'effective_decision_tick': decision_tick if decision_tick is not None and decision_tick < 6 else None,
            'exposures': exposures, 'invalid_accepted': len(accepted) if invalid else 0,
            'invalid_after_report': post_report, 'valid_completed': 0 if invalid else len(accepted),
            'false_blocks': false_blocks, 'gate_rejections': rejected,
            'trace': trace}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cases = [run_case(*cell) for cell in itertools.product(CONTROLS, (0, 2, 6), (False, True),
                                                         (False, True), (False, True), (False, True))]
    (args.out / 'traces.json').write_text(json.dumps(cases, indent=2) + '\n')
    columns = [k for k in cases[0] if k != 'trace']
    with (args.out / 'summary.csv').open('w') as f:
        writer = csv.DictWriter(f, columns, lineterminator='\n')
        writer.writeheader()
        writer.writerows({k: c[k] for k in columns} for c in cases)
    text = ['# Commons response: deterministic ablation', '',
            f'{len(cases)} design cells. Scripted reports, reuse and correct review; no LLM inference or confidence intervals.', '',
            'Main slice: visible report, unsuppressed relay, bypass on. Invalid acceptances by human delay; false blocks on valid work.', '',
            '| Control | Invalid: delay 0 | delay 2 | delay 6 | False blocks: delay 0 / 2 / 6 |',
            '|---|---:|---:|---:|---|']
    for control in CONTROLS:
        bad = [run_case(control, d, True, False, True, True)['invalid_accepted'] for d in (0, 2, 6)]
        benign = [run_case(control, d, True, False, True, False)['false_blocks'] for d in (0, 2, 6)]
        text.append(f'| {control} | ' + ' | '.join(map(str, bad)) + ' | ' + ' / '.join(map(str, benign)) + ' |')
    text += ['', 'Receipt alone does not stop reuse. Quarantine trades immediate containment for false-report cost. '
             'The queue, delegate and matched monitor have identical information and review rules, so their equality is constructed. '
             'A perfect semantic gate is an oracle upper bound on coverage, not an implemented Lean verifier. '
             'Zero delay still permits the seeded tick-0 event. Invisible or suppressed reports defeat reactive controls; '
             'bypass restores delivery only for reports that exist. See docs/commons-response-design.md.', '']
    (args.out / 'summary.md').write_text('\n'.join(text))
    sources = ['scripts/commons_response.py', 'docs/commons-response-design.md']
    (args.out / 'manifest.json').write_text(json.dumps({'cells': len(cases), 'source': 'https://arxiv.org/html/2609.04170v1',
        'kind': 'deterministic mechanism ablation; scripted seed, no emergent behavior',
        'sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources}}, indent=2) + '\n')
    print(json.dumps({'cells': len(cases), 'out': str(args.out)}))


if __name__ == '__main__':
    main()
