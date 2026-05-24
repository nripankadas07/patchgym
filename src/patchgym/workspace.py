from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import tarfile
import time
from pathlib import Path
from typing import Optional

from .gitutils import git, init_repo, run

DEFAULT_GIT_ARCHIVE_TIMEOUT = 60


class WorkspaceError(RuntimeError):
    pass


def _within(path: Path, root: Path) -> bool:
    path = path.resolve()
    root = root.resolve()
    return os.path.commonpath([str(root), str(path)]) == str(root)


def safe_remove_tree(path: Path, allowed_root: Path) -> None:
    path = Path(path).resolve()
    allowed_root = Path(allowed_root).resolve()
    if not _within(path, allowed_root):
        raise WorkspaceError(f"refusing to delete outside allowed root: {path}")
    if path == allowed_root:
        raise WorkspaceError(f"refusing to delete allowed root itself: {path}")
    shutil.rmtree(path, ignore_errors=True)


def _safe_extract(tar: tarfile.TarFile, dest: Path) -> None:
    dest = dest.resolve()
    for member in tar:
        target = (dest / member.name).resolve()
        if os.path.commonpath([str(dest), str(target)]) != str(dest):
            raise WorkspaceError(f"unsafe path in git archive: {member.name}")
        try:
            tar.extract(member, dest, filter="data")
        except TypeError:
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
        try:
            returncode = proc.wait(timeout=DEFAULT_GIT_ARCHIVE_TIMEOUT)
        except subprocess.TimeoutExpired as exc:
            proc.kill()
            raise WorkspaceError(f"git archive timed out for {commit}") from exc
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


def run_command(
    command: str,
    cwd: Path,
    timeout: Optional[int] = None,
    env: Optional[dict] = None,
    shell: bool = False,
):
    cwd = Path(cwd)
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    merged_env.setdefault("PYTHONPYCACHEPREFIX", str(cwd / ".patchgym_pycache"))
    argv = command if shell else shlex.split(command)

    start = time.monotonic()
    proc = subprocess.run(
        argv,
        cwd=str(cwd),
        shell=shell,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout if timeout is not None else 120,
        env=merged_env,
    )
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "duration_s": time.monotonic() - start,
    }


def run_shell(command: str, cwd: Path, timeout: Optional[int] = None, env: Optional[dict] = None):
    # Only use the shell for explicit user-supplied agent commands.
    return run_command(command, cwd=cwd, timeout=timeout, env=env, shell=True)


def clean_python_bytecode(root: Path) -> None:
    root = Path(root).resolve()
    cache_root = root / ".patchgym_pycache"
    if cache_root.exists():
        safe_remove_tree(cache_root, allowed_root=root)
    for cache_dir in Path(root).rglob("__pycache__"):
        safe_remove_tree(cache_dir, allowed_root=root)
    for pyc in Path(root).rglob("*.pyc"):
        if _within(pyc, root):
            pyc.unlink(missing_ok=True)
