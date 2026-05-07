---
name: mrrate-contrastive-pretraining
owner: medatasci
description: Use this skill when the user wants to plan, inspect, or operate MR-RATE contrastive vision-language pretraining. Use for VJEPA2 and VJEPA 2.1 encoder selection, multi-volume fusion modes, pooling strategies, report JSONL input contracts, native/coreg/atlas space selection, normalization, Accelerate and SLURM command planning, checkpoint resume, W&B logging, and training-side safety gates.
title: MR-RATE Contrastive Pretraining
short_description: Plan MR-RATE multi-sequence MRI and report contrastive pretraining with source-grounded encoder, fusion, data, and launch settings.
expanded_description: Use this skill for the `contrastive-pretraining` branch of MR-RATE. It covers the MRRATE model, VJEPA2 vision encoders, BiomedVLP-CXR-BERT text encoder, VL-CABS contrastive training, variable-volume MRI data loading, fusion modes, pooling strategies, normalizers, Accelerate launch, SLURM submission, checkpoint resume, and test-backed source constraints.
aliases:
  - MR-RATE pretraining
  - MR-RATE contrastive training
  - MR-RATE VJEPA2 training
  - MR-RATE VL-CABS
  - MR-RATE vision language model training
categories:
  - Medical Imaging
  - Model Training
  - Research
tags:
  - mr-rate
  - contrastive-learning
  - vjepa2
  - biomedvlp
  - accelerate
  - slurm
  - lora
tasks:
  - plan MR-RATE contrastive training
  - choose encoder fusion pooling and normalizer settings
  - prepare Accelerate or SLURM launch commands
  - explain report JSONL and MRI folder data contracts
  - review checkpoint resume and W&B logging behavior
use_when:
  - The user wants to train or fine-tune the MR-RATE contrastive model.
  - The user needs to choose among VJEPA2, VJEPA 2.1, sliding encoders, or fusion modes.
  - The user wants a source-supported launch command without starting GPU training yet.
do_not_use_when:
  - The user wants zero-shot inference from an existing checkpoint; use `mrrate-contrastive-inference`.
  - The user only needs dataset downloads; use `mrrate-dataset-access`.
  - The user wants unsupported clinical claims about model outputs.
inputs:
  - data folder containing MR-RATE study images
  - report JSONL with volume_name, valid_json, and extracted_sentences
  - encoder, fusion mode, pooling strategy, normalizer, image space, and split settings
  - optional VJEPA 2.1 checkpoint, pretrained weights, results folder, W&B settings
outputs:
  - training command plan
  - SLURM environment variable plan
  - data contract checklist
  - checkpoint and resume explanation
examples:
  - Plan a MR-RATE VJEPA2 late-fusion training run on native-space data.
  - Compare early, mid_cnn, late, and late_attn fusion modes for MR-RATE training.
  - Prepare a SLURM command using vjepa21_sliding and explain required checkpoint inputs.
related_skills:
  - mrrate-repository-guide
  - mrrate-dataset-access
  - mrrate-contrastive-inference
  - mrrate-report-preprocessing
risk_level: medium
permissions:
  - read local source files and user-provided training config metadata
  - propose commands that may download models, run GPUs, write checkpoints, and log to W&B
  - do not launch training, download model assets, or use W&B/network services without explicit approval
  - do not present research training as clinical validation
page_title: MR-RATE Contrastive Pretraining Skill - VJEPA2 MRI Vision-Language Training
meta_description: Use the MR-RATE Contrastive Pretraining Skill to plan VJEPA2 encoder selection, fusion modes, report JSONL inputs, Accelerate or SLURM training, and checkpoint resume workflows.
---

# MR-RATE Contrastive Pretraining

## What This Skill Does

Use this skill to plan MR-RATE contrastive vision-language pretraining. The
source model aligns variable numbers of brain and spine MRI volumes with
radiology report sentences using VJEPA-family image encoders and a
BiomedVLP-CXR-BERT text encoder.

## Safe Default Behavior

Default to planning and source inspection. Do not launch Accelerate, SLURM,
GPU training, model downloads, torch hub downloads, W&B logging, or checkpoint
writes unless the user approves the side effects and paths.

Keep all claims research-scoped. Do not imply that training success means
clinical validation.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Train locally or with Accelerate | Plan `accelerate launch ... scripts/run_train.py`. |
| Train on a cluster | Plan `scripts/submit_train.sh` environment variables. |
| Use VJEPA 2.1 | Require `--vjepa21_checkpoint`. |
| Use tiled depth chunks | Choose `vjepa2_sliding` or `vjepa21_sliding` with `--chunk_size`. |
| Evaluate a trained checkpoint | Route to `mrrate-contrastive-inference`. |

## Source Context

Important source files:

- `contrastive-pretraining/README.md`: architecture, installation, data
  format, training examples, arguments, inference, and tests.
- `contrastive-pretraining/scripts/run_train.py`: parser and training
  entrypoint.
- `contrastive-pretraining/scripts/submit_train.sh`: SLURM wrapper and
  environment variables.
- `contrastive-pretraining/scripts/data.py`: MRReportDataset, normalizers,
  layouts, resampling, crop/pad behavior, and split filtering.
- `contrastive-pretraining/mr_rate/mr_rate/mr_rate.py`: MRRATE model,
  pooling, and contrastive loss implementation.
- `contrastive-pretraining/vision_encoder/`: VJEPA2 and VJEPA 2.1 encoder
  variants.
- `contrastive-pretraining/tests/`: source-backed behavior tests.

Inspected source version:
`forithmus/MR-RATE` commit `e02b4ed79ff427fb3578f03242de2d9d51dc709d`
on May 5, 2026.

## Workflow

1. Confirm data layout: space-based `<study>/<space>/img/` or batch-based
   `batchXX/<study>/img/`.
2. Confirm report JSONL fields: `volume_name`, `valid_json`, and
   `extracted_sentences`.
3. Choose encoder: `vjepa2`, `vjepa21`, `vjepa2_sliding`, or
   `vjepa21_sliding`.
4. Choose fusion mode: `early`, `mid_cnn`, `late`, or `late_attn`.
5. Choose pooling strategy for `late_attn`: `simple_attn`, `cross_attn`, or
   `gated`.
6. Choose `space`, `normalizer`, optional split CSV, and output folder.
7. Plan local Accelerate or SLURM launch and explicitly state downloads,
   checkpoint writes, W&B behavior, and resume behavior.

## Boundaries

- Do not assume model weights are published; the root README says model weights
  are coming soon.
- Do not assume VJEPA 2.1 checkpoints exist locally.
- Do not run tests or training unless the user asks; test dependencies and
  model downloads may be nontrivial.
- Do not claim the model supports modalities or input layouts beyond the
  source README and data loader.

## Examples

```text
Use mrrate-contrastive-pretraining to plan a late-fusion VJEPA2 training run on native-space MR-RATE data.
```

```text
Prepare SLURM environment variables for vjepa21_sliding with chunk size 64, but do not submit.
```

```text
Explain the MR-RATE training data JSONL contract and how split filtering works.
```
