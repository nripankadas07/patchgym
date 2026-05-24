# How It Works

PatchGym scans first-parent Git history and looks for small commits that changed both test-looking files and source files.

For each candidate:

- the parent commit becomes the base state,
- test-file changes become hidden tests,
- source-file changes become the oracle patch,
- the commit subject becomes part of the task prompt,
- the configured validation command becomes the grader.

The task is accepted only if hidden tests fail on the base and pass after the oracle patch.
