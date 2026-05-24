# PatchGym Final QA Report

## Summary
- Repo: `nripankadas07/patchgym`
- Branch: `main`
- Commit: `72f9ad6` verified from clean clone
- Public URL: https://github.com/nripankadas07/patchgym
- Profile repo: `nripankadas07/nripankadas07`
- Profile commit: `459d8f1`

## Fresh clone status
- Result: Pass
- Command: `rm -rf /tmp/patchgym-verify && git clone https://github.com/nripankadas07/patchgym /tmp/patchgym-verify`
- Notes: Clean clone succeeded. Latest verified commit was `72f9ad6 Harden PatchGym release gates`.

## Install status
- Result: Pass
- Command: `python3 -m venv .venv && . .venv/bin/activate && python -m pip install -U pip && python -m pip install -e ".[dev]"`
- Notes: Editable source install succeeded and created the `patchgym` console script.

## CLI status
- Result: Pass
- Commands verified: `patchgym --help`, `python -m patchgym --help`
- Notes: Help lists `init`, `mine`, `build`, `list`, `show`, `verify`, `run`, `grade`, `report`, `context`, and `replay`.

## Tests
- ruff: Pass, `ruff check .` -> `All checks passed!`
- pytest: Pass, `pytest -q` -> `5 passed`; `pytest -q -ra` -> `5 passed`
- build: Pass, `python -m build` built `patchgym-0.1.0.tar.gz` and `patchgym-0.1.0-py3-none-any.whl`
- demo: Pass, `bash scripts/demo.sh` mined one task, built `1/1` valid task, toy agent solved `1/1`, and generated JSON, Markdown, and HTML reports

## End-to-end task validity
- Task id: `d44a5852-fix-clamp-upper-bound-1e98b1ca`
- Base + hidden tests: failed as expected, exit `1`
- Base + hidden tests + oracle: passed, exit `0`
- Toy agent grade: `1/1`

## Reports generated
- JSON: `.patchgym/reports/report.json`
- Markdown: `.patchgym/reports/report.md`
- HTML: `.patchgym/reports/index.html`

## Security review
- eval/exec: Pass, no `eval(` or `exec(` found in `src`, `tests`, or `examples`
- shell usage: One `shell=True` call, restricted to explicit user-supplied agent commands
- cleanup safety: Cleanup goes through `safe_remove_tree`, which checks resolved paths against an allowed root
- timeout coverage: Git helpers, git archive, validation commands, and agent commands have timeouts
- documented warnings: README and SECURITY.md warn that untrusted repos, tests, and agents execute local code

## README truth check
- PyPI claims: Pass, README says PatchGym is not published to PyPI
- fake metrics: Pass, no fake benchmark numbers, stars, downloads, or leaderboard claims
- unsupported badges: Pass, no fake badges
- demo command: Pass, README uses `bash scripts/demo.sh`
- limitations: Pass, README and docs/limitations.md explain alpha scope and sandbox limitations

## Profile integration
- Profile README updated: Pass
- PatchGym card: Pass, profile README contains `### patchgym` with source install and `bash scripts/demo.sh`
- Catalog updated: Pass, profile README AI/evaluation catalog includes PatchGym
- Manual pins documented: Pass, both repos include `MANUAL_ACTIONS.md`

## Public verification
- PatchGym public URL: Pass
- Profile public URL: Partial, README card is visible but pinned repos still require manual update
- CI URL: Pass
- Docs URL: Pass

## Remaining blockers
- None for repository readiness.
- Manual profile pinning remains outside Codex API control.

## Manual actions
- Pin PatchGym in position 1.
- Add social preview image.
- Enable Discussions if desired.
- Create GitHub Release only after approval.
- Publish to PyPI only after approval.

## Exact commands run

```bash
pwd
git --version
gh --version || true
gh auth status || true
gh repo view nripankadas07/patchgym --json name,nameWithOwner,url,description,visibility,isPrivate,isArchived,repositoryTopics,defaultBranchRef || true
rm -rf /tmp/patchgym-verify
git clone https://github.com/nripankadas07/patchgym /tmp/patchgym-verify
cd /tmp/patchgym-verify
git status --short
git log --oneline -5
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
python -c "import patchgym; print(patchgym.__name__)"
patchgym --help
python -m patchgym --help
ruff check .
python -m build
python -m pip install dist/*.whl --force-reinstall
patchgym --help
pytest -q
pytest -q -ra
bash scripts/demo.sh
rm -rf /tmp/patchgym-manual
mkdir -p /tmp/patchgym-manual
cd /tmp/patchgym-manual
python /tmp/patchgym-verify/tests/fixtures/make_tinycalc_repo.py tinycalc
cd tinycalc
patchgym init
test -f patchgym.toml
patchgym mine .
patchgym build .
patchgym list
TASK_ID="$(patchgym list --plain 2>/dev/null | head -1 | awk '{print $1}' || true)"
patchgym show "$TASK_ID"
patchgym verify "$TASK_ID"
patchgym context "$TASK_ID"
find .patchgym/tasks/"$TASK_ID" -maxdepth 3 -type f | sort
patchgym run "$TASK_ID" --agent "bash /tmp/patchgym-verify/examples/custom_agent/agent.sh"
patchgym report
gh run list --repo nripankadas07/patchgym --limit 5
gh repo view nripankadas07/patchgym --json description,repositoryTopics,homepageUrl,licenseInfo,isPrivate,isArchived,hasIssuesEnabled,hasDiscussionsEnabled
```
