---
name: radiological-report-to-roi
owner: medatasci
description: Use this skill when the user has a medical image volume and corresponding radiological report and wants to generate a region of interest using report-derived anatomy selection, existing segmentations, or NV-Segment-CTMR outputs. Use for MR-RATE report plus MRI volume workflows, anatomy mention extraction, segmentation label selection, ROI mask extraction, ROI summary JSON, and provenance. This is for research workflows only, not diagnosis, treatment, triage, or clinical decision-making.
title: Radiological Report to ROI
short_description: Generate research ROI masks and summaries from a radiology report, image volume, segmentation mask, and selected anatomy labels.
expanded_description: Use this skill to turn a radiology report plus matching image volume into an evidence-grounded ROI workflow. The skill guides the agent through report interpretation, anatomy disambiguation, segmentation source selection, label ID resolution, deterministic ROI extraction, and provenance reporting. The MVP CLI supports local image plus local segmentation plus label IDs.
aliases:
  - radiological report to ROI
  - radiology report to ROI
  - report guided ROI
  - medical image ROI generator
  - MR-RATE ROI analysis
  - radiology report ROI
  - anatomy guided segmentation
  - NV-Segment-CTMR ROI workflow
  - MR-RATE-nvseg-ctmr segmentation
  - NIfTI ROI audit report
  - MONAI bundle medical segmentation
categories:
  - Medical Imaging
  - Research
  - Agent Workflows
tags:
  - medical-imaging
  - roi
  - radiology-report
  - segmentation
  - nifti
  - mri
  - brain-mri
  - mr-rate
  - nv-segment-ctmr
  - monai
  - medical-image-segmentation
tasks:
  - generate a medical image ROI from report context
  - extract ROI masks from segmentation labels
  - map radiology report anatomy to candidate labels
  - summarize ROI provenance
  - support MR-RATE report and MRI workflows
use_when:
  - The user has a radiology report and corresponding medical image volume and wants an ROI.
  - The user wants to use MR-RATE reports, MRI volumes, and NV-Segment-CTMR segmentations for ROI analysis.
  - The user provides a local image, segmentation mask, and label IDs for deterministic ROI extraction.
  - The user asks for an agentic pipeline that connects report evidence, anatomy labels, segmentation, and ROI outputs.
do_not_use_when:
  - The user asks for diagnosis, treatment, triage, or clinical decision-making.
  - The user wants to redistribute restricted medical data or model outputs without permission.
  - The user only wants to run generic segmentation without radiological report-to-ROI logic.
inputs:
  - local image volume path
  - local segmentation mask path
  - label IDs for the target ROI
  - optional radiology report path or anatomy phrase
  - optional output directory
outputs:
  - binary ROI mask NIfTI
  - ROI summary JSON
  - provenance JSON
  - optional HTML report with slice previews
  - optional report evidence summary
examples:
  - Use radiological-report-to-roi to extract an ROI for label 10 from this image and segmentation.
  - I have an MR-RATE MRI volume and matching report. Generate an ROI for the anatomy discussed in the report.
  - Extract labels 10 and 11 from segmentation.nii.gz as an ROI mask and return JSON provenance.
  - Check whether this machine can run the Radiological Report to ROI CLI.
related_skills:
  - nv-segment-ctmr
  - huggingface-datasets
  - skillforge
authoritative_sources:
  - "NVIDIA-Medtech NV-Segment-CTMR GitHub source: https://github.com/NVIDIA-Medtech/NV-Segment-CTMR"
  - "NV-Segment-CTMR model card on Hugging Face: https://huggingface.co/nvidia/NV-Segment-CTMR"
  - "MR-RATE dataset card: https://huggingface.co/datasets/Forithmus/MR-RATE"
  - "MR-RATE-nvseg-ctmr derivative segmentation dataset card: https://huggingface.co/datasets/Forithmus/MR-RATE-nvseg-ctmr"
  - "MONAI healthcare imaging framework: https://github.com/Project-MONAI/MONAI"
  - "NiBabel neuroimaging/NIfTI Python documentation: https://nipy.org/nibabel/"
