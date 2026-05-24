# Hidden Tests

A hidden test patch is the part of a historical commit that changed tests. An
oracle solution patch is the part of the same commit that changed source code.

The validity invariant is:

```text
base + hidden tests fails
base + hidden tests + oracle patch passes
```

Hidden tests matter because the agent should not simply read the expected
solution. The agent gets the base repository and prompt; the verifier keeps the
hidden tests and oracle patch separate.

False positives can happen if path heuristics classify files incorrectly. False
negatives can happen when a real fix has no tests in the same commit. PatchGym
therefore treats mining as candidate generation and verification as the gate.
