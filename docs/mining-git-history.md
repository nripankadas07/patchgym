# Mining Git History

Good candidates usually have:

- one parent commit,
- a small diff,
- at least one source file change,
- at least one test file change,
- a validation command that can run locally.

PatchGym prefers commits with source plus tests because hidden tests need to
describe the behavior being fixed. Commits that only change source are hard to
grade. Commits that only change tests are not agent repair tasks.

Common rejection reasons:

- merge commit,
- rename-heavy or very large diff,
- no test-looking paths,
- no source-looking paths,
- patch too large for a readable local task.

The test-path detector is intentionally heuristic. Repositories with unusual
layouts may need manual curation or future language-specific detection.
