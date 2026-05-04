---
name: nv-generate-ctmr
owner: medatasci
description: >
  Plan and guide research-only NVIDIA-Medtech NV-Generate-CTMR synthetic CT and
  MRI generation workflows, including model variant selection, CT image/mask
  pair planning, MR and MR brain image-only planning, setup guidance,
  configuration previews, output verification, and explicitly approved guarded
  execution. Do not use for diagnosis, treatment, triage, or clinical
  decision-making.
---

# NV-Generate-CTMR

## What This Skill Does

Use this skill when a user asks for research-only synthetic CT or MRI volume
generation using NVIDIA-Medtech NV-Generate-CTMR.

This skill helps an agent turn high-level user requests such as "generate a
synthetic CT with a paired mask" or "create a synthetic T1 brain MRI" into a
safe, reproducible workflow grounded in the upstream NV-Generate-CTMR README,
docs, scripts, configs, model cards, model-weight terms, and explicit user
approval for any execution.

## Safe Default Behavior

Default to planning, setup guidance, configuration previews, and output
inspection.

Do not clone source, install dependencies, download model weights, launch CUDA
jobs, run inference, or write generated medical volumes unless the user has
explicitly approved the side effects. The bundled adapter refuses execution
unless `--confirm-execution` is present; because upstream commands can download
weights and data, guarded execution also requires `--confirm-downloads`.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Generate synthetic CT with paired segmentation mask | Use `rflow-ct` and the `ct-paired` planning path. |
| Generate CT image only | Use `rflow-ct` or legacy `ddpm-ct` with the `image-only` planning path. |
| Generate brain MRI | Use `rflow-mr-brain` with a supported brain MRI contrast. |
| Generate non-brain MRI | Use `rflow-mr`; warn that model weights are non-commercial and brain MRI is better served by `rflow-mr-brain`. |
| Prepare runtime | Use the read-only `setup-plan` adapter command before clone, install, model download, or GPU execution. |
| Prepare executable configs | Use `config-template --config-dir` to write source-compatible config files before a guarded run. |
| Check a generated volume | Use `verify-output` on the generated NIfTI file. |

## SkillForge Discovery Metadata

This section is written as Markdown so people can read it, while SkillForge can
still extract the same discovery fields for catalogs, search, and generated
pages.

### Title

NV-Generate-CTMR

### Short Description

Plan and guide research synthetic CT and MRI generation workflows with
NVIDIA-Medtech NV-Generate-CTMR, MAISI models, model variants, config previews,
and guarded execution.

### Expanded Description

Use this skill to help an agent turn user intent into a safe, source-grounded
NV-Generate-CTMR workflow. The skill helps choose among `rflow-mr-brain`,
`rflow-mr`, `rflow-ct`, and `ddpm-ct`; distinguish CT image/mask pair
generation from image-only generation; select supported MRI contrast codes;
preview and write source-compatible inference configuration; explain setup requirements,
GPU memory expectations, model download behavior, model-weight licenses,
output artifacts, and provenance; and verify generated NIfTI volumes. The
bundled Python adapter implements `schema`, `check`, `setup-plan`, `models`,
`modalities`, `config-template`, `plan`, guarded `run`, and `verify-output`.
Direct execution requires explicit approval and local prerequisites.

### Aliases

- NV-Generate-CTMR
- nv-generate-ctmr
- NVIDIA-Medtech NV-Generate-CTMR
- MAISI synthetic imaging
- synthetic CT generation
- synthetic MRI generation
- CT image mask generation
- CT paired image mask synthesis
- MR brain generation
- rflow-ct
- rflow-mr
- rflow-mr-brain
- ddpm-ct

### Categories

- Medical Imaging
- Research
- Agent Workflows
- AI ML

### Tags

- nv-generate-ctmr
- synthetic-medical-imaging
- synthetic-ct
- synthetic-mri
- maisi
- latent-diffusion
- rectified-flow
- controlnet
- nifti
- monai
- cuda
- hugging-face

### Tasks

