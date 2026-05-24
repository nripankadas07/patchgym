# Architecture

PatchGym is intentionally small. The code has four stages:

1. `mine`: scan Git history and split a commit into hidden tests and an oracle patch.
2. `verify`: prove the split is useful by checking that hidden tests fail on the base and pass with the oracle patch.
3. `run`: export the base snapshot, run an agent command, capture its diff, apply hidden tests, and validate.
4. `report`: write machine-readable JSON and a compact Markdown summary.

## Why Git History

Git history is a practical source of benchmark tasks because it contains real project context:

- the code before a change,
- the tests that described the desired behavior,
- the patch that fixed the behavior,
- the commit message that summarized intent.

PatchGym does not infer correctness from the commit message. It uses the repository's validation command as the grader.

## Hidden Tests

The miner treats files that look like tests as the hidden test patch and all other changed files as the oracle solution patch. This is a heuristic, but it is easy to inspect. Bad tasks should be removed or curated instead of silently trusted.

## Isolation Model

PatchGym exports a Git archive of the base commit into a temporary directory, initializes a fresh Git repo, and runs the agent there. The agent does not receive the original Git history by default.

This is not a security sandbox. Agent commands and validation commands execute locally.

## Failure Modes

Common reasons a mined task is invalid:

- the historical commit did not include tests,
- hidden tests pass before the fix,
- the oracle patch no longer applies cleanly,
- validation depends on services or files outside the repo,
- test-file path heuristics split the commit incorrectly.

The `patchgym verify` command exists to catch these before agent runs.
