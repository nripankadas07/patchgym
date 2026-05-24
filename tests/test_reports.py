from __future__ import annotations

import json
from pathlib import Path

from patchgym.context_pack import write_context_pack
from patchgym.reports import write_reports
from patchgym.runner import run_tasks


def test_context_pack_and_reports_are_generated(tmp_path: Path, tinycalc_tasks) -> None:
    task = tinycalc_tasks[0]
    context = write_context_pack(task)
    results = run_tasks(tinycalc_tasks, agent="oracle", out_dir=tmp_path / "runs")
    paths = write_reports(tmp_path / "reports", "oracle", [result.to_dict() for result in results])

    task_text = (context / "CODEX_TASK.md").read_text()
    assert (context / "AGENTS.md").exists()
    assert "oracle_solution.patch" not in task_text
    assert json.loads(Path(paths["json"]).read_text())["results"][0]["solved"] is True
    assert "Tasks generated: 1" in Path(paths["markdown"]).read_text()
    assert Path(paths["html"]).read_text().startswith("<!doctype html>")
