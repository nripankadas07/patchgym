from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .miner import is_test_path


def split_paths(paths: Sequence[str]) -> tuple[list[str], list[str]]:
    test_files = [path for path in paths if is_test_path(path)]
    source_files = [path for path in paths if not is_test_path(path)]
    return test_files, source_files


def patch_line_count(patch: str) -> int:
    return sum(1 for line in patch.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---")))


def patch_changed_files(patch_file: Path) -> list[str]:
    files: list[str] = []
    for line in Path(patch_file).read_text().splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                files.append(parts[3].removeprefix("b/"))
    return files
