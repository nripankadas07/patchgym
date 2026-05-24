# X Thread Draft

1. PatchGym turns your Git history into local coding-agent benchmarks.

2. Many bug-fix commits already contain a useful benchmark shape: base code,
hidden regression test, and source fix.

3. PatchGym verifies the key invariant: base + hidden tests fails; base + hidden
tests + oracle patch passes.

4. Then it runs an agent command, applies hidden tests, and reports whether the
patch actually fixed the code.

5. It is alpha, local-first, source-installable, and intentionally not a
leaderboard.
