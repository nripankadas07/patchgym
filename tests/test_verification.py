from __future__ import annotations

import sys
from pathlib import Path

from patchgym.verify import verify_tasks
from patchgym.workspace import apply_patch, export_base_snapshot, run_command


def test_base_hidden_fails_and_oracle_passes(tmp_path: Path, tinycalc_tasks) -> None:
    task = tinycalc_tasks[0]

    base = export_base_snapshot(task.repo_path(), task.base_commit, tmp_path / "base")
    hidden = export_base_snapshot(task.repo_path(), task.base_commit, tmp_path / "hidden")
    oracle = export_base_snapshot(task.repo_path(), task.base_commit, tmp_path / "oracle")

    base_result = run_command(f"{sys.executable} -m pytest -q", base, timeout=60)

    apply_patch(hidden, task.test_patch_path)
    hidden_result = run_command(f"{sys.executable} -m pytest -q", hidden, timeout=60)

    apply_patch(oracle, task.test_patch_path)
    apply_patch(oracle, task.solution_patch_path)
    oracle_result = run_command(f"{sys.executable} -m pytest -q", oracle, timeout=60)

    assert base_result["returncode"] == 0
    assert hidden_result["returncode"] != 0
    assert oracle_result["returncode"] == 0


def test_verifier_marks_task_valid(tinycalc_tasks) -> None:
    results = verify_tasks(tinycalc_tasks)

    assert len(results) == 1
    assert results[0].valid
    assert results[0].base_with_hidden_tests_failed
    assert results[0].oracle_passed
