# NV-Segment-CTMR Skill Requirements And Development Plan

Status: implemented with first WSL2 runtime smoke test  
Date: 2026-05-04  
Skill ID: `nv-segment-ctmr`

## Purpose

Create a SkillForge skill named `nv-segment-ctmr` that gives Codex an
agentic interface to NVIDIA-Medtech NV-Segment-CTMR:

https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR

The skill should help users and agents safely plan, review, and eventually run
research CT/MRI segmentation workflows without requiring the user to memorize
NV-Segment-CTMR setup details, mode names, label prompt syntax, MONAI bundle
commands, brain MRI preprocessing, output paths, or provenance rules.

This document uses the local discovery report as the starting point:

`docs/reports/nv-segment-ctmr-skill-discovery.html`

## Source Context

Authoritative sources:

- NV-Segment-CTMR GitHub implementation README:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR
- NV-Segment-CTMR Hugging Face model card:
  https://huggingface.co/nvidia/NV-Segment-CTMR
- VISTA3D CVPR 2025 paper:
  https://openaccess.thecvf.com/content/CVPR2025/html/He_VISTA3D_A_Unified_Segmentation_Foundation_Model_For_3D_Medical_Imaging_CVPR_2025_paper.html
- VISTA3D arXiv record:
  https://arxiv.org/abs/2406.05285
- Project MONAI VISTA source lineage:
  https://github.com/Project-MONAI/VISTA

Source facts to preserve:

- NV-Segment-CTMR is a CT and MRI 3D medical image segmentation model based on
  VISTA3D.
- The upstream README describes segment-everything modes `CT_BODY`,
  `MRI_BODY`, and `MRI_BRAIN`.
- The upstream README and model card describe label-prompt segmentation by
  class index.
- The model card says NV-Segment-CTMR does not support point-based interactive
  segmentation and points users to VISTA3D for interactive use.
- The model card says the model is for research and development only.
- The upstream README describes brain MRI preprocessing with skull stripping,
  LUMIR template alignment, MONAI bundle inference, and native-space mask
  reversion.
- The upstream README says code is Apache License 2.0 and model weights use an
  NVIDIA non-commercial license.

## Paper Context For LLM Prompting

The VISTA3D paper explains why the agent should treat this as a 3D medical
imaging workflow, not a generic 2D image segmentation task.

Prompting implications:

- Ask whether the user wants automatic supported-class segmentation, label
  prompt segmentation, report-guided ROI, batch segmentation, fine-tuning, or
  another workflow.
- Treat 3D medical images as volumes. Do not suggest slice-by-slice 2D
  segmentation as the default.
- Distinguish supported anatomy from novel or unsupported anatomy. Unsupported
  anatomy should trigger label-map review, limitation language, or another
  workflow.
- Do not imply open-vocabulary text segmentation. User anatomy language must be
  resolved to supported label IDs or one of the predefined modes.
- Do not imply NV-Segment-CTMR supports point-click interactive segmentation.
  The VISTA3D method lineage includes interactive ideas, but the NV-Segment-CTMR
  model card says this model does not expose point prompts.
- Treat fine-tuning as a separate higher-cost workflow that requires data,
  labels, checkpoints, compute, and validation planning.

## Primary Users

- Medical-imaging researchers.
- ML engineers.
- Imaging platform developers.
- Codex agents helping those users.
- SkillForge maintainers turning medical AI codebases into agentic skills.

## User Stories

- As a researcher, I want to ask "Create a segmentation map from this MRI" and
  have Codex ask the minimum questions needed to choose `MRI_BODY` or
  `MRI_BRAIN`.
- As an ML engineer, I want to ask "Segment the spleen in this CT scan" and
  have Codex resolve the anatomy to exact label candidates before planning a
  model run.
- As an agent, I want stable JSON commands for checking the local environment,
  resolving labels, planning commands, verifying outputs, and reporting
  provenance.
- As a workflow developer, I want Radiological Report to ROI to call or reuse
  NV-Segment-CTMR without duplicating model-running logic.
- As a reviewer, I want the skill to clearly state research-only, license,
  data handling, and write-side-effect boundaries.

## Scope

MVP scope:

