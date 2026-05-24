# Mining Git History

PatchGym uses Git history as data. It reads recent first-parent commits, skips merge commits, and selects commits where at least one test-looking path and one source path changed.

This keeps the MVP readable, but it is a heuristic. Repositories with unusual test layouts may need manual curation or future language-specific detectors.

Candidate tasks should always be verified before they are used for agent comparison.