citations:
  - "VISTA3D paper: https://arxiv.org/abs/2406.05285"
  - "NV-Segment-CTMR label dictionary: https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/blob/main/NV-Segment-CTMR/configs/label_dict.json"
  - "NV-Segment-CTMR MRI brain segmentation docs: https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR"
  - "dcm2niix DICOM to NIfTI converter: https://github.com/rordenlab/dcm2niix"
  - "HD-BET brain extraction tool: https://github.com/MIC-DKFZ/HD-BET"
  - "ANTs registration tools: https://github.com/ANTsX/ANTs"
risk_level: medium
permissions:
  - read local medical image, report, and segmentation files
  - write ROI mask and JSON summaries to the requested output directory
  - no network access for the MVP local ROI extraction command
  - future MR-RATE download or NV-Segment-CTMR execution requires explicit user confirmation
page_title: Radiological Report to ROI Skill - MR-RATE And NV-Segment-CTMR Segmentation Workflow
meta_description: Use the Radiological Report to ROI Skill to connect MR-RATE radiology reports, NV-Segment-CTMR segmentations, NIfTI image volumes, ROI masks, summary JSON, and provenance for research workflows.
---

# Radiological Report to ROI

## What This Skill Does

Use this skill when a user wants to generate a research region of interest from
a medical image volume, a matching radiology report, and a segmentation source.

The MVP executable slice is intentionally narrow:

```text
local image.nii.gz + local segmentation.nii.gz + label IDs
-> roi_mask.nii.gz + roi_summary.json + provenance.json
```

## Safe Default Behavior

- This skill is for research workflows.
- Do not present outputs as diagnosis, treatment guidance, triage, or clinical
  decision support.
- Do not attempt re-identification.
- Do not redistribute restricted medical data or derived outputs unless the
  governing terms allow it.
- Ask before downloading gated datasets, running NV-Segment-CTMR, using Docker,
  or writing large outputs.

## Workflow

1. Confirm the user's goal, input files, target anatomy, and intended output.
2. If the user has only a report/anatomy phrase, identify likely anatomy terms
   and ask for clarification when the target is ambiguous.
3. Prefer an existing segmentation mask when available.
4. Use exact label IDs from a known label map. Do not invent label IDs.
5. For local deterministic extraction, call the Python CLI in `scripts/`.
6. Return output paths, label IDs, ROI statistics, report evidence if supplied,
   and provenance.

## Agent CLI

