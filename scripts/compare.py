import sys
from pathlib import Path
left,right=map(Path,sys.argv[1:])
for name in ['runs.csv','summary.csv','replay.json','checkpoints.json','compliance.json']:
 if (left/name).read_bytes()!=(right/name).read_bytes():raise SystemExit('Mismatch: '+name)
print('Exact reproduction: all results, checkpoints and compliance summaries match. Runtime is excluded.')
