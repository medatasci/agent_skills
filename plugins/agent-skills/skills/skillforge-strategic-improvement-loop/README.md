# SkillForge Strategic Improvement Loop

Skill ID: `skillforge-strategic-improvement-loop`

Run recurring, strategic, reviewable improvement cycles for SkillForge itself,
with special focus on healthcare-domain `codebase-to-agentic-skills` workflows.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/skillforge-strategic-improvement-loop

Parent package:
SkillForge Agent Skills Marketplace

Parent package repo URL:
https://github.com/medatasci/agent_skills

Distribution or marketplace:
SkillForge local catalog and Codex skill install workflow

Version or release channel:
Main branch draft until the automation workflow is reviewed in practice.

## Parent Collection

Parent collection:
SkillForge Agent Skills Marketplace

Collection URL:
https://github.com/medatasci/agent_skills

Categories:
Agent Workflows, Developer Tools, Skill Management

Collection context:
This skill is part of the SkillForge operating layer. It helps SkillForge
improve its own CLI, docs, skills, tests, and repo-to-skills workflows.

## What This Skill Does

This skill defines how Codex should run recurring strategic improvement cycles
for SkillForge. It can research, plan, build, harden, review safety, brainstorm,
or create new skills when doing so improves SkillForge.

The main target is SkillForge itself, especially
`skills/codebase-to-agentic-skills` and healthcare-domain skills derived from
NVIDIA-Medtech and MONAI repositories.

## Why You Would Call It

Call this skill when:

- You want SkillForge to keep improving over time.
- You want recurring Codex work to be strategic rather than random.
- You want healthcare repo-to-skills work to continue across sessions.
- You want each automation run to leave a reviewable log.
- You want concurrent runs to avoid editing the same files blindly.

Use it to:

- Improve SkillForge itself.
- Improve `codebase-to-agentic-skills`.
- Research NVIDIA-Medtech and MONAI repositories for agentic-skill candidates.
- Harden tests, docs, safety guidance, or deterministic CLIs.
- Create new healthcare skills when a source-backed opportunity is ready.

Do not use it when:

- You need a one-time direct answer unrelated to SkillForge.
- You want autonomous merging, pushing, dependency installation, or model
  downloads without human review.

## Keywords

SkillForge, improvement loop, recurring automation, Codex automation,
codebase-to-agentic-skills, healthcare AI, NVIDIA-Medtech, MONAI, agentic
skills, strategic planning, safety review, skill hardening.

## Search Terms

Improve SkillForge automatically, run a SkillForge improvement loop, improve
codebase-to-agentic-skills, recurring Codex automation, healthcare repo to
skills, turn NVIDIA-Medtech repos into agentic skills, turn MONAI workflows into
skills, strategic skill improvement, autonomous SkillForge research log.

## How It Works

The skill combines agent guidance with a deterministic CLI helper.

The helper selects or continues a focus, reports the current Git snapshot,
lists healthcare source priorities, creates a unique run log when requested,
and uses an advisory active-run lock so overlapping 20-minute jobs can avoid
trampling each other.

The Codex run then does one small strategic task and updates the run log with
sources, commands, changed files, tests, outcomes, and next action.

## API And Options

SkillForge CLI options:

```text
python -m skillforge install skillforge-strategic-improvement-loop --scope global
python -m skillforge search "improve SkillForge healthcare codebase skills" --json
python -m skillforge evaluate skillforge-strategic-improvement-loop --json
```

Improvement-loop commands:

```text
python -m skillforge help improvement-loop
python -m skillforge improve-cycle --json
python -m skillforge improve-cycle --write-log --claim-run --json
python -m skillforge improve-cycle --lane researcher --write-log --claim-run --json
python -m skillforge improve-cycle --focus "Improve MONAI repo-to-skills scanning" --write-log --claim-run --json
python -m skillforge improve-cycle --release-run <run-id> --json
```

Options:

- `--lane`: choose `researcher`, `planner`, `builder`, `hardener`, `safety`, or
  `brainstormer`.
