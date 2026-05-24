from __future__ import annotations

import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

from .models import Task
from .workspace import apply_patch, clean_python_bytecode, export_base_snapshot, run_command


@dataclass
class VerificationResult:
    task_id: str
    valid: bool
    base_with_hidden_tests_failed: bool
    oracle_passed: bool
    base_returncode: int
    oracle_returncode: int
    workspace: str
    error: str = ""

    def to_dict(self):
        return asdict(self)


def verify_task(
    task: Task,
    repo: Optional[Path] = None,
    timeout: int = 120,
    keep_workspace: bool = False,
) -> VerificationResult:
    root = tempfile.mkdtemp(prefix=f"patchgym-verify-{task.id}-")
    workspace = Path(root) / "repo"
    error = ""
    base_result = {"returncode": 999, "stdout": "", "stderr": ""}
    oracle_result = {"returncode": 999, "stdout": "", "stderr": ""}

    try:
        export_base_snapshot(task.repo_path(repo), task.base_commit, workspace)
        apply_patch(workspace, task.test_patch_path)
        clean_python_bytecode(workspace)
        base_result = run_command(task.validation_command, workspace, timeout=timeout)
        base_failed = base_result["returncode"] != 0
        apply_patch(workspace, task.solution_patch_path)
        clean_python_bytecode(workspace)
        oracle_result = run_command(task.validation_command, workspace, timeout=timeout)
        oracle_passed = oracle_result["returncode"] == 0
        return VerificationResult(
            task_id=task.id,
            valid=base_failed and oracle_passed,
            base_with_hidden_tests_failed=base_failed,
            oracle_passed=oracle_passed,
            base_returncode=base_result["returncode"],
            oracle_returncode=oracle_result["returncode"],
            workspace=str(workspace) if keep_workspace else "",
        )
    except Exception as exc:  # pragma: no cover - exercised through CLI error paths
        error = str(exc)
        return VerificationResult(
            task_id=task.id,
            valid=False,
            base_with_hidden_tests_failed=base_result["returncode"] != 0,
            oracle_passed=False,
            base_returncode=base_result["returncode"],
            oracle_returncode=oracle_result["returncode"],
            workspace=str(workspace) if keep_workspace else "",
            error=error,
        )


def verify_tasks(
    tasks: List[Task],
    repo: Optional[Path] = None,
    timeout: int = 120,
    keep_workspace: bool = False,
) -> List[VerificationResult]:
    return [
        verify_task(task, repo=repo, timeout=timeout, keep_workspace=keep_workspace)
        for task in tasks
    ]
