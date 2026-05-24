# PatchGym

Turn any Git repository into a local SWE-bench-style coding-agent benchmark.

PatchGym turns your Git history into a coding-agent gym. It mines real commits, extracts hidden tests and oracle patches, verifies that the task is meaningful, runs an agent command against the base repo, and reports whether the agent actually fixed the code.

The core idea is small: your repository already contains a history of bugs, fixes, tests, and design choices. PatchGym turns that history into reproducible coding-agent tasks.

## Why

Coding agents are useful, but public benchmark scores do not answer the question most maintainers care about:

> Which agent can safely fix my codebase, under my tests, with my architecture, using my real history?

PatchGym is a local-first reference implementation for answering that question. It does not require an API key for the demo. It does not run a cloud service. It does not claim leaderboard numbers. It gives you a readable harness you can inspect, modify, and run on your own repositories.

## Quickstart

Run the built-in demo from a checkout:

```bash
git clone https://github.com/nripankadas07/patchgym.git
cd patchgym
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
patchgym demo
```

The demo creates a tiny Git repo with one historical bug fix, mines it into a task, verifies the hidden-test/oracle split, runs a no-op agent, runs an oracle agent, and writes a Markdown report.

Expected shape:

```text
tasks mined: 1
verification: valid
noop solved: 0/1
oracle solved: 1/1
```

## CLI

Mine tasks from a repository:

```bash
patchgym mine /path/to/repo \
  --out .patchgym/tasks \
  --validation "python -m pytest -q" \
  --max-tasks 20
```

Verify mined tasks:

```bash
patchgym verify .patchgym/tasks --repo /path/to/repo
```

Run a shell-based agent:

```bash
patchgym run .patchgym/tasks \
  --repo /path/to/repo \
  --agent "python /path/to/my_agent.py" \
  --out .patchgym/runs/my-agent
```

PatchGym also includes two built-in baselines:

```bash
patchgym run .patchgym/tasks --agent noop
patchgym run .patchgym/tasks --agent oracle
```

`noop` changes nothing. `oracle` applies the historical solution patch and is useful for validating the benchmark harness itself.

## How It Works

For each selected historical commit, PatchGym tries to split the change into:

- a base commit,
- a hidden test patch,
- an oracle solution patch,
- a task prompt,
- a validation command.

A task is only useful if:

- `base + hidden tests` fails,
- `base + hidden tests + oracle solution` passes.

That invariant is the heart of the project.

At run time, an agent sees a clean exported snapshot of the base commit and a prompt. It does not receive the hidden tests or oracle solution. PatchGym captures the agent diff, applies the hidden tests, runs the validation command, and records the result.

For a deeper walkthrough, read [docs/TECHNICAL_ARTICLE.md](docs/TECHNICAL_ARTICLE.md).

## Agent Contract

PatchGym can run any command as an agent. The command is executed inside the base repository snapshot. The following environment variables are provided:

- `PATCHGYM_TASK_ID`
- `PATCHGYM_REPO_DIR`
- `PATCHGYM_PROMPT_FILE`
- `PATCHGYM_METADATA_FILE`
- `PATCHGYM_VALIDATION_COMMAND`

The agent should modify files in the current working directory. PatchGym captures those modifications with `git diff`.

Example agent:

```python
# examples/replace_agent.py
from pathlib import Path

path = Path("calculator.py")
text = path.read_text()
path.write_text(text.replace("return lower", "return upper", 1))
```

Then:

```bash
patchgym run .patchgym/tasks --agent "python examples/replace_agent.py"
```

## Task Format

Each task directory contains:

```text
task.json
hidden_tests.patch
oracle_solution.patch
```

`task.json` stores reproducibility metadata, including the base commit, target commit, prompt, validation command, changed files, and relative patch paths.

The patch files are ordinary Git patches. They can be inspected with:

```bash
git apply --stat .patchgym/tasks/<task>/hidden_tests.patch
git apply --stat .patchgym/tasks/<task>/oracle_solution.patch
```

## What This Is Not

PatchGym is not a cloud execution platform, a public leaderboard, a full SWE-bench replacement, or a sandbox for arbitrary untrusted code. It is a compact local benchmark generator and runner.

If you point PatchGym at an untrusted repository or run an untrusted agent command, you are executing code locally. Use a disposable machine, container, or VM when appropriate.

## Design Principles

- Local first.
- Readable over clever.
- Standard library runtime.
- Verification before benchmarking.
- Honest reports over inflated claims.
- Shell commands over vendor lock-in.
- Small enough to understand from source.

## Limitations

PatchGym currently works best on repositories where fixes and tests land in the same commit. It uses path heuristics to identify test files, so unusual layouts may need manual task curation. It does not provide strong isolation by default. Docker support is intentionally left as a thin optional layer rather than a required dependency.

## Roadmap

- More language-aware test-file heuristics.
- Optional Docker runner.
- Task curation commands.
- Adapters for common coding-agent CLIs.
- SWE-bench-compatible export.
- Richer failure classification.

## Development

```bash
python -m pip install -e ".[dev]"
pytest -q
patchgym demo
```

## License

MIT
