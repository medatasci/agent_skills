---
name: codebase-to-agentic-skills
owner: medatasci
description: Use this skill when a user wants to turn a GitHub repository, local codebase, algorithm package, model repo, MONAI workflow, or other source project into one or more reviewable SkillForge agentic skills. Use for source-context mapping, candidate skill discovery, repo-to-skills planning, Skill Design Cards, LLM versus deterministic responsibility splits, adapter planning, smoke-test planning, and publication evidence. Do not use to blindly wrap code without source evidence, license review, safety boundaries, or user approval for writes/network/runtime work.
---

# Codebase To Agentic Skills

## What This Skill Does

Use this skill when a user asks to convert a repository, local codebase,
algorithm, model package, or workflow into a set of candidate agentic skills.

This skill guides Codex through an evidence-driven repo-to-skills process:
source-context map, candidate skill table, Skill Design Cards, scope decisions,
adapter plans, smoke-test plans, and publication checks. It is designed for one
repo becoming one skill, several functional-block skills, one workflow skill, or
a mixed package.

## Safe Default Behavior

Default to read-only analysis and draft artifacts.

Do not clone repositories, call networks, install dependencies, run upstream
code, download model/data assets, write generated skill files, or publish
catalog changes unless the user explicitly approves that side effect.

Do not invent capabilities, safety claims, licenses, owners, citations,
runtime support, or trust status. Every candidate skill claim should trace back
to source context, user-provided workflow requirements, or implemented adapter
behavior.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| "Turn this repo into skills" | Build a source-context map, candidate table, and Skill Design Cards before generating skill files. |
| "What skills could this repo support?" | Create a candidate skill table with source evidence and recommendations. |
| "Package this repo as a skill" | Check readiness first, then create `SKILL.md`, README, references, adapter plan, and tests only for source-supported behavior. |
| "Scan this local repo" | Use `python -m skillforge codebase-scan <path> --json` for deterministic evidence collection. |

## SkillForge Discovery Metadata

This section is written as Markdown so people can read it, while SkillForge can
still extract the same discovery fields for catalogs, search, and generated
pages.

### Title

Codebase To Agentic Skills

### Short Description

Turn a source repository or local codebase into a reviewable set of candidate
SkillForge agentic skills using source-context maps, candidate tables,
Skill Design Cards, adapter plans, and publication evidence.

### Expanded Description

Use this skill to make repo-to-skills work repeatable and source-grounded. It
helps an agent inspect a repository, explain what each important source artifact
contributes, propose candidate skills, decide one-skill versus many-skill scope,
split LLM responsibilities from deterministic Python responsibilities, draft
Skill Design Cards, plan adapters and smoke tests, and prepare source-supported
SkillForge skill packages. The bundled Python helper can scan a local repo and
draft source-context, candidate-table, and skill-design-card artifacts without
running upstream code.

### Aliases

- repo to skills
- repository to agentic skills
- codebase to skills
- codebase-to-agentic-skills
- source-context map
- candidate skill discovery
- skill generator

### Categories

- Developer Tools
- Agent Workflows
- Skill Generation

### Tags

- codebase
- repository-analysis
- agentic-skills
- skillforge
- source-context
- skill-design-card
- readiness-card
- adapter-planning

### Tasks

- turn a repository into candidate agentic skills
- build a source-context map
- create a candidate skill table
- draft Skill Design Cards
- split LLM and deterministic Python responsibilities
- plan adapter commands and smoke tests
- prepare repo-derived SkillForge skills for publication

### Use When

- The user asks what agentic skills could be created from a repo or local codebase.
- The user wants a repeatable process for converting an algorithm repository into SkillForge skills.
- The user needs source-supported candidate skills, Skill Design Cards, adapter plans, or publication evidence.
- The user wants to analyze NVIDIA-Medtech, MONAI, or similar algorithm repos for agentic skill opportunities.

### Do Not Use When

- The user wants to use an already-created domain skill directly.
- The user wants generic code review with no skill packaging or agentic workflow goal.
- The user wants to publish unsupported claims, skip license review, or wrap code without source evidence.
- The request requires running untrusted code, downloading models/data, or using credentials without explicit approval.

