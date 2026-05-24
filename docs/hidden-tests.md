# Hidden Tests

Hidden tests are the grading signal. PatchGym extracts them from historical test changes and keeps them separate from the agent context.

The required invariant is:

```text
base + hidden tests fails
base + hidden tests + oracle source patch passes
```

Without that invariant, a task may be too easy, impossible, or unrelated to the historical fix.
