"""Export public-evidence prefixes for a future local decision probe; no inference."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_prompts(data, config):
    for case in data['cases']:
        for cutoff in range(len(case['steps'])):
            # Whitelist fields: future context, outcomes and our interpretation stay out.
            evidence = [{k: step[k] for k in ['kind', 'actor', 'context', 'quotes']}
                        for step in case['steps'][:cutoff+1]]
            observation = {'episode': case['episode'], 'source_id': case['source_id'],
                           'event_time': case['time'], 'evidence': evidence}
            encoded = json.dumps(observation, ensure_ascii=False, sort_keys=True)
            for control, role in config['controls'].items():
                yield {'id': f'{case["id"]}-p{cutoff+1}-{control}', 'case_id': case['id'],
                       'cutoff': cutoff, 'control': control, 'input_sha256': hashlib.sha256(encoded.encode()).hexdigest(),
                       'messages': [{'role': 'system', 'content': role+'\n'+config['shared_instruction']+
                                     '\nRecommended actions: '+', '.join(config['recommended_actions'])},
                                    {'role': 'user', 'content': encoded}],
                       'interpretation': config['scope']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    data = json.loads((ROOT / 'data/grounded_cases.json').read_text())
    config = json.loads((ROOT / 'configs/grounded_replay.json').read_text())
    prompts = list(build_prompts(data, config))
    with args.out.open('x') as output:
        for prompt in prompts:
            output.write(json.dumps(prompt, ensure_ascii=False)+'\n')
    print(f'Exported {len(prompts)} prompts; no models called and no outcomes inferred.')


if __name__ == '__main__':
    main()
