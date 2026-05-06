---
name: mrrate-registration-derivatives
owner: medatasci
description: Use this skill when the user wants to plan, inspect, or operate MR-RATE co-registration and atlas-registration derivative workflows. Use for ANTs registration command planning, partitioned registration runs, coreg and atlas output layout, registration upload zipping, backfilled registration study downloads, and safe handling of derivative MRI outputs.
title: MR-RATE Registration Derivatives
short_description: Plan and inspect MR-RATE coregistration, atlas-registration, upload, and backfilled registration derivative workflows.
expanded_description: Use this skill for the MR-RATE registration branch after native MRI preprocessing or dataset download. It covers `registration.py`, `registration/upload.py`, coreg and atlas output structures, ANTs runtime assumptions, partitioned SLURM-style execution, Hugging Face derivative uploads, and backfilled registration recovery guidance.
aliases:
  - MR-RATE registration
  - MR-RATE coreg
  - MR-RATE atlas registration
  - MR-RATE registration upload
  - MR-RATE backfilled coreg atlas
categories:
  - Medical Imaging
  - Registration
  - Data Preprocessing
tags:
  - mr-rate
  - registration
  - ants
  - coreg
  - atlas
  - mni152
tasks:
  - plan MR-RATE registration commands
  - explain coreg and atlas output structures
  - plan partitioned registration jobs
  - upload registration derivatives to Hugging Face
  - recover backfilled registration studies
use_when:
  - The user wants co-registration or atlas-registration of MR-RATE processed studies.
  - The user has native processed study folders and metadata with center modality flags.
  - The user wants to upload, download, or verify coreg/atlas derivative outputs.
do_not_use_when:
  - The user wants raw DICOM preprocessing before native outputs exist; use `mrrate-mri-preprocessing`.
  - The user only wants to download already-published derivative datasets; use `mrrate-dataset-access`.
  - The user wants model training or inference; use contrastive skills.
inputs:
  - native processed input directory
  - metadata CSV with study_uid, series_id, and is_center_modality
  - output directory
  - process and thread counts
  - optional partition index and total partitions
  - upload repo ID and zip suffix
outputs:
  - coreg and atlas registration plan
  - partitioned command plan
  - output layout checklist
  - upload and backfilled recovery plan
examples:
  - Plan a MR-RATE registration run for one batch with four processes and four ANTs threads each.
  - Explain which files should appear under coreg_img, atlas_img, and transform.
  - Prepare the safe upload command for MR-RATE-atlas zipped outputs.
related_skills:
  - mrrate-repository-guide
  - mrrate-dataset-access
  - mrrate-mri-preprocessing
  - mrrate-contrastive-pretraining
risk_level: medium
permissions:
  - read local source files and user-provided registration metadata
  - propose commands that write registered images, transforms, zips, and uploads
  - do not run ANTs registration, upload, or zip deletion without explicit approval
  - treat imaging derivatives and transforms as sensitive research data
page_title: MR-RATE Registration Derivatives Skill - Coreg, Atlas, Upload, and Backfills
meta_description: Use the MR-RATE Registration Derivatives Skill to plan ANTs co-registration, atlas-registration, derivative upload, and backfilled study recovery workflows.
---

# MR-RATE Registration Derivatives

## What This Skill Does

Use this skill to plan MR-RATE registration derivatives. The source pipeline
uses ANTs to co-register moving modalities to a T1w center modality and then
map center and moving modalities into MNI152 atlas space.

## Safe Default Behavior

Default to planning. Do not run ANTs, zip outputs, upload to Hugging Face, or
delete zips unless the user approves the local paths, compute cost, and output
behavior.

Registration writes large imaging derivatives and transform files. Treat them
as research data tied to `study_uid` and `series_id`.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Produce coreg and atlas outputs | Plan `registration.py`. |
| Split a large batch across jobs | Use `--total-partitions` and `--partition-index`. |
| Upload completed derivatives | Plan `registration/upload.py`. |
| Recover previously missing studies | Use backfilled registration docs and downloader. |
| Just consume downloaded derivatives | Use `mrrate-dataset-access`. |

## Source Context

Important source files:

- `data-preprocessing/README.md`: registration overview and example commands.
- `data-preprocessing/src/mr_rate_preprocessing/registration/registration.py`:
  ANTs coreg and atlas workflow with resume/cleanup behavior.
- `data-preprocessing/src/mr_rate_preprocessing/registration/upload.py`: zips
  derivative study folders and uploads them to Hugging Face.
- `data-preprocessing/docs/backfilled_reg_studies.md`: recovery guidance for
  coreg/atlas studies added after the original upload.
- `data-preprocessing/scripts/hf/download_backfilled_reg_studies.py`: manifest
  based download helper.

Inspected source version:
`forithmus/MR-RATE` commit `e02b4ed79ff427fb3578f03242de2d9d51dc709d`
on May 5, 2026.

## Workflow

1. Confirm native processed input layout and metadata CSV.
2. Verify the metadata has exactly one `is_center_modality=True` row per study.
3. Explain the output families: `MR-RATE-coreg_<batch>` and
   `MR-RATE-atlas_<batch>`.
4. Plan `registration.py` with `--input-dir`, `--metadata-csv`,
   `--output-dir`, `--num-processes`, and `--threads-per-process`.
5. If the run is large, plan independent partitions.
6. For upload, plan `upload.py` separately for coreg and atlas with explicit
   `--zip-suffix`, `--repo-id`, worker counts, and optional Xet settings.
7. For old local downloads, decide whether to re-run `download.py` or use the
   backfilled manifest downloader.

## Boundaries

- Do not assume ANTsPy, atlas resources, CPU capacity, or Hugging Face
  credentials are installed.
- Do not hide that incomplete registration outputs may be cleaned and
  reprocessed by the source script.
- Do not delete zips with `--delete-zips` without a direct user request.
- Do not treat coreg/atlas outputs as validated biomarkers or clinical results.

## Examples

```text
Use mrrate-registration-derivatives to plan coreg and atlas registration for batch00.
```

```text
Split this MR-RATE registration batch into eight independent partition commands.
```

```text
Explain how to recover the backfilled MR-RATE coreg and atlas studies without redownloading everything.
```
