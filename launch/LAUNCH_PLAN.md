# Launch Plan

PatchGym should launch only after CI is green on the release commit.

Checklist:

- README uses source install, not PyPI install.
- Demo runs from a fresh clone.
- CI passes on supported Python versions.
- No fake benchmark numbers or model comparisons.
- Manual profile pinning is complete or clearly marked as manual.

Do not publish to PyPI or create a GitHub release without explicit approval.
