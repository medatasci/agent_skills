# Codebase-To-Agentic-Skill Generator

Status: project launch draft  
Date: 2026-05-03

## Purpose

The codebase-to-agentic-skill generator turns useful algorithm repositories into
Codex skills that humans and agents can discover, install, evaluate, and use.

The generator should be automated where possible, but directed by the workflow
the user wants to support. The goal is not to wrap every repository blindly. The
goal is to identify where a codebase can become a reliable agentic capability:
an agent-readable skill with a deterministic execution path, clear data
contracts, source provenance, safety boundaries, and enough examples to be
useful.

## Decisions So Far

- Name the project `codebase-to-agentic-skill generator`.
- Use the generator for both automated codebase inspection and user-directed
  workflow support.
- Start with one concrete exemplar before building generalized automation.
- Use Radiological Report to ROI as the first exemplar.
- Require a readiness card before generating a skill package.
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
- A small test fixture or example input.
- License, model weight, dataset, and intended-use boundaries that can be
  stated clearly.
- Useful agent decisions around setup, input selection, parameter choice,
  result interpretation, or follow-up actions.

A codebase is a weak candidate when it cannot be run reproducibly, has unclear
license or data-use terms, requires undocumented credentials, has no meaningful
input/output contract, or needs unsupported clinical claims to be useful.

## Generator Inputs

The generator should accept:

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

The generator should produce a reviewable skill package:

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

Not every generated skill needs every file. The generator should keep
`SKILL.md` concise and move detailed source notes, labels, schemas, and command
variants into `references/`.

The generator should also produce:

- A skill readiness card.
- An agent-facing Python CLI contract for deterministic execution when the skill
  has side effects or fragile file operations.
- A deterministic smoke test plan.
- Suggested search/discovery terms.
- Risk and side-effect notes.
- Known gaps and questions.
- Suggested catalog metadata.

## Skill Readiness Card

Each candidate codebase should get a short readiness card:

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

Readiness cards should live in `docs/readiness-cards/`. The reusable template
lives in `docs/templates/codebase-readiness-card.md`.

## Architecture

The generator should separate five layers:

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

The generator should support three skill shapes:

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
codebase-to-agentic-skill
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

Create the readiness-card workflow and use it to evaluate a small set of
NVIDIA-Medtech and MONAI candidates.

Acceptance criteria:

- At least five candidate codebases have readiness cards.
- Each candidate has a recommended next action.
- The generator workflow identifies missing docs, examples, adapters, or
  license review needs.

### MVP 3: Draft Generator Skill

Create `skills/codebase-to-agentic-skill/SKILL.md`.

Acceptance criteria:

- Codex can use the skill to inspect a repo and draft a skill package.
- The generated package follows SkillForge conventions.
- The workflow produces a readiness card before generating files.
- The workflow asks before writing generated skill files.

### MVP 4: Adapter And Smoke Test Scaffolding

Add deterministic helpers that can scaffold adapters and smoke tests.

Acceptance criteria:

- The generator can create a placeholder `adapter.py`.
- The generator can create a placeholder `smoke_test.py`.
- The generated smoke test records expected inputs, outputs, and skipped-test
  reasons when dependencies or data are unavailable.

## Open Questions

- Should generated skills be created as draft folders first, then promoted into
  `skills/` only after evaluation?
- Should large model dependencies be represented as install instructions,
  Docker recipes, Conda environment checks, or optional adapters?
- Should SkillForge maintain a separate `algorithms/` or `candidates/`
  directory for readiness cards before a full skill exists?
- How much source inspection should happen live over the network versus from a
  pinned local clone?
- Should the generator create one skill per algorithm, one skill per workflow,
  or both when a workflow composes several algorithms?
