"""Replay retained decisions without inference and verify the local freeze.

This checks record consistency, not whether the models reasoned correctly or
whether the benchmark generalizes. No model-supplied text is executed.
"""
from collections import Counter
import copy
from datetime import datetime
import hashlib
import itertools
import json
from pathlib import Path

from commons_behavior import run_episode
from study_common import INVALID, validate

ROOT = Path(__file__).resolve().parents[1]
MODELS = ['qwen-standard', 'qwen-abliterated', 'gemma-standard', 'gemma-abliterated']


def check(ok, description):
    if not ok:
        raise ValueError(description)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_run(path, freeze):
    run = json.loads((path / 'run_config.json').read_text())
    manifest = json.loads((path / 'manifest.json').read_text())
    episodes = json.loads((path / 'episodes.json').read_text())
    calls = [json.loads(line) for line in (path / 'calls.jsonl').read_text().splitlines()]
    cfg, split = run['config'], run['split']
    provenance = json.loads((ROOT / f'data/commons-model-{run["model_tag"]}.json').read_text())
    properties = json.loads((path / 'server_properties.json').read_text())
    check(Path(run['model']).name == Path(provenance['filename']).name, 'Served model differs from provenance')
    check(Path(properties['model_path']).name == Path(provenance['filename']).name, 'Server model differs from provenance')
    check(manifest['model'] == run['model'] and manifest['model_tag'] == run['model_tag'], 'Manifest model identity')
    check(cfg == json.loads((ROOT / 'configs/commons_behavior.json').read_text()), 'Run configuration differs from frozen configuration')
    expected = set(itertools.product(cfg['institutions'], cfg['validity'], cfg[split + '_seeds']))
    actual = [(e['institution'], e['valid'], e['seed']) for e in episodes]
    check(len(actual) == len(expected) and set(actual) == expected, f'{path.name}: incomplete grid')
    check(manifest['episodes'] == len(episodes), 'Manifest episode count')
    check(manifest['calls'] == len(calls), 'Manifest call count')
    check(manifest['invalid_calls'] == sum(not c['valid'] for c in calls), 'Format-failure count')
    check(manifest['total_tokens'] == sum(c.get('response', {}).get('usage', {}).get('total_tokens', 0) or 0 for c in calls), 'Token count')
    check(manifest['input_sha256'] == run['input_sha256'], 'Inputs changed during run')
    for source, sha in run['input_sha256'].items():
        p = Path(source)
        snapshot = path / (p.stem + '_snapshot' + p.suffix)
        check(digest(snapshot) == sha, f'Snapshot mismatch: {snapshot}')
        if split == 'heldout':
            check(freeze['input_sha256'][source] == sha, f'Held-out freeze mismatch: {source}')
    if split == 'heldout':
        check(datetime.fromisoformat(run['started_at']) > datetime.fromisoformat(freeze['frozen_at']), 'Run predates freeze')
    else:
        check(datetime.fromisoformat(manifest['finished_at']) < datetime.fromisoformat(freeze['frozen_at']), 'Development ended after freeze')
        check(digest(path / 'manifest.json') == freeze['development'][path.name]['manifest_sha256'], 'Development manifest changed')
    cursor = iter(calls)
    consumed = Counter()

    def replay(messages, schema, seed, episode, actor, round_index):
        c = next(cursor)
        check((c['episode'], c['actor'], c['round']) == (episode, actor, round_index), 'Call ordering')
        request = c['request']
        check(request['messages'] == messages and request['seed'] == seed, 'Prompt or seed mismatch')
        check(request['response_format']['schema'] == schema, 'Output schema mismatch')
        check(request['temperature'] == cfg['temperature'] and request['max_tokens'] == cfg['max_tokens'], 'Sampling request mismatch')
        check(request['model'] == run['model'], 'Model identity mismatch')
        if c['valid']:
            parsed = json.loads(c['response']['content'])
            check(validate(parsed, schema) and parsed == c['decision'], 'Parsed decision mismatch')
        consumed[episode] += 1
        return copy.deepcopy(c['decision'] if c['valid'] else INVALID)

    for episode in episodes:
        cell = {k: episode[k] for k in ['seed', 'valid', 'institution', 'split']}
        check(run_episode(cfg, cell, replay) == episode, f'Replay mismatch: {episode["id"]}')
        check(consumed[episode['id']] == cfg['workers'] * cfg['rounds'] + episode['advisor_calls'], 'Worker/advisor opportunities')
    check(next(cursor, None) is None, 'Unaccounted calls')
    return {'run': path.name, 'episodes': len(episodes), 'calls': len(calls),
            'episodes_sha256': digest(path / 'episodes.json'), 'calls_sha256': digest(path / 'calls.jsonl')}


def main():
    freeze = json.loads((ROOT / 'data/commons-heldout-freeze.json').read_text())
    for source, sha in freeze['input_sha256'].items():
        check(digest(ROOT / source) == sha, f'Frozen input changed: {source}')
    runs = [verify_run(ROOT / f'results/commons-{split}-{model}', freeze)
            for split in ['development', 'heldout'] for model in MODELS]
    out = ROOT / 'results/commons-behavior-summary'
    out.mkdir(exist_ok=True)
    (out / 'record-verification.json').write_text(json.dumps({
        'scope': 'Offline consistency replay; no independent human validation or new inference',
        'verified_episodes': sum(r['episodes'] for r in runs),
        'verified_calls': sum(r['calls'] for r in runs), 'runs': runs}, indent=2) + '\n')
    print(f'Verified {sum(r["episodes"] for r in runs)} episodes and their prompts, calls, results and freeze hashes.')


if __name__ == '__main__':
    main()
