# Codebase To Agentic Skills

Skill ID: `codebase-to-agentic-skills`

Turn a repository, algorithm package, model repo, or local codebase into a
reviewable set of candidate SkillForge agentic skills. The skill helps humans
and agents move from source evidence to candidate skills, skill design cards,
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
source-context map, candidate skill table, skill design cards, LLM/Python
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
- Draft skill design cards and decide what is ready to package.

Do not use it when:

- You only want to use an existing domain skill.
- You want generic code review with no skill packaging goal.
- You want to publish unsupported capability, safety, license, or trust claims.

## Keywords

codebase-to-agentic-skills, repo to skills, repository analysis, agentic skill
generation, SkillForge, source-context map, candidate skill table, skill design
card, readiness card, adapter planning, smoke test planning, skill publication,
Codex skills, MONAI skills, NVIDIA-Medtech skills.

## Search Terms

turn this repo into skills, convert a GitHub repository to agentic skills,
create SkillForge skills from a codebase, repo to skills workflow, source
context map, candidate agentic skills, skill design card for a repository,
readiness card for a repository, scan a codebase for skill opportunities,
package an algorithm as a Codex skill, make a MONAI workflow into an agentic
skill, make an NVIDIA-Medtech repo accessible to agents.

## How It Works

The skill separates source-grounded reasoning from deterministic scanning:

1. The agent clarifies the user workflow goal, target users, expected inputs,
   expected outputs, and constraints.
2. The agent builds or refines a source-context map. This records what each
   source artifact contributes to skill design, adapter design, LLM prompting,
   safety, tests, and publication claims.
3. The agent creates a candidate skill table from the source-context map, with
   compact candidate review summaries followed by a detailed evidence table.
4. The agent creates skill design cards before generating skill files.
5. The agent decides whether the repo should become one algorithm skill,
   multiple functional-block skills, a workflow skill, or a mixed package.
6. The agent separates what the LLM may infer from what deterministic Python
   must verify.
7. The agent plans adapters, runtime/deployment, smoke tests, and publication
   evidence.
8. The agent generates SkillForge source files only after the user approves file
   creation.

