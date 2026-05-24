# Quality Notes

PatchGym is maintained as a local-first, source-installable reference
implementation.

Quality bar:

- hidden-test/oracle verification before benchmark claims,
- reproducible demo from a fresh clone,
- honest benchmark reporting with no fake metrics,
- no fake model comparisons or leaderboard claims,
- no PyPI claim until a package is actually published,
- CI must run CLI smoke tests, Ruff, pytest, build, wheel install, and demo.
