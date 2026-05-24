from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional, Sequence

DEFAULT_COMMAND_TIMEOUT = 60


@dataclass
class CommandResult:
    cmd: Sequence[str]
    returncode: int
    stdout: str
    stderr: str
    duration_s: float


class CommandError(RuntimeError):
    def __init__(self, result: CommandResult):
        self.result = result
        joined = " ".join(result.cmd)
        super().__init__(
            f"command failed with exit code {result.returncode}: {joined}\n"
            f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )


def run(
    cmd: Sequence[str],
    cwd: Optional[Path] = None,
    check: bool = True,
    timeout: Optional[int] = None,
    env: Optional[Mapping[str, str]] = None,
) -> CommandResult:
    start = time.monotonic()
    proc = subprocess.run(
        list(cmd),
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout if timeout is not None else DEFAULT_COMMAND_TIMEOUT,
        env=dict(env) if env else None,
    )
    result = CommandResult(
        cmd=list(cmd),
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
        duration_s=time.monotonic() - start,
    )
    if check and result.returncode != 0:
        raise CommandError(result)
    return result


def git(repo: Path, *args: str, check: bool = True, timeout: Optional[int] = None) -> CommandResult:
    return run(["git", *args], cwd=repo, check=check, timeout=timeout or DEFAULT_COMMAND_TIMEOUT)


def git_top_level(repo: Path) -> Path:
    result = git(repo, "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip()).resolve()


def require_git_repo(repo: Path) -> Path:
    repo = Path(repo).resolve()
    try:
        return git_top_level(repo)
    except CommandError as exc:
        raise ValueError(f"{repo} is not a Git repository") from exc


def init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "-q"], cwd=path)
    git(path, "config", "user.email", "patchgym@example.local")
    git(path, "config", "user.name", "PatchGym")


def commit_all(path: Path, message: str) -> str:
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", message)
    return git(path, "rev-parse", "HEAD").stdout.strip()
