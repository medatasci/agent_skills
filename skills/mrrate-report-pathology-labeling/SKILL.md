---
name: mrrate-report-pathology-labeling
owner: medatasci
description: Use this skill when the user wants to classify MR-RATE structured brain/spine MRI reports into source-defined pathology labels or merge per-rank pathology JSON outputs. Use for the 37-pathology JSON ontology, SNOMED/RadLex mapping awareness, CoT-to-JSON cross-validation, PRESENT-label verification, deterministic seed planning, per-rank JSON output review, and labels CSV merge commands.
title: MR-RATE Report Pathology Labeling
short_description: Guide MR-RATE LLM pathology classification and label merging for structured MRI reports.
expanded_description: Use this skill for the MR-RATE pathology classification stage. It covers `classify_pathologies_parallel.py`, `merge_labels.py`, the source `pathologies.json` label set, SNOMED/RadLex map provenance, CoT reasoning, JSON extraction, verification of PRESENT labels, reproducibility metadata, and safe handling of research labels.
aliases:
  - MR-RATE pathology labels
  - MR-RATE pathology classification
  - radiology report pathology labeling
  - 37 pathology labels
categories:
  - Medical Imaging
  - Labeling
  - Research
tags:
  - mr-rate
  - pathology-labels
  - snomed-ct
  - radiology-reports
  - vllm
tasks:
  - prepare pathology classification commands
  - inspect pathology JSON definitions
  - merge per-rank label JSON files
  - explain CoT JSON verification logic
  - summarize label output provenance
use_when:
  - The user has structured MR-RATE reports and wants binary pathology labels.
  - The user wants to inspect or use the source 37-pathology ontology.
  - The user wants to merge `labels_rank_*.json` outputs into `labels.csv`.
do_not_use_when:
  - The user needs report structuring or QC before labeling.
  - The user asks for clinical diagnosis, triage, or patient-care decisions.
inputs:
  - directory containing `batch{NN}_reports.csv` files with `study_uid` and `findings`
  - `pathologies.json` from the MR-RATE source tree
  - optional `pathologies_snomed_map.json` for provenance
outputs:
  - `labels_rank_{rank}.json`
  - merged `labels.csv`
  - aggregate classification and verification stats
examples:
  - Use mrrate-report-pathology-labeling to prepare classification commands for structured reports.
  - Explain the 37 MR-RATE pathology labels and merge outputs.
  - Merge labels_rank JSON files into a study_uid-by-pathology CSV.
related_skills:
  - mrrate-report-structuring-qc
  - mrrate-report-shard-operations
  - radiological-report-to-roi
risk_level: medium
permissions:
  - read local structured reports, label JSON, and source scripts
  - propose GPU/vLLM commands and merge commands that write labels
  - do not present labels as clinical ground truth or patient-care guidance
page_title: MR-RATE Report Pathology Labeling Skill - 37 Binary MRI Report Labels
meta_description: Use the MR-RATE Report Pathology Labeling Skill to plan LLM classification of structured MRI reports into 37 source-defined pathology columns and merge label outputs.
---

# MR-RATE Report Pathology Labeling

## What This Skill Does

Use this skill for the final MR-RATE report preprocessing stage: classifying
structured `findings` text against the source-defined pathology set and merging
per-rank JSON results into a label CSV.

## Safe Default Behavior

Treat generated labels as research labels from an LLM pipeline, not clinical
truth. Ask before running vLLM, reading report findings, or writing label
outputs. Cite the source label files instead of inventing label names.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Classify structured reports | Prepare `06_pathology_classification/classify_pathologies_parallel.py`. |
| Inspect supported pathologies | Read `data/pathologies.json` and optional SNOMED map. |
| Merge per-rank outputs | Prepare `06_pathology_classification/merge_labels.py`. |

## Source-Grounded Contract

Classification source:
`06_pathology_classification/classify_pathologies_parallel.py`

- Required inputs: `--reports_dir`, `--pathologies_json`, `--output_dir`.
- Optional inputs: `--model_name`, `--batch_size`, `--seed`,
  `--max_retries`.
- Reads `batch00_reports.csv` through `batch27_reports.csv` when present.
- Requires `study_uid` and non-empty `findings`.
- Uses deterministic data hash metadata and SLURM rank/world sharding.
- Default model: `Qwen/Qwen3.5-35B-A3B`.
- Default seed: `42`.
- Writes `labels_rank_{rank}.json` with metadata, stats, CoT, and labels.
- Three-stage method: CoT reasoning for all labels, JSON extraction, then
  verification of PRESENT labels with only 1-to-0 flips allowed.

Merge source:
`06_pathology_classification/merge_labels.py`

- Reads `labels_rank_*.json`.
- Writes a CSV with `study_uid` plus one column per pathology.
- Prints aggregate stats and per-pathology prevalence.

Label sources:

- `06_pathology_classification/data/pathologies.json`
- `06_pathology_classification/data/pathologies_snomed_map.json`

The inspected `pathologies.json` contains 37 pathology keys.

## Workflow

1. Confirm structure QC has passed or that the user accepts the current
   structured reports as input.
2. Verify reports directory contains `batch{NN}_reports.csv` files with
   `study_uid` and `findings`.
3. Verify the pathology JSON path and optional SNOMED/RadLex map path.
4. Prepare the classification command and state runtime implications.
5. After per-rank JSON files exist, prepare the merge command.
6. Report label columns, aggregate stats, and caveats without quoting report
   findings unnecessarily.

## Example Commands

```text
srun python 06_pathology_classification/classify_pathologies_parallel.py --reports_dir /path/to/reports --pathologies_json 06_pathology_classification/data/pathologies.json --output_dir /path/to/output --model_name Qwen/Qwen3.5-35B-A3B --batch_size 500 --seed 42
```

```text
python 06_pathology_classification/merge_labels.py --input_dir /path/to/output --output /path/to/labels.csv
```

## Boundaries

- Do not add labels outside the source pathology JSON unless the user is
  explicitly editing the MR-RATE source.
- Do not treat SNOMED/RadLex mappings as proof of clinical validation.
- Do not use pathology labels for diagnosis, triage, treatment, or patient
  management.
