---
name: mrrate-repository-guide
owner: medatasci
description: Use this skill when the user wants to understand, navigate, or plan work across the full MR-RATE repository, including Hugging Face dataset access, MRI and metadata preprocessing, radiology report preprocessing, registration derivatives, contrastive pretraining, and zero-shot pathology inference. Use it as the umbrella router for the MR-RATE skill family and for source-grounded whole-repo runbooks.
title: MR-RATE Repository Guide
short_description: Route whole-repo MR-RATE tasks to the right source-grounded skill and explain the dataset, preprocessing, training, and inference surfaces.
expanded_description: Use this skill as the top-level MR-RATE repository interface. It summarizes the repository structure, public dataset and license context, data preprocessing branch, report preprocessing branch, registration derivatives, and contrastive vision-language model branch. It routes users to narrower skills without running source code or broadening MR-RATE's research-only claims.
aliases:
  - MR-RATE repository
  - MR-RATE whole repo
  - MR-RATE skill family
  - MR-RATE dataset and model guide
  - MR-RATE vision language workflow
categories:
  - Medical Imaging
  - Agent Workflows
  - Research
tags:
  - mr-rate
  - mri
  - radiology-reports
  - vision-language
  - dataset
  - skill-family
tasks:
  - explain the full MR-RATE repository
  - route an MR-RATE task to the right child skill
  - plan a source-grounded MR-RATE workflow
  - summarize dataset preprocessing training and inference surfaces
  - identify MR-RATE safety and license boundaries
use_when:
  - The user asks about the whole MR-RATE repository or does not know which MR-RATE skill applies.
  - The task spans multiple branches such as dataset download, preprocessing, reports, training, and inference.
  - The user wants a source-grounded map of MR-RATE before executing commands.
do_not_use_when:
  - A narrower MR-RATE child skill directly covers the task.
  - The user asks for clinical diagnosis, treatment, triage, or patient management.
  - The user wants to download gated data, run GPU jobs, or upload outputs without confirming permissions and side effects.
inputs:
  - MR-RATE checkout path or GitHub URL
  - user's workflow goal and current artifacts
  - optional dataset, preprocessing, training, inference, or report-processing constraints
outputs:
  - whole-repo orientation
  - child skill recommendation
  - source-grounded runbook or checklist
  - safety, license, data, and compute notes
examples:
  - SkillForge, use mrrate-repository-guide to map the whole MR-RATE repo into skills.
  - I have MR-RATE metadata and images. Which MR-RATE skill should I use next?
  - Explain how MR-RATE data preprocessing connects to contrastive pretraining and inference.
related_skills:
  - mrrate-dataset-access
  - mrrate-mri-preprocessing
  - mrrate-report-preprocessing
  - mrrate-registration-derivatives
  - mrrate-contrastive-pretraining
  - mrrate-contrastive-inference
risk_level: medium
permissions:
  - read local MR-RATE source files and user-provided file metadata
  - propose source-grounded commands and child-skill routing
  - do not run downloads, uploads, model training, inference, or PHI processing without explicit approval
  - write only requested planning artifacts or SkillForge-generated files
page_title: MR-RATE Repository Guide Skill - Whole-Repo Skill Family Router
meta_description: Use the MR-RATE Repository Guide Skill to navigate dataset access, MRI preprocessing, report preprocessing, registration, contrastive pretraining, and inference workflows.
---

# MR-RATE Repository Guide

## What This Skill Does

Use this umbrella skill to orient around the full MR-RATE repository and route
work to the correct MR-RATE child skill. The repository contains a data
preprocessing branch for MRI, metadata, reports, downloads, and registration,
plus a contrastive pretraining branch for a vision-language model and
zero-shot pathology inference.

## Safe Default Behavior

Default to read-only orientation and planning. Do not run MR-RATE source
scripts, download gated Hugging Face datasets, upload outputs, launch GPU jobs,
or inspect PHI-bearing files unless the user explicitly approves that scope.

MR-RATE repository content is described as non-commercial research material
under CC BY-NC-SA 4.0. Do not broaden that license claim or present model,
label, report, segmentation, or imaging outputs as clinical advice.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Understand the repo or choose a workflow | Use this skill first, then route. |
| Download or merge MR-RATE dataset repositories | Use `mrrate-dataset-access`. |
| Build the native-space dataset from raw DICOM/PACS exports | Use `mrrate-mri-preprocessing`. |
| Work with report anonymization, translation, structuring, or labels | Use `mrrate-report-preprocessing` and its child skills. |
| Produce or upload coreg/atlas derivatives | Use `mrrate-registration-derivatives`. |
| Train the MR-RATE contrastive model | Use `mrrate-contrastive-pretraining`. |
| Run zero-shot pathology scoring or AUROC evaluation | Use `mrrate-contrastive-inference`. |

## Source Context

Read the relevant README chain before making claims:

- `README.md`: repository overview, components, workflow summary, license, and
  research framing.
- `data-preprocessing/README.md`: MRI, metadata, report, registration, download,
  and upload workflows.
- `data-preprocessing/docs/dataset_guide.md`: dataset keys, batches, repository
  layouts, split tables, and data relationships.
- `data-preprocessing/docs/backfilled_reg_studies.md`: backfilled coreg/atlas
  recovery workflow.
- `data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing/README.md`:
  detailed report preprocessing stages.
- `contrastive-pretraining/README.md`: model architecture, data format,
  training, inference, and test suite.

Inspected source version:
`forithmus/MR-RATE` commit `e02b4ed79ff427fb3578f03242de2d9d51dc709d`
on May 5, 2026.

## Workflow

1. Identify whether the user is working with public dataset consumption, raw
   data preprocessing, reports, registration derivatives, training, or
   inference.
2. State the source files and README context that ground the answer.
3. Route to the narrowest MR-RATE skill that can safely handle the task.
4. Before any side effect, name the operation: download, unzip, delete zips,
   move derivative folders, upload to Hugging Face, run GPU inference, train,
   or process sensitive reports.
5. Preserve source-supported identifiers and data contracts: `patient_uid`,
   `study_uid`, `series_id`, `batch00` through `batch27`, and the four Hugging
   Face dataset repositories.
6. Keep outputs in research language. Do not convert labels, reports, model
   scores, or segmentations into clinical conclusions.

## Child Skills

- `mrrate-dataset-access`: Hugging Face downloads, batch selection, merging,
  and local dataset layout checks.
- `mrrate-mri-preprocessing`: raw DICOM/PACS to defaced native-space NIfTI,
  metadata, and upload preparation.
- `mrrate-report-preprocessing`: report anonymization, translation, structuring,
  QC, pathology labeling, and shard operations.
- `mrrate-registration-derivatives`: coreg/atlas registration, upload, and
  backfilled registration recovery.
- `mrrate-contrastive-pretraining`: VJEPA2/BiomedVLP contrastive training.
- `mrrate-contrastive-inference`: zero-shot pathology scoring and evaluation.

## Boundaries

- Do not assume the user has access to the gated Hugging Face datasets.
- Do not run or plan destructive cleanup such as `--delete-zips` without naming
  the storage tradeoff and getting approval.
- Do not assume model weights are available; the root README says model weights
  are coming soon.
- Do not imply the paper or citation is available; the root README says
  "coming soon".

## Examples

```text
Use mrrate-repository-guide to explain the whole MR-RATE repo and route me to the right skill.
```

```text
I downloaded MR-RATE native and atlas repos. What should I do next to use them for model inference?
```

```text
Build a source-grounded MR-RATE workflow from dataset download to zero-shot evaluation, but do not download anything.
```
