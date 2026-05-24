# Contributing

PatchGym is meant to stay small, readable, and honest. Contributions are welcome when they make the benchmark harness easier to understand, easier to verify, or safer to run locally.

Good first contributions:

- improve test-file detection for a language,
- add focused tests around mining edge cases,
- improve report clarity,
- document a real-world task curation workflow.

Please avoid adding mandatory cloud services, heavyweight databases, or vendor-specific assumptions to the core path.

## Local Checks

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest -q
patchgym demo
```
