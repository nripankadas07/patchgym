from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Dict, Optional

from .gitutils import commit_all, init_repo
from .miner import mine_repo
from .runner import run_tasks
from .verify import verify_tasks


def create_demo_repo(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    init_repo(path)

    (path / "calculator.py").write_text(
        "\n".join(
            [
                "def clamp(value, lower, upper):",
                "    if lower > upper:",
                "        raise ValueError('lower must not exceed upper')",
                "    if value < lower:",
                "        return lower",
                "    if value > upper:",
                "        return lower",
                "    return value",
                "",
            ]
        )
    )
    (path / "tests").mkdir()
    (path / "tests" / "test_calculator.py").write_text(
        "\n".join(
            [
                "from calculator import clamp",
                "",
                "",
                "def test_clamp_lower_bound():",
                "    assert clamp(-5, 0, 10) == 0",
                "",
                "",
                "def test_clamp_inside_range():",
                "    assert clamp(5, 0, 10) == 5",
                "",
            ]
        )
    )
    commit_all(path, "initial calculator")

    (path / "calculator.py").write_text(
        "\n".join(
            [
                "def clamp(value, lower, upper):",
                "    if lower > upper:",
                "        raise ValueError('lower must not exceed upper')",
                "    if value < lower:",
                "        return lower",
                "    if value > upper:",
                "        return upper",
                "    return value",
                "",
            ]
        )
    )
    (path / "tests" / "test_calculator.py").write_text(
        "\n".join(
            [
                "from calculator import clamp",
                "",
                "",
                "def test_clamp_lower_bound():",
                "    assert clamp(-5, 0, 10) == 0",
                "",
                "",
                "def test_clamp_inside_range():",
                "    assert clamp(5, 0, 10) == 5",
                "",
                "",
                "def test_clamp_upper_bound():",
                "    assert clamp(50, 0, 10) == 10",
                "",
            ]
        )
    )
    commit_all(path, "fix clamp upper bound")
    return path


def run_demo(root: Path, keep_dir: Optional[Path] = None) -> Dict:
    root = Path(root).resolve()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    repo = create_demo_repo(root / "sample-repo")
    tasks_dir = root / "tasks"
    validation = f"{sys.executable} -m pytest -q"
    tasks = mine_repo(repo, tasks_dir, validation_command=validation, max_tasks=1)
    verification = verify_tasks(tasks)
    noop = run_tasks(tasks, agent="noop", out_dir=root / "runs" / "noop")
    oracle = run_tasks(tasks, agent="oracle", out_dir=root / "runs" / "oracle")

    summary = {
        "root": str(root),
        "tasks_mined": len(tasks),
        "verification_valid": sum(1 for result in verification if result.valid),
        "noop_solved": sum(1 for result in noop if result.solved),
        "oracle_solved": sum(1 for result in oracle if result.solved),
        "report": str(root / "runs" / "oracle" / "report.md"),
    }

    if keep_dir:
        keep_dir = Path(keep_dir).resolve()
        if keep_dir.exists():
            shutil.rmtree(keep_dir)
        shutil.copytree(root, keep_dir)
        summary["root"] = str(keep_dir)
        summary["report"] = str(keep_dir / "runs" / "oracle" / "report.md")

    return summary
