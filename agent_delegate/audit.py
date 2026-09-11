"""Verify hash chains against separately retained checkpoints and check semantics."""
import argparse,json
from pathlib import Path
from .harness import verify,semantic_audit

def main():
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args()
    checkpoints=json.loads((a.directory/'checkpoints.json').read_text());errors=[]
    actual={p.stem for p in (a.directory/'traces').glob('*.jsonl')}
    if actual!=set(checkpoints):errors.append('trace inventory differs from checkpoints')
    for name,cp in checkpoints.items():
        path=a.directory/'traces'/f'{name}.jsonl'
        if not path.exists():errors.append(f'missing {name}');continue
        try:
            rows=[json.loads(line) for line in path.read_text().splitlines()]
            errors.extend(f'{name}: {e}' for e in verify(rows,cp['head'],cp['records'])+semantic_audit(rows))
        except (ValueError,KeyError,TypeError) as e:errors.append(f'{name}: malformed trace {e}')
    print(json.dumps({'checked':len(checkpoints),'errors':errors,'assurance':'checkpoints must be retained outside writer control for tamper evidence'},indent=2))
    raise SystemExit(bool(errors))
if __name__=='__main__':main()
