from __future__ import annotations

import os
import shutil
import subprocess
import tarfile
from pathlib import Path
from typing import Optional

from .gitutils import git, init_repo, run


class WorkspaceError(RuntimeError):
    pass


def _safe_extract(tar: tarfile.TarFile, dest: Path) -> None:
    dest = dest.resolve()
    for member in tar:
        target = (dest / member.name).resolve()
        if os.path.commonpath([str(dest), str(target)]) != str(dest):
            raise WorkspaceError(f"unsafe path in git archive: {member.name}")
        tar.extract(member, dest)


def export_base_snapshot(source_repo: Path, commit: str, dest: Path, init_git: bool = True) -> Path:
    source_repo = Path(source_repo).resolve()
    dest = Path(dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen(
        ["git", "-C", str(source_repo), "archive", "--format=tar", commit],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None
    try:
        with tarfile.open(fileobj=proc.stdout, mode="r|") as tar:
            _safe_extract(tar, dest)
    finally:
        stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
        returncode = proc.wait()
    if returncode != 0:
        raise WorkspaceError(f"git archive failed for {commit}: {stderr}")

    if init_git:
        init_repo(dest)
        git(dest, "add", "-A")
        git(dest, "commit", "-q", "-m", "patchgym baseline")
    return dest


def apply_patch(workspace: Path, patch_file: Path, check: bool = True):
    return run(
        ["git", "apply", "--whitespace=nowarn", str(patch_file)],
        cwd=workspace,
        check=check,
    )


def run_shell(command: str, cwd: Path, timeout: Optional[int] = None, env: Optional[dict] = None):
    import subprocess
    import time

    cwd = Path(cwd)
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    merged_env.setdefault("PYTHONPYCACHEPREFIX", str(cwd / ".patchgym_pycache"))

    start = time.monotonic()
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        env=merged_env,
    )
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "duration_s": time.monotonic() - start,
    }


def clean_python_bytecode(root: Path) -> None:
    shutil.rmtree(Path(root) / ".patchgym_pycache", ignore_errors=True)
    for cache_dir in Path(root).rglob("__pycache__"):
        shutil.rmtree(cache_dir, ignore_errors=True)
    for pyc in Path(root).rglob("*.pyc"):
        pyc.unlink(missing_ok=True)
