# SkillForge Strategic Improvement Loop

Status: draft implementation
Cadence: every 20 minutes when the Codex automation is active

## Purpose

The SkillForge strategic improvement loop is an ongoing, reviewable automation
for improving SkillForge itself and related skills, especially
`skills/codebase-to-agentic-skills` and healthcare-domain skills derived from
NVIDIA-Medtech and MONAI repositories.

The loop is not a background auto-merge bot. Each run should choose or continue
one focus, do useful work, leave a log, and keep changes easy for a human to
review.

## Strategic Scope

The loop may work as:

- Researcher: look for relevant repositories, papers, examples, standards, and
  prior art.
- Planner: convert findings into requirements, plans, backlog items, or issue
  drafts.
- Builder: implement a small reviewable improvement to SkillForge or a skill.
- Hardener: improve tests, cross-platform behavior, failure handling, and
  maintainability.
- Safety officer: review healthcare, privacy, license, data handling,
  permissions, and side effects.
- Brainstormer: identify and triage new healthcare skill opportunities.

Development of new skills is in scope when it is the best way to improve
SkillForge or healthcare repo-to-skills workflows.

## Healthcare Focus Sources

Start from these sources unless a run has a more specific user-approved focus:

- NVIDIA-Medtech: https://github.com/NVIDIA-Medtech
- NV-Segment-CTMR: https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR
- NV-Generate-CTMR: https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/tree/main
- MONAI: https://github.com/project-monai/monai
- Local design doc: `docs/codebase-to-agentic-skills.md`
- Local generator skill: `skills/codebase-to-agentic-skills/`

## Run Contract

Every run should:

1. Start with the deterministic helper:

```text
python -m skillforge improve-cycle --write-log --claim-run --json
```

2. If another run is active, avoid editing shared files. Prefer read-only
   research, or stop cleanly.
3. Choose or continue one focus. Do not thrash across unrelated ideas.
4. Prefer a small reviewable outcome over a large unfinished change.
5. Record source URLs, local files, commands, files changed, tests, what went
   well, what could improve, and the next action.
6. Release the run lock at the end:

```text
python -m skillforge improve-cycle --release-run <run-id> --json
```

## Concurrency

The automation cadence is intentionally short enough that one run may still be
active when the next one starts. The loop therefore uses:

- Unique Markdown run logs under `docs/improvement-loop/runs/`.
- An advisory active-run lock under `.skillforge/improvement-loop/`, which is
  ignored by Git.
- A stale-lock window so interrupted runs do not block the loop forever.
- Human-reviewable branches or worktrees for code changes.

The lock is advisory. It helps agents avoid collisions; it is not a permission
or security model.

## Review Expectations

Autonomous runs should not merge, push, publish, or install risky dependencies
without explicit human approval. A good run leaves one of these outcomes:

- A small code or documentation patch with tests.
- A source-backed research note.
- A clearer requirement or backlog item.
- A Skill Design Card or candidate table for a future healthcare skill.
- A clear blocker with what would unblock it.

## Related Commands

```text
python -m skillforge help improvement-loop
python -m skillforge improve-cycle --json
python -m skillforge improve-cycle --write-log --claim-run --json
python -m skillforge improve-cycle --release-run <run-id> --json
python -m skillforge codebase-scan <repo-path> --workflow-goal "Identify healthcare agentic skills" --json
python -m skillforge evaluate codebase-to-agentic-skills --json
```
