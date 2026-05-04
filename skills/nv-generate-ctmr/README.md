# NV-Generate-CTMR

Skill ID: `nv-generate-ctmr`

Plan and guide research synthetic CT and MRI volume generation using
NVIDIA-Medtech NV-Generate-CTMR. This skill helps people and agents choose the
right MAISI model variant, preview configuration, plan commands, understand
side effects, and run only after explicit approval.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/nv-generate-ctmr

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
Medical Imaging, Research, Agent Workflows, AI ML

Collection context:
This skill is part of the medical AI codebase-to-agentic-skills workstream. It
is a reusable algorithm-interface skill for synthetic medical image generation
and pairs naturally with segmentation, ROI, dataset, and evaluation skills.

## What This Skill Does

This skill gives Codex an agentic interface to NVIDIA-Medtech
NV-Generate-CTMR, a MAISI-based repository for generating high-resolution
synthetic 3D CT and MRI medical volumes.

The current version is planning-first by default. It helps with:

- Choosing among `rflow-mr-brain`, `rflow-mr`, `rflow-ct`, and `ddpm-ct`.
- Choosing CT paired image/mask generation versus image-only generation.
- Selecting supported MR contrast or CT modality codes from the upstream
  modality mapping.
- Explaining setup, CUDA, GPU memory, MONAI, model download, and model license
  requirements.
- Creating source-grounded configuration previews and command plans.
- Writing source-compatible config files for approved smoke tests or runs.
- Refusing execution unless the user explicitly confirms both execution and
  downloads.
- Verifying generated NIfTI files when they already exist locally.

The skill should not silently download model weights, install dependencies,
launch CUDA jobs, or write generated volumes. Those actions require explicit
approval through the deterministic Python adapter.

## Why You Would Call It

Call this skill when:

- You want to generate synthetic CT or MRI image volumes for research.
- You want paired synthetic CT images and segmentation masks.
- You need to choose between `rflow-ct`, `ddpm-ct`, `rflow-mr`, and
  `rflow-mr-brain`.
- You want a safe command plan before running an expensive GPU workflow.
- You need to understand model weights, licenses, GPU memory, setup, or output
  artifacts before approving a run.
- You want an agent to verify a generated NIfTI file.

Use it to:

- Plan synthetic CT image/mask generation.
- Plan synthetic CT image-only generation.
- Plan synthetic brain MRI or non-brain MRI generation.
- Preview inference configuration values such as output size, spacing, anatomy,
  contrast, random seed, and sample count.
- Run guarded generation only after approval.
- Preserve source URLs, model terms, and provenance.

Do not use it when:

- You need diagnosis, treatment, triage, or clinical decision support.
- You need segmentation of an existing patient image. Use `nv-segment-ctmr`.
- You need report-guided ROI extraction. Use `radiological-report-to-roi`.
- You want commercial-use claims for model weights without reviewing the exact
  model license.

## Keywords

NV-Generate-CTMR, NVIDIA-Medtech, MAISI, synthetic medical imaging, synthetic
CT, synthetic MRI, 3D latent diffusion, rectified flow, ControlNet, NIfTI,
MONAI, CUDA, Hugging Face, rflow-ct, rflow-mr, rflow-mr-brain, ddpm-ct, CT
image mask pair, brain MRI synthesis, model weights, generated medical volume.

## Search Terms

Generate a synthetic CT with segmentation mask, create synthetic MRI data, make
a synthetic brain MRI, plan CT image and mask generation, choose an
NV-Generate-CTMR model, generate synthetic NIfTI images, run MAISI inference,
preview config_infer.json, create CT paired image mask data, generate T1 brain
MRI, generate FLAIR skull-stripped MRI, check GPU requirements for
NV-Generate-CTMR, verify generated NIfTI output.

## How It Works

The skill separates agent reasoning from deterministic adapter behavior.

1. The agent clarifies whether the user wants CT, MRI, brain MRI, paired CT
   masks, or image-only generation.
