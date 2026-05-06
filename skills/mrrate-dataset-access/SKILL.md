---
name: mrrate-dataset-access
owner: medatasci
description: Use this skill when the user wants to download, inspect, merge, or plan local use of the MR-RATE Hugging Face dataset family. Use for gated dataset access checks, batch selection, native/coreg/atlas/nvseg repository selection, metadata and reports downloads, unzip/delete-zips tradeoffs, backfilled registration study downloads, derivative repo merging, and local dataset layout explanations.
title: MR-RATE Dataset Access
short_description: Plan and inspect MR-RATE Hugging Face dataset downloads, derivative merges, backfilled studies, and local dataset layout.
expanded_description: Use this skill for the public MR-RATE dataset consumption path. It covers the four Hugging Face repositories, 28-batch layout, metadata/reports/pathology labels/splits, download.py, merge_downloaded_repos.py, download_backfilled_reg_studies.py, and the source data guide's file relationships.
aliases:
  - MR-RATE download
  - MR-RATE Hugging Face dataset
  - MR-RATE dataset guide
  - MR-RATE merge downloaded repos
  - MR-RATE backfilled registration studies
categories:
  - Medical Imaging
  - Data Access
  - Research
tags:
  - mr-rate
  - hugging-face
  - gated-dataset
  - dataset-download
  - mri
  - batch-download
tasks:
  - plan MR-RATE dataset downloads
  - explain MR-RATE dataset repository layout
  - merge MR-RATE derivative repositories
  - download backfilled registration studies
  - check local dataset structure and join keys
use_when:
  - The user wants to download any MR-RATE dataset repository or subset of batches.
  - The user needs to choose native, coreg, atlas, nvseg, metadata, reports, labels, or splits.
  - The user wants to merge downloaded derivative repos into a local MR-RATE folder.
  - The user asks about study_uid, patient_uid, series_id, batches, or local file layout.
do_not_use_when:
  - The user wants to generate MR-RATE from raw DICOMs; use `mrrate-mri-preprocessing`.
  - The user wants to train or run inference; use the contrastive child skills after data is available.
  - The user has no access to the gated datasets and is asking for a way around access controls.
inputs:
  - desired repositories or modalities
  - batch selector such as all or 00,01
  - output base directory
  - unzip and delete-zips preference
  - Hugging Face access status
outputs:
  - safe download command plan
  - local layout explanation
  - merge command plan
  - backfilled study recovery plan
  - data contract checklist
examples:
  - Plan a MR-RATE download for native MRI, metadata, and reports for batches 00 and 01.
  - Explain how MR-RATE-coreg and MR-RATE-atlas merge into the native MR-RATE folder.
  - Check whether this local MR-RATE download has the files needed for inference.
related_skills:
  - mrrate-repository-guide
  - mrrate-registration-derivatives
  - mrrate-contrastive-pretraining
  - mrrate-contrastive-inference
  - mrrate-report-preprocessing
risk_level: medium
permissions:
  - read local dataset folder metadata and source docs
  - propose commands that may download, unzip, merge, or delete zip archives
  - do not run network downloads or delete zips without explicit approval
  - do not bypass gated dataset access requirements
page_title: MR-RATE Dataset Access Skill - Hugging Face Downloads and Local Layout
meta_description: Use the MR-RATE Dataset Access Skill to plan gated Hugging Face downloads, derivative repo merges, backfilled studies, and local dataset layout checks.
---

# MR-RATE Dataset Access

## What This Skill Does

Use this skill to plan and inspect MR-RATE dataset access. The source dataset
guide describes four gated Hugging Face repositories keyed by `study_uid`:
native-space MR-RATE, co-registered derivatives, atlas derivatives, and
NV-Segment-CTMR segmentations.

## Safe Default Behavior

Default to planning and local inspection. Do not start Hugging Face downloads,
unzip large archives, delete zips, move derivative folders, or query gated
repositories unless the user approves the side effect and confirms access.

Warn about scale. The data guide lists native data in terabytes, coreg/atlas
derivatives in additional terabytes, and nvseg derivatives in hundreds of GB.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Download metadata or reports only | Use `download.py --no-mri` with metadata/report flags. |
| Download native MRI | Use `download.py --native` for selected batches. |
| Download registered derivatives | Use `--coreg` and/or `--atlas`; consider backfilled studies. |
| Download NV-Segment-CTMR segmentations | Use `--nvseg`. |
| Merge derivatives into native layout | Use `merge_downloaded_repos.py`. |
| Recover old coreg/atlas downloads | Use `download_backfilled_reg_studies.py` with the manifest. |

## Source Context

Important source files:

- `data-preprocessing/docs/dataset_guide.md`: dataset size, keys, four-repo
  layout, batches, metadata, reports, labels, and splits.
- `data-preprocessing/README.md`: download and merge examples.
- `data-preprocessing/scripts/hf/download.py`: batch-level, resumable HF
  downloader and status table.
- `data-preprocessing/scripts/hf/merge_downloaded_repos.py`: in-place merge of
  coreg, atlas, and nvseg derivatives into `MR-RATE/`.
- `data-preprocessing/docs/backfilled_reg_studies.md` and
  `scripts/hf/backfilled_reg_study_ids.json`: backfilled coreg/atlas studies.

Inspected source version:
`forithmus/MR-RATE` commit `e02b4ed79ff427fb3578f03242de2d9d51dc709d`
on May 5, 2026.

## Workflow

1. Confirm which repositories are needed: native, coreg, atlas, nvseg,
   metadata, reports, pathology labels, or splits.
2. Confirm batch scope: `all` or a comma-separated list such as `00,01`.
3. Confirm local storage, output base, and whether zips should be kept.
4. Confirm Hugging Face authentication for gated datasets.
5. Prefer a dry status command before large downloads when the user already
   has local files.
6. For merges, confirm that derivative repos were already unzipped and that
   `MR-RATE/` exists under the same `--output-base`.
7. For backfilled studies, choose full re-run if caches and zips remain, or
   dedicated manifest download if old zips/caches were removed.

## Source Commands

Examples to adapt, not run without approval:

```text
python scripts/hf/download.py --batches 00,01 --native --metadata --reports --unzip
python scripts/hf/download.py --batches all --no-mri --no-metadata --no-reports
python scripts/hf/merge_downloaded_repos.py --coreg --atlas --nvseg --batches 00,01
python scripts/hf/download_backfilled_reg_studies.py --json-path scripts/hf/backfilled_reg_study_ids.json --output-base ./data --coreg --atlas
```

## Boundaries

- Do not bypass or minimize the gated dataset requirement.
- Do not use `--delete-zips` casually; it saves storage but can remove the
  files that make later resumability cheaper.
- Do not assume partial unzipped folders are complete; the downloader notes
  that interrupted unzip has no built-in content completeness check.
- Do not expose local dataset paths, study IDs, or reports in public artifacts
  without user approval.

## Examples

```text
Use mrrate-dataset-access to plan a metadata-and-reports-only download for MR-RATE.
```

```text
I have MR-RATE-coreg and MR-RATE-atlas unzipped. Plan the safe merge command for batches 00 and 01.
```

```text
Explain how `study_uid`, `series_id`, and `patient_uid` connect MR-RATE metadata, reports, labels, and zips.
```
