# Task Format

A PatchGym task is a directory:

```text
<task-id>/
  task.json
  hidden_tests.patch
  oracle_solution.patch
```

## `task.json`

Important fields:

- `id`: deterministic identifier based on the historical commit.
- `source_repo`: local path used when the task was mined.
- `base_commit`: parent commit used as the starting snapshot.
- `target_commit`: historical commit containing the fix and tests.
- `validation_command`: shell command used to grade the task.
- `prompt`: text shown to the agent.
- `test_files`: paths included in the hidden test patch.
- `solution_files`: paths included in the oracle solution patch.

## Patch Semantics

The benchmark invariant is:

```text
base + hidden_tests.patch fails
base + hidden_tests.patch + oracle_solution.patch passes
```

During an agent run:

```text
base + agent_patch + hidden_tests.patch passes => solved
```

The agent should not receive `hidden_tests.patch` or `oracle_solution.patch` in normal evaluation.