Use the bundled Python CLI for deterministic work:

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py check --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py schema --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py prepare-mrrate-case --study-uid 22B7CXEZ6T --image-zip 22B7CXEZ6T.zip --segmentation-zip 22B7CXEZ6T_nvseg-ctmr.zip --reports-csv batch00_reports.csv --labels-csv mrrate_labels.csv --output-dir test-data/radiological-report-to-roi --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py extract-roi --image image.nii.gz --segmentation segmentation.nii.gz --labels 10,11 --output-dir output --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py report-html --manifest manifest.json --roi-summary roi_summary.json --provenance provenance.json --output-html roi_report.html --json
```

Optional fields:

```text
--anatomy "left temporal lobe"
--report report.txt
--name temporal-lobe-roi
```

## CLI Contract

`check --json` is read-only and reports whether optional dependencies such as
`numpy` and `nibabel` are importable.

`schema --json` is read-only and returns the command contract for calling
agents.

`prepare-mrrate-case --json` reads local MR-RATE image and segmentation ZIP
files plus report/label CSVs, extracts a matched image and segmentation, and
writes a manifest, report text, report JSON, and label-summary JSON.

`extract-roi --json` reads local image and segmentation files, writes an ROI
mask and JSON summaries under `--output-dir`, and returns machine-readable paths
and warnings.

`report-html --json` reads a prepared case manifest, ROI summary, provenance,
image, segmentation, and ROI mask, then writes a human-readable HTML report plus
PNG slice previews through the ROI center. It does not implement a custom 3D
viewer. If interactive review is needed, use an existing NIfTI-capable viewer
such as NiiVue or Papaya from a local HTTP server.

The HTML report should also audit anatomy mentioned in the impression. For each
detected region, show the evidence line, whether a segmentation mask exists in
the selected segmentation, label IDs and voxel counts when available, and a
separate list of mentioned regions that have no corresponding mask.

The HTML report should include the Python commands needed to reproduce the
processing pipeline: dependency check, case preparation, ROI extraction, and
report generation.

## Optional Local Integration Test Data

Use MR-RATE case `22B7CXEZ6T` as the preferred local integration test when the
user already has access to the MR-RATE files. Do not package or publish the
image, report, segmentation, or label CSV data in this repository.

Expected local files:

```text
test-data/radiological-report-to-roi/22B7CXEZ6T.zip
test-data/radiological-report-to-roi/22B7CXEZ6T_nvseg-ctmr.zip
test-data/radiological-report-to-roi/batch00_reports.csv
test-data/radiological-report-to-roi/mrrate_labels.csv
```

The known smoke-test ROI uses label `220` for `Brain-Stem` with the
NV-Segment-CTMR brain segmentation selected by `prepare-mrrate-case`.

The CLI does not download MR-RATE data and does not run NV-Segment-CTMR in the
MVP. Those are future steps that require explicit confirmation.

## LLM Responsibilities

Use the LLM for:

- Interpreting the user's anatomy request.
- Extracting anatomy mentions from report text.
- Asking clarifying questions.
- Choosing whether existing segmentation is enough or whether model execution
  is needed.
- Explaining outputs and limitations.

Do not use the LLM for:

- Exact label ID resolution without a label map.
- NIfTI mask extraction.
- Voxel count or volume calculation.
- Claiming clinical validity.

## Deterministic Responsibilities

Use Python for:

- Checking dependencies.
- Loading NIfTI image and segmentation files.
- Validating shape compatibility.
- Selecting exact segmentation label IDs.
- Writing a binary ROI mask.
- Computing voxel counts, physical volume, and bounding box.
- Writing `roi_summary.json` and `provenance.json`.

## MR-RATE And NV-Segment-CTMR Direction

For MR-RATE workflows, prefer precomputed `MR-RATE-nvseg-ctmr` segmentations
when available and appropriate. Running NV-Segment-CTMR directly should be a
later phase because it adds GPU, Conda, model weights, Docker/SynthStrip, and
brain MRI preprocessing concerns.

## Authority Sources

Ground discovery and explanations in the authoritative source chain:

- `NVIDIA-Medtech/NV-Segment-CTMR` for model capabilities, supported modes,
  label dictionary, MONAI bundle usage, MRI_BRAIN preprocessing, and model
  limitations.
- `nvidia/NV-Segment-CTMR` Hugging Face model card for research-only model
  terms, NIfTI input, CT/MR modality support, label prompts, and the VISTA3D
  reference.
- `Forithmus/MR-RATE` for MRI volume/report organization, access terms,
  privacy restrictions, pathology-label context, and data split context.
- `Forithmus/MR-RATE-nvseg-ctmr` for precomputed native-space
  NV-Segment-CTMR segmentation derivatives that support ROI extraction.
- MONAI and NiBabel docs for bundle execution and NIfTI file handling.

When improving SEO/search language, prefer these source names and their linked
terms over invented phrasing. Do not expose local report text, image data, or
case-specific medical content as public SEO copy.

## Outputs To Report

Return:

- ROI mask path.
- ROI summary JSON path.
- Provenance JSON path.
- HTML report path when `report-html` is run.
- Selected label IDs.
- Voxel count and volume when available.
- Bounding box.
- Any shape or affine warnings.
- Research-only limitation statement.
