# Public Verification

Verification date: 2026-05-24

## URLs

| URL | Result | Notes |
| --- | --- | --- |
| https://github.com/nripankadas07/patchgym | Pass | Public repository page is accessible. |
| https://github.com/nripankadas07/patchgym/actions | Pass | Actions page is public. The latest `main` workflow must be green before pinning. |
| https://github.com/nripankadas07/patchgym/blob/main/README.md | Pass | README URL is public. The hardening branch keeps source install, demo, CLI, safety, limitations, comparison, development commands, roadmap, and license. |
| https://github.com/nripankadas07/patchgym/blob/main/docs/patchgym-from-scratch.md | Pass | Documentation URL is public. |
| https://github.com/nripankadas07/nripankadas07 | Pass | Profile repository is public. |
| https://github.com/nripankadas07 | Partial | Profile is public, but repository pins still need manual UI updates. |

## Notes

- No broken local image references are used in the README.
- PatchGym profile pinning has not been changed by Codex.
- Re-run this checklist after future pushes because the live Actions page is the source of truth for current CI status.
