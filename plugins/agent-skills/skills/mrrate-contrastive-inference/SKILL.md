---
name: mrrate-contrastive-inference
owner: medatasci
description: Use this skill when the user wants to plan, inspect, or operate MR-RATE zero-shot pathology inference and evaluation from a trained contrastive checkpoint. Use for pathology prompt files, labels CSV contracts, split filtering, native/coreg/atlas space selection, normalizer matching, results folder outputs, predicted_scores.npz, scores.json, labels.npz, AUROC XLSX/CSV, and research-only interpretation.
title: MR-RATE Contrastive Inference
short_description: Plan MR-RATE zero-shot pathology scoring and AUROC evaluation from trained contrastive checkpoints.
expanded_description: Use this skill for the MR-RATE contrastive inference branch. It covers `scripts/inference.py`, `scripts/eval.py`, pathology positive/negative prompt JSON files, labels CSVs, split filtering, model checkpoint loading, result artifacts, and the boundary between research scores and clinical interpretation.
aliases:
  - MR-RATE inference
  - MR-RATE zero-shot pathology
  - MR-RATE AUROC evaluation
  - MR-RATE predicted scores
  - MR-RATE contrastive evaluation
categories:
  - Medical Imaging
  - Model Inference
  - Evaluation
tags:
  - mr-rate
  - zero-shot
  - pathology
  - auroc
  - inference
  - contrastive-learning
tasks:
  - plan MR-RATE zero-shot inference
  - explain pathology prompt and labels file formats
  - prepare source-grounded inference commands
  - interpret output artifacts at a research level
  - plan AUROC evaluation from labels
use_when:
  - The user has a trained MR-RATE checkpoint and wants pathology scores.
  - The user wants to evaluate predictions against MR-RATE pathology labels.
  - The user needs to understand `predicted_scores.npz`, `scores.json`, `labels.npz`, or AUROC outputs.
do_not_use_when:
  - The user wants to train a checkpoint; use `mrrate-contrastive-pretraining`.
  - The user wants LLM-derived pathology labels from reports; use `mrrate-report-pathology-labeling`.
  - The user wants clinical diagnosis or patient-care interpretation.
inputs:
  - checkpoint weights path
  - data folder
  - report JSONL file
  - pathology prompts JSON
  - labels CSV with study_uid and pathology columns
  - optional splits CSV, split, image space, normalizer, fusion mode, and pooling strategy
outputs:
  - inference command plan
  - output artifact checklist
  - AUROC evaluation explanation
  - research-scope interpretation notes
examples:
  - Plan MR-RATE zero-shot inference for the test split and write outputs under inference_results.
  - Explain the required labels CSV columns for MR-RATE contrastive evaluation.
  - Compare scores.json and predicted_scores.npz outputs from MR-RATE inference.
related_skills:
  - mrrate-repository-guide
  - mrrate-contrastive-pretraining
  - mrrate-dataset-access
  - mrrate-report-pathology-labeling
risk_level: medium
permissions:
  - read local source files and user-provided inference metadata
  - propose commands that may run GPU inference and write score/evaluation outputs
  - do not run inference, load private checkpoints, or process local medical data without explicit approval
  - do not present predictions as clinical truth
page_title: MR-RATE Contrastive Inference Skill - Zero-Shot Pathology Scores and AUROC
meta_description: Use the MR-RATE Contrastive Inference Skill to plan checkpoint-based zero-shot pathology scoring, labels-based evaluation, and research output interpretation.
---

# MR-RATE Contrastive Inference

## What This Skill Does

Use this skill to plan MR-RATE zero-shot pathology inference and evaluation.
The source inference script compares positive and negative text prompts for
each pathology and writes per-subject scores plus AUROC outputs when labels
are provided.

## Safe Default Behavior

Default to command planning and artifact explanation. Do not run GPU inference,
load local checkpoints, or process local medical imaging data unless the user
approves the paths, compute target, and output directory.

Treat outputs as research scores, not diagnoses. A positive score or AUROC
table is not clinical truth.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Run pathology scoring | Plan `python scripts/inference.py ...`. |
| Explain pathology prompts | Inspect `data/pathologies.json`. |
| Evaluate against labels | Ensure labels CSV has `study_uid` and pathology columns. |
| Train or choose encoders | Route to `mrrate-contrastive-pretraining`. |
| Generate report-derived labels | Route to `mrrate-report-pathology-labeling`. |

## Source Context

Important source files:

- `contrastive-pretraining/README.md`: inference usage, pathologies file
  formats, labels file format, arguments, and outputs.
- `contrastive-pretraining/scripts/inference.py`: zero-shot scoring engine and
  CLI arguments.
- `contrastive-pretraining/scripts/eval.py`: AUROC and evaluation helpers.
- `contrastive-pretraining/scripts/data_inference.py`: inference dataset
  loading and optional label handling.
- `contrastive-pretraining/data/pathologies.json`: 37 pathology prompt pairs.
- `data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing/06_pathology_classification/`:
  source of report-derived labels used by the dataset.

Inspected source version:
`forithmus/MR-RATE` commit `e02b4ed79ff427fb3578f03242de2d9d51dc709d`
on May 5, 2026.

## Workflow

1. Confirm checkpoint path and that it matches the planned fusion mode,
   pooling strategy, image space, and normalizer.
2. Confirm data folder layout and report JSONL file.
3. Confirm pathology prompt JSON format. Source supports
   `{"pathologies": {"Name": {"positive": "...", "negative": "..."}}}` and a
   legacy list of names.
4. Confirm labels CSV when evaluation is requested. It must include `study_uid`
   and columns matching pathology names.
5. Plan inference with explicit `--results_folder`.
6. Explain expected outputs: `predicted_scores.npz`, `subject_ids.txt`,
   `scores.json`, optional `labels.npz`, and optional `aurocs.xlsx` or
   `aurocs.csv`.

## Boundaries

- The inspected `inference.py` initializes `VJEPA2Encoder`; do not claim the
  CLI accepts every training encoder variant unless source is updated.
- Do not assume model weights are available; the root README says model weights
  are coming soon.
- Do not expose scores for identifiable studies in public artifacts.
- Do not translate pathology scores into patient-care recommendations.

## Examples

```text
Use mrrate-contrastive-inference to plan zero-shot scoring for the MR-RATE test split.
```

```text
Explain the MR-RATE `scores.json`, `predicted_scores.npz`, and `aurocs.xlsx` outputs.
```

```text
Check whether this labels CSV is shaped correctly for MR-RATE inference evaluation.
```
