# Codebase-To-Agentic-Skills

Status: project launch draft  
Date: 2026-05-03

## Purpose

Codebase-to-agentic-skills turns useful algorithm repositories into Codex
skills that humans and agents can discover, install, evaluate, and use.

The workflow should be automated where possible, but directed by the workflow
the user wants to support. The goal is not to wrap every repository blindly. The
goal is to identify where a codebase can become a reliable agentic capability:
an agent-readable skill with a deterministic execution path, clear data
contracts, source provenance, safety boundaries, and enough examples to be
useful.

## Decisions So Far

- Name the project and SkillForge skill `codebase-to-agentic-skills`.
- Use codebase-to-agentic-skills for both automated codebase inspection and user-directed
  workflow support.
- Start with one concrete exemplar before building generalized automation.
- Use Radiological Report to ROI as the first exemplar.
- Require a Skill Design Card before generating a skill package.
- Keep `SKILL.md` as the normal Codex agent-facing contract.
- Require an agent-callable Python CLI or adapter for stateful deterministic
  work whenever the skill reads data, writes outputs, runs a model, or validates
  artifacts.
- Put detailed source notes, labels, data contracts, and execution variants in
  `references/` so skills stay concise.
- Treat deterministic adapters and smoke tests as first-class outputs, not
  afterthoughts.

## First Exemplar

The first exemplar is Radiological Report to ROI:

```text
radiology report + matching MRI image volume
-> infer relevant anatomy or region of interest
-> choose the correct segmentation strategy
-> call NV-Segment-CTMR or use an existing NV-Segment-CTMR segmentation
-> map anatomy to segmentation labels
-> extract ROI outputs
-> summarize evidence, files, labels, commands, and limitations
```

This exemplar uses:

- MR-RATE image volumes and reports:
  https://huggingface.co/datasets/Forithmus/MR-RATE
- MR-RATE NV-Segment-CTMR derivative segmentations:
  https://huggingface.co/datasets/Forithmus/MR-RATE-nvseg-ctmr
- NV-Segment-CTMR:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR

See `docs/radiological-report-to-roi.md` for the concrete
workflow.

## Broader Source Targets

The project should learn from the exemplar, then apply the pattern to:

- NVIDIA-Medtech repositories:
  https://github.com/NVIDIA-Medtech
- MONAI repositories and MONAI Bundle-style workflows:
  https://github.com/project-monai/monai

NVIDIA-Medtech is a good source because its repositories expose model families
around medical-imaging perception, generation, reconstruction, reasoning, and
physical-AI workflows. MONAI is a good source because it already provides
healthcare-imaging primitives, transforms, inference patterns, metrics, and
bundle conventions.

## What Makes A Codebase Skill-Ready

A codebase is a good candidate when it has:

- A real workflow need, not only an interesting algorithm.
- Clear input and output artifacts.
- A reproducible quick start or inference path.
- A stable execution surface, such as a Python API, CLI, MONAI bundle, script,
  Docker command, or notebook that can be made deterministic.
- A reviewable path from detected entrypoints to an adapter CLI contract,
  including clear notes about side effects, platform assumptions, runtime
  requirements, and commands that still need source review.
- Source-grounded command evidence from quick-start snippets or Python CLI
  framework clues, with source path, line or notebook cell, nearby Markdown or
  notebook markdown heading, snippet, platform assumption, and side-effect
  risk.
- A side-effect summary that separates likely read-only inspection, installs,
  downloads, network access, file writes, GPU/model execution, container use,
  environment changes, shell scripts, and unknown commands needing review.
- Conservative execution gates that tell reviewers whether a command is safe to
  inspect, needs user approval, needs runtime planning, needs data-safety
  review, or should not be run from scanner output.
- A small test fixture or example input.
- License, model weight, dataset, and intended-use boundaries that can be
  stated clearly.
- Useful agent decisions around setup, input selection, parameter choice,
  result interpretation, or follow-up actions.