- Skill package under `skills/nv-segment-ctmr/`.
- `SKILL.md` agent contract.
- `README.md` human-facing home page.
- Reference docs for source context, prompting, requirements, and development
  plan.
- Planning-first workflow that can be called by Codex.
- Deterministic Python adapter for planning, verification, and guarded
  single-volume execution.

MVP out of scope:

- Silent model execution.
- Silent model-weight download.
- Silent Docker/SynthStrip use.
- Silent GPU-heavy runs.
- Clinical claims.
- Full TensorRT execution.
- Fine-tuning automation beyond planning.

## Functional Requirements

### FR1: Skill Triggering

The skill must trigger for:

- NV-Segment-CTMR.
- NVIDIA-Medtech NV-Segment-CTMR.
- VISTA3D CT/MRI segmentation.
- CT_BODY, MRI_BODY, MRI_BRAIN.
- MONAI bundle segmentation.
- CT or MRI NIfTI segmentation.
- Anatomy-specific label prompt segmentation.

The skill should not trigger for generic medical advice, generic NIfTI
conversion, or final report-guided ROI extraction when `radiological-report-to-roi`
is the better fit.

### FR2: Intent Routing

The agent must classify the user intent into one of these routes:

- label lookup
- single-volume segment-everything
- single-volume anatomy-specific segmentation
- brain MRI segmentation with preprocessing
- batch or cohort segmentation
- output verification
- Radiological Report to ROI composition
- TensorRT readiness
- fine-tuning planning

### FR3: Clarifying Questions

The agent must ask only for missing information needed for the next safe step:

- CT or MRI?
- Body or brain?
- All supported structures or specific anatomy?
- Plan only or run inference?
- Local image path?
- Local upstream repo and model path?
- Output directory?
- Is Docker allowed for skull stripping?
- Is this data allowed to be processed locally?

### FR4: Label Lookup

The skill must require exact label IDs from authoritative label maps before
planning label-prompt segmentation.

The read-only adapter supports:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py labels --query "brain stem" --json
```

Label lookup output must include:

- query
- candidate labels
- label IDs
- source file
- modality notes when available
- ambiguity warnings

### FR5: Environment Check

The read-only adapter supports:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py check --json
```

The check must report:

- Python executable and version.
- Whether the upstream source checkout exists.
- Whether expected config files exist.
- Whether model weights exist.
- Whether optional dependencies are importable.
- Whether `conda`, `git`, `hf`, `torchrun`, and Docker are available when
  relevant.
- Whether CUDA or GPU visibility can be detected.
- Whether the output directory is writable when provided.

### FR6: Runtime Setup Planning

The read-only adapter supports:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py setup-plan --target wsl2-linux --json
```

The setup plan must not clone repositories, create environments, download
packages, download model weights, or write files. It must return:

- target runtime, such as `wsl2-linux` or `linux`
- planned runtime directory
- upstream clone URL
- planned source directory
- planned conda environment name and Python version
- model repository and planned model path
- ordered setup commands
- detected local tools where available
- side effects if the user executes the plan
- approvals needed before clone, environment creation, dependency install, or
  model download
- warnings for missing local tooling or Docker/SynthStrip readiness gaps

### FR7: Command Planning

The read-only adapter supports:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py plan --image scan.nii.gz --mode MRI_BODY --output-dir results --json
```

The plan must return:

- selected route
- command array
- source working directory
- required files
- expected output paths
- side effects
- warnings
- approvals needed
- provenance template

Planning must be read-only.

### FR8: Guarded Execution

Direct execution must be explicit and separate from planning:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py run --image scan.nii.gz --mode MRI_BODY --output-dir results --confirm-execution --json
```

Execution must require:

- explicit user approval from the agent conversation
- explicit output directory
- existing local source checkout
- existing model weights
- valid mode
- readable input
- writable output directory

Execution must capture logs and return JSON with success, failure, warnings,
and provenance.

### FR9: Brain MRI Workflow

Brain MRI workflow must be separate from body CT/MRI because it can involve:

- skull stripping
- LUMIR template alignment
- temporary preprocessing files
- native-space mask reversion
- Docker/SynthStrip
- `--no-skullstrip`
- `--keep-temp`

The agent must ask before Docker or temporary-file-heavy preprocessing.

The adapter supports read-only brain MRI planning:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-plan --image brain_t1.nii.gz --output-dir results --json
```

