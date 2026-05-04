# NV-Segment-CTMR Readiness Card

Status: first-pass readiness card  
Date: 2026-05-03

## Summary

Name:
NV-Segment-CTMR

Source:
https://github.com/NVIDIA-Medtech/NV-Segment-CTMR

Workflow goal:
Expose NV-Segment-CTMR as a reusable segmentation capability for agentic
medical-imaging workflows, starting with Radiological Report to ROI for
MR-RATE MRI studies.

Primary users:
Medical-imaging researchers, ML engineers, imaging platform developers, and
agents helping those users run reproducible segmentation or ROI workflows.

Recommendation:
`needs-adapter-first`

Recommendation rationale:
The codebase has a clear quick start, explicit segmentation modes, documented
commands, model weights on Hugging Face, and useful examples. It should become
an agentic skill, but first needs a deterministic adapter that checks the local
environment, resolves model weights, routes modes, records provenance, and
normalizes outputs.

## Candidate Scope

Proposed skill type:
Algorithm skill first, then composed workflow skill.

Proposed skill ID:
`nv-segment-ctmr`

Should this be one skill or multiple skills?
Use at least two skills:

- `nv-segment-ctmr`: reusable algorithm skill and execution adapter.
- `radiological-report-to-roi`: workflow skill that uses a
  report, image volume, label map, segmentation result, and ROI extraction.

Why this scope:
NV-Segment-CTMR is broadly reusable beyond MR-RATE. The Radiological Report to ROI
generator is a specific workflow that should call or reuse NV-Segment-CTMR
rather than own all model-running details.

## Source Inventory

Repository or codebase URL:
https://github.com/NVIDIA-Medtech/NV-Segment-CTMR

Main implementation directory:
https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR

Model card URL:
https://huggingface.co/nvidia/NV-Segment-CTMR

Documentation URLs:

- Quick start and README:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR#quick-start
- Brain MRI segmentation:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR#brain-mri-segmentation-any-mri-sequence

Example or quick-start URLs:
https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR#single-image-inference-to-segment-everything-automatic

License URLs:

- Code license is described in the repository README as Apache License 2.0.
- Model weights are described in the repository README as NVIDIA Non-Commercial
  License.

Relevant files or commands:

- `requirements.txt`
- `configs/inference.json`
- `configs/batch_inference.json`
- `configs/mgpu_inference.json`
- `configs/label_dict.json`
- `configs/metadata.json`
- `brain_t1_preprocess/run_brain_segmentation.sh`
- `brain_t1_preprocess/synthstrip-docker`

Version, commit, tag, or release to pin:
Pin a Git commit before implementation. The readiness card currently points to
the `main` branch and should be updated with a pinned commit before building a
reproducible adapter.

Source version status:
Unpinned first-pass readiness card. This is acceptable for planning and
requirements discovery only. Before publishing execution claims, reproducing
benchmarks, or treating command behavior as stable, pin the upstream
NVIDIA-Medtech/NV-Segment-CTMR commit, model-card revision, model-weight
revision, and any linked dataset/model artifacts used in examples or tests.

## Source Context Map

This table records what each source area contributes to the skill. It is more
than a file list: each row explains how the source should affect the agent
contract, adapter design, LLM prompting, safety posture, tests, and publication
claims.

