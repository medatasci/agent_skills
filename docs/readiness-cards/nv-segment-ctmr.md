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
