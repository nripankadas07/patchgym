from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .artifacts import write_run_artifacts
from .gitutils import run
from .models import Task
from .report import write_json, write_markdown_report
from .workspace import (
    apply_patch,
    clean_python_bytecode,
    export_base_snapshot,
    run_command,
    run_shell,
)


@dataclass
class AgentRunResult:
    task_id: str
    solved: bool
    validation_returncode: int
    hidden_tests_applied: bool
    agent_returncode: int
    agent_duration_s: float
    patch_lines: int
    patch_file: str
    stdout_file: str
    stderr_file: str
    workspace: str
    changed_files: List[str]
    validation_command: str
    error: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


def _count_patch_lines(patch: str) -> int:
    return sum(
        1
        for line in patch.splitlines()
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    )


def _agent_environment(
    task: Task,
    workspace: Path,
    prompt_file: Path,
    metadata_file: Path,
) -> Dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "PATCHGYM_TASK_ID": task.id,
            "PATCHGYM_REPO_DIR": str(workspace),
            "PATCHGYM_PROMPT_FILE": str(prompt_file),
            "PATCHGYM_METADATA_FILE": str(metadata_file),
            "PATCHGYM_VALIDATION_COMMAND": task.validation_command,
        }
    )
    return env


def run_task(
    task: Task,
    agent: str,
    out_dir: Path,
    repo: Optional[Path] = None,
    agent_timeout: int = 300,
    validation_timeout: int = 120,
    keep_workspace: bool = False,
) -> AgentRunResult:
    task_out = Path(out_dir) / task.id
    task_out.mkdir(parents=True, exist_ok=True)
    root = tempfile.mkdtemp(prefix=f"patchgym-run-{task.id}-")
    workspace = Path(root) / "repo"
    prompt_file = Path(root) / "prompt.md"
    metadata_file = Path(root) / "task.json"

    stdout_file = task_out / "agent.stdout.txt"
    stderr_file = task_out / "agent.stderr.txt"
    patch_file = task_out / "agent.patch"
    error = ""
    hidden_applied = False
    validation_returncode = 999
    agent_result = {"returncode": 0, "duration_s": 0.0, "stdout": "", "stderr": ""}

    try:
        export_base_snapshot(task.repo_path(repo), task.base_commit, workspace)
        prompt_file.write_text(task.prompt)
        metadata_file.write_text(json.dumps(task.redacted_dict(), indent=2) + "\n")

        if agent == "noop":
            agent_result = {"returncode": 0, "duration_s": 0.0, "stdout": "", "stderr": ""}
        elif agent == "oracle":
            patch_result = apply_patch(workspace, task.solution_patch_path)
            agent_result = {
                "returncode": patch_result.returncode,
                "duration_s": patch_result.duration_s,
                "stdout": patch_result.stdout,
                "stderr": patch_result.stderr,
            }
        else:
            agent_result = run_shell(
                agent,
                workspace,
                timeout=agent_timeout,
                env=_agent_environment(task, workspace, prompt_file, metadata_file),
            )

        stdout_file.write_text(agent_result.get("stdout", ""))
        stderr_file.write_text(agent_result.get("stderr", ""))

        patch = run(["git", "diff", "--binary"], cwd=workspace).stdout
        changed_files = run(["git", "diff", "--name-only"], cwd=workspace).stdout.splitlines()
        patch_file.write_text(patch)
        patch_lines = _count_patch_lines(patch)

        if agent_result.get("returncode", 1) != 0:
            error = "agent command failed"
            solved = False
        else:
            hidden = apply_patch(workspace, task.test_patch_path, check=False)
            hidden_applied = hidden.returncode == 0
            if hidden_applied:
                clean_python_bytecode(workspace)
                validation = run_command(
                    task.validation_command,
                    workspace,
                    timeout=validation_timeout,
                )
                validation_returncode = validation["returncode"]
                (task_out / "validation.stdout.txt").write_text(validation["stdout"])
                (task_out / "validation.stderr.txt").write_text(validation["stderr"])
                solved = validation_returncode == 0
            else:
                (task_out / "validation.stderr.txt").write_text(hidden.stderr)
                solved = False
                error = "hidden test patch did not apply after agent changes"

        return AgentRunResult(
            task_id=task.id,
            solved=solved,
            validation_returncode=validation_returncode,
            hidden_tests_applied=hidden_applied,
            agent_returncode=int(agent_result.get("returncode", 1)),
            agent_duration_s=float(agent_result.get("duration_s", 0.0)),
            patch_lines=patch_lines,
            patch_file=str(patch_file),
            stdout_file=str(stdout_file),
            stderr_file=str(stderr_file),
            workspace=str(workspace) if keep_workspace else "",
            changed_files=changed_files,
            validation_command=task.validation_command,
            error=error,
        )
    except Exception as exc:  # pragma: no cover - exercised through CLI error paths
        return AgentRunResult(
            task_id=task.id,
            solved=False,
            validation_returncode=validation_returncode,
            hidden_tests_applied=hidden_applied,
            agent_returncode=int(agent_result.get("returncode", 1)),
            agent_duration_s=float(agent_result.get("duration_s", 0.0)),
            patch_lines=0,
            patch_file=str(patch_file),
            stdout_file=str(stdout_file),
            stderr_file=str(stderr_file),
            workspace=str(workspace) if keep_workspace else "",
            changed_files=[],
            validation_command=task.validation_command,
            error=str(exc),
        )


def run_tasks(
    tasks: List[Task],
    agent: str,
    out_dir: Path,
    repo: Optional[Path] = None,
    agent_timeout: int = 300,
    validation_timeout: int = 120,
    keep_workspace: bool = False,
) -> List[AgentRunResult]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = [
        run_task(
            task,
            agent=agent,
            out_dir=out_dir,
            repo=repo,
            agent_timeout=agent_timeout,
            validation_timeout=validation_timeout,
            keep_workspace=keep_workspace,
        )
        for task in tasks
    ]
    data = [result.to_dict() for result in results]
    write_json(out_dir / "report.json", {"agent": agent, "results": data})
    write_markdown_report(out_dir / "report.md", agent=agent, results=data)
    write_run_artifacts(out_dir, agent, tasks, data)
    return results