### FR10: Batch And Cohort Planning

Batch planning must report:

- discovered input scope
- recursive vs direct-folder behavior
- skip/resume policy
- expected outputs
- number of queued volumes
- GPU/process assumptions
- cache behavior
- commands for single-GPU and multi-GPU plans

Batch execution should wait until single-volume execution and output
verification are reliable.

### FR11: Output Verification

The adapter supports:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py verify-output --segmentation results/scan_trans.nii.gz --json
```

Verification must check:

- file exists
- file size is non-zero
- NIfTI can be opened when `nibabel` is available
- shape and affine are recorded
- label values are summarized when practical
- warnings are surfaced

### FR12: Provenance

Every plan and execution response must preserve:

- source repo URL
- source repo commit when available
- model card URL
- model path or model version
- command
- working directory
- mode
- label IDs
- input path
- output path
- timestamp
- environment summary
- warnings
- research-only limitation

### FR13: Safety And License

The skill must always preserve these boundaries:

- research and development use
- not diagnosis, treatment, triage, or clinical decision support
- medical images may contain PHI or restricted data
- no upload or redistribution without permission
- model weights may have non-commercial license terms
- downloads, Docker, GPU jobs, and writes require explicit approval

## LLM Responsibilities

The LLM should:

- map user intent to the correct route
- ask clarifying questions
- explain source limitations
- expand anatomy terms into label-search queries
- decide when to route to `radiological-report-to-roi`
- summarize verified outputs in user language

The LLM must not:

- invent label IDs
- claim clinical validity
- claim model execution succeeded without output verification
- imply point-prompt support for NV-Segment-CTMR
- assume commercial license rights
- silently process PHI or restricted data

## Deterministic Python Responsibilities

The adapter should:

- parse CLI arguments
- load source metadata
- inspect the local environment
- read label maps
- validate NIfTI paths
- build command arrays with `shell=False`
- verify outputs
- write provenance JSON
- return stable JSON for agents

## File Requirements

Skill package:

```text
skills/nv-segment-ctmr/
  SKILL.md
  README.md
  references/
    source-context-and-prompting.md
    requirements-and-development-plan.md
  scripts/
    nv_segment_ctmr.py
```

Generated publication files after `build-catalog`:

```text
catalog/skills/nv-segment-ctmr.json
plugins/agent-skills/skills/nv-segment-ctmr/
site/skills/nv-segment-ctmr/index.html
catalog/skills.json
catalog/search-index.json
site/search-index.json
plugins/agent-skills/skills/skill_list.md
```

## CLI Contract

Implemented read-only commands:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py schema --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py check --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py setup-plan --target wsl2-linux --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py labels --query "brain stem" --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py plan --image scan.nii.gz --mode MRI_BODY --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-plan --image brain_t1.nii.gz --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py batch-plan --input-dir cohort --mode MRI_BODY --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py verify-output --segmentation results/scan_trans.nii.gz --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py segment-test-mri --json
```

`segment-test-mri` is the one-command agent workflow for the accepted local
`22B7CXEZ6T` smoke test. By default it must be read-only, verify the existing
segmentation, and return `segmentation_path`. If the expected output is
missing, it must return a planned run and refuse execution unless
`--run-if-missing --confirm-execution` is supplied.

