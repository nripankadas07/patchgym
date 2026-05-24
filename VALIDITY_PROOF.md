# PatchGym Validity Proof

Task id: `d44a5852-fix-clamp-upper-bound-1e98b1ca`

Base commit: `4164c1a5fee430a8a7e5829332b1534ea34684ed`

Solution commit: `d44a5852b03fdaa096e57229ecd24d98643cce66`

Fixture repository: `/tmp/patchgym-manual/tinycalc`

Task directory: `/tmp/patchgym-manual/tinycalc/.patchgym/tasks/d44a5852-fix-clamp-upper-bound-1e98b1ca`

## Commands

```bash
. /tmp/patchgym-verify/.venv/bin/activate
TASK_ID="$(cd /tmp/patchgym-manual/tinycalc && patchgym list --plain | head -1 | awk '{print $1}')"
TASK_DIR="/tmp/patchgym-manual/tinycalc/.patchgym/tasks/$TASK_ID"
BASE_COMMIT="$(python - <<PY
import json
from pathlib import Path
print(json.loads(Path('$TASK_DIR/task.json').read_text())['base_commit'])
PY
)"
TARGET_COMMIT="$(python - <<PY
import json
from pathlib import Path
print(json.loads(Path('$TASK_DIR/task.json').read_text())['target_commit'])
PY
)"
mkdir -p /tmp/patchgym-validity/base /tmp/patchgym-validity/hidden /tmp/patchgym-validity/oracle
for d in base hidden oracle; do
  git -C /tmp/patchgym-manual/tinycalc archive "$BASE_COMMIT" | tar -x -C "/tmp/patchgym-validity/$d"
done

cd /tmp/patchgym-validity/base
python -m pytest -q

cd /tmp/patchgym-validity/hidden
git apply "$TASK_DIR/hidden_tests.patch"
python -m pytest -q

cd /tmp/patchgym-validity/oracle
git apply "$TASK_DIR/hidden_tests.patch"
git apply "$TASK_DIR/oracle_solution.patch"
python -m pytest -q
```

## Observed Results

State A: base only

```text
..                                                                       [100%]
2 passed in 0.00s
STATE_A_EXIT=0
```

State B: base + hidden tests

```text
..F                                                                      [100%]
FAILED tests/test_tinycalc.py::test_upper_bound - assert 0 == 10
1 failed, 2 passed in 0.01s
STATE_B_EXIT=1
```

State C: base + hidden tests + oracle source patch

```text
...                                                                      [100%]
3 passed in 0.00s
STATE_C_EXIT=0
```

## Explanation

This is a valid coding-agent task because the base repository passes its original tests, the hidden regression test fails against the base implementation, and the historical oracle source patch makes the hidden test pass.
