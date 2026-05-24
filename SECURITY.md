# Security Policy

PatchGym is a local benchmark harness, not a security sandbox.

Running PatchGym can execute:

- Git commands,
- repository validation commands,
- test suites,
- explicit user-provided agent shell commands.

Only run PatchGym on repositories and agent commands you trust. For untrusted code, use a disposable container, virtual machine, or isolated machine.

`shell=True` is reserved for the explicit agent command because agent adapters are intentionally shell-command based. Validation commands are executed without a shell and both agent and validation commands have timeouts.

Report security concerns by opening a GitHub issue with minimal reproduction details and no secrets.
