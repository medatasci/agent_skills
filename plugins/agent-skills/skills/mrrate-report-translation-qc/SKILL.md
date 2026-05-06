---
name: mrrate-report-translation-qc
owner: medatasci
description: Use this skill when the user wants to translate MR-RATE anonymized Turkish radiology reports to English or run translation quality control, Turkish-language detection, and retranslation loops from the reports_preprocessing source tree. Use for source-supported command planning, required columns, per-rank outputs, QC verdict review, non-English filtering, retry thresholds, and manual review handoff.
title: MR-RATE Report Translation QC
short_description: Guide MR-RATE Turkish-to-English report translation, QC, language detection, and retranslation loops.
expanded_description: Use this skill for MR-RATE translation and translation QC stages. It covers `translate_reports_parallel.py`, `quality_check_parallel.py`, `detect_turkish_parallel.py`, and `retranslate_parallel.py`, including input/output columns, shard outputs, sampling defaults, source QC rules, and safe handling of translated medical report text.
aliases:
  - MR-RATE translation QC
  - Turkish to English report translation
  - detect Turkish in MR-RATE reports
  - retranslate MR-RATE reports
categories:
  - Medical Imaging
  - Translation
  - Quality Control
tags:
  - mr-rate
  - translation
  - translation-qc
  - radiology-reports
  - vllm
tasks:
  - prepare report translation commands
  - run or inspect translation QC
  - detect remaining Turkish report text
  - plan retranslation of non-English outputs
  - summarize manual review handoff
use_when:
  - The user has anonymized Turkish MR-RATE reports and wants English translations.
  - The user wants to QC translations for clinical meaning, token preservation, or remaining Turkish text.
  - The user wants to retranslate reports flagged as non-English or failed QC.
do_not_use_when:
  - The user needs PHI anonymization before translation.
  - The user needs structuring or pathology classification after translation.
inputs:
  - anonymized report CSV with `Anonymized_Rapor`
  - translation QC CSV with `turkish_anonymized_report` and `english_anonymized_report`
  - optional language detection CSV with `detected_language`
outputs:
  - `translated_rank_{RANK}.csv`
  - `qc_rank_{RANK}.csv`
  - `detect_rank_{RANK}.csv`
  - `retranslate_rank_{RANK}.csv`
examples:
  - Use mrrate-report-translation-qc to plan translation and QC for this anonymized reports CSV.
  - Prepare commands to detect remaining Turkish text and retranslate failures.
  - Explain how the MR-RATE translation QC loop reaches manual review.
related_skills:
  - mrrate-report-anonymization
  - mrrate-report-structuring-qc
  - mrrate-report-shard-operations
risk_level: medium
permissions:
  - read local CSV schemas and source scripts
  - propose GPU/vLLM commands that write translated and QC outputs
  - do not run model jobs or send report text externally without explicit approval
page_title: MR-RATE Report Translation QC Skill - Translation, Detection, and Retranslation
meta_description: Use the MR-RATE Report Translation QC Skill to plan Turkish-to-English radiology report translation, quality checks, language detection, and retranslation loops.
---

# MR-RATE Report Translation QC

## What This Skill Does

Use this skill for the MR-RATE stages that convert anonymized Turkish reports
to English and verify translation quality before structuring.

## Safe Default Behavior

Default to planning and schema inspection. Ask before running vLLM, reading
full report text, downloading model weights, or writing new translation outputs.
Keep anonymization tokens intact and treat translated reports as sensitive.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Translate anonymized Turkish reports | Prepare `02_translation/translate_reports_parallel.py`. |
| Check clinical translation quality | Prepare `03_translation_qc/quality_check_parallel.py`. |
| Detect remaining Turkish text | Prepare `03_translation_qc/detect_turkish_parallel.py`. |
| Re-translate failures | Prepare `03_translation_qc/retranslate_parallel.py`. |

## Source-Grounded Contract

Translation source:
`02_translation/translate_reports_parallel.py`

- Required input column: `Anonymized_Rapor`.
- Default output directory: `translated_shards`.
- Writes `translated_rank_{RANK}.csv`.
- Adds `Translated_Rapor`.
- Uses Qwen/Qwen3.5-35B-A3B-FP8, temperature 0, max tokens 30000.

Translation QC source:
`03_translation_qc/quality_check_parallel.py`

- Expects `turkish_anonymized_report` and `english_anonymized_report`.
- Writes `qc_rank_{RANK}.csv`.
- Emits `verdict`, `issues`, `thinking`, and `response`.
- Flags only high-confidence clinical translation errors and preserves a
  conservative PASS bias when uncertain.

Language detection source:
`03_translation_qc/detect_turkish_parallel.py`

- Reads `english_anonymized_report`.
- Writes `detect_rank_{RANK}.csv`.
- Emits `detected_language` as `english`, `turkish`, `mixed`, or `unknown`.

Retranslation source:
`03_translation_qc/retranslate_parallel.py`

- Requires `--reports_file`; optional `--detection_file`.
- Normalizes `Anonymized_Rapor` to `turkish_anonymized_report` and `Batch` to
  `batch_number` when needed.
- Filters to `detected_language != "english"` when a detection file is supplied.
- Writes `retranslate_rank_{RANK}.csv` with `english_translation`.
- Uses a stronger terminology prompt and retries outputs that still look
  Turkish.

## Workflow

1. Confirm whether the current artifact is anonymized Turkish, translated
   English, QC output, or language detection output.
2. Verify required columns without dumping report text.
3. Prepare the appropriate stage command and output directory.
4. Explain resume behavior: rank files skip existing `AccessionNo` values.
5. Merge shards with `mrrate-report-shard-operations`.
6. Summarize QC verdicts or language counts.
7. Keep remaining failures for manual review instead of auto-fixing uncertain
   clinical content.

## Example Commands

```text
srun python 02_translation/translate_reports_parallel.py --input_file anonymized_reports.csv --output_dir translated_shards
```

```text
srun python 03_translation_qc/quality_check_parallel.py --input_file translated_reports_for_qc.csv --output_dir quality_check_shards
```

```text
srun python 03_translation_qc/detect_turkish_parallel.py --input_file translated_reports.csv --output_dir detect_turkish_shards
```

```text
srun python 03_translation_qc/retranslate_parallel.py --reports_file anonymized_reports.csv --detection_file detected_languages.csv --output_dir retranslate_shards
```

## Boundaries

- Do not treat QC PASS as proof of perfect translation.
- Do not silently change medical meaning when summarizing QC failures.
- Do not expose full report text in logs, public docs, or issue drafts.

