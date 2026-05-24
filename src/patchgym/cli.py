from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import List, Optional

from .config import load_config, write_default_config
from .context_pack import write_context_pack
from .demo import run_demo
from .graders import grade_report
from .miner import describe_tasks, mine_repo
from .reports import report_from_run, write_reports
from .runner import run_tasks
from .tasks import list_tasks, load_task, load_task_selection, task_rows
from .verify import verify_tasks


def _path(value: str) -> Path:
    return Path(value).expanduser()


def _latest_run_report(root: Path) -> Path:
    latest = root / ".patchgym" / "runs" / "latest" / "report.json"
    if latest.exists():
        return latest
    reports = sorted((root / ".patchgym" / "runs").glob("*/report.json"))
    if not reports:
        raise FileNotFoundError("no PatchGym run report found")
    return reports[-1]


def cmd_init(args: argparse.Namespace) -> int:
    root = args.repo.resolve()
    config_path = write_default_config(root)
    config = load_config(root)
    for directory in [config.tasks_dir, config.runs_dir, config.reports_dir, config.context_dir]:
        (root / directory).mkdir(parents=True, exist_ok=True)
    print(f"initialized {config_path}")
    return 0


def cmd_mine(args: argparse.Namespace) -> int:
    root = Path(".").resolve()
    config = load_config(root)
    validation = args.validation or config.validation_command
    out = args.out or root / config.tasks_dir
    tasks = mine_repo(
        repo=args.repo,
        out_dir=out,
        validation_command=validation,
        max_tasks=args.max_tasks or config.max_tasks,
        max_commits=args.max_commits or config.max_commits,
        max_files=args.max_files,
        max_patch_lines=args.max_patch_lines,
        require_keyword=args.require_keyword,
    )
    print(f"mined {len(tasks)} task(s) into {out}")
    if tasks:
        print(describe_tasks(tasks))
    return 0 if tasks else 2


def cmd_build(args: argparse.Namespace) -> int:
    root = Path(".").resolve()
    tasks = list_tasks(root)
    if not tasks:
        print("no mined tasks found")
        return 2
    config = load_config(root)
    results = verify_tasks(tasks, timeout=config.validation_timeout)
    build_path = root / ".patchgym" / "build.json"
    build_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"results": [result.to_dict() for result in results]}
    build_path.write_text(json.dumps(payload, indent=2) + "\n")
    valid = sum(1 for result in results if result.valid)
    print(f"built {valid}/{len(results)} valid task(s)")
    return 0 if valid else 1


def cmd_list(args: argparse.Namespace) -> int:
    tasks = list_tasks(Path(".").resolve())
    if args.plain:
        for row in task_rows(tasks):
            print(row)
    else:
        for task in tasks:
            print(f"{task.id}: {task.commit_subject}")
    return 0 if tasks else 1