- plan an NV-Generate-CTMR synthetic image generation run
- choose rflow-mr-brain rflow-mr rflow-ct or ddpm-ct
- plan CT image and segmentation mask pair generation
- plan CT image-only generation
- plan MR brain image-only generation
- plan MR contrast-specific image generation
- preview inference or model configuration values
- explain setup GPU CUDA MONAI and model weight requirements
- verify a generated NIfTI image volume
- run guarded generation after explicit approval

### Use When

- The user wants to generate synthetic CT or MRI medical image volumes.
- The user asks which NV-Generate-CTMR model variant fits a generation task.
- The user wants paired CT image and segmentation masks.
- The user wants synthetic T1w, T2w, FLAIR, SWI, or skull-stripped brain MRI.
- The user wants a reproducible command plan before running an expensive GPU job.
- The user asks what setup, model weights, licenses, or GPU memory are needed.
- The user wants to inspect whether a generated NIfTI output is readable.

### Do Not Use When

- The user asks for diagnosis, treatment guidance, triage, or clinical decision-making.
- The user wants to segment an existing patient image; prefer `nv-segment-ctmr`.
- The user wants a report-guided ROI workflow; prefer `radiological-report-to-roi`.
- The user wants to run unreviewed downloads, CUDA jobs, or file writes without explicit approval.
- The user wants unsupported modalities or contrast-enhanced MRI claims not documented by the upstream source.

### Inputs

- generation goal in user language
- model variant or desired modality and contrast
- workflow type: CT paired image/mask or image-only generation
- optional output size, voxel spacing, body region, anatomy list, and number of samples
- optional local NV-Generate-CTMR source checkout
- optional output directory, custom config paths, or generated config directory

### Outputs

- source-grounded generation plan
- selected model variant and workflow route
- command plan, configuration preview, and optional source-compatible config files
- setup and model-download approval notes
- expected generated NIfTI image and optional mask outputs
- guarded execution result and provenance when run is approved
- output verification summary for existing NIfTI files

### Examples

- Use NV-Generate-CTMR to plan synthetic CT image and mask generation for a chest case, but ask before running anything.
- Create source-compatible config files for one `rflow-ct` sample with lung tumor anatomy and 256x256x128 output size.
- Which NV-Generate-CTMR model should I use for synthetic T1 brain MRI?
- Plan a guarded `rflow-mr-brain` generation run for FLAIR skull-stripped MRI and explain the model license.
- Verify this generated NIfTI file and tell me its shape and voxel spacing.

### Related Skills

- nv-segment-ctmr
- radiological-report-to-roi
- codebase-to-agentic-skills
- skill-discovery-evaluation
- huggingface-datasets

### Authoritative Sources

- NV-Generate-CTMR GitHub source: https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/tree/main
- NV-Generate-CT model card: https://huggingface.co/nvidia/NV-Generate-CT
- NV-Generate-MR model card: https://huggingface.co/nvidia/NV-Generate-MR
- NV-Generate-MR-Brain model card: https://huggingface.co/nvidia/NV-Generate-MR-Brain
- MAISI-v1 paper: https://arxiv.org/abs/2409.11169
- MAISI-v2 paper: https://arxiv.org/abs/2508.05772
- MONAI project: https://monai.io/

### Citations

- Guo et al. MAISI: Medical AI for Synthetic Imaging. WACV 2025.
- Zhao et al. MAISI-v2: Accelerated 3D high-resolution medical image synthesis with rectified flow and region-specific contrastive loss. AAAI 2026.
- NVIDIA-Medtech NV-Generate-CTMR repository and model cards.

### Risk Level

medium

### Permissions

- read local source documentation, configs, and user-provided output paths
- produce command plans, configuration previews, source-compatible config files, setup guidance, and output verification
- do not clone source, install packages, download weights, call Hugging Face, launch CUDA, or write generated medical volumes without explicit user approval
- guarded execution may download model/data assets, use GPU memory, and write generated NIfTI files, logs, and provenance to user-selected locations

### Page Title

NV-Generate-CTMR Skill - Agentic Synthetic CT And MRI Medical Image Generation Planning

### Meta Description