2. The agent chooses a source-supported model variant and explains why.
3. The adapter reports model metadata, modality mappings, setup plans,
   configuration previews, and planned commands without running upstream code.
4. The agent asks for approval before any clone, install, model download, CUDA
   run, TensorRT use, or output write.
5. If approved, the guarded `run` command executes the source-supported command
   sequence from a local checkout and records command output and provenance.
6. The `verify-output` command can inspect an existing NIfTI file for shape,
   voxel spacing, dtype, and readability when `nibabel` is available.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "NV-Generate-CTMR"
python -m skillforge info nv-generate-ctmr --json
python -m skillforge install nv-generate-ctmr --scope global
python -m skillforge evaluate nv-generate-ctmr --json
```

Promptable examples:

```text
SkillForge, use NV-Generate-CTMR to plan synthetic CT image and mask generation for a chest case.
```

```text
SkillForge, which NV-Generate-CTMR model should I use to create a synthetic T1 brain MRI?
```

```text
SkillForge, preview the configuration for rflow-ct with lung tumor anatomy and 256x256x256 output.
```

Implemented adapter commands:

```text
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py schema --json
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py check --json
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py setup-plan --target wsl2-linux --json
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py models --json
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py modalities --json
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py config-template --generate-version rflow-ct --workflow ct-paired --anatomy "lung tumor" --json
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py config-template --generate-version rflow-ct --workflow ct-paired --output-size 256,256,128 --spacing 1.5,1.5,2.0 --config-dir output/nv-generate-ctmr-configs --json
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py plan --generate-version rflow-mr-brain --contrast mri_t1 --workflow image-only --json
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py verify-output --image output/generated.nii.gz --json
```

Guarded execution:

```text
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py run --source-dir ~/.skillforge/runtime/nv-generate-ctmr --generate-version rflow-ct --workflow ct-paired --confirm-execution --confirm-downloads --json
```

The planning commands are read-only. The `config-template` command is read-only
unless `--output-file` or `--config-dir` is supplied. `--output-file` writes a
preview JSON; `--config-dir` writes source-compatible inference/model and
environment config files for `plan` and guarded `run`. The `run` command can
download model/data assets, use GPU memory, and write generated outputs, so it
requires explicit confirmation.

## Inputs And Outputs

Inputs:

- Desired modality, contrast, and generation goal.
- Model variant: `rflow-mr-brain`, `rflow-mr`, `rflow-ct`, or `ddpm-ct`.
- Workflow: `ct-paired` or `image-only`.
- Optional output size, spacing, anatomy list, body region, sample count, and
  random seed.
- Optional local NV-Generate-CTMR checkout.
- Optional output directory and config paths.
- Optional config output directory for generated source-compatible configs.

Outputs:

- Model/workflow recommendation.
- Source-grounded command plan.
- Configuration preview JSON.
- Setup, model download, and license notes.
- Expected NIfTI image and optional mask outputs.
- Guarded execution results when approved.
- NIfTI verification summary for existing outputs.

## Limitations

- This skill is for research workflows, not clinical decisions.
- Full generation requires a local CUDA-capable environment and model weights.
- The adapter does not validate generated image quality.
- `rflow-mr` model weights are described as non-commercial by the upstream
  README; review model-card terms before use.
- The upstream workflow stores many generation parameters in JSON config files,
  so custom runs should use generated or edited configs rather than relying on
  a single shell command.

## Examples

Plan CT paired image/mask generation:

```text
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py plan --generate-version rflow-ct --workflow ct-paired --body-region chest --anatomy "lung tumor" --output-size 256,256,256 --spacing 1.5,1.5,2.0 --json
```

Write source-compatible configs for a smaller local smoke test:

```text
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py config-template --generate-version rflow-ct --workflow ct-paired --body-region chest --anatomy "lung tumor" --output-size 256,256,128 --spacing 1.5,1.5,2.0 --config-dir output/nv-generate-ctmr-configs --output-dir output/nv-generate-ctmr --json
```

Plan brain MRI image generation:

```text
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py plan --generate-version rflow-mr-brain --workflow image-only --contrast mri_flair --output-dir output/mr-brain --json
```

Verify a generated NIfTI output:

```text
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py verify-output --image output/generated.nii.gz --json
```

## Help And Getting Started

Start with a planning prompt:

```text
SkillForge, use NV-Generate-CTMR to help me choose a model and plan a generation run.
```

If you already know the target:

```text
SkillForge, plan rflow-ct paired CT image and mask generation for chest anatomy. Do not run it yet.
```

If you are preparing a machine:

```text
SkillForge, show me the setup plan for NV-Generate-CTMR on WSL2/Linux.
```

## How To Call From An LLM

An LLM should:

- Ask whether the user wants CT, MRI, brain MRI, paired mask output, or image
  only.
- Ask before downloads, dependency installation, CUDA jobs, TensorRT, or writes.
- Use `models`, `modalities`, `config-template`, and `plan` before `run`.
- Explain selected model license and model-card implications.
- Preserve source URLs and provenance.

Example:

```text
Use the NV-Generate-CTMR skill to plan a synthetic T2 brain MRI generation run. Show the selected model, config preview, expected outputs, side effects, and ask before executing.
```

## How To Call From The CLI

```text
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py models --json
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py modalities --json
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py setup-plan --target wsl2-linux --json
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py plan --generate-version rflow-ct --workflow ct-paired --json
python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py run --source-dir <NV-Generate-CTMR-checkout> --generate-version rflow-ct --workflow ct-paired --confirm-execution --confirm-downloads --json
```

## Trust And Safety

Risk level:
Medium.

Permissions:

- Read local source and config files.
- Optionally write a generated config file when `--output-file` is supplied.
- Guarded execution can call Hugging Face, use CUDA, and write generated
  medical image volumes.

Data handling:

- The skill does not need patient data for synthetic generation planning.
- Do not commit generated medical volumes or user-provided local outputs.
- Record model variant, config values, model-card URLs, source commit, and run
  time in provenance.

Writes vs read-only:

- `schema`, `check`, `setup-plan`, `models`, `modalities`, `config-template`
  without `--output-file` or `--config-dir`, `plan`, and `verify-output` are
  read-only.
- `config-template --output-file` writes a config preview.
- `config-template --config-dir` writes source-compatible config files.
- `run` writes outputs and requires explicit confirmation.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Use this prompt:

```text
Please help me send feedback about the nv-generate-ctmr SkillForge skill.
```

## Contributing

Contributions should preserve the safety boundaries:

- Keep source-grounded claims tied to the upstream README, docs, scripts, model
  cards, and licenses.
- Add deterministic tests for any adapter behavior.
- Do not add NVIDIA-internal data or private knowledge.
- Do not commit model weights, generated volumes, or medical data.

## Author

Initial SkillForge interface by medatasci with Codex assistance.

## Citations

- NV-Generate-CTMR source repository:
  https://github.com/NVIDIA-Medtech/NV-Generate-CTMR
- NV-Generate-CT model card:
  https://huggingface.co/nvidia/NV-Generate-CT
- NV-Generate-MR model card:
  https://huggingface.co/nvidia/NV-Generate-MR
- NV-Generate-MR-Brain model card:
  https://huggingface.co/nvidia/NV-Generate-MR-Brain
- MAISI-v1 paper:
  https://arxiv.org/abs/2409.11169
- MAISI-v2 paper:
  https://arxiv.org/abs/2508.05772

## Related Skills

- `nv-segment-ctmr`: segment existing CT and MRI volumes.
- `radiological-report-to-roi`: generate report-guided ROI masks and reports.
- `codebase-to-agentic-skills`: convert source repositories into candidate
  SkillForge skills.
- `skill-discovery-evaluation`: evaluate SkillForge search and publication
  readiness.
