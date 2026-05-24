from __future__ import annotations

import shutil
import subprocess
import sys


def test_patchgym_help_entrypoints_work() -> None:
    assert shutil.which("patchgym"), "patchgym console script is not on PATH"

    cli = subprocess.run(["patchgym", "--help"], text=True, capture_output=True, timeout=30)
    module = subprocess.run(
        [sys.executable, "-m", "patchgym", "--help"],
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert cli.returncode == 0, cli.stderr
    assert module.returncode == 0, module.stderr
    for command in ["init", "mine", "build", "list", "show", "verify", "run", "grade", "report"]:
        assert command in cli.stdout
        assert command in module.stdout
