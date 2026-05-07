---
name: mrrate-report-shard-operations
owner: medatasci
description: Use this skill when the user wants to inspect, merge, deduplicate, or summarize MR-RATE report preprocessing per-rank shard outputs. Use for CSV shards written as `*_rank_{RANK}.csv`, pathology JSON shards written as `labels_rank_*.json`, status distribution checks, deduplication by `AccessionNo`, safe rerun/resume checks, and handoff to downstream report preprocessing stages.
title: MR-RATE Report Shard Operations
short_description: Merge and inspect MR-RATE report preprocessing CSV and pathology JSON shards safely.
expanded_description: Use this skill for the deterministic shard handling utilities in MR-RATE reports_preprocessing. It covers `utils/merge_shards.py` for per-rank CSVs and `06_pathology_classification/merge_labels.py` for label JSON outputs, including file patterns, deduplication behavior, status summaries, output paths, and safe checks before overwriting merged artifacts.
aliases:
  - MR-RATE shard merge
  - merge MR-RATE report shards
  - labels_rank merge
  - SLURM shard operations
categories:
  - Data Engineering
  - Medical Imaging
tags:
  - mr-rate
  - shard-merge
  - slurm
  - csv
  - json
tasks:
  - merge per-rank CSV shard outputs
  - deduplicate shards by accession number
  - inspect status distributions
  - merge pathology label JSON outputs
  - check safe rerun behavior
use_when:
  - The user has MR-RATE report preprocessing per-rank CSV outputs to combine.
  - The user wants to summarize parse, verdict, or QC status distributions.
  - The user has `labels_rank_*.json` pathology outputs to merge.
do_not_use_when:
  - The user needs to generate new LLM outputs rather than merge existing shards.
  - The user wants to delete or overwrite source shards without explicit approval.
inputs:
  - shard directory containing `*_rank_*.csv`
  - output CSV path
  - optional shard prefix and deduplication column
  - pathology label output directory containing `labels_rank_*.json`
outputs:
  - merged CSV
  - status distribution summary
  - pathology labels CSV
examples:
  - Use mrrate-report-shard-operations to merge anonymized_rank CSV shards.
  - Summarize parse_status counts in these structure shards.
  - Merge labels_rank JSON files into labels.csv.
related_skills:
  - mrrate-report-preprocessing
  - mrrate-report-pathology-labeling
  - mrrate-report-structuring-qc
risk_level: low
permissions:
  - read local shard CSV or JSON files
  - write one requested merged output file
  - ask before overwriting existing merged outputs or deleting shards
page_title: MR-RATE Report Shard Operations Skill - Merge CSV and Label JSON Outputs
meta_description: Use the MR-RATE Report Shard Operations Skill to merge per-rank report preprocessing CSV shards, inspect status distributions, and merge pathology label JSON outputs.
---

# MR-RATE Report Shard Operations

## What This Skill Does

Use this skill for deterministic file operations around MR-RATE report
preprocessing shards. Most source LLM scripts write one file per SLURM rank; this
skill helps merge those outputs, inspect status columns, and prepare downstream
handoffs.

## Safe Default Behavior

Default to read-only inspection unless the user has requested a specific merged
output path. Ask before overwriting existing files or deleting any shard.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Merge per-rank CSVs | Use `utils/merge_shards.py`. |
| Summarize status counts | Use the merge utility or inspect `parse_status`, `verdict`, and `qc_status`. |
| Merge pathology JSON labels | Use `06_pathology_classification/merge_labels.py`. |

## Source-Grounded Contract

CSV merge source:
`utils/merge_shards.py`

- Required arguments: `--shard_dir`, `--output`.
- Optional arguments: `--shard_prefix`, `--dedup_col`.
- Default `--shard_prefix`: `*_rank_`.
- Default `--dedup_col`: `AccessionNo`.
- Reads matching CSVs, concatenates them, drops duplicate `dedup_col` values
  keeping the last occurrence, prints status distributions if `parse_status`,
  `verdict`, or `qc_status` exists, and writes the merged CSV.

Pathology label merge source:
`06_pathology_classification/merge_labels.py`

- Required arguments: `--input_dir`, `--output`.
- Reads `labels_rank_*.json`.
- Writes `study_uid` plus pathology columns.
- Prints aggregate classification stats and prevalence counts.

## Workflow

1. Identify the stage that produced the shards and the expected filename
   prefix.
2. List shard files and check counts before merging.
3. Ask before overwriting an existing merged output.
4. Use `merge_shards.py` for CSV shards and `merge_labels.py` for pathology
   JSON outputs.
5. Report row counts, deduplication count, status distributions, and output
   path.
6. Recommend the next pipeline stage based on the merged artifact.

## Example Commands

```text
python utils/merge_shards.py --shard_dir anonymized_shards --output anonymized_reports.csv --shard_prefix anonymized_rank_ --dedup_col AccessionNo
```

```text
python utils/merge_shards.py --shard_dir structure_shards --output structured_reports.csv --shard_prefix structure_rank_ --dedup_col AccessionNo
```

```text
python 06_pathology_classification/merge_labels.py --input_dir pathology_output --output labels.csv
```

## Boundaries

- Do not delete shards after merge unless the user explicitly asks.
- Do not assume missing ranks are okay; report the observed shard set.
- Do not merge pathology JSON files with the generic CSV utility.
