from __future__ import annotations

from pathlib import Path

from patchgym.config import load_config, write_default_config
from patchgym.patches import patch_changed_files, split_paths
from patchgym.tasks import list_tasks


def test_config_init_and_mining_create_task(tinycalc_repo: Path, tinycalc_tasks) -> None:
    config_path = write_default_config(tinycalc_repo)
    config = load_config(tinycalc_repo)

    assert config_path.exists()
    assert config.validation_command == "python -m pytest -q"
    assert len(tinycalc_tasks) == 1

    discovered = list_tasks(tinycalc_repo)
    assert discovered[0].id == tinycalc_tasks[0].id
    assert discovered[0].test_files == ["tests/test_tinycalc.py"]
    assert discovered[0].solution_files == ["tinycalc.py"]


def test_patch_splitting_and_changed_files(tinycalc_tasks) -> None:
    tests, sources = split_paths(["tinycalc.py", "tests/test_tinycalc.py"])

    assert tests == ["tests/test_tinycalc.py"]
    assert sources == ["tinycalc.py"]
    assert patch_changed_files(tinycalc_tasks[0].test_patch_path) == ["tests/test_tinycalc.py"]
