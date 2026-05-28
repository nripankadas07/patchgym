from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .models import Task
from .report import write_json

TRACE_SCHEMA = "patchgym.trace.v1"
MANIFEST_SCHEMA = "patchgym.run_manifest.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _relative(path: Path, root: Path) -> str:
    path = Path(path)
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def artifact_entry(path: Path, root: Path) -> Dict[str, Any]:
    path = Path(path)
    return {
        "path": _relative(path, root),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _maybe_artifact(path: Path, root: Path) -> Dict[str, Any]:
    return artifact_entry(path, root) if Path(path).exists() else {}


def build_run_manifest(
    out_dir: Path,
    agent: str,
    tasks: Iterable[Task],
    rows: List[Dict],
) -> Dict[str, Any]:
    out_dir = Path(out_dir)
    task_by_id = {task.id: task for task in tasks}
    task_rows: List[Dict[str, Any]] = []
    for row in rows:
        task = task_by_id[row["task_id"]]
        task_dir = out_dir / task.id
        artifacts = {
            "agent_patch": _maybe_artifact(Path(row["patch_file"]), out_dir),
            "agent_stdout": _maybe_artifact(Path(row["stdout_file"]), out_dir),
            "agent_stderr": _maybe_artifact(Path(row["stderr_file"]), out_dir),
            "validation_stdout": _maybe_artifact(task_dir / "validation.stdout.txt", out_dir),
            "validation_stderr": _maybe_artifact(task_dir / "validation.stderr.txt", out_dir),
        }
        task_rows.append(
            {
                "task_id": task.id,
                "base_commit": task.base_commit,
                "target_commit": task.target_commit,
                "commit_subject": task.commit_subject,
                "source_repo": task.source_repo,
                "validation_command": task.validation_command,
                "hidden_tests_patch_sha256": sha256_file(task.test_patch_path),
                "oracle_solution_patch_sha256": sha256_file(task.solution_patch_path),
                "result": {
                    "solved": bool(row.get("solved")),
                    "agent_returncode": row.get("agent_returncode"),
                    "validation_returncode": row.get("validation_returncode"),
                    "hidden_tests_applied": row.get("hidden_tests_applied"),
                    "agent_duration_s": row.get("agent_duration_s"),
                    "patch_lines": row.get("patch_lines"),
                    "changed_files": row.get("changed_files") or [],
                    "error": row.get("error", ""),
                },
                "artifacts": {key: value for key, value in artifacts.items() if value},
            }
        )
    solved = sum(1 for row in rows if row.get("solved"))
    return {
        "schema_version": MANIFEST_SCHEMA,
        "created_at": _utc_now(),
        "agent": agent,
        "run_dir": str(out_dir),
        "totals": {"tasks": len(rows), "solved": solved, "failed": len(rows) - solved},
        "tasks": task_rows,
    }


def trace_events(agent: str, rows: List[Dict]) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = [
        {
            "schema_version": TRACE_SCHEMA,
            "actor": "patchgym",
            "tool": "runner",
            "action": "run_start",
            "status": "ok",
            "input": {"agent": agent, "tasks": len(rows)},
            "output": "",
        }
    ]
    for row in rows:
        task_id = row["task_id"]
        agent_ok = int(row.get("agent_returncode", 1)) == 0
        solved = bool(row.get("solved"))
        events.extend(
            [
                {
                    "schema_version": TRACE_SCHEMA,
                    "actor": "patchgym",
                    "tool": "workspace",
                    "action": "prepare_task",
                    "status": "ok",
                    "input": {"task_id": task_id},
                    "output": {"validation_command": row.get("validation_command", "")},
                },
                {
                    "schema_version": TRACE_SCHEMA,
                    "actor": "agent",
                    "tool": "agent_command",
                    "action": "run",
                    "status": "ok" if agent_ok else "error",
                    "input": {"task_id": task_id, "agent": agent},
                    "output": {
                        "returncode": row.get("agent_returncode"),
                        "duration_s": row.get("agent_duration_s"),
                    },
                },
                {
                    "schema_version": TRACE_SCHEMA,
                    "actor": "patchgym",
                    "tool": "git",
                    "action": "capture_patch",
                    "status": "ok",
                    "input": {"task_id": task_id},
                    "output": {
                        "patch_lines": row.get("patch_lines"),
                        "changed_files": row.get("changed_files") or [],
                    },
                },
                {
                    "schema_version": TRACE_SCHEMA,
                    "actor": "patchgym",
                    "tool": "hidden_tests",
                    "action": "apply",
                    "status": "ok" if row.get("hidden_tests_applied") else "error",
                    "input": {"task_id": task_id},
                    "output": {"hidden_tests_applied": row.get("hidden_tests_applied")},
                },
                {
                    "schema_version": TRACE_SCHEMA,
                    "actor": "patchgym",
                    "tool": "validation",
                    "action": "run",
                    "status": "ok" if row.get("validation_returncode") == 0 else "error",
                    "input": {"task_id": task_id, "command": row.get("validation_command", "")},
                    "output": {"returncode": row.get("validation_returncode")},
                },
                {
                    "schema_version": TRACE_SCHEMA,
                    "actor": "patchgym",
                    "tool": "grader",
                    "action": "task_result",
                    "status": "ok" if solved else "error",
                    "input": {"task_id": task_id},
                    "output": {"solved": solved, "error": row.get("error", "")},
                },
            ]
        )
    events.append(
        {
            "schema_version": TRACE_SCHEMA,
            "actor": "patchgym",
            "tool": "runner",
            "action": "run_summary",
            "status": "ok",
            "input": {"agent": agent},
            "output": {
                "tasks": len(rows),
                "solved": sum(1 for row in rows if row.get("solved")),
            },
        }
    )
    return events


def write_jsonl(path: Path, events: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, sort_keys=True) + "\n")


def write_run_artifacts(
    out_dir: Path,
    agent: str,
    tasks: Iterable[Task],
    rows: List[Dict],
) -> Dict[str, str]:
    out_dir = Path(out_dir)
    manifest = build_run_manifest(out_dir, agent, tasks, rows)
    manifest_path = out_dir / "manifest.json"
    trace_path = out_dir / "trace.jsonl"
    write_json(manifest_path, manifest)
    write_jsonl(trace_path, trace_events(agent, rows))
    return {"manifest": str(manifest_path), "trace": str(trace_path)}