A codebase is a weak candidate when it cannot be run reproducibly, has unclear
license or data-use terms, requires undocumented credentials, has no meaningful
input/output contract, or needs unsupported clinical claims to be useful.

## Canonical Repo-To-Skills Workflow

Use this ordered workflow whenever turning a repository into one or more
agentic skills. The purpose is to make the process hard to skip: no candidate
skill should be packaged before its source context, readiness, execution path,
and publication evidence are understood.

1. **Define the user workflow first.** Capture the workflow goal, target users,
   example prompts, expected inputs, expected outputs, and constraints such as
   offline use, GPU, Docker, Conda, corporate workstation, privacy, or license
   limits.
2. **Build a source-context map.** Do more than list files. For every important
   artifact, write down what it contributes to the future skill:
   - README and quick starts provide intended use, setup path, example
     commands, supported workflows, advertised limits, and public language.
   - Docs and tutorials provide workflow variants, parameter meanings, edge
     cases, troubleshooting guidance, and domain vocabulary.
   - Scripts, CLIs, Python APIs, notebooks, and MONAI bundles provide
     executable entrypoints, arguments, side effects, return artifacts, and
     adapter opportunities.
   - Configs, manifests, metadata, label maps, and schemas provide modes,
     labels, defaults, supported modalities, model paths, validation rules, and
     structured fields for deterministic code.
   - Examples, tests, sample data, expected outputs, and demo notebooks provide
     realistic input/output contracts and smoke-test fixtures.
   - Dependency files, Dockerfiles, Conda files, install scripts, and CI
     provide runtime, OS, GPU, CUDA, Docker, package, and environment
     requirements.
   - Model cards, dataset cards, papers, standards, and benchmarks provide
     intended use, method context, citations, limitations, model/data terms, and
     claims that may or may not be safe to repeat.
   - Licenses, release notes, issues, discussions, and security notes provide
     permitted use, restricted use, version pinning, known bugs, and maintenance
     status.
3. **Pin or record the source version.** Capture repo URL, source subdirectory,
   commit, tag, release, model card URL, license URL, and date inspected. If the
   source is unpinned, say so and explain the risk.
4. **Create a candidate skill table from the source-context map.** Start with
   compact candidate review summaries so humans can compare candidates without
   reading a very wide table first. Then keep a detailed evidence table for
   agents and deeper review. Each candidate row should include skill name, what
   it does, why it is useful, source evidence links or paths, sample prompt
   call, CLI contract, inputs, outputs, deterministic entrypoint, LLM context
   needed, safety/license notes, smoke-test source, and recommendation. Do not
   promote a candidate whose key claims cannot be traced back to source context.
   If the scanner produced `command_evidence` or `provisional_cli_draft`, use
   those fields to guide adapter planning, but verify commands against source
   docs before treating them as supported. Use `command_evidence_summary` to
   triage side-effect risk before deciding which commands can become read-only
   `check`, planning, or guarded execution adapters. Use `execution_gate` as
   the first review gate, not as permission to run a command. Use
   `adapter_policy` to decide whether
   the next design artifact should be a read-only check adapter, setup-plan
   adapter, runtime-plan adapter, guarded-run adapter, or no runnable adapter
   until source review. Use `adapter_plan_stubs` to draft the adapter
   implementation plan and smoke-test plan, but do not treat stub commands as
   existing behavior until they are implemented and tested.
5. **Create Skill Design Cards.** Each candidate needs a human-reviewable
   Skill Design Card before skill files are created. Use
   `docs/templates/codebase-readiness-card.md` for now; existing file paths may
   still say `readiness-card` until a deliberate migration is approved.
6. **Decide scope.** Choose one algorithm skill, multiple functional-block
   skills, one workflow skill, or a mixed package. Record why.
   Default to one umbrella skill when the source repo, setup path, safety
   boundaries, and user intent are shared. Split into smaller skills only when
   a candidate has a distinct workflow, deterministic adapter surface,
   smoke-test evidence, and enough search demand to justify another installable
   catalog item.
