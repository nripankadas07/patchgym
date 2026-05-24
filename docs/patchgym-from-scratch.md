# PatchGym From Scratch

PatchGym starts from a repository's own Git history. A useful historical commit often contains three things: the code before a change, tests that describe the desired behavior, and the source patch that satisfies those tests.

The minimum loop is:

```bash
patchgym init
patchgym mine .
patchgym build .
patchgym list
patchgym run <task-id> --agent "your-agent-command"
patchgym report
```

The implementation is intentionally small so maintainers can inspect how tasks are created and graded.
