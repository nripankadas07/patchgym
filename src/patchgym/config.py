from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

CONFIG_FILE = "patchgym.toml"


@dataclass
class PatchGymConfig:
    validation_command: str = "python -m pytest -q"
    tasks_dir: str = ".patchgym/tasks"
    runs_dir: str = ".patchgym/runs"
    reports_dir: str = ".patchgym/reports"
    context_dir: str = ".patchgym/context"
    agent_timeout: int = 300
    validation_timeout: int = 120
    max_tasks: int = 20
    max_commits: int = 400

    def path(self, root: Path, value: str) -> Path:
        return (Path(root) / value).resolve()


def _parse_scalar(value: str):
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.isdigit():
        return int(value)
    return value


def _parse_simple_toml(text: str) -> Dict[str, object]:
    data: Dict[str, object] = {}
    in_patchgym = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_patchgym = line == "[patchgym]"
            continue
        if in_patchgym and "=" in line:
            key, value = line.split("=", 1)
            data[key.strip()] = _parse_scalar(value)
    return data


def load_config(root: Path = Path(".")) -> PatchGymConfig:
    root = Path(root)
    config_path = root / CONFIG_FILE
    config = PatchGymConfig()
    if not config_path.exists():
        return config
    values = _parse_simple_toml(config_path.read_text())
    for key, value in values.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config


def write_default_config(root: Path = Path(".")) -> Path:
    root = Path(root)
    path = root / CONFIG_FILE
    if path.exists():
        return path
    path.write_text(
        "\n".join(
            [
                "[patchgym]",
                'validation_command = "python -m pytest -q"',
                'tasks_dir = ".patchgym/tasks"',
                'runs_dir = ".patchgym/runs"',
                'reports_dir = ".patchgym/reports"',
                'context_dir = ".patchgym/context"',
                "agent_timeout = 300",
                "validation_timeout = 120",
                "max_tasks = 20",
                "max_commits = 400",
                "",
            ]
        )
    )
    return path
