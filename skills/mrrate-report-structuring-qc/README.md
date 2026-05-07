# MR-RATE Report Structuring QC

Skill ID: `mrrate-report-structuring-qc`

Guide MR-RATE report section extraction and structure verification for
translated English radiology reports.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-report-structuring-qc

Parent package:
SkillForge Agent Skills Marketplace

Parent package repo URL:
https://github.com/medatasci/agent_skills

Distribution or marketplace:
SkillForge local catalog and Codex skill install workflow

Version or release channel:
Repository `main` branch when published

## Parent Collection

Parent collection:
SkillForge Agent Skills Marketplace

Collection URL:
https://github.com/medatasci/agent_skills

Categories:
Medical Imaging, Data Structuring, Quality Control

Collection context:
This skill covers structuring and structure-QC stages in the MR-RATE report
preprocessing family.

## What This Skill Does

This skill helps Codex prepare and inspect the MR-RATE source scripts that
extract four report fields: `clinical_information`, `technique`, `findings`,
and `impression`. It also covers LLM-based verification against the raw report.

## Why You Would Call It

Call this skill when:

- You have translated English reports and need four structured sections.
- You need to retry parse failures with no-think mode.
- You need to QC structured reports for missing, hallucinated, or misplaced content.

Use it to:

- Prepare structuring commands.
- Summarize parse and QC status distributions.
- Decide when manual review is needed.

Do not use it when:

- Reports need anonymization or translation first.
- You need pathology labels from already structured reports.

## Keywords

MR-RATE, report structuring, clinical information, technique, findings,
impression, structure QC, no-think, parse_status, vLLM.

## Search Terms

structure MR-RATE reports, extract findings and impression from MR-RATE,
MR-RATE structure QC, no-think fallback for report parsing.

## How It Works

The structuring scripts read translated report text and ask the model for JSON
with four sections. Failed parses can be retried with no-think mode. The QC
scripts compare the raw report with structured fields and flag missing content,
hallucinated content, or wrong section placement.

## API And Options

Source commands:

```text
srun python 04_structuring/structure_reports_parallel.py --input_file translated_reports.csv --output_dir structure_shards
```

```text
srun python 04_structuring/structure_nothink_parallel.py --input_file parse_failures.csv --output_dir structure_nothink_shards
```

```text
srun python 05_structure_qc/qc_llm_verify.py --input_file structured_reports.csv --output_dir qc_llm_shards
```

Configuration:

- Structuring output file pattern: `structure_rank_{RANK}.csv`.
- QC output file pattern: `qc_rank_{RANK}.csv`.
- Rank sharding follows `SLURM_PROCID` and `SLURM_NTASKS`.

## Inputs And Outputs

Inputs can include:

- Translated CSV with `english_anonymized_report`.
- Structured CSV with `raw_report`, structured fields, and `parse_status`.
- Output directories for structure and QC shards.

Outputs can include:

- Structured section CSV shards.
- QC verdict CSV shards.
- Parse status and QC status summaries.

Output locations:

- User-supplied `--output_dir`.
- Merged outputs through `mrrate-report-shard-operations`.

## Limitations

Known limitations:

- The source README notes common QC false positives that require manual review.
- The skill does not fix medical content by itself.
- Formatting differences may be acceptable and should not always be treated as errors.

Choose another skill when:

- Translation is incomplete.
- You need to classify pathologies after structure QC.

## Examples

Beginner example:

```text
Use mrrate-report-structuring-qc to explain the expected four output columns.
```

Task-specific example:

```text
Prepare structuring and structure-QC commands for these translated MR-RATE reports.
```

Safety-aware example:

```text
Summarize parse_status counts only. Do not print raw_report values.
```

## Trust And Safety

Risk level:
Medium

Permissions:

- Reads local CSV schemas and source scripts.
- Proposes commands that write structured reports and QC outputs.
- Requires approval before running vLLM or printing report text.

Data handling:
Raw, translated, and structured reports may still be sensitive.

Writes vs read-only:
Planning is read-only. Source scripts write CSV shards when run.

External services:
The source scripts may access Hugging Face model files if not cached.

Credentials:
No credentials for planning. Runtime access depends on local environment.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes missing parse-state guidance, weak manual review
handoff, or unclear structure QC boundaries.

## Contributing

Contributions are welcome by pull request. Update source skill files, rebuild
the catalog, and evaluate before PR.

## Author

medatasci

Maintainer status:
Draft source-derived SkillForge skill for review.

## Citations

- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/

## Related Skills

- `mrrate-report-translation-qc`: previous stage.
- `mrrate-report-pathology-labeling`: next stage.
- `mrrate-report-shard-operations`: merge structure and QC shards.