### Inputs

- GitHub repository URL or local codebase path
- workflow goal in user language
- target users or audience
- optional example inputs, expected outputs, and constraints
- optional safety, privacy, license, runtime, or platform constraints

### Outputs

- source-context map
- candidate skill table
- Skill Design Card
- scope recommendation
- LLM versus deterministic responsibility split
- adapter and smoke-test plan
- draft SkillForge skill package plan
- optional generated Markdown and JSON scan artifacts

### Examples

- SkillForge, turn this GitHub repo into a set of candidate agentic skills.
- Use codebase-to-agentic-skills to scan this local repo and draft a source-context map.
- Analyze this MONAI workflow and tell me which functional blocks should become SkillForge skills.
- Create Skill Design Cards for the best candidate skills in this repository before generating files.

### Related Skills

- skill-discovery-evaluation
- skillforge
- project-retrospective
- nv-segment-ctmr
- radiological-report-to-roi

### Authoritative Sources

- SkillForge requirements: https://github.com/medatasci/agent_skills/blob/main/requirements.md
- Codebase-To-Agentic-Skills design: https://github.com/medatasci/agent_skills/blob/main/docs/codebase-to-agentic-skills.md
- Skill Design Card template: https://github.com/medatasci/agent_skills/blob/main/docs/templates/codebase-readiness-card.md

### Citations

- Not applicable. This is a SkillForge workflow skill. Cite upstream source repositories, model cards, papers, licenses, and dataset cards in each generated Skill Design Card or skill package.

### Risk Level

low

### Permissions

- read local repository files
- optionally write Markdown and JSON draft artifacts when the user supplies an output directory
- no network access unless the user approves cloning or fetching source material
- no upstream code execution, dependency installation, model download, or credential use by default

### Page Title

Codebase To Agentic Skills - Convert Repositories Into SkillForge Agentic Skills

### Meta Description

Use Codebase To Agentic Skills to convert source repositories into candidate
SkillForge skills with source-context maps, Skill Design Cards, adapter plans,
smoke tests, and publication evidence.

## Workflow

1. Clarify the user's workflow goal, target users, expected inputs, expected
   outputs, and constraints.
2. If the source is a URL, ask before cloning or fetching. If the source is a
   local path, confirm read-only scanning is acceptable.
3. Use the deterministic scanner when useful:

```text
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
python -m skillforge codebase-scaffold-adapter setup-plan --adapter-name <adapter-name> --output-dir skills/<skill-id> --json
python -m skillforge codebase-scaffold-adapter --from-scan-json docs/reports/<repo>-repo-to-skills/scan.json --candidate-id <candidate-id> --stub-type guarded-run --output-dir skills/<skill-id> --json
```

Or call the skill-specific helper directly:

```text
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scaffold-adapter setup-plan --adapter-name <adapter-name> --output-dir skills/<skill-id> --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scaffold-adapter --from-scan-json docs/reports/<repo>-repo-to-skills/scan.json --candidate-id <candidate-id> --stub-type guarded-run --output-dir skills/<skill-id> --json
```

4. Build or refine the source-context map. Read important artifacts before
   making claims.
5. Review `command_evidence` for documented quick-start commands and Python
   CLI framework clues. Read the cited source path, line or notebook cell,
   snippet, and `source_heading` when present; the nearest Markdown section
   heading or preceding notebook markdown heading is often the best clue for
   generic commands such as `python tool.py run --config ...`.
   Use `command_evidence_summary` to spot likely installs, downloads, network
   access, file writes, GPU/model execution, containers, and read-only
   inspection. Use `execution_gate` to decide whether a command is safe to
   inspect, needs user approval, needs a runtime plan, needs a data safety
   review, or should not be run from scanner output. Treat these fields as
   evidence to read, not approval to execute. Use `adapter_policy` to decide
   whether the next wrapper should be read-only, a setup plan, a runtime plan, a
   guarded run adapter, or no adapter until source review. Use
   `adapter_plan_stubs` as scaffolds for the next implementation plan, not as
   completed adapters. Keep the conservative highest adapter policy across all
   commands separate from the candidate-level recommended adapter policy. If
   repo-maintenance-only commands such as pre-commit, lint, or formatting
   configuration are detected, preserve them as evidence but do not let them
   dominate the candidate recommendation when workflow-specific command evidence
   exists.
