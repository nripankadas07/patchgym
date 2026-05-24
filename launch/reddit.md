# Reddit Draft

I built PatchGym, a small local tool for evaluating coding agents on your own
Git history.

The idea is simple: many bug-fix commits contain the base code, the regression
test, and the source fix. PatchGym turns that into a local benchmark task,
keeps the tests hidden from the agent, and grades the resulting patch with your
validation command.

It is alpha software, source-install only, and not a sandbox. I would value
feedback on the benchmark design and failure modes.
