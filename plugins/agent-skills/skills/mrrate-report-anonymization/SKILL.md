---
name: mrrate-report-anonymization
owner: medatasci
description: Use this skill when the user wants to anonymize MR-RATE Turkish radiology reports or verify anonymization quality with the reports_preprocessing source scripts. Use for raw report CSV column checks, Qwen/vLLM anonymization command planning, token mapping outputs, PHI leakage validation, SLURM shard behavior, resume behavior, and safe handling of potentially identifiable report text.
title: MR-RATE Report Anonymization
short_description: Guide MR-RATE Turkish report anonymization and anonymization QC with source-supported commands and safety gates.
expanded_description: Use this skill for the MR-RATE reports_preprocessing anonymization stage. It helps prepare and explain the `anonymize_reports_parallel.py` and `validate_anonymization_parallel.py` workflows, required columns, per-rank outputs, token mapping files, validation outputs, and merge handoff without exposing PHI or running expensive vLLM jobs unless approved.
aliases:
  - MR-RATE anonymization
  - Turkish report anonymization
  - anonymize MR-RATE reports
  - anonymization QC
categories:
  - Medical Imaging
  - Privacy
  - Data Preprocessing
tags:
  - mr-rate
  - anonymization
  - phi
  - radiology-reports
  - vllm
tasks:
  - prepare MR-RATE anonymization commands
  - validate anonymized report outputs
  - explain token mapping files
  - merge anonymization shards
  - review PHI leakage gates
use_when:
  - The user has raw Turkish MR-RATE report CSVs and wants anonymized report outputs.
  - The user wants to run or inspect anonymization validation shards.
  - The user asks about required columns, output filenames, or token mapping behavior.
do_not_use_when:
  - The user asks for translation, structuring, or pathology labeling after anonymization is complete.
  - The user wants to publish raw reports, token mappings, or PHI-bearing examples.
inputs:
  - raw Turkish report CSV with `AccessionNo` and `RaporText`
  - optional `UID`, `Batch`, `KabulTarihi`, and `TetkikAdi` columns
  - output directory for per-rank anonymization or validation CSVs
outputs:
  - `anonymized_rank_{RANK}.csv`
  - `mapping_rank_{RANK}.csv`
  - `validation_rank_{RANK}.csv`
examples:
  - Use mrrate-report-anonymization to prepare the anonymization command for this raw reports CSV.
  - Check what columns anonymize_reports_parallel.py requires.
  - Plan anonymization QC and shard merge, but do not run vLLM.
related_skills:
  - mrrate-report-preprocessing
  - mrrate-report-shard-operations
  - mrrate-report-translation-qc
risk_level: medium
permissions:
  - read local report CSV schemas and source scripts
  - propose commands that write anonymized and mapping CSVs
  - do not run model jobs or inspect raw PHI content without explicit approval
page_title: MR-RATE Report Anonymization Skill - PHI Tokenization and QC
meta_description: Use the MR-RATE Report Anonymization Skill to plan anonymization, token mapping, PHI validation, and shard merging for Turkish radiology reports.
---

# MR-RATE Report Anonymization

## What This Skill Does

Use this skill for the first MR-RATE report preprocessing stage: replacing
names, dates, hospitals, radiologists, accession numbers, and related sensitive
entities with deterministic tokens, then validating that no obvious PHI remains.

## Safe Default Behavior

Treat all raw reports, token mappings, and validation failures as sensitive.
Do not quote raw report text or token mappings into public artifacts. Ask before
running vLLM, using GPUs, reading PHI-bearing rows, or writing outputs.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Anonymize raw reports | Prepare `01_anonymization/anonymize_reports_parallel.py`. |
| Check PHI leakage | Prepare `utils/validate_anonymization_parallel.py`. |
| Combine per-rank CSVs | Use `mrrate-report-shard-operations`. |

## Source-Grounded Contract

Anonymization source:
`01_anonymization/anonymize_reports_parallel.py`

- Required input columns: `AccessionNo`, `RaporText`.
- Optional carried columns: `UID`, `Batch`, `KabulTarihi`, `TetkikAdi`.
- Default input: `merged_filtered_with_uid.csv`.
- Default output directory: `anonymized_shards`.
- Writes `anonymized_rank_{RANK}.csv` and `mapping_rank_{RANK}.csv`.
- Adds `Anonymized_Rapor` and `Token_Mapping`.
- Uses Qwen/Qwen3.5-35B-A3B-FP8 through vLLM.
- Uses `SLURM_PROCID`, `SLURM_NTASKS`, and `SLURM_LOCALID` for rank sharding
  and GPU isolation, with local single-rank defaults.
- Supports resume by skipping `AccessionNo` values already present in the
  rank output.

Validation source:
`utils/validate_anonymization_parallel.py`

- Required input column: `Anonymized_Rapor`.
- Default output directory: `validation_shards`.
- Writes `validation_rank_{RANK}.csv`.
- Produces `final_result`, `leaked_items`, `notes`, and `raw_llm_output`.

## Workflow

1. Confirm the CSV path and verify required columns without printing sensitive
   report text.
2. Confirm output directory and whether existing per-rank files should be used
   for resume.
3. Confirm compute target, model availability, and Hugging Face/cache behavior.
4. Prepare the anonymization command.
5. Prepare validation commands after anonymization shards are merged or
   selected.
6. Route shard merges to `mrrate-report-shard-operations`.
7. Summarize pass/fail counts and manual review needs without exposing PHI.

## Example Commands

```text
srun python 01_anonymization/anonymize_reports_parallel.py --input_file merged_filtered_with_uid.csv --output_dir anonymized_shards
```

```text
srun python utils/validate_anonymization_parallel.py --input_file anonymized_reports.csv --output_dir validation_shards
```

## Boundaries

- Do not claim the anonymizer proves full de-identification; it is an LLM
  workflow plus validation and manual review.
- Do not publish token mappings.
- Do not change source prompts unless the user explicitly asks to edit the
  MR-RATE repo.
