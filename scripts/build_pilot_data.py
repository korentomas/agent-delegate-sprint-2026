"""Export recorded local model choices and sourced behavioral annotations."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    models = []
    for ident, label, directory in [
        ('qwen4b', 'Qwen3-4B Instruct · Q4_K_M', 'local-pilot-qwen4b'),
        ('qwen27b', 'Qwen3.8-27B · ROCm FP4', 'local-pilot-qwen27b'),
    ]:
        folder = ROOT / 'results' / directory
        models.append(dict(id=ident, label=label, directory=directory,
                           manifest=json.loads((folder / 'manifest.json').read_text()),
                           episodes=json.loads((folder / 'episodes.json').read_text()),
                           calls_sha256=hashlib.sha256((folder / 'calls.jsonl').read_bytes()).hexdigest()))
    out = ROOT / 'web/data'
    (out / 'local-pilots.json').write_text(json.dumps({'models': models}, ensure_ascii=False, separators=(',', ':')) + '\n')
    (out / 'behavioral-evidence.json').write_bytes((ROOT / 'data/behavioral-evidence.json').read_bytes())
    print('Exported two recorded local pilots and eight sourced behavior annotations.')


if __name__ == '__main__':
    main()
