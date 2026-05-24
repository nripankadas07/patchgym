from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchgym.config import load_config, write_default_config
from patchgym.context_pack import write_context_pack
from patchgym.graders import grade_report
from patchgym.miner import mine_repo
from patchgym.patches import patch_changed_files, split_paths
from patchgym.reports import write_reports
from patchgym.runner import run_tasks
from patchgym.tasks import list_tasks
from patchgym.verify import verify_tasks

FIXTURE = Path(__file__).parent / "fixtures" / "make_tinycalc_repo.py"


def make_fixture(tmp_path: Path) -> Path:
    repo = tmp_path / "tinycalc"
    subprocess.run([sys.executable, str(FIXTURE), str(repo)], check=True, timeout=60)
    return repo


def test_config_loading_and_init(tmp_path: Path) -> None:
    path = write_default_config(tmp_path)
    assert path.exists()
    config = load_config(tmp_path)
    assert config.validation_command == "python -m pytest -q"
    assert config.tasks_dir == ".patchgym/tasks"


def test_patch_splitting_heuristic() -> None:
    tests, sources = split_paths(["tinycalc.py", "tests/test_tinycalc.py"])
    assert tests == ["tests/test_tinycalc.py"]
    assert sources == ["tinycalc.py"]


def test_task_verification_context_grading_and_reports(tmp_path: Path) -> None:
    repo = make_fixture(tmp_path)
    tasks = mine_repo(repo, repo / ".patchgym" / "tasks", validation_command=f"{sys.executable} -m pytest -q")
    assert len(tasks) == 1

    discovered = list_tasks(repo)
    assert discovered[0].id == tasks[0].id
    assert patch_changed_files(discovered[0].test_patch_path) == ["tests/test_tinycalc.py"]

    verification = verify_tasks(discovered)
    assert verification[0].valid
    assert verification[0].base_with_hidden_tests_failed
    assert verification[0].oracle_passed

    context_dir = write_context_pack(discovered[0])
    assert (context_dir / "CODEX_TASK.md").exists()
    assert (context_dir / "AGENTS.md").exists()
    assert "oracle_solution.patch" not in (context_dir / "CODEX_TASK.md").read_text()

    agent = Path(__file__).parents[1] / "examples" / "custom_agent" / "agent.sh"
    results = run_tasks(discovered, agent=f"bash {agent}", out_dir=repo / ".patchgym" / "runs" / "latest")
    assert results[0].solved
    assert "tinycalc.py" in results[0].changed_files

    grade = grade_report(repo / ".patchgym" / "runs" / "latest" / "report.json")
    assert grade == {"solved": 1, "total": 1}

    paths = write_reports(repo / ".patchgym" / "reports", "toy", [result.to_dict() for result in results])
    assert json.loads(Path(paths["json"]).read_text())["results"][0]["solved"] is True
    assert Path(paths["markdown"]).read_text().startswith("# PatchGym Report")
    assert Path(paths["html"]).read_text().startswith("<!doctype html>")
