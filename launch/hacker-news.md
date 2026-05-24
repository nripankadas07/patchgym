# Hacker News Draft

Title:

Show HN: PatchGym - turn your Git history into coding-agent benchmarks

Post:

PatchGym is a small local-first Python tool for turning a repository's own Git
history into SWE-bench-style coding-agent tasks.

It mines commits that changed source and tests, splits them into hidden tests
and an oracle patch, verifies that base+hidden-tests fails and oracle passes,
then runs an agent command and reports whether the patch actually fixed the
code.

It is intentionally not a cloud service or leaderboard. The goal is a readable
reference implementation that maintainers can run on their own repositories.