- `--focus`: override the selected focus for one run.
- `--write-log`: write a Markdown run log under `docs/improvement-loop/runs/`.
- `--claim-run`: claim an advisory active-run lock under `.skillforge/`.
- `--release-run <run-id>`: release the advisory lock after the run completes.
- `--lock-path`: use an alternate advisory lock path for isolated tests or
  advanced automation.
- `--stale-minutes`: set when a lock should be treated as stale.

## Inputs And Outputs

Inputs:

- Optional focus override.
- Optional strategic lane.
- SkillForge repository checkout.
- Optional healthcare repository URL or local path.
- Optional user-approved implementation, research, or safety target.

Outputs:

- Selected focus.
- Suggested actions.
- Git snapshot.
- Healthcare source list.
- Unique Markdown run log.
- Optional code, docs, tests, requirements, research notes, Skill Design Cards,
  or skill packages.
- Next action for the next run or human reviewer.

## Limitations

- The skill cannot wake itself. Recurrence requires Codex automation.
- The active-run lock is advisory, not a security or permission model.
- Network research depends on the active environment and approval policy.
- Runtime work for healthcare models may require licenses, datasets, GPUs,
  WSL2/Linux, dependencies, and explicit human approval.
- The loop should not auto-merge or push changes.

## Examples

Promptable:

```text
SkillForge, run one strategic improvement loop for healthcare codebase-to-agentic-skills work.
```

```text
SkillForge, research one NVIDIA-Medtech repo and identify candidate agentic skills.
```

CLI:

```text
python -m skillforge improve-cycle --write-log --claim-run --json
```

```text
python -m skillforge improve-cycle --lane safety --write-log --claim-run --json
```

## Help And Getting Started

Start with:

```text
python -m skillforge help improvement-loop
python -m skillforge improve-cycle --json
```

For a real recurring run:

```text
python -m skillforge improve-cycle --write-log --claim-run --json
```

Then do one small piece of reviewable work and release the lock:

```text
python -m skillforge improve-cycle --release-run <run-id> --json
```

## How To Call From An LLM

Use plain language:

```text
SkillForge, improve SkillForge itself. Focus on healthcare codebase-to-agentic-skills work, leave a run log, and keep the changes reviewable.
```

An automation prompt should tell Codex to call the deterministic helper first,
honor the lock response, avoid merging or pushing without approval, update the
run log, run relevant tests, and release the lock at the end.

## How To Call From The CLI

Run commands from a SkillForge checkout:

```text
python -m skillforge improve-cycle --write-log --claim-run --json
```

Use `--json` for agents and scripts. Use `--lane` or `--focus` when a run needs
a narrower direction.

## Trust And Safety

Risk level:
medium

Permissions:

- Reads local SkillForge files and docs.
- Writes run logs when `--write-log` is used.
- Writes an advisory local lock when `--claim-run` is used.
- May write code, docs, tests, requirements, or skill files only when the user
  or automation asks for implementation work.
- Must not merge, push, publish, install large dependencies, download models,
  or use credentials without explicit human approval.

Data handling:
Do not add private NVIDIA data, secrets, PHI, or restricted datasets to public
SkillForge files or run logs. Healthcare source claims should be tied to public
source URLs or approved local evidence.

Writes vs read-only:
`improve-cycle --json` is read-only. `--write-log` writes a Markdown log.
`--claim-run` writes an advisory lock under `.skillforge/`, which is ignored by
Git.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Promptable feedback:

```text
SkillForge, send feedback on skillforge-strategic-improvement-loop that the recurring run logs are hard to review.
```

## Contributing

Use pull requests for changes:

```text
python -m skillforge contribute "improve strategic improvement-loop logging" --type feature --changed skills/skillforge-strategic-improvement-loop/SKILL.md --changed skillforge/improvement_loop.py --json
```

## Author

medatasci

## Citations

Not applicable for the improvement loop itself. Cite upstream repositories,
papers, model cards, dataset cards, licenses, and commits in each generated
skill artifact or run log.

## Related Skills

- `skillforge`
- `codebase-to-agentic-skills`
- `skill-discovery-evaluation`
- `nv-segment-ctmr`
- `nv-generate-ctmr`
