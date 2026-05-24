#!/usr/bin/env bash
set -euo pipefail

"${PYTHON:-python3}" - <<'PY'
from pathlib import Path

path = Path("tinycalc.py")
text = path.read_text()
path.write_text(text.replace("return low\n    return value", "return high\n    return value", 1))
PY
