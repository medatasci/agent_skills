# NV-Generate-CTMR Readiness Card

Status: first-pass SkillForge interface implemented
Date: 2026-05-04

## Summary

Name:
NV-Generate-CTMR

Source:
https://github.com/NVIDIA-Medtech/NV-Generate-CTMR

Pinned source commit used for first-pass evidence:
`40f5109dc77eaf01fbc5741809003f89ca3a36c7`

Source commit: 40f5109dc77eaf01fbc5741809003f89ca3a36c7

Workflow goal:
Expose NV-Generate-CTMR as a reusable SkillForge capability for planning,
configuring, and optionally running research synthetic CT and MRI generation
workflows.

Primary users:
Medical-imaging researchers, ML engineers, imaging platform developers, and
agents helping those users plan reproducible synthetic image generation.

Recommendation:
`make-skill-now`

Recommendation rationale:
The upstream repository has clear model variants, quick-start commands,
configuration files, setup guidance, model cards, and documented inference
parameters. It can be made useful immediately as a planning-first agentic skill
with guarded execution.

## Candidate Scope

Proposed skill type:
Algorithm-interface skill with guarded execution.

Proposed skill ID:
`nv-generate-ctmr`

Should this be one skill or multiple skills?
Start with one skill because the model variants share source, setup, runtime,
and configuration concepts. If usage grows, split future skills around CT
paired generation, MR brain generation, training/fine-tuning, and evaluation.

Split decision:
Keep `nv-generate-ctmr` as one umbrella algorithm-interface skill for MVP.
Split later only when a candidate workflow has distinct user demand, adapter
commands, smoke-test evidence, and enough search value to justify another
installable skill.

Why this scope:
Most user tasks begin with "what should I run?" and "what will it do?" rather
than direct model execution. One skill can route across the variants while
sharing setup, safety, and config-preview behavior.

## Source Inventory

Repository URL:
https://github.com/NVIDIA-Medtech/NV-Generate-CTMR

Main branch tree:
https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/tree/main

Model card URLs:

- https://huggingface.co/nvidia/NV-Generate-CT
- https://huggingface.co/nvidia/NV-Generate-MR
- https://huggingface.co/nvidia/NV-Generate-MR-Brain

Documentation URLs:

- Setup:
  https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/blob/main/docs/setup.md
- Inference:
  https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/blob/main/docs/inference.md
- Training:
  https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/blob/main/docs/training.md
- Data:
  https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/blob/main/docs/data.md
- Evaluation:
  https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/blob/main/docs/evaluation.md
- Performance:
  https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/blob/main/docs/performance.md

Relevant files or commands:

- `README.md`
- `requirements.txt`
- `configs/config_infer.json`
- `configs/modality_mapping.json`
- `configs/config_network_rflow.json`
- `configs/config_network_ddpm.json`
- `configs/config_maisi_diff_model_rflow-mr-brain.json`
- `configs/config_maisi_diff_model_rflow-mr.json`
- `configs/config_maisi_diff_model_rflow-ct.json`
- `configs/config_maisi_diff_model_ddpm-ct.json`
- `configs/environment_rflow-ct.json`
- `configs/environment_ddpm-ct.json`
- `configs/environment_maisi_diff_model_rflow-mr-brain.json`
- `configs/environment_maisi_diff_model_rflow-mr.json`
- `scripts/download_model_data.py`
- `scripts/inference.py`
- `scripts/diff_model_infer.py`
- `scripts/train_controlnet.py`
- `scripts/diff_model_train.py`
- `scripts/compute_fid_2-5d_ct.py`

Source version status:
Pinned for first-pass source evidence. Model-card and model-weight revisions
should be pinned before full reproducibility claims.

## Source Context Map

