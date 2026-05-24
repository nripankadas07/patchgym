# Dev.to Draft

# PatchGym: turn Git history into coding-agent benchmarks

PatchGym is a small Python project for maintainers who want to evaluate coding
agents on their own repositories.

It mines historical commits, extracts hidden tests, verifies task validity, runs
an explicit agent command, and generates reports. The project is intentionally
local-first and readable rather than a hosted benchmark platform.

The most important invariant is:

```text
base + hidden tests fails
base + hidden tests + oracle patch passes
```

That keeps the benchmark honest before any agent score is reported.
