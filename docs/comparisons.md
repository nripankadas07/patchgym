# Comparisons

PatchGym is easiest to understand by what it is not. It is not trying to be the
largest public benchmark, the smartest coding agent, or a repo summarizer. It is
a local harness for turning a repository's own history into coding-agent repair
tasks.

| Comparison | What They Optimize For | What PatchGym Optimizes For |
|---|---|---|
| SWE-bench-style public benchmarks | Shared public comparison across agents and models. | Local evaluation against a maintainer's own repository history. |
| SWE-Gym / SWE-smith-style research environments | Large-scale benchmark generation, research workflows, or training/evaluation datasets. | A small readable reference harness that can be audited from source. |
| Repo-to-prompt tools | Packaging repository context for a model. | Creating verifiable tasks, running agents, applying hidden tests, and writing reports. |
| Coding agents | Producing code changes in a workspace. | Evaluating whether those changes survive hidden tests and validation commands. |
| Plain test runners | Checking the current state of a codebase. | Replaying historical bug-fix tasks as agent-evaluation items. |

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
