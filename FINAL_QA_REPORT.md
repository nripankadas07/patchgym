# PatchGym Final QA Report

## Repository
- URL: https://github.com/nripankadas07/patchgym
- Branch: `main`
- Commit: latest pushed `main`; see final release response or `git log -1` for the exact hash
- Public: yes, repository is public

## CI
- Workflow: `.github/workflows/ci.yml`
- Python versions: `3.9`, `3.10`, `3.11`, `3.12`, `3.13`
- Commands: install package, CLI smoke test, `ruff check .`, `pytest -q`, `python -m build`, wheel reinstall smoke test, `patchgym demo --keep-dir patchgym-demo-ci`
- Latest status: green on `main` during final verification; verify the live result at https://github.com/nripankadas07/patchgym/actions

## Local fresh-clone verification
- Clone: pass, `git clone https://github.com/nripankadas07/patchgym /tmp/patchgym-final-hardening`
- Install: pass, `python -m pip install -e ".[dev]"`
- CLI: pass, `patchgym --help` and `python -m patchgym --help`
- Ruff: pass, `ruff check .` -> `All checks passed!`
- Tests: pass, `pytest -q` -> `11 passed`
- Build: pass, `python -m build` created sdist and wheel
- Wheel install: pass, `python -m pip install --force-reinstall dist/*.whl`
- Demo: pass, `bash scripts/demo.sh` and `patchgym demo --keep-dir patchgym-demo-final-rerun`

## Task validity
- Base + hidden tests: fail as expected, exit code `1`
- Base + hidden tests + oracle: pass, exit code `0`
- Noop baseline: fail, `0/1`
- Oracle baseline: pass, `1/1`

## Reports
- Markdown: `.patchgym/reports/report.md` from `bash scripts/demo.sh`
- JSON if generated: `.patchgym/reports/report.json` from `bash scripts/demo.sh`
- HTML if generated: `.patchgym/reports/index.html` from `bash scripts/demo.sh`

## Security review
- eval/exec: no `eval(` or `exec(` in `src`, `tests`, or `examples`
- shell command handling: `shell=True` is limited to the explicit user-provided agent command adapter
- cleanup safety: `safe_remove_tree` resolves paths and only removes directories under an allowed root
- timeout coverage: Git helpers, validation commands, and agent commands use timeouts
- untrusted code warning: README and SECURITY.md warn that tests and agent commands can execute arbitrary local code

## README truth check
- No PyPI claim: pass; README says PatchGym is not published to PyPI
- No fake metrics: pass
- No fake leaderboard: pass; leaderboard mentions are limitations or non-goals only
- Demo command works: pass, `bash scripts/demo.sh` and `patchgym demo --keep-dir ...`

## Profile integration
- Profile README: polished on `main`; PatchGym appears as the first flagship.
- Manual pinning required: no, PatchGym is pinned first on the public GitHub profile.

## Known limitations
- Works best when tests and fixes land in the same historical commit.
- Test-file detection is heuristic.
- There is no strong sandbox by default; use a VM/container for untrusted repos or agents.
- Local test flakiness affects benchmark quality.
- PatchGym is not a public leaderboard and does not publish model comparisons.

## Exact commands run

```bash
rm -rf /tmp/patchgym-final-hardening
git clone https://github.com/nripankadas07/patchgym /tmp/patchgym-final-hardening
cd /tmp/patchgym-final-hardening
git status --short
git log --oneline -5
git checkout -b harden/launch-readiness
find . -maxdepth 2 -type f | sort
find docs -maxdepth 2 -type f | sort || true
find tests -maxdepth 2 -type f | sort || true
find .github -maxdepth 3 -type f | sort || true
cat pyproject.toml
cat .github/workflows/ci.yml
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
patchgym --help
python -m patchgym --help
ruff check .
pytest -q
python -m build
python -m pip install --force-reinstall dist/*.whl
patchgym --help
python -c "import patchgym; print(patchgym.__name__)"
patchgym demo --keep-dir patchgym-demo-final
bash scripts/demo.sh
patchgym demo --keep-dir patchgym-demo-final-rerun
```