7. **Split LLM and deterministic responsibilities.** State what the LLM may
   infer, what Python must verify, and what must never be guessed.
8. **Define runtime and deployment.** If source code must run, document install
   location, OS/runtime target, dependencies, model/data downloads, license
   review, environment checks, smoke-test data, and cleanup.
9. **Create the skill package.** Write `SKILL.md`, `README.md`, references,
   adapter scripts, and smoke-test scaffolding as needed.
10. **Run publication gates using source context.** Verify that behavior,
    examples, CLI commands, safety claims, citations, README copy, catalog
    metadata, and search terms are supported by the source-context map.
    Unsupported claims should be removed, marked as assumptions, or turned into
    open questions.
11. **Add smoke tests or skip reasons.** If executable behavior is proposed,
    identify a minimal test fixture and command. If it cannot run safely yet,
    record the skip condition and what would unblock it.
    Separate preflight smoke tests, such as source checkout, CUDA visibility,
    adapter planning, generated config writing, and guarded refusal behavior,
    from runtime acceptance, such as dependency installation, model download,
    model inference, output verification, and cleanup. Record acceptance per
    workflow or model variant rather than implying the whole repo is accepted.
12. **Build and evaluate.** Run `python -m skillforge build-catalog --json` and
    `python -m skillforge evaluate <skill-id> --json`.
13. **Publish by PR.** Include source files, generated catalog/site/plugin
    files, Skill Design Cards, evaluation results, and unresolved gaps.

The source-context map should be preserved in the Skill Design Card or a
`references/source-summary.md` file. It is the evidence layer that informs the
candidate table, adapter design, `SKILL.md`, README, SEO/search metadata, and
publication evaluation.

## Human-Facing Document Names

Use names that help contributors understand which document to open and why:

- **Skill Design Card:** preferred public name for the candidate review
  artifact. It records source evidence, scope, design decisions, adapter plans,
  safety gates, smoke tests, recommendation, and gaps.
- **Readiness Card:** legacy/internal term for the same artifact. It is still
  acceptable in file paths during migration, especially under
  `docs/readiness-cards/`.
- **Requirements:** binding product or implementation requirements. Do not use
  this name for the evidence-and-review card.
- **POR / Plan of Record:** avoid in public SkillForge docs unless the team has
  formally committed to a plan.
- **Skill Family Roadmap:** preferred name for planning future child skills
  within a family. Avoid "split roadmap" in human-facing copy because the goal
  is not splitting by default; the goal is deciding when a separate skill
  becomes useful and evidence-backed.

Skill READMEs are human-facing user guides. They should give practical links
and next actions, not only internal taxonomy. Standard practice guidance should
live in this design document, `requirements.md`, templates, and references.

## Generator Inputs

Codebase-to-agentic-skills should accept:

- Codebase URL or local path.
- Workflow goal, written in user language.
- Target user group.
- Example input files or dataset references.
- Expected output artifacts.
- Constraints such as GPU, CPU-only, offline, Docker, Conda, private network,
  or managed corporate workstation.
- Safety context, including medical, privacy, security, license, and data-use
  constraints.
- Preferred skill scope: narrow workflow skill, reusable algorithm skill, or
  both.

## Generator Outputs

Codebase-to-agentic-skills should produce a reviewable skill package:

```text
skills/<skill-id>/
  SKILL.md
  README.md
  references/
    source-summary.md
    data-contract.md
    safety-and-license.md
    execution.md
  scripts/
    adapter.py
    smoke_test.py
```

Not every generated skill needs every file. The workflow should keep
`SKILL.md` concise and move detailed source notes, labels, schemas, and command
variants into `references/`.

Codebase-to-agentic-skills should also produce:

- A Skill Design Card.
- Healthcare and medical-imaging signal summaries plus detailed signals when
  the scanner detects likely modality, runtime, model/data, task, or
  medical-safety evidence.
