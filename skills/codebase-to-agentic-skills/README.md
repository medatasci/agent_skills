# Codebase To Agentic Skills

Skill ID: `codebase-to-agentic-skills`

Turn a repository, algorithm package, model repo, or local codebase into a
reviewable set of candidate SkillForge agentic skills. The skill helps humans
and agents move from source evidence to candidate skills, readiness cards,
adapter plans, smoke tests, and publication-ready SkillForge artifacts.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/codebase-to-agentic-skills

Parent package:
SkillForge Agent Skills Marketplace

Parent package repo URL:
https://github.com/medatasci/agent_skills

Distribution or marketplace:
SkillForge local catalog and Codex skill install workflow

Version or release channel:
Repository `main` branch when published

## Parent Collection

Parent collection:
SkillForge Agent Skills Marketplace

Collection URL:
https://github.com/medatasci/agent_skills

Categories:
Developer Tools, Agent Workflows, Skill Generation

Collection context:
This skill belongs in SkillForge's developer and skill-generation workflows. It
is the process skill for turning source repositories into one or more
discoverable, reviewable, and evidence-backed Codex skills.

## What This Skill Does

Codebase To Agentic Skills guides the repo-to-skills process. It helps Codex
inspect a repository, map source artifacts to their meaning, propose candidate
skills, decide whether one repo should become one skill or many skills, and
prepare the evidence needed before creating publishable SkillForge packages.

The skill is planning-first. It does not blindly wrap a repo. It requires a
source-context map, candidate skill table, readiness cards, LLM/Python
responsibility split, adapter plan, smoke-test plan, and publication evidence.

## Why You Would Call It

Call this skill when:

- You found a useful repo and want to know what agentic skills it could support.
- You want to convert a local codebase into one or more SkillForge skills.
- You need a repeatable process for extracting skills from NVIDIA-Medtech,
  MONAI, model, dataset, API, or tool repositories.

Use it to:

- Build a source-context map from README files, docs, scripts, configs, model
  cards, tests, licenses, and examples.
- Create a candidate skill table with sample prompts, CLI contracts, inputs,
  outputs, entrypoints, safety notes, and recommendations.
- Draft readiness cards and decide what is ready to package.

Do not use it when:

- You only want to use an existing domain skill.
- You want generic code review with no skill packaging goal.
- You want to publish unsupported capability, safety, license, or trust claims.

## Keywords

codebase-to-agentic-skills, repo to skills, repository analysis, agentic skill
generation, SkillForge, source-context map, candidate skill table, readiness
card, adapter planning, smoke test planning, skill publication, Codex skills,
MONAI skills, NVIDIA-Medtech skills.

## Search Terms

turn this repo into skills, convert a GitHub repository to agentic skills,
create SkillForge skills from a codebase, repo to skills workflow, source
context map, candidate agentic skills, readiness card for a repository, scan a
codebase for skill opportunities, package an algorithm as a Codex skill, make a
MONAI workflow into an agentic skill, make an NVIDIA-Medtech repo accessible to
agents.

## How It Works

The skill separates source-grounded reasoning from deterministic scanning:

1. The agent clarifies the user workflow goal, target users, expected inputs,
   expected outputs, and constraints.
2. The agent builds or refines a source-context map. This records what each
   source artifact contributes to skill design, adapter design, LLM prompting,
   safety, tests, and publication claims.
3. The agent creates a candidate skill table from the source-context map.
4. The agent creates readiness cards before generating skill files.
5. The agent decides whether the repo should become one algorithm skill,
   multiple functional-block skills, a workflow skill, or a mixed package.
6. The agent separates what the LLM may infer from what deterministic Python
   must verify.
7. The agent plans adapters, runtime/deployment, smoke tests, and publication
   evidence.
8. The agent generates SkillForge source files only after the user approves file
   creation.

