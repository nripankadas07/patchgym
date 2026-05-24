from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Dict, Iterable, List

from .report import write_json


def render_markdown(agent: str, rows: Iterable[Dict]) -> str:
    results: List[Dict] = list(rows)
    solved = sum(1 for row in results if row.get("solved"))
    lines = [
        "# PatchGym Report",
        "",
        f"Tasks generated: {len(results)}",
        f"Run result: {solved}/{len(results)} solved by `{agent}`",
        "",
        "| Task | Pass/Fail | Changed files | Test command | Duration |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for row in results:
        changed = ", ".join(row.get("changed_files") or []) or "none"
        status = "pass" if row.get("solved") else "fail"
        lines.append(
            f"| `{row.get('task_id')}` | {status} | {changed} | "
            f"`{row.get('validation_command', '')}` | {row.get('agent_duration_s', 0):.2f}s |"
        )
    lines.extend(
        [
            "",
            "Safety note: PatchGym runs local validation and agent commands. "
            "Use a container or VM for untrusted repos.",
            "",
        ]
    )
    return "\n".join(lines)


def render_html(markdown: str) -> str:
    escaped = html.escape(markdown)
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        "<title>PatchGym Report</title>"
        "<style>body{font-family:system-ui,sans-serif;max-width:960px;"
        "margin:40px auto;line-height:1.5}"
        "pre{white-space:pre-wrap;background:#f6f8fa;padding:16px;border-radius:8px}</style>"
        "</head><body><pre>"
        f"{escaped}"
        "</pre></body></html>\n"
    )


def write_reports(report_dir: Path, agent: str, results: Iterable[Dict]) -> Dict[str, str]:
    report_dir.mkdir(parents=True, exist_ok=True)
    rows = list(results)
    json_path = report_dir / "report.json"
    md_path = report_dir / "report.md"
    html_path = report_dir / "index.html"
    write_json(json_path, {"agent": agent, "results": rows})
    markdown = render_markdown(agent, rows)
    md_path.write_text(markdown)
    html_path.write_text(render_html(markdown))
    return {"json": str(json_path), "markdown": str(md_path), "html": str(html_path)}


def report_from_run(run_report: Path, report_dir: Path) -> Dict[str, str]:
    data = json.loads(Path(run_report).read_text())
    return write_reports(report_dir, data.get("agent", "unknown"), data.get("results", []))