- A healthcare reading plan that turns detected signals into source files,
  bounded evidence hints, related source-context artifacts, review questions,
  and claim boundaries for medical AI repositories.
- Provisional candidate skill hypotheses that seed candidate table review when
  task/output signals are detected.
- Source coverage for each provisional hypothesis so reviewers can quickly see
  whether README/docs, entrypoints, configs, examples, runtime, model/data, and
  license/safety evidence were detected.
- Adapter-policy summaries and adapter-plan stubs that convert command evidence
  into reviewable wrapper-design paths before any source command is treated as
  runnable.
- An agent-facing Python CLI contract for deterministic execution when the skill
  has side effects or fragile file operations.
- A deterministic smoke test plan.
- Suggested search/discovery terms.
- Risk and side-effect notes.
- Known gaps and questions.
- Suggested catalog metadata.

For healthcare and medical-imaging repositories, the deterministic scan should
also report `healthcare_signal_summary` and `healthcare_signals` when it detects
likely evidence around NIfTI/DICOM formats, MONAI bundles, GPU/CUDA runtime
needs, model or dataset cards, segmentation/generation tasks, or medical-use
safety language. The summary should group signals by type, count, representative
terms, and files to review so agents can quickly identify the most important
source evidence. A single file may contribute several terms for the same signal
type; the scanner should not stop at the first task/output term when a README or
doc mentions multiple workflows. The scan should also report `healthcare_reading_plan`, a
prioritized checklist that asks what to verify and names the claim boundary for
each review area. Each checklist item should also include related
source-context artifacts, such as README, docs, configs, runtime files,
model/data cards, or license/security files when detected. It may include short
line-aware evidence hints when the source is a sampled text file, but those
hints are navigation aids only. These outputs are triage aids. They must point
the agent to files to read; they must not be treated as proof of supported
modality, clinical safety, license status, or runtime acceptance.

When task/output signals are present, the scan may report
`candidate_skill_hypotheses`. These hypotheses should connect source-context
artifacts and healthcare reading-plan evidence to possible skill rows, but they
must be marked provisional. They are prompts for human or LLM review, not
publication recommendations. Each hypothesis should include source coverage,
but coverage must be treated as artifact presence only, not claim validation.
When command evidence exists, each hypothesis should also include adapter-policy
summary and adapter-plan stubs. These stubs should name suggested adapter
commands, required inputs, expected outputs, guardrails, required reviews, and
smoke-test ideas, but they must remain design scaffolding until implemented.
The scanner should keep two adapter-policy concepts visible: the conservative
highest policy across all detected commands, and the candidate-level
recommended policy derived from workflow command evidence. Repo-maintenance
signals such as pre-commit, lint, or formatting configuration should be
preserved as evidence and counted in the conservative policy, but should be
ignored for the candidate-level recommendation when workflow-specific command
evidence exists. Provisional CLI drafts should similarly show workflow commands
before repo-maintenance commands so a reviewer sees the task path first.
When several hypotheses are present, provisional CLI drafts should be generated
per candidate, not shared across every row. The scanner should score command
evidence against the candidate's task terms, matched workflow-goal terms, and
source-section context such as nearby Markdown headings or the most recent
notebook markdown heading before a code cell. That lets a command like
`python tool.py run ...` inherit useful meaning from a "Synthetic Image
Generation" section in a README or a tutorial notebook. A generation candidate
should surface generation commands first, a segmentation candidate should
surface segmentation commands first, and unrelated commands should remain
available as review context rather than becoming the apparent next step.

## Skill Design Card

Each candidate codebase should get a short Skill Design Card:

```text
Name:
Source:
Workflow goal:
Primary users:
Input artifacts:
Output artifacts:
Execution surface:
Dependencies:
GPU needed:
Network needed:
Credentials needed:
License:
Model/data terms:
Risk level:
Read-only vs writes:
Deterministic adapter possible:
LLM decisions needed:
Minimal smoke test:
Known blockers:
Recommendation:
```

