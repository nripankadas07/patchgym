from __future__ import annotations

import json
import sys
from pathlib import Path

from patchgym.graders import grade_report
from patchgym.runner import run_tasks


def test_noop_fails_and_oracle_passes(tmp_path: Path, tinycalc_tasks) -> None:
    noop = run_tasks(tinycalc_tasks, agent="noop", out_dir=tmp_path / "runs" / "noop")
    oracle = run_tasks(tinycalc_tasks, agent="oracle", out_dir=tmp_path / "runs" / "oracle")

    assert noop[0].solved is False
    assert oracle[0].solved is True
    assert grade_report(tmp_path / "runs" / "oracle" / "report.json") == {"solved": 1, "total": 1}

    manifest = json.loads((tmp_path / "runs" / "oracle" / "manifest.json").read_text())
    trace_lines = (tmp_path / "runs" / "oracle" / "trace.jsonl").read_text().splitlines()
    assert manifest["schema_version"] == "patchgym.run_manifest.v1"
    assert manifest["totals"] == {"tasks": 1, "solved": 1, "failed": 0}
    assert manifest["tasks"][0]["hidden_tests_patch_sha256"]
    assert manifest["tasks"][0]["oracle_solution_patch_sha256"]
    assert "agent_patch" in manifest["tasks"][0]["artifacts"]
    assert any('"action": "run_summary"' in line for line in trace_lines)


def test_shell_agent_solves_and_timeout_is_enforced(tmp_path: Path, tinycalc_tasks) -> None:
    agent = Path.cwd() / "examples" / "custom_agent" / "agent.sh"
    solved = run_tasks(tinycalc_tasks, agent=f"bash {agent}", out_dir=tmp_path / "runs" / "agent")
    timed_out = run_tasks(
        tinycalc_tasks,
        agent=f"{sys.executable} -c \"import time; time.sleep(2)\"",
        out_dir=tmp_path / "runs" / "timeout",
        agent_timeout=1,
    )

    assert solved[0].solved is True
    assert "tinycalc.py" in solved[0].changed_files
    assert timed_out[0].solved is False
    assert "timed out" in timed_out[0].error.lower()