Use the NV-Generate-CTMR Skill to plan research synthetic CT and MRI volume
generation with NVIDIA-Medtech NV-Generate-CTMR, MAISI, `rflow-ct`,
`rflow-mr`, `rflow-mr-brain`, `ddpm-ct`, configuration previews, and guarded
execution.

## Workflow

1. Clarify the user's goal, modality, desired contrast, CT mask requirement,
   output size, spacing, sample count, and output location.
2. Route the request to one of the source-supported model variants:
   - `rflow-ct` for CT image/mask pair generation or CT image-only generation
   - `ddpm-ct` for legacy CT generation
   - `rflow-mr-brain` for brain MRI image-only generation
   - `rflow-mr` for other MRI image-only generation
3. Confirm boundaries before any execution: source checkout, dependency
   install, model terms, Hugging Face downloads, CUDA/GPU use, output writes,
   and public-safe handling of generated artifacts.
4. Use the deterministic adapter commands for schema, setup planning, model
   selection, modality lookup, configuration preview, source-compatible config
   writing, command planning, guarded execution, and output verification.
5. Return assumptions, selected variant, planned commands, config changes,
   expected outputs, side effects, source URLs, and next steps.

## Method

This skill separates LLM judgment from deterministic adapter work.

The LLM chooses the appropriate workflow, asks clarifying questions, explains
source limits, and keeps the user informed about risk and side effects. The
Python adapter handles stable model metadata, modality mappings, source
checkout checks, setup plans, configuration preview JSON, source-compatible
config writing, command construction, execution refusal unless confirmed, and
NIfTI output verification.

## Inputs

- User generation request, modality, contrast, and CT mask requirement.
- Optional `--generate-version`, `--workflow`, `--contrast`, `--output-size`,
  `--spacing`, `--body-region`, `--anatomy`, `--samples`, and
  `--random-seed`.
- Optional local source checkout, custom config paths, and `--config-dir` for
  generated source-compatible configs.

## Outputs

- Source-grounded model/workflow route.
- Configuration preview, optional generated config files, and planned upstream
  command sequence.
- Setup and license warnings.
- Generated image/mask output expectations.
- Guarded execution logs and provenance when approved.
- NIfTI output inspection summary.

## Boundaries

- Do not claim clinical validity, diagnosis support, treatment support, or
  regulatory approval.
- Do not imply that generated synthetic images can be used without reviewing
  model, data, and downstream validation requirements.
- Do not imply commercial rights for model weights whose terms are
  non-commercial.
- Do not execute source clone, dependency install, Hugging Face download, CUDA,
  TensorRT, or output writes unless the user approves.
- Keep public-safe content public-safe. Do not add NVIDIA-internal data,
  private process knowledge, secrets, or privileged automation.

## Runtime And Deployment Notes

This skill wraps an executable upstream repository but defaults to read-only
planning.

- Install location: local runtime checkout such as
  `~/.skillforge/runtime/nv-generate-ctmr`.
- OS/runtime target: Linux or WSL2/Linux with NVIDIA CUDA is the practical
  execution target; Windows and macOS are planning-first unless the user has a
  verified CUDA-capable setup.
- Dependency setup: Python 3.11+, CUDA-enabled PyTorch, MONAI, nibabel,
  huggingface_hub, and other upstream requirements.
- Model/data download policy: model weights and CT mask assets are downloaded
  only after explicit approval.
- License review: source code is Apache 2.0; model weights have separate
  NVIDIA Open Model or NVIDIA Non-Commercial terms depending on the variant.
- Environment checks: run `check` and `setup-plan` before execution.
- Smoke-test data: use generated or user-approved local test outputs; do not
  commit medical data or large generated volumes.
- Rollback/cleanup notes: remove runtime checkout, cached model/data files,
  generated outputs, and temporary configs when no longer needed.

## Examples

```text
SkillForge, use NV-Generate-CTMR to plan a synthetic CT image and mask generation run for chest anatomy.
```

```text
SkillForge, create a configuration preview for synthetic T1 brain MRI with rflow-mr-brain, but do not run it yet.
```

```text
SkillForge, write source-compatible configs for a small rflow-ct paired CT smoke test, then show the plan before running.
```
