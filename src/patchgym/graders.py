from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


def grade_report(run_report: Path) -> Dict[str, int]:
    data = json.loads(Path(run_report).read_text())
    results = data.get("results", [])
    solved = sum(1 for row in results if row.get("solved"))
    return {"solved": solved, "total": len(results)}
