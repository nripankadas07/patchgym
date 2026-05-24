from __future__ import annotations

from pathlib import Path

from .models import Task


def write_context_pack(task: Task) -> Path:
    out_dir = task.task_dir / "context"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "CODEX_TASK.md").write_text(
        "\n".join(
            [
                f"# PatchGym Task: {task.id}",
                "",
                task.prompt,
                "",
                "Hidden tests and oracle patches are intentionally not included "
                "in this context pack.",
                "",
            ]
        )
    )
    (out_dir / "AGENTS.md").write_text(
        "\n".join(
            [
                "# Agent Instructions",
                "",
                "Edit the working tree to satisfy the task prompt.",
                "Run the validation command when useful.",
                "Do not inspect future Git history, hidden test patches, "
                "or oracle solution patches.",
                "",
            ]
        )
    )
    return out_dir
