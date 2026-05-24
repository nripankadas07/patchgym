# Security Policy

PatchGym is a local benchmark harness, not a security sandbox.

PatchGym runs local repository validation commands and test suites. PatchGym can
also run arbitrary user-provided agent commands. Unknown repositories, unknown
tests, and unknown agents can execute arbitrary code on your machine.

Use a disposable VM, container, or separate machine for untrusted repositories or
agents. Do not point PatchGym at private code unless you are comfortable with
the local commands you ask it to run.

Report vulnerabilities privately through GitHub security advisories if enabled,
or contact the maintainer with a minimal reproduction and no secrets.
