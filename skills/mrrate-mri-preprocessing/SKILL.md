---
name: mrrate-mri-preprocessing
owner: medatasci
description: Use this skill when the user wants to plan, inspect, or operate the MR-RATE MRI and metadata preprocessing pipeline from raw DICOM folders and PACS metadata through NIfTI conversion, metadata filtering, series classification, modality filtering, brain segmentation, defacing, zipping, metadata preparation, and Hugging Face upload handoff.
title: MR-RATE MRI Preprocessing
short_description: Plan and inspect the MR-RATE raw MRI and metadata preprocessing pipeline from DICOM/PACS exports to defaced native-space dataset outputs.
expanded_description: Use this skill for the MR-RATE data-preprocessing MRI branch. It covers the YAML-driven `run_mri_preprocessing.py` and `run_mri_upload.py` workflows, dcm2niix conversion, PACS metadata cleaning, rule-based modality classification, modality acceptance criteria, HD-BET brain segmentation, Quickshear defacing, study zipping, anonymized metadata preparation, and Hugging Face upload gates.
aliases:
  - MR-RATE MRI preprocessing
  - MR-RATE DICOM to NIfTI
  - MR-RATE metadata filtering
  - MR-RATE defacing
  - MR-RATE upload pipeline
categories:
  - Medical Imaging
  - Data Preprocessing
  - Privacy
tags:
  - mr-rate
  - dicom
  - nifti
  - metadata
  - defacing
  - hdbet
  - quickshear
tasks:
  - plan MR-RATE MRI preprocessing
  - prepare batch YAML configuration
  - explain DICOM to NIfTI conversion and metadata filtering
  - route modality classification and filtering issues
  - plan brain segmentation defacing and upload handoff
use_when:
  - The user wants to run or understand the MR-RATE raw MRI preprocessing pipeline.
  - The user has raw DICOM folder paths, PACS metadata CSVs, mapping spreadsheets, or batch YAML configs.
  - The user wants a source-grounded command sequence for steps 1 through 7.
do_not_use_when:
  - The user only wants to download already-preprocessed MR-RATE data; use `mrrate-dataset-access`.
  - The user wants report anonymization or pathology labels; use `mrrate-report-preprocessing`.
  - The user wants registration derivatives after native preprocessing; use `mrrate-registration-derivatives`.
inputs:
  - batch YAML config path
  - DICOM folder path CSV with FolderPath column
  - PACS metadata CSV
  - patient and study-date mapping files
  - output directories, GPU device, and Hugging Face repo settings
outputs:
  - preprocessing command plan
  - config checklist
  - expected intermediate and processed file layout
  - upload handoff plan and safety gates
examples:
  - Build a safe MR-RATE batch00 preprocessing plan from raw DICOM folders to defaced NIfTI outputs.
  - Review this mri_batch00.yaml for missing MR-RATE preprocessing paths.
  - Explain which source step creates the modalities_to_process JSON and metadata CSV.
related_skills:
  - mrrate-repository-guide
  - mrrate-dataset-access
  - mrrate-registration-derivatives
  - mrrate-report-preprocessing
risk_level: medium
permissions:
  - read local source files and user-provided config or schema metadata
  - propose commands that write NIfTI, masks, metadata, zips, logs, and uploads
  - do not run DICOM processing, defacing, uploads, or GPU jobs without explicit approval
  - treat raw DICOM, PACS metadata, mapping spreadsheets, and intermediate outputs as sensitive
page_title: MR-RATE MRI Preprocessing Skill - DICOM, Metadata, Defacing, and Upload Planning
meta_description: Use the MR-RATE MRI Preprocessing Skill to plan DICOM to NIfTI conversion, PACS metadata filtering, modality filtering, HD-BET defacing, zipping, and metadata upload workflows.
---

# MR-RATE MRI Preprocessing

## What This Skill Does

Use this skill to reason about the MR-RATE MRI and metadata preprocessing
pipeline. The source pipeline converts raw DICOM exports and PACS metadata into
cleaned, defaced, native-space NIfTI study folders and associated metadata
ready for Hugging Face upload.

## Safe Default Behavior

Default to config review and command planning. Do not run preprocessing until
the user confirms local data permissions, output locations, compute target,
and whether Hugging Face uploads are allowed.

Treat raw DICOMs, PACS metadata, accession numbers, mapping spreadsheets, and
intermediate outputs as sensitive. Defacing is a privacy step, not proof that
all downstream artifacts are public-safe.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Run steps 1 through 5 | Plan `python run/run_mri_preprocessing.py --config ...`. |
| Run zip and metadata upload | Plan `python run/run_mri_upload.py --config ...`. |
| Debug metadata columns | Inspect `config_metadata_columns.json` and `pacs_metadata_filtering.py`. |
| Debug modality acceptance | Inspect `config_mri_preprocessing.py` and `modality_filtering.py`. |
| Avoid upload | Set source-supported skip-upload flags in the YAML. |

## Source Context

Important source files:

- `data-preprocessing/README.md`: seven-step MRI and metadata preprocessing
  narrative and example commands.
- `data-preprocessing/run/configs/mri_batch00.yaml`: source batch config shape.
- `data-preprocessing/run/run_mri_preprocessing.py`: orchestrates steps 1 to 5.
- `data-preprocessing/run/run_mri_upload.py`: orchestrates steps 6 and 7.
- `mri_preprocessing/dcm2nii.py`: reads `FolderPath`, extracts
  `AccessionNumber`, and calls `dcm2niix`.
- `pacs_metadata_filtering.py`, `series_classification.py`,
  `modality_filtering.py`: metadata cleaning, classification, and acceptance.
- `brain_segmentation_and_defacing.py`: HD-BET plus Quickshear workflow.
- `zip_and_upload.py` and `prepare_metadata.py`: zips studies and prepares
  anonymized metadata for Hugging Face.

Inspected source version:
`forithmus/MR-RATE` commit `e02b4ed79ff427fb3578f03242de2d9d51dc709d`
on May 5, 2026.

## Workflow

1. Confirm the user is operating from `data-preprocessing/`.
2. Read the batch YAML and identify the configured batch ID, log directory,
   raw paths, interim paths, processed paths, mapping files, upload repo, and
   GPU device.
3. Check source contract for each stage before proposing a command.
4. For preprocessing steps 1 to 5, explain expected outputs: raw NIfTI folders,
   filtered metadata, classified metadata, modalities JSON, modality metadata,
   defaced images, brain masks, and defacing masks.
5. For upload steps 6 to 7, explain zip output, metadata CSV output, upload
   settings, Xet option, and skip-upload/delete behavior.
6. State side effects before execution: subprocesses, GPU use, DICOM reads,
   file writes, zips, uploads, and logs.

## Boundaries

- Do not assume `dcm2niix`, CUDA, HD-BET, Quickshear, or Hugging Face
  credentials are installed.
- Do not claim defacing or metadata cleaning is sufficient for public release
  without user review.
- Do not invent metadata columns; use `config_metadata_columns.json` and the
  source script contracts.
- Do not delete zips or local processed data unless explicitly requested.

## Examples

```text
Use mrrate-mri-preprocessing to review this batch YAML before I run native preprocessing.
```

```text
Plan the MR-RATE commands from DICOM folder CSV to defaced NIfTI outputs, but do not run them.
```

```text
Explain which MR-RATE preprocessing step creates `batch00_modalities_to_process.json`.
```