Implemented guarded execution commands:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py run --image scan.nii.gz --mode MRI_BODY --output-dir results --confirm-execution --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-run --image brain_t1.nii.gz --output-dir results --confirm-execution --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py batch-run --input-dir cohort --mode MRI_BODY --output-dir results --confirm-execution --json
```

## JSON Response Requirements

Every command must return:

```json
{
  "ok": true,
  "command": "plan",
  "side_effects": [],
  "warnings": [],
  "errors": [],
  "provenance": {}
}
```

Error responses must include:

- stable error kind
- message
- suggested fix
- whether the command was read-only
- whether any outputs were written

## Development Plan

### Phase 0: Skill Package And Documentation

Deliver:

- `skills/nv-segment-ctmr/SKILL.md`
- `skills/nv-segment-ctmr/README.md`
- source context reference
- requirements and development plan
- catalog rebuild and evaluation

Acceptance:

- no unresolved template placeholders
- skill is searchable
- safety and source references are present
- execution is described as guarded work requiring explicit confirmation

### Phase 1: Read-Only Adapter

Status: implemented.

Deliver:

- `scripts/nv_segment_ctmr.py`
- `schema --json`
- `check --json`
- `setup-plan --json`
- `labels --query ... --json`
- `plan --json`

Acceptance:

- works on Windows, macOS, and Linux
- uses `pathlib`
- uses subprocess argument arrays, not shell strings
- does not execute model inference in `plan`
- returns stable JSON

### Phase 2: Output Verification

Status: implemented.

Deliver:

- `verify-output --json`
- optional `nibabel` detection
- shape, affine, file size, label summary, and warnings

Acceptance:

- verifies real or synthetic NIfTI outputs when available
- returns actionable errors when dependencies are missing
- does not modify files

### Phase 3: Guarded Single-Volume Execution

Status: implemented.

Deliver:

- `run --json`
- log capture
- provenance JSON
- output verification after run

Acceptance:

- refuses missing model weights
- refuses missing output directory
- refuses unsupported mode
- requires user approval at the agent layer
- captures upstream errors without hiding them

### Phase 4: Brain MRI Workflow

Status: implemented.

Deliver:

- `brain-plan --json`
- guarded brain MRI execution wrapper
- skull-strip and no-skullstrip handling
- keep-temp behavior
- native-space output verification

Acceptance:

- Docker/SynthStrip is never used silently
- preprocessing steps and outputs are recorded
- failures are visible and actionable

### Phase 5: Batch And Cohort Workflows

Status: implemented.

Deliver:

- `batch-plan --json`
- guarded `batch-run --json`
- resume/skip reporting
- multi-GPU planning

Acceptance:

- batch planning is read-only
- expected writes are shown before execution
- GPU/process count and queued input count are validated

### Phase 6: Advanced Workflows

Deliver later:

- TensorRT readiness checks
- fine-tuning planning helper
- source commit pinning
- integration with Radiological Report to ROI
- smoke tests using permitted local example data

### Phase 7: Agent-Friendly Smoke-Test Workflow

Status: implemented.

Deliver:

- `segment-test-mri --json`
- default read-only verification of `22B7CXEZ6T`
- deterministic `segmentation_path` in JSON
- guarded generation path with `--run-if-missing --confirm-execution`

Acceptance:

- verifies the existing local output without rerunning the model
- reports missing output with a suggested fix
- never writes unless explicit execution flags and local prerequisites are present

## Testing Requirements

Unit tests:

- schema command shape
- mode validation
- setup-plan command is read-only and returns clone/download/environment side
  effects as planned actions only
- label query parsing
- path handling on Windows-style and POSIX-style paths
- command construction
- JSON error shape

Integration tests:

- check command in an environment without upstream checkout
- plan command with a fake image path returns useful missing-file error
- labels command against a small fixture label map
- verify-output against a small synthetic NIfTI when `nibabel` is available
- segment-test-mri reports the expected path for a missing synthetic workflow
- segment-test-mri verifies an existing synthetic NIfTI output when `nibabel`
  is available
- brain-plan returns read-only MRI_BRAIN plan JSON
- batch-plan discovers local NIfTI-like inputs without execution
- run refuses execution without explicit `--confirm-execution`
- brain-run refuses execution without explicit `--confirm-execution`
- batch-run refuses execution without explicit `--confirm-execution`

Manual tests:

- plan MRI_BODY run
- plan CT_BODY run
- plan MRI_BRAIN run
- verify output using local MR-RATE case `22B7CXEZ6T` when the image and
  NV-Segment-CTMR segmentation zip files are available on the user's machine
- route report-guided ROI prompt to `radiological-report-to-roi`
- confirm unsafe clinical prompt is refused or reframed

Manual smoke-test data:

- Prefer `22B7CXEZ6T` for local realistic testing because it was already
  provided as local MR-RATE image data plus NV-Segment-CTMR segmentation output.
- When present in this workspace, the input image used for direct model
  execution is
  `test-data/nv-segment-ctmr/22B7CXEZ6T/img/22B7CXEZ6T_t1w-raw-axi.nii.gz`.
- The generated smoke-test segmentation is
  `test-output/nv-segment-ctmr/22B7CXEZ6T/22B7CXEZ6T_t1w-raw-axi_trans.nii.gz`.
- Agents should prefer this command to verify and return the local smoke-test
  segmentation path:

  ```text
  python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py segment-test-mri --json
  ```

- Existing precomputed ROI workflow segmentations may also be checked under
  `test-data/radiological-report-to-roi/22B7CXEZ6T/segmentation/` when
  available.
- Do not commit MR-RATE images, reports, segmentation masks, or extracted
  derivatives unless licensing, privacy, and size constraints are explicitly
  reviewed.
- Keep automated unit tests on synthetic NIfTI fixtures generated at test time.

## WSL2 Runtime Acceptance Record

First local runtime target:

- OS/runtime: WSL2 Ubuntu.
- GPU: CUDA-visible NVIDIA RTX 3500 Ada Generation Laptop GPU.
- Source checkout: `~/.skillforge/runtime/nv-segment-ctmr/repo/NV-Segment-CTMR`.
- Source commit: `4046a027492266f22872880fea665ffd6aba1e36`.
- Python environment: Miniforge conda environment `nvseg-ctmr`, Python 3.11.15.
- Installed dependencies: upstream `requirements.txt` from NV-Segment-CTMR.
- Model weights: `models/model.pt` from `nvidia/NV-Segment-CTMR` on Hugging Face.

Smoke test executed:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-run \
  --source-dir ~/.skillforge/runtime/nv-segment-ctmr/repo/NV-Segment-CTMR \
  --image test-data/nv-segment-ctmr/22B7CXEZ6T/img/22B7CXEZ6T_t1w-raw-axi.nii.gz \
  --output-dir test-output/nv-segment-ctmr/22B7CXEZ6T \
  --no-skullstrip \
  --confirm-execution \
  --json
```

