# Agent Adapters

PatchGym's adapter interface is a shell command:

```bash
patchgym run <task-id> --agent "your-agent-command"
```

The command runs inside a temporary base repository snapshot and should edit the
working tree in place.

PatchGym provides these environment variables:

- `PATCHGYM_TASK_ID`
- `PATCHGYM_REPO_DIR`
- `PATCHGYM_PROMPT_FILE`
- `PATCHGYM_METADATA_FILE`
- `PATCHGYM_VALIDATION_COMMAND`

You can use this manually with tools such as Codex, Claude Code, Aider, or
OpenHands by wrapping the tool invocation in a shell script. PatchGym does not
depend on any of those tools and does not require an API key for the demo.
