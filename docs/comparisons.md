# Comparisons

## PatchGym vs SWE-bench

SWE-bench-style public benchmarks help compare agents on shared tasks. PatchGym
asks a local question: can an agent fix tasks mined from your own repository,
under your tests and project style?

## PatchGym vs SWE-Gym / SWE-smith-style Research Environments

Research environments can generate or curate large benchmark sets. PatchGym is
smaller and intentionally readable. It is a local reference harness, not a
dataset factory or training environment.

## PatchGym vs Repo-to-Prompt Tools

Repo-to-prompt tools package context. PatchGym creates verifiable tasks, runs
agents, applies hidden tests, and writes reports.

## PatchGym vs Coding Agents

PatchGym is not a coding agent. It is a gym for evaluating coding agents with
local repository history.
