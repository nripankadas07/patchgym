# Reproducible Runs

PatchGym run directories are meant to be inspected after the agent finishes.
Every `patchgym run` now writes three layers of evidence:

- `report.json` and `report.md`: human and machine-readable pass/fail summary.
- `manifest.json`: commits, validation commands, hidden-test patch hashes,
  oracle patch hashes, return codes, changed files, and artifact SHA-256s.
- `trace.jsonl`: event stream for task preparation, agent execution, patch
  capture, hidden-test application, validation, grading, and run summary.

The agent never receives hidden tests, oracle patches, or the manifest. Those
files are written after execution so maintainers can audit what happened.

## Stack Flow

```bash
patchgym run <task-id> --agent "bash examples/custom_agent/agent.sh"
traceweave patchgym .patchgym/runs/latest --json
sandboxledger ingest-patchgym ledger.jsonl .patchgym/runs/latest
sandboxledger verify ledger.jsonl
```

This creates a local chain:

1. PatchGym executes the task and writes reproducibility artifacts.
2. TraceWeave analyzes the run trace for loops, churn, drift, and errors.
3. SandboxLedger records the run artifacts in a hash chain with a Merkle root.

## What The Manifest Proves

The manifest records:

- task id, base commit, target commit, and commit subject;
- SHA-256 of the hidden-test patch and oracle solution patch;
- validation command and return code;
- agent return code and duration;
- patch line count and changed files;
- SHA-256 digests for stdout, stderr, validation output, and agent patch.

It does not prove that the host machine was isolated. Use containers or VMs for
untrusted repositories and agents.