Observed result:

- Guarded execution returned `ok: true` with upstream return code `0`.
- Logs and provenance were written under
  `test-output/nv-segment-ctmr/22B7CXEZ6T/_nv_segment_ctmr_logs/`.
- Output NIfTI was verified with `verify-output --json`.
- Verified output shape: `512 x 512 x 252`.
- Verified spacing: `0.390625 x 0.390625 x 0.6000000238418579`.
- Verified label values: `0`, `220`, `223`, `227`, `228`, `276`, `284`.
- Verified non-zero voxel count: `3,752,025`.

Caveats:

- Docker was not installed in the WSL2 environment, so the first brain MRI
  smoke test used `--no-skullstrip`.
- The no-skullstrip path is useful for smoke testing the integration, but it
  assumes the selected input is appropriate for that execution mode.
- The Docker/SynthStrip skull-stripping path, CT_BODY execution, MRI_BODY
  execution, and batch execution still need separate runtime acceptance tests.
- This is a research/development smoke test only, not a clinical validation.

Rollback and cleanup notes:

- Adapter execution writes only to the user-selected output directory.
- Runtime logs and provenance are written under `_nv_segment_ctmr_logs/` inside
  that output directory.
- Upstream temporary brain MRI files should be removed by the upstream script
  unless `--keep-temp` is selected.
- Clean a failed smoke test by deleting only the selected output directory
  after confirming no user data should be preserved.
- Do not automatically remove the WSL2 source checkout, conda environment, or
  downloaded model weights; those shared runtime assets require explicit user
  approval before cleanup.

## Open Questions

- Should the product eventually provide a first-class setup command that clones
  the upstream repo, installs the conda environment, and downloads model
  weights, or should these remain explicit setup prerequisites?
- Should label maps be vendored into the skill, downloaded from a pinned
  upstream commit, or read from a local checkout?
- Which upstream commit should be pinned for published reproducible behavior?
- What additional smoke-test data can be public-safe and license-compliant for
  CT_BODY, MRI_BODY, skull-stripped MRI_BRAIN, and batch execution?

## Recommended Next Step

Add a documented setup helper for the WSL2/Linux runtime path, then broaden
runtime acceptance testing to Docker/SynthStrip brain preprocessing, CT_BODY,
MRI_BODY, and batch execution with approved test data and model terms.