The bundled Python helper can scan a local repo and draft the first-pass
source-context map, candidate skill table, and skill design card Markdown files.
For healthcare and medical-imaging repos, it also extracts deterministic
evidence candidates such as NIfTI/DICOM terms, MONAI or bundle clues, GPU/CUDA
runtime clues, model or dataset card clues, task/output terms, and medical-use
safety language. The helper groups these clues into `healthcare_signal_summary`
so reviewers can quickly see which kinds of medical evidence were found and
which files should be read before making claims. A single source file can
contribute multiple task/output terms, so a README that mentions both
segmentation and generation can seed both kinds of candidate hypotheses. It also creates
`healthcare_reading_plan`, a prioritized checklist of review areas, questions,
source files, bounded evidence hints, related source-context artifacts, and
claim boundaries for medical AI repos. Current helper output still uses the filename
`readiness-card-draft.md`. It also extracts source-grounded command evidence
from documented quick starts, notebook code cells, and common Python CLI
patterns so reviewers can see candidate adapter commands with file, line or
notebook cell, source-heading, platform, and side-effect context.
Command evidence includes both per-command side-effect categories and a summary
that groups likely installs, downloads, network access, file writes, GPU/model
execution, environment changes, container use, and read-only inspection. It
also assigns conservative execution gates such as `safe-to-inspect`,
`needs-user-approval`, `needs-runtime-plan`, `needs-data-safety-review`, and
`do-not-run-from-scanner`.
It then maps those gates to adapter-policy suggestions such as
`read-only-check`, `setup-plan`, `runtime-plan`, `guarded-run`, and
`no-adapter-until-review` so reviewers can decide what kind of wrapper is safe
to design next.
The helper keeps the conservative highest adapter policy across all detected
commands separate from the candidate-level recommended adapter policy. That
matters when a repo contains maintenance-only command clues, such as
pre-commit, lint, or formatting configuration. Those clues are still recorded
for review, but workflow-specific command evidence should drive the recommended
candidate adapter path when it exists.
When a repo produces several candidate skills, each candidate gets its own
provisional CLI draft. The helper scores command evidence against candidate
task terms, the matched workflow goal, nearby Markdown headings, and the most
recent notebook markdown heading before a code cell. That means a generic run
command under a "Synthetic Image Generation" heading in a README or tutorial
notebook can be ranked for the generation candidate even when the command text
itself is terse.
This lets a synthetic image generation candidate show generation commands
before segmentation commands, while a segmentation candidate can do the reverse.
It does not run upstream code.
When task/output signals are present, the helper can also seed
`candidate_skill_hypotheses` in `scan.json` and `candidate-skill-table.md`.
Those hypotheses are provisional prompts for review, not recommendations to
publish a skill. Each hypothesis includes source coverage so reviewers can see
which artifact types were detected before investing in a candidate. Each
hypothesis can also include a provisional CLI draft derived from detected
entrypoints, configs, runtime files, command evidence, and adapter-policy
suggestions. The draft can include adapter-plan stubs for read-only checks,
setup plans, runtime plans, guarded runs, or blocked source-review paths. Those
draft commands and stubs are review aids, not validated commands to run.
Suggested commands in the draft prioritize workflow-scoped evidence before
repo-maintenance evidence so humans and agents see the likely task path first.
When several task hypotheses are possible, the helper uses the user-supplied
workflow goal to order the provisional candidates. This keeps a repo that
mentions segmentation masks and synthetic image generation from putting the
wrong task first when the user asked for generation.
For local Git repositories, the helper also records source-version provenance
when available, including commit, branch, origin remote URL, dirty-worktree
status, lookup status, and whether a safe-directory override was used. If Git
blocks read-only provenance lookup because of ownership or safe-directory
checks, the helper retries with a per-command `safe.directory` override and
records that fact in `source_version` without changing global Git
configuration. The generated source-context map, candidate skill table,
readiness card, scan JSON, and scan-backed adapter scaffold metadata preserve
that provenance so reviewers can trace a candidate back to the source state
that produced it.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "repo to skills"
python -m skillforge info codebase-to-agentic-skills --json
python -m skillforge install codebase-to-agentic-skills --scope global
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --json
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
python -m skillforge codebase-scaffold-adapter setup-plan --adapter-name <adapter-name> --output-dir skills/<skill-id> --json
python -m skillforge codebase-scaffold-adapter --from-scan-json docs/reports/<repo>-repo-to-skills/scan.json --candidate-id <candidate-id> --stub-type guarded-run --output-dir skills/<skill-id> --json
python -m skillforge evaluate codebase-to-agentic-skills --json
```

Skill-specific CLI:

```text
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py check --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py schema --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scan <repo-path> --workflow-goal "<goal>" --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scaffold-adapter setup-plan --adapter-name <adapter-name> --output-dir skills/<skill-id> --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scaffold-adapter --from-scan-json docs/reports/<repo>-repo-to-skills/scan.json --candidate-id <candidate-id> --stub-type guarded-run --output-dir skills/<skill-id> --json
```

Options:

- `scan <repo-path>`: inspect a local repository or codebase path.
- `--workflow-goal`: record the user workflow goal that should guide candidate
  selection.
- `--output-dir`: write `scan.json`, `source-context-map.md`,
  `candidate-skill-table.md`, and `readiness-card-draft.md` skill design draft.
- `--max-files-per-category`: cap the number of evidence artifacts reported per
  source area.
- `--max-total-files`: cap total files scanned.
- `scaffold-adapter <adapter-type>`: write a review-only Python adapter
  skeleton for `read-only-check`, `setup-plan`, `runtime-plan`, `guarded-run`,
  or `no-adapter-until-review`.
- `--from-scan-json`: read scanner output and seed the scaffold from one
  candidate's source-grounded adapter-plan stub.
- `--candidate-id` / `--candidate-index`: choose which candidate hypothesis in
  `scan.json` should drive the scaffold.
- `--stub-type` / `--stub-index`: choose which adapter-plan stub should drive
  the scaffold.
- `--adapter-name`: set the generated adapter script name. If omitted with
  `--from-scan-json`, the helper derives a script name from the selected
  candidate and stub type.
- `--force`: overwrite an existing generated adapter scaffold after review.
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
- Healthcare and medical-imaging signal summary and detailed signal list when
  detected.
- Healthcare reading plan with review questions, healthcare signal files,
  bounded evidence hints, related source-context artifacts, and claim boundaries
  when healthcare signals are detected.
- Source-grounded command evidence from README/docs snippets, notebook code
  cells, and Python CLI framework clues, including source path, line or
  notebook cell, source heading, snippet, platform assumption, side-effect risk,
  side-effect categories, execution gate, and a grouped risk summary.
- Adapter-policy suggestions that map command gates to wrapper design paths:
  read-only checks, setup plans, runtime plans, guarded run adapters, or no
  adapter until source review.
- Provisional candidate skill hypotheses when task/output signals are detected.
- Source coverage for each provisional hypothesis, covering README/docs,
  executable entrypoints, configs, examples, runtime, model/data, and
  license/safety evidence.
- Provisional CLI drafts for each hypothesis when entrypoints are detected,
  including source paths, runtime/config references, and review-only command
  hints.
- Adapter-plan stubs for each relevant adapter policy, including suggested
  adapter commands, required inputs, expected outputs, guardrails, required
  reviews, confirmation requirements, source references, and smoke-test ideas.
- Review-only adapter skeletons that implement `schema`, `check`, and
  `setup-plan` when `scaffold-adapter` is explicitly requested. These can be
  generated from a specific `scan.json` candidate while preserving the selected
  stub's source refs, guardrails, required reviews, and planned commands.
- Candidate skill table.
- Skill Design Card draft.
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
- Healthcare signal extraction finds deterministic clues for an agent to read;
  it does not prove modality support, clinical safety, license status, or model
  validity.
- The healthcare reading plan is a review checklist; it does not replace reading
  authoritative source files, model cards, dataset cards, licenses, or papers.
- Evidence hints are short navigation aids with line numbers when available;
  they are not sufficient evidence by themselves.
- Related source-context artifacts are included to keep the reading plan tied to
  README, docs, configs, runtime, model/data, and license evidence rather than
  isolated keyword hits.
- Candidate skill hypotheses are scanner-generated review prompts. They must be
  confirmed against source evidence before becoming candidate table rows or skill
  files.
- Source coverage only reports whether artifact types were detected; it does
  not mean a source claim, runtime path, or safety boundary has been validated.
- Command evidence extraction is heuristic. It highlights commands worth
  reviewing and groups likely side effects, but does not prove they are
  complete, current, safe, or portable.
- Execution gates are conservative scanner recommendations. They tell an agent
  what kind of review is needed; they are not permission to execute a command.
- Adapter policies are conservative wrapper-design suggestions. They help
  decide whether a generated skill should expose only read-only checks, a setup
  plan, a runtime plan, a guarded run command, or no runnable adapter until
  review is complete.
- Adapter-plan stubs are scaffolds, not implemented adapters. They are useful
  for planning `check`, `setup-plan`, `runtime-plan`, `plan`, `run`, and
  `verify-output` commands, but each command still needs source review,
  implementation, tests, and explicit approval for side effects.
- Generated adapter skeletons are intentionally limited to review-only
  `schema`, `check`, and `setup-plan`. They do not implement source execution,
  installs, downloads, network access, GPU work, model inference, or output
  generation.
- Provisional CLI drafts are adapter-design prompts. They must not be treated
  as safe or correct until source docs, runtime requirements, side effects, and
  smoke tests are reviewed.
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

Create a source-context map, candidate skill table, and skill design card
drafts.
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
source-context map, candidate skill table, skill design card drafts, and recommend
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
- The generated Skill Design Card was too thin.
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
Skill Design Card or repo-derived skill package. Core SkillForge sources:

- SkillForge requirements:
  https://github.com/medatasci/agent_skills/blob/main/requirements.md
- Codebase-To-Agentic-Skills design:
  https://github.com/medatasci/agent_skills/blob/main/docs/codebase-to-agentic-skills.md
- Skill Design Card template:
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

## Additional Information

You do not need to understand every generated document to use this skill. Start
with the artifact that matches the question you are trying to answer.

### If You Want To Decide What To Build

Read the **Skill Design Card** first. It is the human review page for a
candidate skill or skill family. It explains the source evidence, user value,
scope, safety gates, adapter plan, smoke tests, recommendation, and remaining
gaps.

Examples:

- [NV-Generate-CTMR Skill Design Card](../../docs/readiness-cards/nv-generate-ctmr.md)
- [NV-Segment-CTMR Skill Design Card](../../docs/readiness-cards/nv-segment-ctmr.md)
- [Radiological Report to ROI Skill Design Card](../../docs/readiness-cards/radiological-report-to-roi.md)

Existing file paths still use `docs/readiness-cards/` for compatibility, but
the human-facing concept is a **Skill Design Card**.

### If You Want To Compare Possible Skills

Look for the **candidate skill table**. It compares possible skills in the same
family and shows what each would do, why it matters, likely entrypoints, sample
prompt calls, proposed CLI calls, inputs, outputs, safety notes, and
recommendation.

Prompt:

```text
SkillForge, analyze this repo and show me the candidate skill table before creating files.
```

### If You Want To Check The Evidence

Read the **source-context map** or source reference docs. These explain what the
README, scripts, configs, papers, model cards, licenses, examples, and tests
contribute to the proposed skill.

Useful references:

- [Codebase-To-Agentic-Skills Design](../../docs/codebase-to-agentic-skills.md)
- [Skill Design Card Template](../../docs/templates/codebase-readiness-card.md)
- [Source Context Map Reference](references/source-context-map.md)
- [NV-Generate-CTMR Source Context](../nv-generate-ctmr/references/source-context-and-prompting.md)

### If You Want To Use A Finished Skill

Read the skill's `README.md`. It is the human-facing home page with purpose,
examples, CLI commands, trust and safety, feedback, related skills, and
citations. `SKILL.md` is mainly for Codex and other agents.

Examples:

- [NV-Generate-CTMR README](../nv-generate-ctmr/README.md)
- [NV-Segment-CTMR README](../nv-segment-ctmr/README.md)
- [Radiological Report to ROI README](../radiological-report-to-roi/README.md)

### If You Want To Know What Comes Next

Read the **Skill Family Roadmap** when a repo may eventually become multiple
skills. The roadmap explains future child skills and what evidence or tests
would justify splitting them out.

Example:

- [NV-Generate-CTMR Skill Family Roadmap](../../docs/backlog/nv-generate-ctmr-split-roadmap.md)

### Quick Prompts

```text
SkillForge, analyze this repo and tell me what agentic skills it could support.
```

```text
SkillForge, create a Skill Design Card for the best candidate skill before writing any skill files.
```

```text
SkillForge, show me the source evidence behind this skill's claims.
```
