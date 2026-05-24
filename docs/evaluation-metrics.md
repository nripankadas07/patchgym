# Evaluation Metrics

The primary metric is binary:

```text
solved = hidden tests apply and validation exits 0
```

PatchGym also records:

- validation exit code,
- changed files,
- patch line count,
- agent duration,
- stdout/stderr files,
- noop and oracle baseline behavior.

The noop baseline should fail on valid tasks. The oracle baseline should pass.
Those baselines test the harness before comparing real agents.