def cmd_show(args: argparse.Namespace) -> int:
    task = load_task(args.task_id, root=Path(".").resolve())
    if args.json:
        print(json.dumps(task.redacted_dict(), indent=2))
    else:
        print(f"# {task.id}\n")
        print(task.prompt)
        print("\nHidden tests and oracle patches are not shown to agents.")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    root = Path(".").resolve()
    tasks = load_task_selection(args.tasks, root=root)
    config = load_config(root)
    results = verify_tasks(
        tasks,
        repo=args.repo,
        timeout=args.timeout or config.validation_timeout,
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


def cmd_context(args: argparse.Namespace) -> int:
    task = load_task(args.task_id, root=Path(".").resolve())
    out_dir = write_context_pack(task)
    print(f"context: {out_dir}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    root = Path(".").resolve()
    config = load_config(root)
    tasks = load_task_selection(args.tasks, root=root)
    out = args.out or root / config.runs_dir / "latest"
    results = run_tasks(
        tasks,
        agent=args.agent,
        out_dir=out,
        repo=args.repo,
        agent_timeout=args.agent_timeout or config.agent_timeout,
        validation_timeout=args.validation_timeout or config.validation_timeout,
        keep_workspace=args.keep_workspace,
    )
    solved = sum(1 for result in results if result.solved)
    print(f"agent {args.agent!r} solved {solved}/{len(results)} task(s)")
    print(f"report: {out / 'report.md'}")
    return 0


def cmd_grade(args: argparse.Namespace) -> int:
    report = args.report or _latest_run_report(Path(".").resolve())
    grade = grade_report(report)
    print(f"grade: {grade['solved']}/{grade['total']}")
    return 0 if grade["total"] else 1


def cmd_report(args: argparse.Namespace) -> int:
    root = Path(".").resolve()
    config = load_config(root)
    source = args.report or _latest_run_report(root)
    paths = report_from_run(source, root / config.reports_dir)
    print(f"json: {paths['json']}")
    print(f"markdown: {paths['markdown']}")
    print(f"html: {paths['html']}")
    return 0


def cmd_replay(args: argparse.Namespace) -> int:
    root = Path(".").resolve()
    task = load_task(args.task_id, root=root)
    config = load_config(root)
    out = root / config.runs_dir / "replay"
    results = run_tasks([task], agent="oracle", out_dir=out)
    write_reports(root / config.reports_dir, "oracle", [result.to_dict() for result in results])
    print(f"replayed oracle for {task.id}: {sum(1 for result in results if result.solved)}/1")
    return 0 if results and results[0].solved else 1


def cmd_demo(args: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory(prefix="patchgym-demo-") as tmp:
        summary = run_demo(Path(tmp), keep_dir=args.keep_dir)
    print(json.dumps(summary, indent=2))
    valid_demo = (
        summary["verification_valid"] == summary["tasks_mined"]
        and summary["oracle_solved"] == summary["tasks_mined"]
    )
    return 0 if valid_demo else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="patchgym",
        description="Turn Git history into local SWE-bench-style coding-agent tasks.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="write patchgym.toml and create .patchgym directories")
    init.add_argument("repo", nargs="?", type=_path, default=Path("."))
    init.set_defaults(func=cmd_init)

    mine = sub.add_parser("mine", help="mine benchmark tasks from Git history")
    mine.add_argument("repo", type=_path)
    mine.add_argument("--out", type=_path)
    mine.add_argument("--validation", help="command used to validate each task")
    mine.add_argument("--max-tasks", type=int)
    mine.add_argument("--max-commits", type=int)
    mine.add_argument("--max-files", type=int, default=16)
    mine.add_argument("--max-patch-lines", type=int, default=500)
    mine.add_argument("--require-keyword", action="store_true")
    mine.set_defaults(func=cmd_mine)

    build = sub.add_parser("build", help="verify mined tasks and write build metadata")
    build.add_argument("repo", nargs="?", type=_path, default=Path("."))
    build.set_defaults(func=cmd_build)

    list_cmd = sub.add_parser("list", help="list mined tasks")
    list_cmd.add_argument("--plain", action="store_true")
    list_cmd.set_defaults(func=cmd_list)

    show = sub.add_parser("show", help="show a task prompt without leaking oracle data")
    show.add_argument("task_id")
    show.add_argument("--json", action="store_true")
    show.set_defaults(func=cmd_show)

    verify = sub.add_parser("verify", help="verify mined tasks")
    verify.add_argument("tasks")
    verify.add_argument("--repo", type=_path)
    verify.add_argument("--timeout", type=int)
    verify.add_argument("--keep-workspace", action="store_true")
    verify.set_defaults(func=cmd_verify)

    run = sub.add_parser("run", help="run an agent command against tasks")
    run.add_argument("tasks")
    run.add_argument("--agent", required=True, help="shell command, or built-in: noop/oracle")
    run.add_argument("--repo", type=_path)
    run.add_argument("--out", type=_path)
    run.add_argument("--agent-timeout", type=int)
    run.add_argument("--validation-timeout", type=int)
    run.add_argument("--keep-workspace", action="store_true")
    run.set_defaults(func=cmd_run)

    grade = sub.add_parser("grade", help="summarize the latest run grade")
    grade.add_argument("--report", type=_path)
    grade.set_defaults(func=cmd_grade)

    report = sub.add_parser("report", help="write JSON, Markdown, and HTML reports")
    report.add_argument("--report", type=_path)
    report.set_defaults(func=cmd_report)

    context = sub.add_parser("context", help="write a task context pack")
    context.add_argument("task_id")
    context.set_defaults(func=cmd_context)

    replay = sub.add_parser("replay", help="replay the oracle patch for a task")
    replay.add_argument("task_id")
    replay.set_defaults(func=cmd_replay)

    demo = sub.add_parser("demo", help="run a no-key end-to-end demo")
    demo.add_argument("--keep-dir", type=_path, help="copy demo artifacts to this directory")
    demo.set_defaults(func=cmd_demo)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
