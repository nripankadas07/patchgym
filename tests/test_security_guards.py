from __future__ import annotations

from pathlib import Path

import pytest

from patchgym.workspace import WorkspaceError, safe_remove_tree


def test_safe_remove_tree_refuses_paths_outside_allowed_root(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()

    with pytest.raises(WorkspaceError):
        safe_remove_tree(outside, allowed_root=allowed)

    assert outside.exists()
