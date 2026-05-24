from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


SCHEMA_VERSION = "0.1"


@dataclass
class Task:
    id: str
    source_repo: str
    base_commit: str
    target_commit: str
    commit_subject: str
    validation_command: str
    prompt: str
    test_patch: str = "hidden_tests.patch"
    solution_patch: str = "oracle_solution.patch"
    test_files: List[str] = field(default_factory=list)
    solution_files: List[str] = field(default_factory=list)
    created_at: str = ""
    schema_version: str = SCHEMA_VERSION
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def task_dir(self) -> Path:
        if not hasattr(self, "_task_dir"):
            raise ValueError("task_dir is only available for loaded or saved tasks")
        return getattr(self, "_task_dir")

    def with_task_dir(self, task_dir: Path) -> "Task":
        setattr(self, "_task_dir", task_dir)
        return self

    @property
    def test_patch_path(self) -> Path:
        return self.task_dir / self.test_patch

    @property
    def solution_patch_path(self) -> Path:
        return self.task_dir / self.solution_patch

    def repo_path(self, override: Optional[Path] = None) -> Path:
        return Path(override if override else self.source_repo).expanduser().resolve()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def redacted_dict(self) -> Dict[str, Any]:
        data = self.to_dict()
        data.pop("source_repo", None)
        data.pop("solution_patch", None)
        data.pop("test_patch", None)
        data.pop("target_commit", None)
        return data

    def save(self, task_dir: Path) -> None:
        task_dir.mkdir(parents=True, exist_ok=True)
        self.with_task_dir(task_dir)
        (task_dir / "task.json").write_text(json.dumps(self.to_dict(), indent=2) + "\n")

    @classmethod
    def load(cls, path: Path) -> "Task":
        path = Path(path)
        task_file = path / "task.json" if path.is_dir() else path
        data = json.loads(task_file.read_text())
        task = cls(**data)
        return task.with_task_dir(task_file.parent)


def load_tasks(path: Path) -> List[Task]:
    path = Path(path)
    if path.is_file():
        return [Task.load(path)]
    tasks = [Task.load(task_json) for task_json in sorted(path.glob("*/task.json"))]
    if not tasks and (path / "task.json").exists():
        tasks = [Task.load(path / "task.json")]
    return tasks