| Source artifact | What it provides | Skill design impact | Adapter or deterministic-code impact | LLM context impact | Safety/license/publication impact | Open questions |
| --- | --- | --- | --- | --- | --- | --- |
| `README.md` | High-level purpose, model variants, quick starts, license table, citations, and resources. | Defines skill purpose and primary model routes. | Drives `models`, `plan`, and `setup-plan` output. | Grounds user-facing descriptions and variant selection. | Must preserve research and model-license caveats. | Need to track upstream changes to model terms. |
| `docs/setup.md` | Python, CUDA, GPU, dependency, MONAI, and model download expectations. | Makes the skill planning-first with setup gates. | Drives `check` and `setup-plan`. | Helps explain blockers clearly. | Clone/install/download are side effects requiring approval. | Need local acceptance on target systems. |
| `docs/inference.md` | Parameters, CT paired generation, image-only generation, TensorRT, quality check notes, MR contrast control, and GPU memory advice. | Defines command routes and useful config preview fields. | Drives `config-template`, `plan`, and command construction. | Helps the LLM ask about output size, spacing, anatomy, and contrast. | Avoid unsupported quality or clinical claims. | Need deeper adapter support for writing full config sets. |
| `configs/modality_mapping.json` | CT and MRI modality/contrast codes. | Supports deterministic contrast choices. | Bundled as adapter metadata. | Prevents free-form unsupported contrast claims. | Do not advertise unsupported contrast-enhanced MRI. | Confirm current MR-Brain model-card contrast support over time. |
| `configs/config_infer*.json` | CT paired generation parameters and GPU-size presets. | Supports CT paired config previews and future preset selection. | Provides fields for `config-template`. | Helps explain memory/output-size tradeoffs. | Wrong output size or spacing can create poor or misleading artifacts. | Add preset selection in a future adapter version. |
| `scripts/inference.py` | CT paired image/mask execution entrypoint. | Supports guarded `ct-paired` execution. | Drives planned command format. | Explains that execution can download models/data and write outputs. | Requires CUDA and downloads; gated execution only. | Need full runtime smoke test with approved GPU. |
| `scripts/diff_model_infer.py` | Image-only CT/MR/MR-brain execution entrypoint. | Supports image-only route. | Drives planned command sequence after model download. | Explains output naming and image-only behavior. | Requires CUDA and model weights; gated execution only. | Need config-writing support before custom output args are fully executable. |
| `scripts/download_model_data.py` | Hugging Face model/data asset download behavior. | Makes download approval explicit. | Drives `--confirm-downloads` gate. | Helps explain why a "run" may call the network. | Model/data terms must be reviewed before download/use. | Pin Hugging Face revisions. |
| `LICENSE` and `LICENSE.weights` | Source and weight license context. | Keeps docs careful about source versus model terms. | Adapter provenance includes source URLs and selected model. | LLM should mention license review for run requests. | Do not imply commercial or clinical permissions. | Model cards remain canonical for current terms. |

## Execution Surface

Execution mode:
Planning-first with guarded execution.

Implemented adapter:

```text
skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py
```

Read-only operations:

- `schema --json`
- `check --json`
- `setup-plan --json`
- `models --json`
- `modalities --json`
- `config-template --json`
- `plan --json`
- `verify-output --json`

Write operations:

- `config-template --output-file <path>` writes a configuration preview JSON.
- `config-template --config-dir <dir>` writes source-compatible config files
  for upstream inference/model and environment inputs.
- `run` can write generated medical image outputs through the upstream
  repository only after explicit confirmation.

Network operations:

- `run` can trigger upstream model/data downloads from Hugging Face.
- Downloads require `--confirm-downloads`.

Compute operations:

- Full inference requires a CUDA-capable NVIDIA GPU and can be long-running.
- The first implementation has read-only adapter tests plus one local WSL2
  guarded CT paired CUDA smoke test.

Deployment notes:

- Use WSL2/Linux for GPU execution when possible.
- Keep Windows support for planning, catalog search, setup guidance, and
  config previews.
- Treat source clone, dependency installation, model download, and inference as
  separate approval gates.

Error handling:

- Return structured JSON with `ok`, `error`, `suggested_fix`, `warnings`, and
  `side_effects` where applicable.
- Refuse execution unless `--confirm-execution` is present.
- Refuse download-capable execution unless `--confirm-downloads` is present.

JSON output fields:

- `ok`
- `model_variant`
- `workflow`
- `planned_commands`
- `config_preview`
- `side_effects`
- `ready_to_execute`
- `blockers`
- `warnings`
- `provenance`

## Dependencies

Runtime requirements from upstream documentation:

- Python 3.11+
- NVIDIA GPU with at least 16 GB VRAM for quick-start inference
- CUDA 11.8+ or CUDA 12.x
- PyTorch with CUDA support
- MONAI, with `monai>=1.5.0` needed for MR workflows
- `nibabel` for NIfTI output verification
- `huggingface_hub` for model-weight download
- NV-Generate-CTMR source checkout
- Accepted model terms for the selected Hugging Face model repository

