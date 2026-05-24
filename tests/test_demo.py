from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_demo_command_succeeds_in_temp_directory(tmp_path: Path) -> None:
    keep_dir = tmp_path / "demo"
    result = subprocess.run(
        [sys.executable, "-m", "patchgym", "demo", "--keep-dir", str(keep_dir)],
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert '"tasks_mined": 1' in result.stdout
    assert '"oracle_solved": 1' in result.stdout
    assert (keep_dir / "runs" / "oracle" / "report.md").exists()


def test_readme_demo_command_is_current() -> None:
    readme = Path("README.md").read_text()
    assert "bash scripts/demo.sh" in readme
    assert Path("scripts/demo.sh").exists()
