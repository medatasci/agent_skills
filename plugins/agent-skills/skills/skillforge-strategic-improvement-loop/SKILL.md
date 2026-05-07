---
name: skillforge-strategic-improvement-loop
owner: medatasci
description: Use this skill when the user wants a recurring, strategic, reviewable improvement loop for SkillForge itself, especially healthcare-domain improvements to codebase-to-agentic-skills, NVIDIA-Medtech or MONAI repo-derived skills, skill hardening, safety review, research, planning, brainstorming, or new skill development. Use it for Codex automation runs that must choose a focus, avoid concurrent-run collisions, work in reviewable branches or worktrees, and log what happened.
title: SkillForge Strategic Improvement Loop
short_description: Run recurring strategic improvement cycles that improve SkillForge and healthcare codebase-to-agentic-skills work with reviewable logs.
expanded_description: Use this skill to guide recurring Codex automation that improves SkillForge itself. The loop can research healthcare AI repositories, plan improvements, implement small patches, harden tests, review safety, brainstorm new skills, and improve codebase-to-agentic-skills. It must keep changes reviewable, avoid auto-merging, coordinate concurrent runs, and write persistent run logs.
aliases:
  - SkillForge improvement loop
  - improve SkillForge
  - recurring SkillForge automation
  - healthcare repo to skills improvement
  - strategic improvement cycle
categories:
  - Agent Workflows
  - Developer Tools
  - Skill Management
tags:
  - skillforge
  - automation
  - improvement-loop
  - codebase-to-agentic-skills
  - healthcare-ai
  - nvidia-medtech
  - monai
  - strategic-planning
tasks:
  - run a recurring SkillForge improvement cycle
  - improve codebase-to-agentic-skills
  - research healthcare AI repos for agentic skills
  - harden SkillForge tests and docs
  - review healthcare skill safety and source evidence
  - brainstorm new healthcare skills
use_when:
  - The user wants SkillForge to keep improving itself over time.
  - The user asks for recurring or scheduled Codex work on SkillForge.
  - The user wants to improve skills/codebase-to-agentic-skills.
  - The user wants healthcare-domain repo-to-skills research or hardening.
  - A Codex automation wakes up to run one SkillForge improvement cycle.
do_not_use_when:
  - The user wants a one-off direct answer unrelated to SkillForge or skills.
  - The user asks to auto-merge, auto-push, or publish changes without review.
  - The task requires installing dependencies, downloading models, running expensive jobs, or using credentials without explicit approval.
inputs:
  - optional focus override
  - optional lane: researcher, planner, builder, hardener, safety, or brainstormer
  - SkillForge repository checkout
  - optional healthcare source repo URL or local path
outputs:
  - selected focus and suggested actions
  - unique run log
  - reviewable code, docs, requirements, tests, research notes, or blocker notes
  - next action for the next run or human reviewer
examples:
  - SkillForge, run one strategic improvement loop for healthcare codebase-to-agentic-skills work.
  - SkillForge, improve SkillForge itself and leave a reviewable log.
  - SkillForge, research one NVIDIA-Medtech repo and identify candidate agentic skills.
  - SkillForge, harden codebase-to-agentic-skills for MONAI-style repositories.
related_skills:
  - skillforge
  - codebase-to-agentic-skills
  - skill-discovery-evaluation
  - nv-segment-ctmr
  - nv-generate-ctmr
risk_level: medium
permissions:
  - read local SkillForge files and docs
  - write run logs under docs/improvement-loop when requested
  - write code, docs, tests, or skill files only when the automation or user explicitly asks for implementation work
  - use network for web or Git research only when allowed by the active environment and task
  - do not merge, push, publish, install large dependencies, download models, or use credentials without explicit human approval
authoritative_sources:
  - https://github.com/medatasci/agent_skills/blob/main/requirements.md
  - https://github.com/medatasci/agent_skills/blob/main/docs/codebase-to-agentic-skills.md
  - https://github.com/NVIDIA-Medtech
  - https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR
  - https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/tree/main
  - https://github.com/project-monai/monai
citations:
  - Not applicable for the improvement loop itself. Cite upstream repositories, papers, model cards, dataset cards, licenses, and commits in each run log or generated skill artifact.
page_title: SkillForge Strategic Improvement Loop - Recurring SkillForge And Healthcare Skill Improvement
meta_description: Use the SkillForge Strategic Improvement Loop to run recurring, reviewable Codex cycles that improve SkillForge, codebase-to-agentic-skills, and healthcare repo-derived skills.
---

