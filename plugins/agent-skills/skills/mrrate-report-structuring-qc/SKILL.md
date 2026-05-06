---
name: mrrate-report-structuring-qc
owner: medatasci
description: Use this skill when the user wants to structure MR-RATE English radiology reports into `clinical_information`, `technique`, `findings`, and `impression` sections or verify structured outputs against raw reports. Use for source-supported command planning, no-think fallback, parse failure review, section formatting rules, structure QC verdicts, shard outputs, and manual review handoff.
title: MR-RATE Report Structuring QC
short_description: Guide MR-RATE report section extraction and structure verification with source-supported commands and QC gates.
expanded_description: Use this skill for MR-RATE report structuring and structure QC stages. It covers `structure_reports_parallel.py`, `structure_nothink_parallel.py`, `qc_llm_verify.py`, and `qc_llm_verify_nothink.py`, including four-section JSON extraction, no-think fallback, parse status handling, QC issue categories, and safe review of structured medical reports.
aliases:
  - MR-RATE report structuring
  - structure MR-RATE reports
  - MR-RATE structure QC
  - clinical information technique findings impression
categories:
  - Medical Imaging
  - Data Structuring
  - Quality Control
tags:
  - mr-rate
  - report-structuring
  - structure-qc
  - radiology-reports
  - vllm
tasks:
  - prepare report structuring commands
  - run no-think fallback for parse failures
  - verify structured output against raw reports
  - summarize parse status and QC verdicts
  - plan manual review of remaining failures
use_when:
  - The user has translated English MR-RATE reports and wants structured report sections.
  - The user wants to QC missing, hallucinated, or misplaced section content.
  - The user asks about parse failures, no-think fallback, or section formatting rules.
do_not_use_when:
  - The user needs translation or retranslation first.
  - The user needs pathology labels after structure QC passes.
inputs:
  - translated report CSV with `english_anonymized_report`
  - structured report CSV with `raw_report`, `findings`, `impression`, and `parse_status`
  - output directory for structure or QC shards
outputs:
  - `structure_rank_{RANK}.csv`
  - `qc_rank_{RANK}.csv`
  - structured section columns and QC verdicts
examples:
  - Use mrrate-report-structuring-qc to structure translated reports into four sections.
  - Prepare no-think fallback for parse_failed rows.
  - Summarize structure QC failures without printing report text.
related_skills:
  - mrrate-report-translation-qc
  - mrrate-report-pathology-labeling
  - mrrate-report-shard-operations
risk_level: medium
permissions:
  - read local CSV schemas and source scripts
  - propose GPU/vLLM commands that write structured reports and QC outputs
  - do not run model jobs or expose report text without explicit approval
page_title: MR-RATE Report Structuring QC Skill - Section Extraction and Verification
meta_description: Use the MR-RATE Report Structuring QC Skill to plan four-section radiology report extraction, no-think fallback, and structure quality checks.
---

# MR-RATE Report Structuring QC

## What This Skill Does

Use this skill to extract four structured fields from MR-RATE English reports:
`clinical_information`, `technique`, `findings`, and `impression`, then verify
that the structured output preserves the raw report content.

## Safe Default Behavior

Default to planning, column checks, and summary statistics. Ask before running
vLLM, printing report text, or writing structured outputs. Do not "repair"
medical content by invention; only plan source-supported reruns and manual
review.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Structure translated reports | Prepare `04_structuring/structure_reports_parallel.py`. |
| Retry parse failures | Prepare `04_structuring/structure_nothink_parallel.py`. |
| Verify structured outputs | Prepare `05_structure_qc/qc_llm_verify.py`. |
| Retry QC parse failures | Prepare `05_structure_qc/qc_llm_verify_nothink.py`. |

## Source-Grounded Contract

Structuring sources:
`04_structuring/structure_reports_parallel.py` and
`04_structuring/structure_nothink_parallel.py`

- Input column: `english_anonymized_report`.
- Default output directory: `structure_shards`.
- Writes `structure_rank_{RANK}.csv`.
- Output columns include `AccessionNo`, `UID`, `raw_report`,
  `clinical_information`, `technique`, `findings`, `impression`,
  `parse_status`, and `invalid_reason`.
- `parse_status` can include `ok`, `invalid`, or `parse_failed`.
- Findings are paragraph sentences; impression uses em-dash style bullets in
  the source prompt; keep this as a formatting rule, not a clinical rule.
- No-think fallback uses `enable_thinking=False` and a `/no_think` prompt.

Structure QC sources:
`05_structure_qc/qc_llm_verify.py` and
`05_structure_qc/qc_llm_verify_nothink.py`

- Reads structured rows where `parse_status == "ok"`.
- Writes `qc_rank_{RANK}.csv`.
- Checks missing content, hallucinated content, and wrong section placement.
- Emits `verdict`, `issues`, and `qc_status`.

## Workflow

1. Confirm translated input file and required columns.
2. Prepare the primary structuring command.
3. Merge and inspect `parse_status` distributions.
4. If needed, prepare no-think fallback for parse failures.
5. Run or plan structure QC only on `parse_status == "ok"` rows.
6. Merge QC shards and summarize `verdict` / `qc_status`.
7. Send real remaining issues to manual review; do not synthesize missing
   sections.

## Example Commands

```text
srun python 04_structuring/structure_reports_parallel.py --input_file translated_reports.csv --output_dir structure_shards
```

```text
srun python 04_structuring/structure_nothink_parallel.py --input_file parse_failures.csv --output_dir structure_nothink_shards
```

```text
srun python 05_structure_qc/qc_llm_verify.py --input_file structured_reports.csv --output_dir qc_llm_shards
```

## Boundaries

- Do not treat section placement debates as automatic errors; the source README
  notes common false positives and manual review.
- Do not create clinical content for empty original sections.
- Do not run pathology classification until structure QC has an acceptable pass
  state.

