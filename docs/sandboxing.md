# Sandboxing

PatchGym creates temporary workspaces, but it is not a strong sandbox.

Local execution includes:

- Git commands,
- repository validation commands,
- test suites,
- explicit agent shell commands.

Agent and validation commands have timeouts. Python bytecode caches are kept
workspace-local where possible and cleaned before validation transitions. Cleanup
helpers check resolved paths before deleting generated directories.

For untrusted repositories or agents, run PatchGym inside a disposable container,
VM, or separate machine. Optional Docker/container execution is a roadmap item,
not an MVP guarantee.
