## Summary

## Tests Run

- [ ] `ruff check .`
- [ ] `pytest -q`
- [ ] `python -m build`
- [ ] `python -m pip install --force-reinstall dist/*.whl`
- [ ] `bash scripts/demo.sh` or `patchgym demo --keep-dir patchgym-demo-ci`

## Docs Updated

- [ ] README/docs updated
- [ ] No fake PyPI, release, benchmark, or leaderboard claims added

## Safety / Security Considerations

- [ ] No new unbounded command execution
- [ ] Agent command execution remains explicit and documented
- [ ] Cleanup paths are constrained to temp or `.patchgym` workspaces

## Breaking Change

- [ ] Yes
- [ ] No