The recommendation should be one of:

- `make-skill-now`
- `needs-adapter-first`
- `needs-docs-or-examples`
- `needs-license-review`
- `not-a-good-skill-yet`

Skill Design Cards should live in `docs/readiness-cards/` until paths are
migrated. The reusable template lives in
`docs/templates/codebase-readiness-card.md`.

## Architecture

Codebase-to-agentic-skills should separate five layers:

1. **Discovery layer:** inspect the repository, README, docs, examples,
   notebooks, scripts, configs, dependencies, releases, licenses, and model
   cards.
2. **Capability layer:** summarize what the codebase can do, what inputs it
   expects, what outputs it produces, and where the real workflow value is.
3. **Adapter layer:** create or identify deterministic Python/CLI wrappers for
   setup checks, execution, file discovery, output validation, and smoke tests.
4. **Agent skill layer:** write `SKILL.md` instructions that tell Codex when to
   use the capability, what to ask, what to run, what not to claim, and how to
   report results.
5. **Publication layer:** create human-facing README content, catalog metadata,
   evaluation checks, search terms, and contribution guidance.

## LLM Versus Deterministic Code

Use the LLM for:

- Understanding user intent.
- Choosing which candidate codebase supports the workflow.
- Reading and summarizing docs.
- Identifying likely input/output contracts.
- Drafting `SKILL.md`, README, references, and safety notes.
- Mapping ambiguous user language to candidate parameters or labels.
- Explaining results and limitations.

Use deterministic Python or shell commands for:

- Cloning or inspecting repositories.
- Parsing files and manifests.
- Checking dependency and environment availability.
- Running quick starts and smoke tests.
- Downloading allowed test artifacts.
- Validating output files.
- Computing checksums, metadata, and catalog entries.

## Agent CLI Standard

Generated skills that perform deterministic work should include a Python CLI in
`scripts/`. The CLI should be callable by agents without reading or rewriting
the implementation.

Required commands when applicable:

```text
python scripts/<adapter>.py check --json
python scripts/<adapter>.py schema --json
python scripts/<adapter>.py <action> ... --json
```

Optional reporting commands are appropriate when the skill produces artifacts
that humans need to audit:

```text
python scripts/<adapter>.py report-html ... --json
```

The repo scan workflow itself is exposed as a top-level SkillForge command:

```text
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --json
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
python -m skillforge codebase-scaffold-adapter setup-plan --adapter-name <adapter-name> --output-dir skills/<skill-id> --json
python -m skillforge codebase-scaffold-adapter --from-scan-json docs/reports/<repo>-repo-to-skills/scan.json --candidate-id <candidate-id> --stub-type guarded-run --output-dir skills/<skill-id> --json
```

Adapter scaffolding is intentionally review-only. The generated Python skeleton
may expose `schema`, `check`, and `setup-plan`, but it must not expose `run`,
download assets, install dependencies, call the network, execute upstream code,
or write workflow outputs.
When `--from-scan-json` is used, the scaffold is grounded in one selected
candidate hypothesis and adapter-plan stub from the scanner output. The
generated skeleton should preserve source refs, guardrails, required reviews,
confirmation requirements, and planned commands as data so the next developer
or agent can review the exact evidence path before implementing execution.

CLI requirements:

- `check --json` reports dependency, environment, credential, model-weight, and
  data availability without writing files.
- `schema --json` returns command names, required arguments, optional arguments,
  side effects, output files, and examples.
- Action commands return stable JSON with `ok`, outputs, warnings, errors,
  suggested fixes, and provenance.
- Report commands should consume deterministic outputs and write human-readable
  artifacts, such as HTML plus image previews, without changing the underlying
  analysis results.
- Commands that write files must require an explicit output path.
- Commands that use network, large downloads, GPUs, Docker, or credentials must
  make those side effects visible and require the user or caller to opt in.
- Human output may be concise, but `--json` output must remain machine-readable.

