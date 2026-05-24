from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Optional

from .demo import run_demo
from .miner import describe_tasks, mine_repo
from .models import load_tasks
from .runner import run_tasks
from .verify import verify_tasks


def _path(value: str) -> Path:
    return Path(value).expanduser()


def cmd_mine(args: argparse.Namespace) -> int:
    tasks = mine_repo(
        repo=args.repo,
        out_dir=args.out,
        validation_command=args.validation,
        max_tasks=args.max_tasks,
        max_commits=args.max_commits,
        max_files=args.max_files,
        max_patch_lines=args.max_patch_lines,
        require_keyword=args.require_keyword,
    )
    print(f"mined {len(tasks)} task(s) into {args.out}")
    if tasks:
        print(describe_tasks(tasks))
    return 0 if tasks else 2


def cmd_verify(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.tasks)
    results = verify_tasks(
        tasks,
        repo=args.repo,
        timeout=args.timeout,
        keep_workspace=args.keep_workspace,
    )
    for result in results:
        label = "valid" if result.valid else "invalid"
        print(
            f"{result.task_id}: {label} "
            f"(base={result.base_returncode}, oracle={result.oracle_returncode})"
        )
        if result.error:
            print(f"  error: {result.error}")
    return 0 if all(result.valid for result in results) else 1


def cmd_run(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.tasks)
    results = run_tasks(
        tasks,
        agent=args.agent,
        out_dir=args.out,
        repo=args.repo,
        agent_timeout=args.agent_timeout,
        validation_timeout=args.validation_timeout,
        keep_workspace=args.keep_workspace,
    )
    solved = sum(1 for result in results if result.solved)
    print(f"agent {args.agent!r} solved {solved}/{len(results)} task(s)")
    print(f"report: {args.out / 'report.md'}")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory(prefix="patchgym-demo-") as tmp:
        summary = run_demo(Path(tmp), keep_dir=args.keep_dir)
    print(json.dumps(summary, indent=2))
    return 0 if summary["verification_valid"] == summary["tasks_mined"] and summary["oracle_solved"] == summary["tasks_mined"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="patchgym",
        description="Turn Git history into local SWE-bench-style coding-agent tasks.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    mine = sub.add_parser("mine", help="mine benchmark tasks from Git history")
    mine.add_argument("repo", type=_path)
    mine.add_argument("--out", type=_path, default=Path(".patchgym/tasks"))
    mine.add_argument("--validation", required=True, help="command used to validate each task")
    mine.add_argument("--max-tasks", type=int, default=20)
    mine.add_argument("--max-commits", type=int, default=400)
    mine.add_argument("--max-files", type=int, default=16)
    mine.add_argument("--max-patch-lines", type=int, default=500)
    mine.add_argument("--require-keyword", action="store_true")
    mine.set_defaults(func=cmd_mine)

    verify = sub.add_parser("verify", help="verify mined tasks")
    verify.add_argument("tasks", type=_path)
    verify.add_argument("--repo", type=_path)
    verify.add_argument("--timeout", type=int, default=120)
    verify.add_argument("--keep-workspace", action="store_true")
    verify.set_defaults(func=cmd_verify)

    run = sub.add_parser("run", help="run an agent command against tasks")
    run.add_argument("tasks", type=_path)
    run.add_argument("--agent", required=True, help="shell command, or built-in: noop/oracle")
    run.add_argument("--repo", type=_path)
    run.add_argument("--out", type=_path, default=Path(".patchgym/runs/default"))
    run.add_argument("--agent-timeout", type=int, default=300)
    run.add_argument("--validation-timeout", type=int, default=120)
    run.add_argument("--keep-workspace", action="store_true")
    run.set_defaults(func=cmd_run)

    demo = sub.add_parser("demo", help="run a no-key end-to-end demo")
    demo.add_argument("--keep-dir", type=_path, help="copy demo artifacts to this directory")
    demo.set_defaults(func=cmd_demo)

    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