6. Create a candidate skill table informed by source context, source coverage,
   and any provisional CLI draft details from detected entrypoints, configs,
   runtime files, and command evidence. Include compact candidate review
   summaries before the detailed evidence table so humans can triage candidates
   quickly while agents still have structured comparison fields. When multiple
   hypotheses exist, expect each candidate to have its own provisional CLI draft
   ordered by candidate task terms, matched workflow-goal terms, and source
   section context such as Markdown headings or notebook markdown headings, not
   one shared command ordering for the whole repo.
7. Create Skill Design Cards for candidates before generating skill files.
8. Decide one skill, many skills, workflow skill, or mixed package.
9. Separate LLM decisions from deterministic Python checks.
10. Plan adapters, runtime/deployment, smoke tests, and publication evidence.
11. Generate `SKILL.md`, README, references, and scripts only after the user
    approves file creation.
12. Run `python -m skillforge build-catalog --json`.
13. Run `python -m skillforge evaluate <skill-id> --json`.
14. Report supported claims, open questions, generated files, and next actions.

## References

Read these only when needed:

- `references/repo-to-skills-workflow.md`: ordered workflow and evidence rule.
- `references/source-context-map.md`: what each source artifact contributes.
- `references/candidate-skill-table.md`: required candidate table columns and promotion rules.

When scanner output includes `command_evidence`, read the cited source path,
line or notebook cell, nearest `source_heading` when present, snippet,
side-effect categories, and risk summary before using the command in a design
card or adapter plan. `execution_gate` is a conservative triage recommendation,
not permission to execute.
When scanner output includes `provisional_cli_draft`, treat it as an adapter
design prompt. It can point at likely entrypoints, source-grounded command
snippets, and review commands, but it does not prove the command is safe,
supported, cross-platform, or ready to run. For multi-candidate scans, compare
the draft's `candidate_relevance`, `candidate_terms`, and any source-section
heading context before assuming a command belongs to a candidate workflow.
When scanner output includes multiple `candidate_skill_hypotheses`, inspect
`workflow_goal_match_score` and `workflow_goal_match_terms` before choosing a
candidate. The first candidate should reflect the user's stated workflow goal
when a task term match exists, but every candidate remains provisional until
source review.
Use `candidate_skill` as the source-scoped name and `generic_candidate_skill`
as the underlying task template when both are present.
When scanner output includes `source_version`, report the commit, branch,
origin remote URL, dirty-worktree status, lookup status, and whether a
safe-directory override was used. `ok-safe-directory-override` means Git
provenance was read with a per-command safe-directory override because the
checkout owner differed from the current process user; it is provenance, not an
approval to execute source code.
When reading generated artifacts, expect the source-context map, candidate
skill table, readiness card, scan JSON, and scan-backed adapter scaffold
metadata to carry the same source provenance summary.
When scanner output includes `adapter_policy` or `adapter_policy_summary`, use
it as wrapper-design guidance only. A `guarded-run` policy still requires
runtime planning, source review, data-safety review when applicable, explicit
user approval, and smoke-test evidence before execution.
Read both the conservative `highest_policy` and the candidate-level
`recommended_policy` when present. If the summary says some commands were
ignored for the recommendation, mention that they were repo-maintenance evidence
and inspect them only as review context.
When scanner output includes `adapter_plan_stubs`, use them to draft the
adapter implementation plan and smoke tests. Do not claim any stubbed command
exists until it has been implemented and tested in the skill package.
When using `scaffold-adapter`, tell the user it writes a review-only Python
adapter skeleton with `schema`, `check`, and `setup-plan`. It does not create
or approve a runnable `run` command.
Prefer `--from-scan-json` when a scanner output already exists. That keeps the
generated skeleton tied to the selected candidate hypothesis and preserves the
source refs, guardrails, required reviews, and planned commands from the
selected adapter-plan stub.