The bundled Python helper can scan a local repo and draft the first-pass
source-context map, candidate skill table, and readiness-card Markdown files. It
does not run upstream code.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "repo to skills"
python -m skillforge info codebase-to-agentic-skills --json
python -m skillforge install codebase-to-agentic-skills --scope global
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --json
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
python -m skillforge evaluate codebase-to-agentic-skills --json
```

Skill-specific CLI:

```text
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py check --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py schema --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scan <repo-path> --workflow-goal "<goal>" --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
```

Options:

- `scan <repo-path>`: inspect a local repository or codebase path.
- `--workflow-goal`: record the user workflow goal that should guide candidate
  selection.
- `--output-dir`: write `scan.json`, `source-context-map.md`,
  `candidate-skill-table.md`, and `readiness-card-draft.md`.
- `--max-files-per-category`: cap the number of evidence artifacts reported per
  source area.
- `--max-total-files`: cap total files scanned.
- `--json`: emit machine-readable output.

Configuration:

- No credentials are required for local scanning.
- Network is not used by the helper.

## Inputs And Outputs

Inputs can include:

- Local repository path.
- GitHub or source repository URL.
- Workflow goal in user language.
- Target users.
- Example input files or dataset references.
- Expected output artifacts.
- Runtime constraints such as GPU, Docker, Conda, WSL2, macOS, Linux, Windows,
  offline use, or corporate workstation restrictions.
- Safety, privacy, license, and data-use constraints.

Outputs can include:

- Source-context map.
- Candidate skill table.
- Readiness-card draft.
- Scope recommendation.
- LLM versus deterministic responsibility split.
- Adapter plan.
- Smoke-test plan.
- Draft SkillForge package plan.
- Publication gaps and open questions.

Output locations:

- Optional scanner output directory supplied by `--output-dir`.
- Future generated skill folders under `skills/<skill-id>/` only after user
  approval.

## Limitations

- The scanner classifies likely evidence artifacts; it does not understand a
  repository by itself.
- The agent still needs to read important artifacts before making claims.
- The helper scans local paths only. URL fetching or cloning requires separate
  user approval and is not performed by default.
- The skill does not execute upstream code, install dependencies, download
  models, or validate scientific correctness.
- Publication readiness still requires `build-catalog`, `evaluate`, and human
  review.

Choose another skill when:

- You want to improve discoverability of an existing skill. Use
  `skill-discovery-evaluation`.
- You want to use an already-packaged domain skill such as
  `nv-segment-ctmr` or `huggingface-datasets`.

## Examples

Beginner example:

```text
SkillForge, help me turn this GitHub repo into a set of agentic skills.
Start with the source-context map and ask before cloning or writing files.
```

Task-specific example:

```text
Use codebase-to-agentic-skills on this local repo:
C:\path\to\repo

Workflow goal:
Make the repo accessible as reusable Codex skills for research workflows.

