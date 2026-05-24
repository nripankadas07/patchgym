#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/.patchgym/demo/tinycalc-$$"

python "$ROOT/tests/fixtures/make_tinycalc_repo.py" "$WORK"
cd "$WORK"

patchgym init
patchgym mine .
patchgym build .
TASK_ID="$(patchgym list --plain | head -1 | awk '{print $1}')"
echo "TASK_ID=$TASK_ID"
patchgym show "$TASK_ID" >/dev/null
patchgym verify "$TASK_ID"
patchgym context "$TASK_ID"
patchgym run "$TASK_ID" --agent "bash $ROOT/examples/custom_agent/agent.sh"
patchgym grade
patchgym report

mkdir -p "$ROOT/.patchgym/reports"
cp .patchgym/reports/report.json "$ROOT/.patchgym/reports/report.json"
cp .patchgym/reports/report.md "$ROOT/.patchgym/reports/report.md"
cp .patchgym/reports/index.html "$ROOT/.patchgym/reports/index.html"

echo "PatchGym demo complete"
