# PatchGym Benchmark Page

PatchGym answers one narrow question:

```text
Can a coding agent fix tasks mined from this repository's own Git history,
under this repository's tests and constraints?
```

It is not a hosted leaderboard and it does not claim broad model superiority.
It is a local benchmark harness for maintainers who want repeatable evidence
before trusting agents on their own code.

## What It Measures

PatchGym measures whether an agent can edit a base repository snapshot so that
hidden tests and the repository validation command pass.

For every mined task, the benchmark invariant is:

```text
base commit + hidden tests fails
base commit + hidden tests + oracle patch passes
```

Only tasks that satisfy that invariant are useful. The invariant keeps the
benchmark grounded: the base must fail, the known historical fix must pass, and
the agent must produce a patch that survives the same hidden test boundary.

## What A Run Produces

A run produces local artifacts that can be inspected without a hosted service:

- task metadata;
- hidden test patch;
- oracle solution patch;
- agent patch;
- validation command result;
- stdout and stderr captures;
- JSON, Markdown, and HTML reports.

## Comparison Table

| Tool Type | Primary Job | Shared Public Score | Local Repo History | Hidden-Test Task Generation | Agent Execution |
|---|---|---:|---:|---:|---:|
| SWE-bench-style benchmarks | Compare agents on a shared public task set | Yes | No | Curated externally | Usually external harness |
| Repo-to-prompt tools | Package repository context for a model | No | Yes | No | No |
| Coding agents | Edit code in a workspace | No | Yes | No | Yes |
| Plain test runners | Check a current codebase | No | Yes | No | No |
| PatchGym | Build and run local coding-agent benchmark tasks | No | Yes | Yes | Yes |

PatchGym is intentionally smaller than public benchmark infrastructure. Its
value is that it lets a maintainer evaluate agents against their own repository
history with ordinary Git patches and local tests.

## Reproducible Demo

From a clean checkout:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
bash scripts/demo.sh
```

Expected shape:

```text
mined 1 task(s)
built 1/1 valid task(s)
agent 'bash .../examples/custom_agent/agent.sh' solved 1/1 task(s)
PatchGym demo complete
```

## Honest Boundaries

PatchGym does not provide strong sandboxing by default. Agent commands,
validation commands, tests, and Git operations execute locally. For untrusted
repositories or untrusted agents, run it inside a disposable container, VM, or
separate machine.

PatchGym also does not claim package-registry publication, production adoption,
hosted results, model rankings, or public leaderboard status.
