# How It Works

Lifecycle:

```text
Git history -> mining -> task files -> verification -> agent run -> grading -> report
```

## Mining

PatchGym scans first-parent commits and looks for small changes that touch both
test-looking files and source files. These commits are likely to contain a
behavior change plus the tests that describe it.

## Task Creation

For each candidate commit, PatchGym writes:

- `task.json`
- `hidden_tests.patch`
- `oracle_solution.patch`

The agent-facing prompt is derived from the historical commit subject and the
changed source paths. The oracle patch remains maintainer-only.

## Verification

PatchGym exports the base commit, applies hidden tests, and expects validation
to fail. It then applies the oracle patch and expects validation to pass.

## Agent Run

An agent command runs inside a temporary base workspace. PatchGym captures the
agent diff, applies hidden tests, and runs validation.

## Grading and Reporting

A task is solved when validation exits with code `0`. Reports include pass/fail,
changed files, validation return code, duration, and patch size.