| Source artifact | What it provides | Skill design impact | Adapter or deterministic-code impact | LLM context impact | Safety/license/publication impact | Open questions |
| --- | --- | --- | --- | --- | --- | --- |
| `NV-Segment-CTMR/README.md` quick start | Install flow, Conda environment, Hugging Face model download, MONAI bundle commands, supported modes, brain MRI preprocessing command, batch and multi-GPU examples. | Defines the first skill as a planning-plus-adapter segmentation skill rather than a free-form medical image assistant. | Drives `setup-plan`, `plan`, `brain-plan`, `batch-plan`, guarded `run`, and output-verification command shapes. | Grounds responses about what the tool can do, when to ask for mode/body/brain clarification, and what outputs to expect. | Claims should not exceed the README. Execution examples should preserve source URLs and require approval before clone, install, model download, Docker, GPU, or writes. | Pin exact README commit before publication-quality reproducibility claims. |
| Brain MRI README section and `brain_t1_preprocess/run_brain_segmentation.sh` | Skull stripping, affine alignment to a template, MONAI bundle inference, and native-space mask restoration workflow for brain MRI. | Supports a distinct `MRI_BRAIN` route and explains why brain MRI is not just another body MRI command. | Requires a `brain-plan`/`brain-run` path, Docker/SynthStrip readiness checks, temporary-file handling, and native-space output verification. | Helps the LLM ask whether Docker is allowed, whether skull stripping can be skipped, and whether the input is already suitable. | Brain preprocessing has extra dependencies and side effects; generated skill copy should warn before Docker/SynthStrip use. | Confirm exact output naming and failure behavior under local WSL2/Linux runtime. |
| `configs/inference.json`, `batch_inference.json`, and `mgpu_inference.json` | MONAI bundle entrypoints for single image, batch, and multi-GPU inference. | Supports separate single-volume, batch, and multi-GPU planning surfaces. | Adapter should construct commands from known configs rather than free-form shell strings, and should expose batch resume/cache behavior. | The LLM can explain when batch or multi-GPU planning matters without inventing parameters. | Multi-GPU and batch runs can be expensive; require explicit approval and clear output directories. | Need local smoke tests to verify exact command compatibility with installed MONAI version. |
| `configs/label_dict.json`, `metadata.json`, and label mappings | Supported anatomy labels, label IDs, metadata, and mapping context. | Supports label lookup as a core skill task and prevents open-vocabulary claims. | Adapter should implement deterministic `labels` lookup and should not guess label IDs when source maps are missing. | LLM should translate anatomy phrases into candidate labels with ambiguity notes, not final unsupported IDs. | Catalog examples and README claims must use supported labels and cite the source label map. | Pin label-map commit and decide how much of the label snapshot may be copied into the SkillForge skill. |
| Hugging Face model card for `nvidia/NV-Segment-CTMR` | Model purpose, supported modalities, NIfTI input expectation, MONAI integration, label-prompt behavior, research/development-only language, and model-weight terms. | Grounds safety language, supported input type, model-weight requirements, and "not interactive point-based segmentation" boundaries. | Adapter `check` and `setup-plan` should report model-weight path and download status without downloading by default. | LLM should not imply clinical readiness, point-click interaction, or unsupported modalities. | Model weights use NVIDIA non-commercial terms; public docs must preserve license and use restrictions. | Pin model card and weight revision before reproducible execution documentation. |
| VISTA3D paper and arXiv record | Method context for the 3D segmentation foundation model lineage and why volumetric workflows differ from generic 2D segmentation. | Adds scientific context but should not expand the skill's practical scope beyond NV-Segment-CTMR packaging. | No direct adapter command; informs provenance and citation output. | LLM can explain high-level context while avoiding unsupported benchmark or clinical claims. | Citation supports method context, not regulatory or clinical use claims. | Decide whether each generated skill should cite the paper or only the upstream model card. |
| `requirements.txt`, Conda setup, Docker/SynthStrip, `hf` CLI, `torchrun` | Runtime dependencies, environment setup, GPU/multi-GPU expectations, model download tooling, and external binaries. | Requires the skill to expose setup planning and readiness checks before execution. | Adapter must check Python, source dir, model path, image path, output dir, WSL2/Linux, Docker, Conda, `git`, and `hf` readiness where relevant. | LLM should explain missing prerequisites as blockers, not silently assume they exist. | Clone/install/download/GPU/Docker operations are side-effectful and need approval. | Confirm supported OS path: WSL2/Linux should be the execution target for this repo-derived skill. |
| Upstream examples and local MR-RATE test data | Candidate smoke-test inputs, expected output patterns, and a practical integration example for report-to-ROI workflows. | Supports a staged smoke test: adapter checks first, synthetic tests for CI, local realistic test with user-provided MR-RATE data. | Deterministic tests should use small synthetic NIfTI fixtures; realistic tests should remain local and uncommitted. | LLM can explain why realistic medical image data is not committed to the public repo. | Do not commit restricted or user-provided medical data. Keep local test paths out of public generated artifacts unless sanitized. | Need a small redistributable upstream example or documented skip reason for full inference CI. |
| Repository and model licenses | Apache 2.0 code license and NVIDIA non-commercial model terms, plus MR-RATE terms when composed with that dataset. | Keeps the skill research-only and separates code license from model-weight terms. | Adapter provenance should record source repo, model card, model path, and dataset terms when known. | LLM should not claim commercial use, clinical use, or redistribution permissions. | Public SkillForge docs must avoid NVIDIA-internal claims and must preserve non-commercial/model/data constraints. | Pin license URLs and model card revision before broader publication. |

