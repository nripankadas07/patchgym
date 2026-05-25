# 90-Second Walkthrough Script

Use this as the script for a short recorded demo.

## 0-15 Seconds: The Problem

Coding agents are easy to demo and hard to evaluate. Public benchmarks are
useful, but they rarely answer the maintainer's practical question: can this
agent fix my repository under my tests and constraints?

## 15-35 Seconds: The Idea

PatchGym turns Git history into local coding-agent benchmark tasks. A historical
bug-fix commit often contains the base code, the tests that describe the desired
behavior, and the patch that fixed the issue.

PatchGym splits that commit into hidden tests and an oracle solution.

## 35-55 Seconds: The Invariant

A task is valid only if:

```text
base + hidden tests fails
base + hidden tests + oracle patch passes
```

That means the task actually grades behavior instead of just packaging a prompt.

## 55-75 Seconds: The Agent Run

PatchGym exports the base commit to a temporary workspace, runs an explicit
agent command, captures the agent diff, applies hidden tests, runs validation,
and writes JSON, Markdown, and HTML reports.

## 75-90 Seconds: The Boundary

PatchGym is local-first and inspectable. It is not a hosted leaderboard, not a
model-ranking claim, and not a sandbox. It is a small evaluation harness for
people who want evidence before trusting agents on their own code.
