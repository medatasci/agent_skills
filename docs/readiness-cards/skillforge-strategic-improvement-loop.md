# Skill Design Card: SkillForge Strategic Improvement Loop

## Summary

This card records the design evidence for
`skillforge-strategic-improvement-loop`, a recurring Codex automation skill for
improving SkillForge itself, especially healthcare-domain
`codebase-to-agentic-skills` work.

## Source Version Status

Source version status: the SkillForge implementation is local to this
repository and changes by branch. The current base commit at design time was
commit: f1d8c4ce1415. Healthcare reference repositories are intentionally listed
as source priorities for future runs and must be pinned in the specific run log
or generated Skill Design Card that uses them.

## Source Context Map

| Source | What it contributes | How it affects skill design |
| --- | --- | --- |
| `requirements.md` | Product requirements for SkillForge, codebase-to-agentic-skills, user affordances, update behavior, and medical AI skill safety. | Defines the loop as reviewable, source-grounded, non-auto-merge work with explicit logging. |
| `docs/codebase-to-agentic-skills.md` | Canonical repo-to-skills workflow and healthcare source-context expectations. | Makes `skills/codebase-to-agentic-skills` the main improvement target and requires source evidence before new healthcare skills. |
| `skills/codebase-to-agentic-skills/` | Agent-facing generator workflow, deterministic scanner, and reference docs. | Provides the workflow that recurring healthcare runs should improve, test, or apply. |
| `skillforge/improvement_loop.py` | Deterministic CLI planner, run-log writer, healthcare source list, Git snapshot, and advisory lock behavior. | Provides the agent-callable API used by scheduled Codex runs. |
| `docs/improvement-loop/` | Persistent run logs, backlog, active state, and initiative notes. | Gives concurrent jobs durable, reviewable coordination surfaces. |
| https://github.com/NVIDIA-Medtech | Healthcare AI repositories that may become agentic skills. | Default research source for candidate skills and source-context maps. |
| https://github.com/project-monai/monai | Healthcare imaging framework, examples, bundles, and reusable inference patterns. | Default research source for future MONAI-oriented skills and repo-to-skills hardening. |

## Candidate Skill Table

| Candidate Skill | What It Does | Recommendation |
| --- | --- | --- |
| `skillforge-strategic-improvement-loop` | Runs recurring, reviewable improvement cycles for SkillForge and healthcare repo-to-skills work. | make-skill-now |
| `codebase-to-agentic-skills` | Converts repositories and algorithms into source-grounded candidate SkillForge skills. | continue-hardening |
| Future healthcare repo-derived skills | Wrap specific NVIDIA-Medtech or MONAI capabilities as source-backed agentic skills. | needs-source-context-map-first |

## Execution Surface

Primary command:

```text
python -m skillforge improve-cycle --write-log --claim-run --json
```

Related commands:

```text
python -m skillforge improve-cycle --json
python -m skillforge improve-cycle --lane researcher --write-log --claim-run --json
python -m skillforge improve-cycle --release-run <run-id> --json
python -m skillforge help improvement-loop
```

The command is implemented in `skillforge/improvement_loop.py` and wired
through `skillforge/cli.py`.

## Dependencies

- Python 3.11 compatible standard library.
- Git on PATH for repository snapshot fields; the command still returns a JSON
  payload if Git is unavailable.
- Writable repository directory for run logs.
- Writable `.skillforge/` ignored directory for advisory locks.
- Codex automation for recurrence. The skill itself does not self-schedule.

## Smoke Test Plan

Expected command:

```text
python -m skillforge improve-cycle --write-log --claim-run --json
python -m skillforge improve-cycle --release-run <run-id> --json
```

Expected result:

- JSON includes `run_id`, `selected_lane`, `focus`, `healthcare_sources`,
  `repo_snapshot`, `concurrency`, and `log_path`.
- A Markdown run log is written under `docs/improvement-loop/runs/` when
  `--write-log` is supplied.
- An advisory active-run lock is written under `.skillforge/improvement-loop/`
  when `--claim-run` is supplied.
- A second `--claim-run` reports the active run instead of silently replacing
  it.
- `--release-run <run-id>` removes the matching lock.

Skip condition:
If Python is unavailable on PATH, use the bundled workspace Python runtime or
the Python environment used for SkillForge development.

## Safety And Review

- The loop must not auto-merge, push, publish, install large dependencies,
  download model weights, use credentials, or run expensive jobs without human
  approval.
- Run logs must not include private NVIDIA data, PHI, secrets, or restricted
  datasets.
- The advisory lock is collision avoidance, not a trust or security model.
- Healthcare claims must be source-backed in the specific run log, Skill Design
  Card, or generated skill artifact.

## Open Gaps

- The recurring Codex automation needs real-world observation to see whether
  20-minute cadence creates useful momentum or too much noise.
- Future runs may need a richer state schema for multi-run initiatives.
- Future runs may need a generated dashboard summarizing open initiatives and
  completed improvements.
