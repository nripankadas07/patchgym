from __future__ import annotations

import sys
from pathlib import Path

from patchgym.demo import create_demo_repo
from patchgym.miner import mine_repo
from patchgym.models import load_tasks
from patchgym.runner import run_tasks
from patchgym.verify import verify_tasks


def test_mine_verify_and_run_baselines(tmp_path: Path) -> None:
    repo = create_demo_repo(tmp_path / "repo")
    tasks_dir = tmp_path / "tasks"
    validation = f"{sys.executable} -m pytest -q"

    tasks = mine_repo(repo, tasks_dir, validation_command=validation, max_tasks=1)

    assert len(tasks) == 1
    loaded = load_tasks(tasks_dir)
    assert loaded[0].id == tasks[0].id
    assert loaded[0].test_files == ["tests/test_calculator.py"]
    assert loaded[0].solution_files == ["calculator.py"]

    verification = verify_tasks(loaded)
    assert [result.valid for result in verification] == [True]

    noop = run_tasks(loaded, agent="noop", out_dir=tmp_path / "runs" / "noop")
    oracle = run_tasks(loaded, agent="oracle", out_dir=tmp_path / "runs" / "oracle")

    assert [result.solved for result in noop] == [False]
    assert [result.solved for result in oracle] == [True]
    assert (tmp_path / "runs" / "oracle" / "report.md").exists()


def test_shell_agent_contract(tmp_path: Path) -> None:
    repo = create_demo_repo(tmp_path / "repo")
    tasks = mine_repo(
        repo,
        tmp_path / "tasks",
        validation_command=f"{sys.executable} -m pytest -q",
        max_tasks=1,
    )
    agent = tmp_path / "agent.py"
    agent.write_text(
        "\n".join(
            [
                "import os",
                "from pathlib import Path",
                "assert Path(os.environ['PATCHGYM_PROMPT_FILE']).exists()",
                "path = Path('calculator.py')",
                "text = path.read_text()",
                "path.write_text(text.replace('return lower\\n    return value', 'return upper\\n    return value', 1))",
                "",
            ]
        )
    )

    results = run_tasks(tasks, agent=f"{sys.executable} {agent}", out_dir=tmp_path / "runs" / "shell")

    assert [result.solved for result in results] == [True]
    patch = Path(results[0].patch_file).read_text()
    assert "return upper" in patch