## Candidate Skill Table

| Candidate skill | What it does | Why it is useful | Source evidence | Sample prompt call | Proposed CLI contract | Inputs | Outputs | Deterministic entrypoints | LLM context needed | Safety/license notes | Smoke-test source | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `nv-segment-ctmr` | Plan, label-check, verify, and optionally run guarded CT/MRI segmentation with NV-Segment-CTMR. | Provides a reusable algorithm skill for many medical-imaging workflows. | README quick start, MONAI configs, label maps, model card, VISTA3D references. | "Create a segmentation map from this MRI, but ask before running anything." | `python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py check|setup-plan|labels|plan|brain-plan|batch-plan|verify-output|run --json` | NIfTI path, mode, optional labels, source dir, model path, output dir. | Command plan, labels, warnings, output segmentation path, provenance JSON. | Existing adapter commands in `skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py`. | Choose CT vs MRI, body vs brain, specific labels vs segment-everything, and when to route to ROI workflow. | Research-only, no clinical decision-making, model terms are non-commercial, writes and downloads require approval. | CI synthetic checks plus optional local MR-RATE or upstream example inference when dependencies and weights are present. | `make-skill-now`; continue strengthening runtime smoke tests. |
| `radiological-report-to-roi` | Compose report evidence, image volume, segmentation labels, and ROI extraction. | Demonstrates how algorithm skills become useful workflow skills. | MR-RATE reports/images, MR-RATE-nvseg-ctmr segmentations, NV-Segment-CTMR label context. | "Use the report and segmentation to generate an ROI for the anatomy in the impression." | `python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py prepare-mrrate-case|extract-roi|report-html --json` | Report, image, segmentation, labels, output dir. | ROI mask, summary JSON, provenance JSON, HTML report. | Existing ROI adapter commands. | Extract report anatomy, resolve ambiguity, decide whether precomputed segmentation is enough. | Research-only, local medical data handling, do not redistribute restricted data. | Local `22B7CXEZ6T` test data and synthetic NIfTI tests. | `make-skill-now`; keep separate from lower-level segmentation execution. |
| `medical-image-segmentation-runtime-setup` | Plan WSL2/Linux, Conda, model download, Docker/SynthStrip, GPU, and environment setup for repo-derived medical imaging tools. | Many algorithm skills fail at environment setup; a shared setup skill could reduce repeated work. | NV-Segment-CTMR quick start, requirements, setup-plan adapter output, WSL2 discussion. | "Prepare this machine to run this medical image segmentation model, but do not install until I approve." | Future `setup-plan`, `doctor`, and optional guarded install commands. | Source repo, target OS, install root, model terms, user approvals. | Setup plan, prerequisite report, commands, warnings. | Not yet separate; currently covered by `nv-segment-ctmr setup-plan`. | Decide target platform and explain side effects. | High side-effect risk; keep approval-gated. | Dry-run setup-plan tests. | `needs-adapter-first`; defer until repeated across repos. |

## Workflow Fit

User problem:
The user has a CT or MRI volume and needs anatomically meaningful segmentation
or ROI support without manually reading model docs, choosing commands, moving
model weights, and interpreting labels.

What the codebase does:
NV-Segment-CTMR is a foundation model for 3D CT and MRI segmentation. The
repository describes segment-everything modes for `CT_BODY`, `MRI_BODY`, and
`MRI_BRAIN`, plus class-specific segmentation through label prompts. It includes
single-image, batch, multi-GPU, TensorRT, and brain MRI preprocessing workflows.

What the codebase does not do:
It does not, by itself, interpret radiology reports, choose anatomy from report
language, map clinical phrases to a user's ROI intent, join MR-RATE reports to
image volumes, or produce a final research narrative with evidence snippets.