Create a source-context map, candidate skill table, and readiness-card drafts.
```

CLI example:

```text
python -m skillforge codebase-scan . --workflow-goal "Find candidate SkillForge skills in this repo" --output-dir test-output/codebase-to-agentic-skills/demo --json
```

Safety-aware example:

```text
Analyze this medical AI repo for possible agentic skills, but do not clone,
download model weights, run code, or write skill files until I approve the plan.
```

## Help And Getting Started

Start with a prompt like:

```text
Use codebase-to-agentic-skills to analyze this repository for candidate
SkillForge skills. First create the source-context map and candidate skill
table. Do not generate skill files until I review the candidates.
```

Provide:

- Repo URL or local path.
- Workflow goal.
- Target users.
- Constraints such as public-safe only, internal-only, GPU, Docker, Conda,
  offline, or privacy-sensitive data.

Ask for help when:

- You are not sure whether one repo should become one skill or many skills.
- Candidate skills sound plausible but lack source evidence.
- A runtime setup is unclear or risky.
- You need to decide whether to make an algorithm skill or a workflow skill.

## How To Call From An LLM

Direct prompt:

```text
Use codebase-to-agentic-skills to turn this repo into candidate agentic skills.
```

Task-based prompt:

```text
Analyze <repo-url-or-path> for SkillForge skill opportunities. Build the
source-context map, candidate skill table, readiness-card drafts, and recommend
what to package first.
```

Guardrail:

```text
Do not run upstream code, clone private repos, download assets, or generate
publishable skill files without explicit user approval.
```

## How To Call From The CLI

Run the helper from the SkillForge repository root:

```text
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py check --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py schema --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scan <repo-path> --workflow-goal "<goal>" --json
```

To write draft artifacts:

```text
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
```

## Trust And Safety

Risk level:
Low for local analysis and draft artifacts. Risk increases if the user asks to
clone repos, fetch external docs, run upstream code, download models/data, use
credentials, process sensitive data, or generate publishable skill files.

Permissions:

- Reads local source files during scanning.
- Writes Markdown and JSON only when `--output-dir` is provided.
- Does not use network by default.
- Does not execute upstream code by default.

Data handling:
Source code, configs, logs, issue text, dataset examples, and generated reports
can contain sensitive or proprietary material. Do not put private source
details, secrets, PHI, or NVIDIA-internal information into public SkillForge
artifacts.

Writes vs read-only:
`check`, `schema`, and `scan` without `--output-dir` are read-only. `scan` with
`--output-dir` writes draft Markdown and JSON artifacts.

External services:
No external services are used by the helper. Cloning or fetching remote repos is
a separate action that requires user approval.

Credential requirements:
None for local scanning. Do not request credentials in chat.

Approval gates:

- Before cloning or fetching a remote repo.
- Before running source code or installing dependencies.
- Before downloading model weights, datasets, or large assets.
- Before writing generated SkillForge skill files.
- Before including private or internal source details in public artifacts.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues/new/choose

Useful feedback:

- The scanner missed an important source artifact.
- The candidate table omitted a useful functional block.
- The workflow allowed a claim without enough source evidence.
- The generated readiness card was too thin.
- A repo-derived skill needs a stronger runtime/deployment gate.

CLI feedback draft:

```text
python -m skillforge feedback "codebase-to-agentic-skills" --trying "scan a repo for candidate skills" --happened "describe what worked, failed, or was confusing"
```

## Contributing

Contributions are welcome through GitHub pull requests.

Useful improvements:

- Add repo-derived publication gates to `evaluate`.
- Improve source-context classification.
- Add HTML report output for candidate skill inventories.
- Backfill source-context maps for existing exemplars.

Contribution prompt:

```text
SkillForge, help me prepare a pull request that improves codebase-to-agentic-skills.
```

## Author

Maintainer:
medatasci

Maintainer status:
Draft SkillForge skill package for review and iteration.

## Citations

This skill is a SkillForge workflow skill. It should cite source repositories,
model cards, dataset cards, papers, licenses, and standards in each generated
readiness card or repo-derived skill package. Core SkillForge sources:

- SkillForge requirements:
  https://github.com/medatasci/agent_skills/blob/main/requirements.md
- Codebase-To-Agentic-Skills design:
  https://github.com/medatasci/agent_skills/blob/main/docs/codebase-to-agentic-skills.md
- Readiness card template:
  https://github.com/medatasci/agent_skills/blob/main/docs/templates/codebase-readiness-card.md

## Related Skills

- `skill-discovery-evaluation`: Use after a repo-derived skill exists to
  improve discoverability and publication readiness.
- `skillforge`: Use to find, inspect, install, share, update, and manage
  SkillForge skills.
- `project-retrospective`: Use to preserve what was tried, what worked, what
  failed, and what should happen next.
- `nv-segment-ctmr`: Example algorithm skill created from a medical AI repo.
- `radiological-report-to-roi`: Example workflow skill that composes reports,
  images, segmentations, and deterministic ROI extraction.
