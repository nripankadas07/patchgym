# Agent Adapters

PatchGym runs any shell command as an agent:

```bash
patchgym run <task-id> --agent "bash examples/custom_agent/agent.sh"
```

The command runs inside a temporary base repository snapshot. PatchGym provides:

- `PATCHGYM_TASK_ID`
- `PATCHGYM_REPO_DIR`
- `PATCHGYM_PROMPT_FILE`
- `PATCHGYM_METADATA_FILE`
- `PATCHGYM_VALIDATION_COMMAND`

The command should edit files in the current working directory.
