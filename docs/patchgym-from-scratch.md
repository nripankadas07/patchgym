# PatchGym From Scratch

PatchGym is built on a simple observation: a project's Git history often already
contains benchmark examples. A useful bug-fix commit has the code before the
fix, the tests that describe the desired behavior, and the source patch that
made those tests pass.

PatchGym turns that structure into a local coding-agent task:

1. Export the parent commit as the base workspace.
2. Treat historical test changes as hidden tests.
3. Treat historical source changes as the oracle patch.
4. Ask an agent to edit the base workspace without seeing the hidden tests.
5. Grade the agent by applying hidden tests and running the validation command.

The central invariant is:

```text
base + hidden tests fails
base + hidden tests + oracle patch passes
```

If that invariant is not true, the task is not a trustworthy benchmark item.
This is why PatchGym verifies tasks before reporting agent results.
