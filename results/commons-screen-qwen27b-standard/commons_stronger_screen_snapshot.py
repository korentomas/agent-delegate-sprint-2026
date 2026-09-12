"""Fresh-input capability screen for the standard 27B; separate from all earlier studies."""
import argparse
import json
from pathlib import Path
import random
import time

from commons_behavior import case_for
from study_common import (Recorder, check_loopback, discover_model, prepare_out,
                          snapshot_inputs, sha256_file, stamp, write_json,
                          write_manifest, request_json)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = {'type': 'object', 'properties': {'answer': {'type': 'integer'}},
          'required': ['answer'], 'additionalProperties': False}
PROMPT = ('Solve the counting task from its requirement and data. Compute your own answer. '
          'Return only JSON containing the integer answer: {"answer": integer}.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--model-tag', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads((ROOT / 'configs/commons_behavior.json').read_text())
    cfg.update(heldout_seeds=list(range(200, 212)), max_tokens=512, timeout_seconds=120)
    inputs = [ROOT / p for p in ['configs/commons_behavior.json', 'docs/commons-stronger-screen.md',
              'scripts/commons_stronger_screen.py', 'scripts/commons_behavior.py', 'scripts/study_common.py',
              f'data/commons-model-{args.model_tag}.json']]
    base = check_loopback(args.base_url)
    model = discover_model(base)
    out = prepare_out(args.out, False)
    snapshot_inputs(out, inputs)
    props = request_json(base, '/props')
    write_json(out / 'server_properties.json', {k: props.get(k) for k in [
        'build_info', 'model_alias', 'model_path', 'model_ftype', 'total_slots',
        'default_generation_settings', 'chat_template', 'chat_template_caps']})
    run = {'started_at': stamp(), 'model': model, 'model_tag': args.model_tag,
           'schema_style': 'llama', 'split': 'posthoc-fresh-capability-screen', 'config': cfg,
           'input_sha256': {str(f.relative_to(ROOT)): sha256_file(f) for f in inputs}}
    write_json(out / 'run_config.json', run)
    recorder = Recorder(base, model, cfg, out)
    cells = [(seed, worker) for seed in cfg['heldout_seeds'] for worker in range(cfg['workers'])]
    random.Random('stronger-screen-20260912').shuffle(cells)
    records = []
    start = time.perf_counter()
    for seed, worker in cells:
        case = case_for(seed, True, cfg)
        eid = f'screen-s{seed}-{chr(65 + worker)}'
        messages = [{'role': 'system', 'content': PROMPT}, {'role': 'user', 'content': json.dumps({
            'requirement': case['rule'], 'data': case['data'][worker]})}]
        decision = recorder.call(messages, SCHEMA, cfg['seed'] + seed * 100 + worker, eid, chr(65 + worker), 0)
        answer = decision.get('answer')
        records.append({'id': eid, 'seed': seed, 'worker': chr(65 + worker), 'family': case['family'],
                        'data': case['data'][worker], 'requirement': case['rule'],
                        'target': case['targets'][worker], 'answer': answer,
                        'correct': type(answer) is int and answer == case['targets'][worker]})
        write_json(out / 'episodes.json', records)
    write_manifest(out, run, inputs, records, start, 0,
                   'Fresh-input capability screen, chosen after the four-model study. Not a randomized model-size comparison.',
                   'Standard 27B UD-Q4_K_XL, upstream llama.cpp HIP, context 8192, one slot, no speculative decoding, thinking disabled at server and request, 512 output tokens.')
    by_family = {f: sum(r['correct'] for r in records if r['family'] == f) for f in sorted({r['family'] for r in records})}
    passed = sum(r['correct'] for r in records) >= 34 and all(n >= 16 for n in by_family.values()) and recorder.invalid == 0
    write_json(out / 'screen.json', {'correct': sum(r['correct'] for r in records), 'total': len(records), 'by_family': by_family, 'invalid': recorder.invalid, 'passed_operational_gate': passed, 'gate': '34/36 total, at least 16/18 per family, all responses valid'})
    print(json.dumps({'model': args.model_tag, 'correct': sum(r['correct'] for r in records), 'calls': len(records)}), flush=True)


if __name__ == '__main__':
    main()
