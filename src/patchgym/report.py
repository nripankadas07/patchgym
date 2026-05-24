from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def write_markdown_report(path: Path, agent: str, results: Iterable[Dict]) -> None:
    rows: List[Dict] = list(results)
    solved = sum(1 for row in rows if row.get("solved"))
    total = len(rows)
    lines = [
        "# PatchGym Report",
        "",
        f"Agent: `{agent}`",
        "",
        f"Score: **{solved}/{total}**",
        "",
        "| Task | Result | Validation | Agent Time | Patch Lines |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        result = "pass" if row.get("solved") else "fail"
        lines.append(
            "| `{task_id}` | {result} | {returncode} | {duration:.2f}s | {patch_lines} |".format(
                task_id=row["task_id"],
                result=result,
                returncode=row.get("validation_returncode", ""),
                duration=row.get("agent_duration_s", 0.0),
                patch_lines=row.get("patch_lines", 0),
            )
        )
    lines.extend(
        [
            "",
            "A task passes when PatchGym can apply the hidden tests after the agent run and the validation command exits with code 0.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))
