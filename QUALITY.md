# Quality Notes

PatchGym release gates:

- fresh clone install from source,
- `ruff check .`,
- `pytest -q`,
- `python -m build`,
- `bash scripts/demo.sh`,
- hidden-test/oracle validity proof,
- README truth check,
- security review.

The project intentionally avoids fake package badges, fake benchmark numbers, and fake production claims.
