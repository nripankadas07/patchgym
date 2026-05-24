from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from .gitutils import CommandError, git, require_git_repo
from .models import Task


BUGFIX_WORDS = (
    "fix",
    "bug",
    "regression",
    "correct",
    "handle",
    "prevent",
    "resolve",
    "repair",
    "fail",
    "failure",
    "error",
    "edge case",
)


def is_test_path(path: str) -> bool:
    lower = path.lower().replace("\\", "/")
    name = lower.rsplit("/", 1)[-1]
    suffixes = (
        "_test.py",
        ".test.js",
        ".test.ts",
        ".spec.js",
        ".spec.ts",
        "_test.go",
        "test.rs",
    )
    return (
        lower.startswith("test/")
        or lower.startswith("tests/")
        or "/test/" in lower
        or "/tests/" in lower
        or name.startswith("test_")
        or name.endswith(suffixes)
        or name in {"test.py", "tests.py"}
    )


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:48] or "task"


def _parse_name_status(raw: str) -> Tuple[List[str], bool]:
    parts = [part for part in raw.split("\0") if part]
    paths: List[str] = []
    i = 0
    has_rename_or_copy = False
    while i < len(parts):
        status = parts[i]
        i += 1
        if status.startswith(("R", "C")):
            has_rename_or_copy = True
            i += 2
            continue
        if i >= len(parts):
            break
        paths.append(parts[i])
        i += 1
    return paths, has_rename_or_copy


def _patch_for_paths(repo: Path, parent: str, commit: str, paths: Sequence[str]) -> str:
    if not paths:
        return ""
    return git(
        repo,
        "diff",
        "--binary",
        parent,
        commit,
        "--",
        *paths,
    ).stdout


def _patch_line_count(patch: str) -> int:
    return sum(1 for line in patch.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---")))


def _commit_subject(repo: Path, commit: str) -> str:
    return git(repo, "show", "-s", "--format=%s", commit).stdout.strip()


def _parent(repo: Path, commit: str) -> str:
    parents = git(repo, "show", "-s", "--format=%P", commit).stdout.strip().split()
    if len(parents) != 1:
        return ""
    return parents[0]


def _changed_paths(repo: Path, parent: str, commit: str) -> Tuple[List[str], bool]:
    raw = git(repo, "diff", "--name-status", "-z", parent, commit).stdout
    return _parse_name_status(raw)


def _score_reason(subject: str, test_files: Sequence[str], solution_files: Sequence[str]) -> str:
    lower = subject.lower()
    matched = [word for word in BUGFIX_WORDS if word in lower]
    if matched:
        return f"commit subject contains: {', '.join(matched[:3])}"
    return f"touches {len(test_files)} test file(s) and {len(solution_files)} source file(s)"


def build_prompt(subject: str, base_commit: str, validation_command: str, solution_files: Sequence[str]) -> str:
    files = "\n".join(f"- {path}" for path in solution_files)
    return (
        "You are given a repository snapshot from a historical commit.\n\n"
        f"Historical change summary: {subject}\n\n"
        "Your job is to edit the code so the hidden tests pass. The hidden tests were written in the same historical commit as the fix.\n\n"
        f"Base commit: {base_commit}\n\n"
        "Likely source files touched by the historical fix:\n"
        f"{files}\n\n"
        f"Validation command: {validation_command}\n\n"
        "Modify the working tree only. Do not rely on network access or inspect future Git history."
    )


def mine_repo(
    repo: Path,
    out_dir: Path,
    validation_command: str,
    max_tasks: int = 20,
    max_commits: int = 400,
    max_files: int = 16,
    max_patch_lines: int = 500,
    require_keyword: bool = False,
) -> List[Task]:
    repo = require_git_repo(Path(repo))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    commits = git(repo, "rev-list", "--first-parent", f"--max-count={max_commits}", "HEAD").stdout.splitlines()
    tasks: List[Task] = []
    seen_ids = set()

    for commit in commits:
        if len(tasks) >= max_tasks:
            break
        parent = _parent(repo, commit)
        if not parent:
            continue

        try:
            paths, has_rename_or_copy = _changed_paths(repo, parent, commit)
        except CommandError:
            continue
        if has_rename_or_copy or not paths or len(paths) > max_files:
            continue

        test_files = [path for path in paths if is_test_path(path)]
        solution_files = [path for path in paths if not is_test_path(path)]
        if not test_files or not solution_files:
            continue

        subject = _commit_subject(repo, commit)
        if require_keyword and not any(word in subject.lower() for word in BUGFIX_WORDS):
            continue

        test_patch = _patch_for_paths(repo, parent, commit, test_files)
        solution_patch = _patch_for_paths(repo, parent, commit, solution_files)
        if not test_patch.strip() or not solution_patch.strip():
            continue

        patch_lines = _patch_line_count(test_patch) + _patch_line_count(solution_patch)
        if patch_lines > max_patch_lines:
            continue

        digest = hashlib.sha1(f"{repo}:{commit}".encode("utf-8")).hexdigest()[:8]
        task_id = f"{commit[:8]}-{_slug(subject)}-{digest}"
        if task_id in seen_ids:
            continue
        seen_ids.add(task_id)

        task = Task(
            id=task_id,
            source_repo=str(repo),
            base_commit=parent,
            target_commit=commit,
            commit_subject=subject,
            validation_command=validation_command,
            prompt=build_prompt(subject, parent, validation_command, solution_files),
            test_files=test_files,
            solution_files=solution_files,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "selection_reason": _score_reason(subject, test_files, solution_files),
                "patch_line_count": patch_lines,
            },
        )

        task_dir = out_dir / task.id
        task.save(task_dir)
        (task_dir / task.test_patch).write_text(test_patch)
        (task_dir / task.solution_patch).write_text(solution_patch)
        tasks.append(task)

    return tasks


def describe_tasks(tasks: Iterable[Task]) -> str:
    rows = []
    for task in tasks:
        rows.append(
            f"{task.id}: {task.commit_subject} "
            f"({len(task.test_files)} test file(s), {len(task.solution_files)} source file(s))"
        )
    return "\n".join(rows)