## Generated Skill Types

Codebase-to-agentic-skills should support three skill shapes:

Candidate skill hypotheses are provisional, but their order should still
reflect the user's workflow goal. If a repository mentions several medical AI
tasks, such as segmentation masks, inference, synthesis, and generation, the
scanner should prefer hypotheses whose task terms match the workflow goal while
still preserving source evidence and review caveats.
Real-repo hypotheses should also carry source-scoped names and provenance. The
scanner should include the source project name in candidate names when it can
infer one from the local repo path, preserve the generic task name separately,
and capture Git provenance when available. `source_version` should include the
commit, branch, origin remote URL, dirty-worktree status, lookup status, and
whether a per-command `safe.directory` override was used. If Git blocks
read-only provenance lookup because the checkout has a different owner, the
scanner may retry with a per-command `safe.directory` override and report that
override in `source_version` without changing global Git configuration. The
generated source-context map, candidate skill table, readiness card, and
scan-backed adapter scaffold metadata should carry the same provenance summary
so reviewers can see the source state from the artifact they are using.

### Algorithm Skill

A reusable skill for one codebase or model.

Example:

```text
nv-segment-ctmr
```

### Workflow Skill

A skill that composes data, reports, models, adapters, and interpretation for a
specific outcome.

Example:

```text
radiological-report-to-roi
```

### Generator Skill

A meta-skill that helps create other skills from codebases.

Example:

```text
codebase-to-agentic-skills
```

## Medical Imaging Safety Baseline

For medical-imaging codebases, generated skills should default to conservative
language:

- Research use only unless the source explicitly supports another use.
- Not for diagnosis, treatment, triage, or clinical decision-making.
- Do not attempt re-identification.
- Respect dataset and model-weight terms.
- Do not redistribute restricted data.
- Identify whether outputs are model predictions, measurements, derived masks,
  or human-reviewed annotations.
- Report provenance for source data, model, command, label mapping, and output
  files.

## MVP Plan

### MVP 1: Manual Exemplar

Create the Radiological Report to ROI design and a first
SkillForge skill package by hand.

Acceptance criteria:

- The workflow is documented.
- Inputs and outputs are explicit.
- LLM-driven and Python-driven responsibilities are separated.
- Safety and license boundaries are explicit.
- A minimal adapter plan exists.

### MVP 2: Generator Checklist

Create the Skill Design Card workflow and use it to evaluate a small set of
NVIDIA-Medtech and MONAI candidates.

Acceptance criteria:

- At least five candidate codebases have Skill Design Cards.
- Each candidate has a recommended next action.
- The codebase-to-agentic-skills workflow identifies missing docs, examples, adapters, or
  license review needs.

### MVP 3: Draft Generator Skill

Create `skills/codebase-to-agentic-skills/SKILL.md`.

Acceptance criteria:

- Codex can use the skill to inspect a repo and draft a skill package.
- The generated package follows SkillForge conventions.
- The workflow produces a Skill Design Card before generating files.
- The workflow asks before writing generated skill files.

### MVP 4: Adapter And Smoke Test Scaffolding

Add deterministic helpers that can scaffold adapters and smoke tests.

Acceptance criteria:

- The workflow can create a placeholder `adapter.py`.
- The workflow can create a placeholder `smoke_test.py`.
- The generated smoke test records expected inputs, outputs, and skipped-test
  reasons when dependencies or data are unavailable.

## Open Questions

- Should generated skills be created as draft folders first, then promoted into
  `skills/` only after evaluation?
- Should large model dependencies be represented as install instructions,
  Docker recipes, Conda environment checks, or optional adapters?
- Should SkillForge maintain a separate `algorithms/` or `candidates/`
  directory for Skill Design Cards before a full skill exists?
- How much source inspection should happen live over the network versus from a
  pinned local clone?
- Should codebase-to-agentic-skills create one skill per algorithm, one skill per workflow,
  or both when a workflow composes several algorithms?
