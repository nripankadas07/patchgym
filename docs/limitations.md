# Limitations

- Works most reliably when tests and fixes land in the same commit.
- Uses heuristic test-file detection.
- Does not provide strong sandboxing by default.
- Local test flakiness can produce noisy benchmark results.
- Does not host datasets or publish a leaderboard.
- Does not include fake model results or model comparisons.
- Does not claim a complete public-benchmark export format.

PatchGym should be treated as a local benchmark harness and educational
reference implementation, not as a production isolation system.