SkillForge adapter dependencies:

- Python standard library for planning, model metadata, modality metadata,
  command construction, and guarded execution checks.
- Optional `nibabel` only when verifying generated NIfTI outputs.

Deployment plan:

1. Use `check --json` to identify local blockers.
2. Use `setup-plan --target wsl2-linux --json` to produce a deterministic
   install plan.
3. Clone upstream source and install upstream dependencies only after approval.
4. Download model weights only after approval and model-license review.
5. Run a small CUDA smoke test before publishing full execution examples.

## Candidate Skill Table

| Candidate skill | What it does | Why it is useful | Source evidence | Sample prompt call | Proposed CLI contract | Inputs | Outputs | Deterministic entrypoints | LLM context needed | Safety/license notes | Smoke-test source | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `nv-generate-ctmr` | Plan, configure, verify, and optionally run guarded synthetic CT/MRI generation. | Gives agents a safe interface to a high-value synthetic medical imaging repo. | README, setup/inference docs, configs, scripts, model cards. | "Create a synthetic CT image and mask, but ask before running." | `python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py check|setup-plan|models|modalities|config-template|plan|run|verify-output --json` | Model variant, workflow, contrast, output size, spacing, anatomy, source dir, output dir. | Plans, config previews, command lists, generated outputs after approval, output verification. | New adapter commands in `skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py`. | Choose variant, clarify CT paired vs image-only, explain model terms and side effects. | Research-only, no clinical claims, model downloads and GPU work require approval. | CI read-only adapter tests; future CUDA acceptance test. | `make-skill-now`. |
| `nv-generate-ctmr-training` | Plan VAE, diffusion, or ControlNet training/fine-tuning. | Training has different inputs, cost, and validation burden than inference. | `docs/training.md`, training notebooks, training scripts. | "Help me plan ControlNet fine-tuning for a new anatomy class." | Future `training-plan` and `data-check` commands. | Dataset manifest, target model, GPU count, configs, license review. | Training plan, config review, risk checklist. | Not implemented yet. | More dataset and evaluation context needed. | High compute, data, and license risk. | Deferred. | `defer`. |
| `synthetic-medical-image-evaluation` | Evaluate generated outputs with FID or quality checks. | Users need confidence and quality triage after generation. | `docs/evaluation.md`, `scripts/compute_fid_2-5d_ct.py`, quality check notes. | "Evaluate these generated CT volumes against a reference set." | Future `evaluate` command. | Generated images, reference set, metric config. | Metric report and caveats. | Not implemented yet. | Need to explain metric limitations. | Requires datasets and careful interpretation. | Deferred. | `defer`. |

## Input Contract

Required planning inputs:

- Generation goal or model variant.
- Workflow: CT paired image/mask or image-only generation.
- Output size and spacing when deviating from defaults.
- Desired output directory.

Optional inputs:

- Contrast/modality code.
- Anatomy list.
- Body region.
- Controllable anatomy size.
- Number of samples.
- Random seed.
- TensorRT request.
- Local source checkout.

Credentials or access requirements:

- Hugging Face access may be needed to download model weights and data assets.
- Model terms must be reviewed for the selected model repository.

## Output Contract

Primary outputs:

- Model/workflow plan.
- Configuration preview.
- Planned command sequence.
- Expected generated image and optional mask artifacts.
- Side effects and approval checklist.

Optional outputs:

- Written config preview when requested.
- Guarded execution result and command logs.
- NIfTI output verification summary.

## LLM Versus Python Split

LLM should:

- Interpret the user's goal.
- Select candidate model variants.
- Ask clarifying questions.
- Explain license, safety, and side effects.
- Ask for approval before execution.

Python should:

- Return stable model metadata.
- Return modality mappings.
- Check dependencies and source checkout.
- Build setup and command plans.
- Build config previews.
- Refuse unapproved execution.
- Verify NIfTI outputs.

## Smoke Test Plan

Minimal test input:
No bundled medical image input is required for read-only planning tests. Full
execution creates synthetic outputs from random seeds and upstream configs.

Expected command:

```text
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py check --json
```

Expected command:

```text
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py plan --generate-version rflow-ct --workflow ct-paired --source-dir <NV-Generate-CTMR checkout> --json
```

Expected command, after CUDA setup, model-license review, and explicit
execution/download approval:

