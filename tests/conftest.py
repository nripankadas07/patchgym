from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from patchgym.miner import mine_repo
from patchgym.models import Task

FIXTURE = Path(__file__).parent / "fixtures" / "make_tinycalc_repo.py"


@pytest.fixture
def tinycalc_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "tinycalc"
    subprocess.run([sys.executable, str(FIXTURE), str(repo)], check=True, timeout=60)
    return repo


@pytest.fixture
def tinycalc_tasks(tinycalc_repo: Path) -> list[Task]:
    return mine_repo(
        tinycalc_repo,
        tinycalc_repo / ".patchgym" / "tasks",
        validation_command=f"{sys.executable} -m pytest -q",
        max_tasks=1,
    )
