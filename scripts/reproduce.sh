#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-results/reproduced-$(date -u +%Y%m%dT%H%M%SZ)}"
python3 -m unittest discover -s tests -v
python3 -m agent_delegate.harness --out "$OUT"
python3 -m agent_delegate.audit "$OUT"
python3 scripts/plots.py "$OUT"
python3 scripts/compare.py results/final "$OUT"