```text
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py run --generate-version rflow-ct --workflow ct-paired --source-dir <NV-Generate-CTMR checkout> --output-dir test-output/nv-generate-ctmr --confirm-execution --confirm-downloads --json
```

Expected outputs:

- Environment and dependency check JSON.
- Planned command list.
- Config preview JSON.
- Generated NIfTI outputs only for the approved CUDA execution path.
- Output verification JSON from `verify-output`.

Skip conditions:

- No CUDA-capable NVIDIA GPU is available.
- Required upstream dependencies are not installed.
- NV-Generate-CTMR source checkout is missing.
- Model weights are missing and Hugging Face download is not approved.
- Model terms have not been reviewed for the selected model variant.
- The user does not explicitly approve execution and downloads.

How to verify output:

- Confirm generated output files exist and are non-empty.
- Load NIfTI output with `verify-output --json`.
- Record shape, dtype, affine, and source path in the verification output.
- Preserve the selected model variant, workflow, random seed, and command plan.

Smoke-test data:
Use only generated synthetic output or user-approved local test outputs. Do not
use private patient data for publication examples.

## Local WSL2 Smoke Test Result

Date:
2026-05-04

Runtime checkout:
`~/.skillforge/runtime/nv-generate-ctmr`

Source commit:
`40f5109dc77eaf01fbc5741809003f89ca3a36c7`

Completed:

- WSL2 Ubuntu availability check.
- CUDA visibility check through WSL `nvidia-smi`.
- Public source checkout clone at the pinned commit.
- Read-only SkillForge adapter planning against the WSL runtime checkout.
- WSL `python3-venv` and `python3-pip` installation.
- Runtime `.venv` creation and upstream dependency installation.
- CUDA-capable PyTorch import check: `torch 2.11.0+cu130`,
  `torch.cuda.is_available() == True`.
- Source-compatible config writing with `config-template --config-dir`.
- Guarded `run` refusal without `--confirm-execution`.
- Guarded `run` with `--confirm-execution` and `--confirm-downloads`.
- NIfTI verification for generated image and paired label output.

Accepted local CUDA smoke-test details:

- Model/workflow: `rflow-ct`, `ct-paired`.
- Config: chest, lung tumor, output size `[256, 256, 128]`, spacing
  `[1.5, 1.5, 2.0]`.
- Output image:
  `/home/marc/skillforge-smoke/nv-generate-ctmr/output/sample_20260504_134014_319438_image.nii.gz`.
- Output label:
  `/home/marc/skillforge-smoke/nv-generate-ctmr/output/sample_20260504_134014_319438_label.nii.gz`.
- Verified NIfTI shape for both outputs: `[256, 256, 128]`.
- Verified voxel spacing for both outputs: `[1.5, 1.5, 2.0]`.
- Peak GPU memory reported by upstream script: 10.36 GB.

Remaining local constraints:

- The local GPU reports 12 GB VRAM, while upstream quick-start guidance says at
  least 16 GB VRAM for the standard quick-start. Use small validated smoke
  configs on this workstation unless a larger GPU is available.
- Model downloads were performed through unauthenticated Hugging Face requests;
  set `HF_TOKEN` when higher rate limits, accepted gated terms, or auditability
  require it.

Current smoke-test conclusion:
The source checkout, CUDA visibility, adapter routing, safety gates,
source-compatible config writing, guarded execution, and output verification
are working for a small CT paired smoke test on this workstation.

## Open Questions

- Which split candidate should be implemented first after the CT paired smoke
  test: MR brain generation, image-only generation, synthetic-output
  evaluation, or training/fine-tuning?
- Should the adapter support named source config presets beyond the small CT
  paired smoke-test config?
- Which local GPU machine and sample size should be used for acceptance tests?
- How should model-card revisions be pinned for auditability?
- Should generated synthetic sample galleries be supported, and where should
  large outputs live?

## Current Readiness

Implemented:

- SkillForge `SKILL.md`
- Skill README home page
- Source-context reference
- Runtime/deployment plan
- Python adapter
- Read-only tests planned in `tests/test_skillforge.py`
- Source-compatible config writer
- Local WSL2 CT paired CUDA smoke test evidence

Not yet implemented:

- MR brain or image-only CUDA smoke tests
- Automatic model-card revision pinning
- Quality metric wrapper
- Training/fine-tuning interface
