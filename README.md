# PatchGym

Turn any Git repository into a local SWE-bench-style coding-agent benchmark.

PatchGym mines real Git history, creates hidden-test coding-agent tasks, runs agents against those tasks, and reports whether their patches actually fixed the code.

PatchGym is alpha software: local-first, practical, research-quality, and designed to be read. It is not a hosted leaderboard, not a cloud service, and not a claim that one model or agent wins everywhere.

## Install From Source

PatchGym is not published to PyPI. Install it from a source checkout:

```bash
git clone https://github.com/nripankadas07/patchgym
cd patchgym
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## 60-Second Demo

```bash
bash scripts/demo.sh
```

The demo creates a tiny Git repository, mines one historical bug fix, verifies the hidden-test/oracle split, runs a toy shell agent, grades the patch, and writes:

- `.patchgym/reports/report.json`
- `.patchgym/reports/report.md`
- `.patchgym/reports/index.html`

Expected shape:

```text
mined 1 task(s)
built 1/1 valid task(s)
agent 'bash .../examples/custom_agent/agent.sh' solved 1/1 task(s)
PatchGym demo complete
```

## Flagship Evidence

PatchGym is the flagship because it is a concrete evaluation loop, not just a
demo wrapper. It mines real Git history, proves task validity with hidden tests
and an oracle patch, runs an agent command in a fresh workspace, and writes
auditable reports.

Reviewer-oriented entry points:

- [Benchmark page](docs/benchmark-page.md): what PatchGym measures, what it does
  not claim, and how the local benchmark invariant works.
- [Comparisons](docs/comparisons.md): a table against public benchmarks,
  repo-to-prompt tools, coding agents, and plain test runners.
- [90-second walkthrough script](docs/walkthrough-90-seconds.md): the short
  recorded-demo script for explaining the project quickly and honestly.

## How It Works

For each selected historical commit, PatchGym splits the change into:

- base commit,
- hidden test patch,
- oracle solution patch,
- task prompt,
- validation command.

A task is valid only when:

```text
base + hidden tests fails
base + hidden tests + oracle patch passes
```

During an agent run, PatchGym exports the base commit into a temporary workspace, runs the agent command there, captures the agent diff, applies hidden tests, runs the validation command, and records the result.

Deeper docs:

- [PatchGym from scratch](docs/patchgym-from-scratch.md)
- [How it works](docs/how-it-works.md)
- [Mining Git history](docs/mining-git-history.md)
- [Hidden tests](docs/hidden-tests.md)
- [Agent adapters](docs/agent-adapters.md)
- [Sandboxing](docs/sandboxing.md)
- [Evaluation metrics](docs/evaluation-metrics.md)
- [Reproducible runs](docs/reproducible-runs.md)
- [Comparisons](docs/comparisons.md)
- [Limitations](docs/limitations.md)

## CLI

```bash
patchgym init
patchgym mine .
patchgym build .
patchgym list
patchgym show <task-id>
patchgym verify <task-id>
patchgym context <task-id>
patchgym run <task-id> --agent "bash examples/custom_agent/agent.sh"
patchgym grade
patchgym report
patchgym replay <task-id>
```

Older path-oriented usage also works:

```bash
patchgym mine /path/to/repo --out .patchgym/tasks --validation "python -m pytest -q"
patchgym verify .patchgym/tasks --repo /path/to/repo
patchgym run .patchgym/tasks --repo /path/to/repo --agent noop
```

## Example Task

A task directory looks like:

```text
.patchgym/tasks/<task-id>/
  task.json
  hidden_tests.patch
  oracle_solution.patch
  context/
    CODEX_TASK.md
    AGENTS.md
```

The agent receives the prompt/context, not the hidden tests or oracle patch. Maintainers can inspect the oracle patch to audit task quality.

## Example Report

`patchgym report` writes JSON, Markdown, and HTML. The Markdown report includes:

- tasks generated,
- pass/fail result,
- changed files,
- validation command,
- duration,
- local execution safety note.

Each run directory also writes:

- `manifest.json`: task commits, hidden-test/oracle patch hashes, artifact
  hashes, changed files, return codes, and totals.
- `trace.jsonl`: a TraceWeave-compatible event stream for agent execution,
  patch capture, hidden-test application, validation, and grading.

These files are designed to be ingested by SandboxLedger and analyzed by
TraceWeave without giving the agent hidden tests or oracle patches.

## Safety Warning

PatchGym runs local Git commands, validation commands, tests, and explicit user-provided agent shell commands. Do not run it on untrusted repositories or with untrusted agents unless you use a disposable container, VM, or machine.

`shell=True` is only used for the explicit agent command. Validation commands are split and executed without a shell. Agent and validation commands both have timeouts.

## Limitations

PatchGym works most reliably when tests and fixes land in the same commit. It uses path heuristics to identify test files. It does not provide strong isolation by default. It does not claim public leaderboard readiness or a complete public-benchmark export format.

More limitations are documented in [docs/limitations.md](docs/limitations.md).

## Comparison

SWE-bench-style public benchmarks are valuable for broad comparison. PatchGym asks a narrower local question: can an agent fix tasks mined from your repository, under your tests, using your project history?

PatchGym is smaller and less comprehensive than public benchmark infrastructure. That is intentional: it is a readable reference harness and a practical local evaluation loop.

## Development

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
ruff check .
pytest -q
python -m build
bash scripts/demo.sh
```

CI runs the same core gates across Python 3.9 through 3.13: CLI smoke tests,
Ruff, pytest, build, wheel install, and demo.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## License

MIT. See [LICENSE](LICENSE).
