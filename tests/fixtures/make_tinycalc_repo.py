#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(
        cmd,
        cwd=str(cwd),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )


def commit_all(repo: Path, message: str) -> None:
    run(["git", "add", "-A"], repo)
    run(["git", "commit", "-q", "-m", message], repo)


def make_repo(path: Path) -> Path:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing path: {path}")
    path.mkdir(parents=True)
    run(["git", "init", "-q"], path)
    run(["git", "config", "user.email", "patchgym@example.local"], path)
    run(["git", "config", "user.name", "PatchGym"], path)
    (path / "tinycalc.py").write_text(
        "\n".join(
            [
                "def clamp(value, low, high):",
                "    if value < low:",
                "        return low",
                "    if value > high:",
                "        return low",
                "    return value",
                "",
            ]
        )
    )
    (path / "tests").mkdir()
    (path / "tests" / "test_tinycalc.py").write_text(
        "\n".join(
            [
                "from tinycalc import clamp",
                "",
                "",
                "def test_lower_bound():",
                "    assert clamp(-1, 0, 10) == 0",
                "",
                "",
                "def test_inside_range():",
                "    assert clamp(5, 0, 10) == 5",
                "",
            ]
        )
    )
    commit_all(path, "initial tinycalc")
    (path / "tinycalc.py").write_text(
        "\n".join(
            [
                "def clamp(value, low, high):",
                "    if value < low:",
                "        return low",
                "    if value > high:",
                "        return high",
                "    return value",
                "",
            ]
        )
    )
    (path / "tests" / "test_tinycalc.py").write_text(
        "\n".join(
            [
                "from tinycalc import clamp",
                "",
                "",
                "def test_lower_bound():",
                "    assert clamp(-1, 0, 10) == 0",
                "",
                "",
                "def test_inside_range():",
                "    assert clamp(5, 0, 10) == 5",
                "",
                "",
                "def test_upper_bound():",
                "    assert clamp(99, 0, 10) == 10",
                "",
            ]
        )
    )
    commit_all(path, "fix clamp upper bound")
    return path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: make_tinycalc_repo.py PATH")
    print(make_repo(Path(sys.argv[1]).resolve()))
