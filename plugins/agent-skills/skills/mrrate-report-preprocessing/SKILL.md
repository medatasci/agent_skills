---
name: mrrate-report-preprocessing
owner: medatasci
description: Use this skill when the user wants to plan, inspect, or operate the MR-RATE radiology report preprocessing pipeline from raw Turkish reports through anonymization, translation, translation QC, structuring, structure QC, pathology classification, and shard merging. Use for source-grounded MR-RATE report preprocessing runbooks, stage selection, command sequencing, data-column checks, SLURM/vLLM runtime planning, failure-loop planning, provenance, and deciding when to call the narrower MR-RATE report skills.
title: MR-RATE Report Preprocessing
short_description: Plan and operate the MR-RATE radiology report preprocessing pipeline as a source-grounded staged workflow.
expanded_description: Use this skill as the umbrella workflow for the MR-RATE reports_preprocessing tree. It routes between anonymization, translation QC, structuring QC, pathology labeling, and shard operations while preserving the source pipeline's run-QC-retry-manual-review loop, SLURM sharding model, Qwen/vLLM runtime assumptions, and research-only data handling boundaries.
aliases:
  - MR-RATE report preprocessing
  - MR-RATE reports pipeline
  - reports_preprocessing
  - Turkish MRI report preprocessing
  - radiology report generation pipeline
categories:
  - Medical Imaging
  - Data Preprocessing
  - Agent Workflows
tags:
  - mr-rate
  - radiology-reports
  - report-preprocessing
  - vllm
  - slurm
  - qwen
tasks:
  - plan the MR-RATE report preprocessing workflow
  - choose the next report preprocessing stage
  - explain required inputs and outputs for each stage
  - prepare source-grounded SLURM/vLLM commands
  - summarize run-QC-retry-manual-review loops
use_when:
  - The user asks how to run or inspect the MR-RATE radiology report preprocessing tree.
  - The user needs to sequence anonymization, translation, QC, structuring, pathology labeling, and shard merge steps.
  - The user wants source-grounded commands without running expensive model jobs yet.
do_not_use_when:
  - The user only needs one narrow stage; call the matching child skill instead.
  - The user asks for diagnosis, treatment, triage, or clinical interpretation.
  - The user wants to process PHI or gated data without confirming local permissions and data handling.
inputs:
  - MR-RATE reports_preprocessing checkout path
  - stage goal or current pipeline state
  - CSV paths, shard directories, output directories, and SLURM/vLLM constraints
outputs:
  - staged run plan
  - source-grounded command list
  - input/output checklist and approval gates
  - routing to child skills
examples:
  - Use mrrate-report-preprocessing to plan the next MR-RATE report preprocessing stage for these files.
  - Explain the MR-RATE reports_preprocessing pipeline and tell me which child skill applies.
  - Build a guarded command sequence from anonymized Turkish reports to pathology labels.
related_skills:
  - mrrate-report-anonymization
  - mrrate-report-translation-qc
  - mrrate-report-structuring-qc
  - mrrate-report-pathology-labeling
  - mrrate-report-shard-operations
risk_level: medium
permissions:
  - read local source files and local report-processing metadata
  - propose commands for source scripts
  - do not run GPU/vLLM jobs, download models, or process PHI without explicit user approval
  - write only requested planning artifacts or generated outputs
page_title: MR-RATE Report Preprocessing Skill - Source-Grounded Radiology Report Pipeline
meta_description: Use the MR-RATE Report Preprocessing Skill to plan anonymization, translation QC, structuring, pathology labeling, and shard merge workflows for MR-RATE radiology reports.
---

# MR-RATE Report Preprocessing

## What This Skill Does

Use this umbrella skill to reason about the MR-RATE `reports_preprocessing`
tree as a staged research workflow. The source pipeline converts raw Turkish
brain MRI radiology reports into anonymized, translated, structured English
reports and then derives binary pathology labels.

## Safe Default Behavior

Default to planning and inspection. Do not run the MR-RATE source scripts until
the user confirms the local data permissions, compute target, output path, and
expected cost. Treat raw and intermediate reports as potentially sensitive.

MR-RATE is released for non-commercial research under the repository license;
do not broaden that claim or present outputs as clinical advice.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Understand the whole report pipeline | Summarize the README chain, stage order, inputs, outputs, and child skills. |
| Run one stage | Route to the matching child skill and prepare that stage's command. |
| Merge or inspect per-rank outputs | Use `mrrate-report-shard-operations`. |
| Produce 37 pathology columns | Use `mrrate-report-pathology-labeling`. |

## Source Context

Read the README chain before making claims:

- MR-RATE root `README.md`: dataset/model context, repository structure, license, and report preprocessing summary.
- `data-preprocessing/README.md`: dependency setup, report preprocessing stage list, and `environment_reports.yml`.
- `data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing/README.md`: detailed report pipeline, commands, columns, QC thresholds, and SLURM sharding behavior.

There were no README files at `data-preprocessing/src/` or
`data-preprocessing/src/mr_rate_preprocessing/` in the inspected tree.

Inspected source version:
`forithmus/MR-RATE` commit `e02b4ed79ff427fb3578f03242de2d9d51dc709d`
on May 5, 2026.

## Workflow

1. Identify the user's current stage and available artifacts.
2. Check whether the stage needs raw Turkish reports, anonymized reports,
   translated reports, structured reports, shard CSVs, or per-rank JSON labels.
3. Confirm runtime assumptions: `mr-rate-reports` Conda environment,
   Python 3.11, PyTorch CUDA 12.6, vLLM, Transformers, Pandas, tqdm, and
   Hugging Face Hub.
4. Confirm SLURM variables or a local single-rank run. The source scripts use
   `SLURM_PROCID`, `SLURM_NTASKS`, and `SLURM_LOCALID`; absent values default
   to a single-rank local mode.
5. Route to a child skill for stage details.
6. For each proposed command, state inputs, outputs, resume behavior, and the
   files that will be written.
7. Preserve the source pipeline's loop: run, automated QC, retry or fallback,
   re-QC, then manual review of remaining failures.

## Child Skills

- `mrrate-report-anonymization`: raw Turkish report anonymization and PHI QC.
- `mrrate-report-translation-qc`: Turkish-to-English translation, translation
  QC, Turkish detection, and retranslation.
- `mrrate-report-structuring-qc`: structured section extraction and structure
  verification.
- `mrrate-report-pathology-labeling`: 37-label pathology classification and
  pathology JSON merge.
- `mrrate-report-shard-operations`: merge and inspect per-rank CSV/JSON outputs.

## Boundaries

- Do not diagnose, triage, or make patient-care recommendations.
- Do not expose report text, token mappings, PHI, or local paths in public
  artifacts unless the user has reviewed and approved them.
- Do not assume vLLM model weights are present. The source scripts may trigger
  Hugging Face model access/downloads depending on the environment.
- Do not invent input columns. Use the stage-specific skill or source script.

## Examples

```text
Use mrrate-report-preprocessing to map my current MR-RATE report files to the next safe stage.
```

```text
Plan the end-to-end MR-RATE reports_preprocessing workflow, but do not run GPU jobs.
```
