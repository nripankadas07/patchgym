# PatchGym: SWE-style Benchmarks From Your Own Git History

Public coding-agent benchmarks are useful, but they are not a substitute for testing agents on the code you actually maintain. PatchGym is a small reference implementation for turning a local Git repository into a coding-agent benchmark.

The project is based on a simple observation: many repositories already contain benchmark data. A historical commit often has the code before a bug fix, the tests that described the desired behavior, and the patch that made the tests pass. PatchGym extracts that structure and turns it into a repeatable task.

## The Benchmark Invariant

A PatchGym task is valid only if this is true:

```text
base commit + hidden tests fails
base commit + hidden tests + oracle patch passes
```

That invariant matters more than the prompt. If the hidden tests already pass on the base commit, the task is not useful. If the oracle patch does not pass, the task is not reproducible. PatchGym rejects the romance of benchmark generation and asks the boring question first: does the task actually grade anything?

## Mining A Task

PatchGym scans first-parent Git history and looks for small commits that changed both tests and source files. It splits each commit by path:

- test-looking files become `hidden_tests.patch`,
- all other changed files become `oracle_solution.patch`.

This is a heuristic, not magic. It works best when projects commit failing regression tests and fixes together. It is intentionally inspectable: the output is ordinary JSON and ordinary Git patches.

## Running An Agent

During evaluation, PatchGym exports the base commit with `git archive`, initializes a fresh Git repository in a temporary directory, and runs the agent command there. The agent receives a prompt file and metadata, then edits the working tree.

PatchGym captures the agent diff with:

```bash
git diff --binary
```

Then it applies the hidden tests and runs the validation command. A task is solved if validation exits with code 0.

## Why Local First

The design goal is not to host another leaderboard. It is to help maintainers ask a sharper question:

```text
Can this agent fix my codebase, with my tests, under my project constraints?
```

That question is local by nature. It depends on repository structure, test speed, project style, and the kinds of mistakes that happen in that codebase.

## Safety Boundary

PatchGym is a benchmark harness, not a sandbox. Validation commands and agent commands execute locally. That is acceptable for trusted repos and trusted commands, but not for arbitrary untrusted code. For untrusted inputs, run PatchGym in a disposable container, VM, or machine.

## What Makes It Useful

The useful unit is not a model score in isolation. It is a report containing:

- which tasks were attempted,
- which patches were produced,
- which hidden tests passed,
- which validation commands failed,
- how long each run took,
- what changed in the working tree.

That makes PatchGym closer to `pytest` for coding agents than a product platform. It gives developers a small, auditable loop for comparing agent behavior on real repository history.