## Agent CLI

The top-level SkillForge CLI exposes the common scan workflow:

```text
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --json
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
python -m skillforge codebase-scaffold-adapter setup-plan --adapter-name <adapter-name> --output-dir skills/<skill-id> --json
python -m skillforge codebase-scaffold-adapter --from-scan-json docs/reports/<repo>-repo-to-skills/scan.json --candidate-id <candidate-id> --stub-type guarded-run --output-dir skills/<skill-id> --json
```

The bundled helper is also deterministic and local-first:

```text
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py check --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py schema --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scan <repo-path> --workflow-goal "<goal>" --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scaffold-adapter setup-plan --adapter-name <adapter-name> --output-dir skills/<skill-id> --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scaffold-adapter --from-scan-json docs/reports/<repo>-repo-to-skills/scan.json --candidate-id <candidate-id> --stub-type guarded-run --output-dir skills/<skill-id> --json
```

The scanner does not run upstream code. It classifies evidence candidates and
can write:

- `scan.json`
- `source-context-map.md`
- `candidate-skill-table.md`
- `readiness-card-draft.md` skill design draft

## Inputs

- Repository URL or local codebase path.
- Workflow goal in user language.
- Target users.
- Constraints such as GPU, Docker, Conda, network, privacy, license, or
  platform requirements.
- Optional example inputs and expected outputs.

## Outputs

- Source-context map.
- Healthcare and medical-imaging signal summary and detailed signal list when
  detected.
- Healthcare reading plan with healthcare signal files, bounded evidence hints,
  related source-context artifacts, review questions, and claim boundaries when
  healthcare signals are detected.
- Provisional candidate skill hypotheses when task/output signals are detected.
- Source coverage for each provisional hypothesis.
- Candidate skill table.
- Skill Design Card draft.
- Scope recommendation.
- Adapter plan.
- Smoke-test plan.
- Publication evidence and open questions.

## Boundaries

- Do not create a publishable skill without source evidence.
- Do not run upstream code during source-context scanning.
- Do not assume a README quick start is safe or complete; verify runtime,
  license, and side effects.
- Do not put private source code, logs, secrets, PHI, or NVIDIA-internal data in
  public SkillForge artifacts.
- For medical, scientific, security, legal, financial, or regulated domains,
  use authoritative source links and conservative claims.

## Runtime And Deployment Notes

This skill is planning-first. The bundled scanner uses only the Python standard
library and local filesystem reads. It writes files only when `--output-dir` is
provided. When scanning healthcare or medical-imaging repos, the scanner returns
`healthcare_signal_summary` and `healthcare_signals` for deterministic evidence
candidates such as NIfTI/DICOM terms, MONAI bundles, GPU/CUDA runtime terms,
model or dataset card clues, task/output terms, and medical-use safety language.
One source file may contribute multiple task or output terms when it supports
more than one candidate workflow; do not collapse a README that mentions both
segmentation and generation into a single candidate signal.
It also returns `healthcare_reading_plan`, a prioritized checklist for reviewing
healthcare signal files, bounded evidence hints, and related source-context
artifacts before proposing medical AI skills. Treat these as files to read, not
proof of supported capabilities or safety. If task/output signals are detected,
the scanner can also return `candidate_skill_hypotheses`; treat those as
provisional review prompts, not recommendations to publish. Hypotheses include
source coverage, which means relevant artifact types were detected, not that the
source has been validated.

Future generated skills may need their own runtime/deployment plans. If a
generated skill runs code, downloads assets, uses credentials, processes
sensitive data, or writes outputs, document install location, OS/runtime target,
dependency setup, model/data download policy, license review, environment
checks, smoke-test data, and cleanup/rollback notes.

## Examples

```text
SkillForge, turn https://github.com/NVIDIA-Medtech/NV-Segment-CTMR into a set of candidate agentic skills. Start with a source-context map and candidate table. Ask before cloning or writing files.
```

```text
Use codebase-to-agentic-skills on this local MONAI workflow repo. Create the source-context map, candidate skill table, Skill Design Card drafts, and tell me which skills are ready to package.
```