Where an agent adds value:

- Decide which mode is appropriate for the user's image and task.
- Ask for missing modality, image path, model path, or output directory.
- Explain whether brain MRI requires preprocessing.
- Select or verify label IDs from a pinned label map.
- Route to precomputed MR-RATE segmentations when available.
- Explain limitations and provenance.

What should remain deterministic:

- Environment checks.
- Model-weight path resolution.
- Command construction.
- NIfTI input validation.
- Output path discovery.
- Log capture.
- JSON provenance.
- ROI mask extraction.

## Input Contract

Required inputs:

- Local NIfTI image volume path, or a file list/root path for batch mode.
- Segmentation mode: `CT_BODY`, `MRI_BODY`, or `MRI_BRAIN`.
- Output directory.

Optional inputs:

- Label prompt IDs for class-specific segmentation.
- Existing model path.
- `--keep-temp` for brain preprocessing.
- `--no-skullstrip` when skull stripping is unavailable or already done.
- Batch file list and partition parameters.

Accepted file formats:

- `.nii`
- `.nii.gz`

Required metadata:

- Modality or intended mode.
- For Radiological Report to ROI workflows, the source image and report provenance.
- For class-specific segmentation, label IDs and label map source.

Credentials or access requirements:

- Hugging Face access may be needed to download model weights.
- MR-RATE workflows may need accepted dataset terms and authenticated access.

Expected input size:
3D medical image volumes; storage and memory requirements depend on volume size
and batch size.

Validation checks:

- File exists and has supported suffix.
- Mode is one of `CT_BODY`, `MRI_BODY`, `MRI_BRAIN`.
- Model weights exist at the expected path.
- Output directory is writable.
- For brain mode, preprocessing dependencies are available or explicitly
  skipped.

## Output Contract

Primary outputs:

- NIfTI segmentation mask for the input volume.
- JSON provenance from the adapter.

Optional outputs:

- Captured command log.
- Temporary preprocessing files when requested.
- ROI mask and ROI summary when used by the Radiological Report to ROI workflow.

Output file formats:

- `.nii.gz`
- `.json`
- `.log`

Expected output locations:
The repository README describes outputs under the configured output directory,
with generated segmentation filenames such as `{basename}_trans.nii.gz` for the
brain script and nested paths for batch inference.

Machine-readable summary:

```json
{
  "ok": true,
  "mode": "MRI_BRAIN",
  "input_image": "image.nii.gz",
  "output_segmentation": "results/image_trans.nii.gz",
  "model_path": "models/model.pt",
  "command": ["..."],
  "warnings": [],
  "provenance": {}
}
```

Provenance fields:

- source repo URL
- source repo commit
- model card URL
- model weight path
- mode
- label IDs, when used
- command
- environment summary
- input image path
- output segmentation path
- timestamp

Validation checks:

- Output segmentation exists.
- Output segmentation is non-empty.
- Output can be opened as NIfTI.
- Shape and affine are recorded.
- Errors are actionable when output is missing.

## Execution Surface

Execution type:

- MONAI Bundle command.
- Shell script for brain MRI preprocessing.
- Torchrun for multi-GPU batch inference.
- Future SkillForge Python adapter around those commands.

Setup commands:

```text
conda create -y -n vista3d-nv python=3.11
conda activate vista3d-nv
git clone https://github.com/NVIDIA-Medtech/NV-Segment-CTMR.git
cd NV-Segment-CTMR/NV-Segment-CTMR
pip install -r requirements.txt
hf download nvidia/NV-Segment-CTMR --local-dir models/
```

The repository README also moves the downloaded model to `models/model.pt`.

Run commands:

```text
python -m monai.bundle run --config_file configs/inference.json --input_dict "{'image':'example/s0289.nii.gz'}" --modality MRI_BODY
```

```text
python -m monai.bundle run --config_file configs/inference.json --input_dict "{'image':'example/s0289.nii.gz','label_prompt':[3]}"
```

Brain MRI command:

```text
./brain_t1_preprocess/run_brain_segmentation.sh --input example/brain_t1.nii.gz --output_dir results/
```

Batch commands:

```text
python -m monai.bundle run --config_file="['configs/inference.json', 'configs/batch_inference.json']" --input_dir="example/" --output_dir="example/" --modality MRI_BODY
```

```text
torchrun --nproc_per_node=2 --nnodes=1 -m monai.bundle run --config_file="['configs/inference.json', 'configs/batch_inference.json', 'configs/mgpu_inference.json']" --input_dir="example/" --output_dir="example/" --modality MRI_BODY
```

Resume or cache behavior:
The batch configuration supports skipping existing outputs by default and can
cache input lists for multi-process runs.

Expected runtime:
Unknown until measured locally. It depends on GPU, volume size, mode, and batch
size. The adapter should report elapsed time.

## Dependencies

Python version:
The repository quick start creates a Python 3.11 Conda environment.

Core packages:
See upstream `requirements.txt`.

External binaries:

- `git`
- `hf` CLI for model download
- `conda`
- `torchrun` for multi-GPU runs
- Docker-compatible environment for SynthStrip when skull stripping is used

GPU required:
Likely required for practical inference. Exact CPU-only support should be
verified before promising it.

CUDA or driver requirements:
Needs verification from the installed PyTorch/MONAI stack and target hardware.

Docker required:
Brain MRI preprocessing uses `brain_t1_preprocess/synthstrip-docker` unless
the user passes `--no-skullstrip`.

Conda required:
The quick start uses Conda. A future adapter may support an existing Python
environment, but Conda should be the documented default until tested.

Network required:
Required for cloning the repo and downloading model weights. Not required for
inference once code, dependencies, and weights are local.

Large downloads:
Model weights from `nvidia/NV-Segment-CTMR` on Hugging Face.

Storage requirements:
Model weights, input volumes, output segmentations, and optional temporary
preprocessing files.

## Safety, License, And Data Use

Code license:
Apache License 2.0, per the repository README.

Model weights license:
NVIDIA Non-Commercial License, per the repository README and linked model
terms.

Dataset terms:
Not inherent to NV-Segment-CTMR, but MR-RATE workflows add gated dataset terms,
privacy constraints, non-commercial/research use, and redistribution
restrictions.

Permitted use:
Research and development workflows, subject to model and dataset terms.

Restricted use:
Commercial use of non-commercial model weights without appropriate rights.
Clinical diagnosis, treatment, triage, or decision-making should not be claimed
by SkillForge skills unless a separate source explicitly supports that use.

Privacy concerns:
Medical images may contain sensitive or restricted data. The adapter should not
upload user data, leak paths or PHI, or redistribute derived data without
permission.

Clinical-use constraints:
Generated skills should state that outputs are research artifacts and not
medical advice or clinical interpretation.

Redistribution constraints:
Respect model and dataset terms. Do not redistribute restricted weights,
MR-RATE data, or derived data unless allowed by the governing terms.

Required user confirmations:

- Before downloading model weights.
- Before downloading gated datasets.
- Before writing large outputs.
- Before running GPU-intensive or long-running inference.
- Before using Docker/SynthStrip in an environment where Docker side effects
  matter.

## Agent Decisions

The LLM should decide:

- Whether the user's task is segmentation, ROI extraction, or report-guided
  analysis.
- Which mode is likely appropriate: `CT_BODY`, `MRI_BODY`, or `MRI_BRAIN`.
- Whether to ask for modality, image path, or desired anatomy.
- Whether precomputed segmentation is preferable for MR-RATE.
- How to explain limitations and next steps.

The LLM should not decide:

- Exact label IDs without checking a pinned label map.
- That output is clinically valid.
- That licensing permits commercial use.
- That dependencies are installed without running checks.
- That a missing or failed segmentation succeeded.

Clarifying questions to ask:

- Is the input CT or MRI?
- Is the target anatomy brain, body, or spine?
- Do you want to use precomputed segmentations or run the model?
- Is the image local, or should the workflow download it from an approved
  source?
- Has the user accepted any gated dataset terms?

Failure modes the agent should recognize:

- Model weights missing.
- `hf` CLI missing or unauthenticated.
- Conda environment missing.
- GPU or CUDA unavailable.
- Docker/SynthStrip unavailable for brain preprocessing.
- Input volume cannot be read.
- Output segmentation missing or empty.
- Mode/label mismatch.

