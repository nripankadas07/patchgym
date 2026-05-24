# Sandboxing

PatchGym is not a strong sandbox. It creates temporary workspaces, but validation commands and agent commands execute locally.

Use trusted repositories and trusted agents for normal local runs. For untrusted code, use an isolated container, VM, or disposable machine.

PatchGym applies timeouts to Git helpers, validation commands, and agent commands.
