from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Union

from .config import load_config
from .models import Task, load_tasks


def default_tasks_dir(root: Path = Path(".")) -> Path:
    config = load_config(root)
    return Path(root) / config.tasks_dir


def resolve_task_path(task_or_path: Union[str, Path], root: Path = Path(".")) -> Path:
    value = Path(task_or_path)
    if value.exists():
        return value
    candidate = default_tasks_dir(root) / str(task_or_path)
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"task or task directory not found: {task_or_path}")


def load_task(task_id: str, root: Path = Path(".")) -> Task:
    return Task.load(resolve_task_path(task_id, root=root))


def load_task_selection(task_or_path: Union[str, Path], root: Path = Path(".")) -> List[Task]:
    return load_tasks(resolve_task_path(task_or_path, root=root))


def list_tasks(root: Path = Path(".")) -> List[Task]:
    task_dir = default_tasks_dir(root)
    if not task_dir.exists():
        return []
    return load_tasks(task_dir)


def task_rows(tasks: Iterable[Task]) -> List[str]:
    return [f"{task.id}\t{task.commit_subject}" for task in tasks]