## Deterministic Adapter Plan

Adapter files to create:

```text
skills/nv-segment-ctmr/scripts/check_environment.py
skills/nv-segment-ctmr/scripts/run_segmentation.py
skills/nv-segment-ctmr/scripts/verify_output.py
```

Adapter command shape:

```text
python scripts/check_environment.py --json
python scripts/run_segmentation.py --image image.nii.gz --mode MRI_BRAIN --output-dir results --json
python scripts/run_segmentation.py --image image.nii.gz --mode MRI_BODY --labels 3,20 --output-dir results --json
```

Read-only operations:

- Environment inspection.
- Model path detection.
- Input validation.
- Label map inspection.

Write operations:

- Output segmentations.
- Logs.
- Provenance JSON.
- Optional temporary files.

Network operations:

- Optional model-weight download.
- Optional source clone in setup workflows.

Error handling:

- Return structured JSON with `ok`, `error`, `suggested_fix`, and
  `side_effects`.
- Preserve command logs.
- Avoid swallowing upstream errors.

JSON output fields:

- `ok`
- `mode`
- `input_image`
- `output_segmentation`
- `model_path`
- `labels`
- `command`
- `elapsed_seconds`
- `warnings`
- `errors`
- `provenance`

## Smoke Test Plan

Minimal test input:
Use the upstream example NIfTI files included in the repository, if small enough
and available after clone. If the example requires model weights or GPU, mark
the smoke test as skipped with a clear reason when those are unavailable.

Expected command:

```text
python scripts/check_environment.py --json
```

Then, when dependencies and model weights are available:

```text
python scripts/run_segmentation.py --image example/s0289.nii.gz --mode MRI_BODY --output-dir test-output/nvseg --json
```

Expected outputs:

- Environment check JSON.
- Segmentation NIfTI when full inference runs.
- Provenance JSON.
- Captured log.

Skip conditions:

- No GPU.
- Model weights missing.
- Conda environment missing.
- Required packages missing.
- Docker unavailable for brain preprocessing.

How to verify output:

- File exists.
- File size is non-zero.
- NIfTI header can be loaded.
- Shape is recorded.
- Command and model path are recorded.

Test data license:
Use only example data distributed with the repository or user-provided local
test data with appropriate permissions.

## Skill Package Plan

Suggested files:

```text
skills/nv-segment-ctmr/
  SKILL.md
  README.md
  references/
    source-summary.md
    execution.md
    labels.md
    safety-and-license.md
  scripts/
    check_environment.py
    run_segmentation.py
    verify_output.py
```

References to include:

- Upstream quick start summary.
- Brain MRI preprocessing summary.
- Label map source and usage.
- Model/data license notes.
- Environment and dependency notes.

Scripts to include:

- Environment checker.
- Segmentation runner.
- Output verifier.

Catalog/search terms:

- NV-Segment-CTMR
- VISTA3D
- medical image segmentation
- CT segmentation
- MRI segmentation
- MRI_BRAIN
- MRI_BODY
- CT_BODY
- brain MRI segmentation
- MONAI bundle segmentation
- NIfTI segmentation

Related skills:

- `radiological-report-to-roi`
- future MONAI Bundle runner skill
- future medical image ROI extraction skill

## Known Blockers

- Need a pinned upstream commit.
- Need local verification of dependency install and model-weight layout.
- Need a pinned label map for exact label ID resolution.
- Need a clear policy for GPU-required commands.
- Need a decision on whether the adapter may download model weights.
- Need to verify whether example inputs are sufficient for smoke tests.

## Open Questions

- Should the first adapter support only local already-installed repos, or also
  clone/setup flows?
- Should model weights be downloaded by the adapter or treated as a user setup
  prerequisite?
- Should brain MRI default to skull stripping, or ask before using Docker?
- Should `MRI_BRAIN` output be the default for MR-RATE center-modality brain
  ROI workflows?
- Should batch inference be deferred until single-volume inference is stable?
- Should TensorRT support be documented but deferred?

## Next Action

Next recommended action:
Create `skills/nv-segment-ctmr/SKILL.md` and a minimal
`scripts/check_environment.py` adapter before attempting full model execution.
