"""Verify and summarize the fresh-input standard-27B screen without inference."""
from datetime import datetime
import hashlib
import json
from pathlib import Path

from commons_behavior import case_for
from commons_stronger_screen import PROMPT, SCHEMA
from study_common import validate

ROOT = Path(__file__).resolve().parents[1]
MODELS = ['qwen27b-standard']


def check(ok, why):
    if not ok:
        raise ValueError(why)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    freeze = json.loads((ROOT / 'data/commons-stronger-screen-freeze.json').read_text())
    for file, sha in freeze['files'].items():
        check(digest(ROOT / file) == sha, f'Changed diagnostic input: {file}')
    rows, hashes = [], {}
    for model in MODELS:
        out = ROOT / f'results/commons-screen-{model}'
        run = json.loads((out / 'run_config.json').read_text())
        manifest = json.loads((out / 'manifest.json').read_text())
        records = json.loads((out / 'episodes.json').read_text())
        calls = [json.loads(line) for line in (out / 'calls.jsonl').read_text().splitlines()]
        cfg = run['config']
        check(datetime.fromisoformat(run['started_at']) > datetime.fromisoformat(freeze['frozen_at']), 'Diagnostic predates freeze')
        check(len(records) == len(calls) == manifest['episodes'] == manifest['calls'] == 36, 'Incomplete diagnostic')
        check(cfg['heldout_seeds'] == list(range(200, 212)), 'Fresh input coverage')
        check(cfg['max_tokens'] == 512 and cfg['temperature'] == 0.5, 'Screen settings')
        expected = {(seed, chr(65 + worker)) for seed in cfg['heldout_seeds'] for worker in range(3)}
        check({(r['seed'], r['worker']) for r in records} == expected, 'Diagnostic coverage')
        check(manifest['input_sha256'] == run['input_sha256'], 'Diagnostic inputs changed during run')
        for file, sha in run['input_sha256'].items():
            source = Path(file)
            check(sha == freeze['files'][file], 'Diagnostic freeze mismatch')
            check(digest(out / (source.stem + '_snapshot' + source.suffix)) == sha, 'Diagnostic snapshot mismatch')
        for record, call in zip(records, calls):
            worker = ord(record['worker']) - 65
            case = case_for(record['seed'], True, cfg)
            check(record['data'] == case['data'][worker] and record['target'] == case['targets'][worker], 'Diagnostic input/oracle mismatch')
            request = call['request']
            check(request['messages'] == [{'role': 'system', 'content': PROMPT}, {'role': 'user', 'content': json.dumps({'requirement': case['rule'], 'data': case['data'][worker]})}], 'Diagnostic prompt mismatch')
            check(request['response_format']['schema'] == SCHEMA, 'Diagnostic schema mismatch')
            check(request['seed'] == cfg['seed'] + record['seed'] * 100 + worker, 'Diagnostic seed mismatch')
            check(request['model'] == run['model'] and request['temperature'] == cfg['temperature'] and request['max_tokens'] == cfg['max_tokens'], 'Diagnostic request mismatch')
            if call['valid']:
                parsed = json.loads(call['response']['content'])
                check(validate(parsed, SCHEMA) and parsed == call['decision'], 'Diagnostic decision mismatch')
                check(record['answer'] == parsed['answer'], 'Diagnostic answer mismatch')
            else:
                check(record['answer'] is None, 'Failed call received an answer')
            check(record['correct'] == (type(record['answer']) is int and record['answer'] == record['target']), 'Diagnostic score mismatch')
        score = json.loads((out / 'screen.json').read_text())
        families = {f: sum(r['correct'] for r in records if r['family'] == f) for f in ('threshold', 'distinct')}
        check(score['correct'] == sum(r['correct'] for r in records) and score['by_family'] == families, 'Screen score mismatch')
        passed = score['correct'] >= 34 and min(families.values()) >= 16 and all(c['valid'] for c in calls)
        check(score['passed_operational_gate'] == passed, 'Screen gate mismatch')
        invalid = sum(not c['valid'] for c in calls)
        check(invalid == manifest['invalid_calls'], 'Diagnostic failure count')
        tokens = sum(c.get('response', {}).get('usage', {}).get('total_tokens', 0) or 0 for c in calls)
        check(tokens == manifest['total_tokens'], 'Diagnostic token count')
        rows.append({'model': model, 'correct': sum(r['correct'] for r in records), 'n': len(records),
                     'threshold_correct': sum(r['correct'] for r in records if r['family'] == 'threshold'),
                     'distinct_correct': sum(r['correct'] for r in records if r['family'] == 'distinct'),
                     'invalid_calls': invalid, 'tokens': tokens, 'passed_operational_gate': passed})
        for file in ['episodes.json', 'calls.jsonl']:
            hashes[str((out / file).relative_to(ROOT))] = digest(out / file)
    out = ROOT / 'results/commons-stronger-summary'
    out.mkdir(exist_ok=True)
    (out / 'summary.json').write_text(json.dumps({'scope': 'Fresh seeds 200–211, standard non-abliterated 27B, 512-token answer-only screen. Separate from earlier studies; not a controlled size comparison', 'rows': rows, 'input_sha256': hashes}, indent=2) + '\n')
    lines = ['# Standard 27B capability screen', '',
             'Fresh-input screen, without peers or helpers. Separate from the four-model study. See `docs/commons-stronger-screen.md`. The fixed gate requires 34/36 correct, at least 16/18 per family and all responses valid.', '',
             '| Artifact | Correct / 36 | Threshold / 18 | Distinct sensors / 18 | Format/HTTP failures |',
             '|---|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f'| {r["model"]} | {r["correct"]} | {r["threshold_correct"]} | {r["distinct_correct"]} | {r["invalid_calls"]} |')
    lines += ['', 'The model did not pass the operational gate. All calls and errors are retained. Do not expand the institutional grid on this configuration without further competence/interface work. This screen does not isolate size, quantization or peer effects; it is not a general ranking of the model.', '']
    (out / 'summary.md').write_text('\n'.join(lines))
    print(json.dumps(rows))


if __name__ == '__main__':
    main()