# SkillForge Strategic Improvement Loop

## What This Skill Does

Use this skill when the user wants SkillForge to keep improving itself through
recurring, strategic, reviewable Codex work.

The priority focus is SkillForge itself, especially
`skills/codebase-to-agentic-skills` and healthcare-domain skills derived from
NVIDIA-Medtech and MONAI repositories. Creating new skills is allowed when that
is the right improvement lever.

## Safe Default Behavior

Default to reviewable work, not autonomous publication.

Do not merge, push, create public PRs, install large dependencies, download
models, run expensive GPU jobs, use credentials, or publish claims without
explicit human approval. Keep local changes on a review branch or worktree and
write enough log detail for a human to understand what happened.

If another improvement-loop run appears active, avoid editing shared files.
Prefer read-only research, a separate worktree, or stopping cleanly with a log.

## Workflow

1. Start with the deterministic helper:

```text
python -m skillforge improve-cycle --write-log --claim-run --json
```

2. Read the selected focus, lane, warnings, healthcare sources, and run-log
   path.
3. Continue the active initiative unless it is blocked, done, or clearly the
   wrong focus for the user request.
4. Choose one useful role for the run:
   - researcher
   - planner
   - builder
   - hardener
   - safety
   - brainstormer
5. Do one small strategic task to a reviewable stopping point.
6. For healthcare repo-to-skills work, ground claims in source URLs, local
   files, papers, model cards, dataset cards, licenses, examples, or commits.
7. Use `codebase-to-agentic-skills` before turning a repository into candidate
   skills.
8. Update the run log with:
   - what was done
   - sources reviewed
   - commands run
   - files changed
   - tests and checks
   - what went well
   - what could be improved
   - the next action
9. Run relevant checks when files changed.
10. Release the advisory run lock:

```text
python -m skillforge improve-cycle --release-run <run-id> --json
```

## Strategic Lanes

Use these lanes to choose work:

| Lane | Use it for |
| --- | --- |
| researcher | Web or repo research, papers, examples, prior art, and source evidence. |
| planner | Requirements, plans, backlog items, issue drafts, and review structure. |
| builder | Small code, docs, tests, skill, or adapter improvements. |
| hardener | Tests, cross-platform behavior, failure modes, and maintainability. |
| safety | Healthcare, privacy, license, permissions, data handling, and side-effect review. |
| brainstormer | New skill ideas and triage, especially healthcare skill candidates. |

## Healthcare Source Priorities

Use these as default source families:

- NVIDIA-Medtech: https://github.com/NVIDIA-Medtech
- NV-Segment-CTMR: https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR
- NV-Generate-CTMR: https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/tree/main
- MONAI: https://github.com/project-monai/monai
- SkillForge codebase-to-agentic-skills docs:
  `docs/codebase-to-agentic-skills.md`
- SkillForge codebase-to-agentic-skills source:
  `skills/codebase-to-agentic-skills/`

## Agent CLI

Use the CLI for deterministic planning, logging, and concurrency checks:

```text
python -m skillforge improve-cycle --json
python -m skillforge improve-cycle --write-log --claim-run --json
python -m skillforge improve-cycle --lane researcher --write-log --claim-run --json
python -m skillforge improve-cycle --focus "Improve MONAI repo-to-skills scanning" --write-log --claim-run --json
python -m skillforge improve-cycle --release-run <run-id> --json
python -m skillforge improve-cycle --write-log --claim-run --lock-path test-output/improvement-loop-lock.json --json
```

Use these related commands during a run:

```text
python -m skillforge help improvement-loop
python -m skillforge codebase-scan <repo-path> --workflow-goal "Identify healthcare agentic skills" --json
python -m skillforge build-catalog --json
python -m skillforge evaluate <skill-id> --json
python -m unittest tests.test_skillforge
```

## Boundaries

- Do not treat recurring automation as a trust model.
- Do not let a recurring run overwrite unrelated user work.
- Do not start multiple unrelated initiatives when an active initiative can be
  completed or unblocked.
- Do not claim that a healthcare model, dataset, algorithm, or skill is safe,
  clinically valid, licensed, or accepted unless source evidence supports it.
- Do not hide write, network, dependency, credential, model-download, or GPU
  side effects.
