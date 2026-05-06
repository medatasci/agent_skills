# MR-RATE Report Anonymization

Skill ID: `mrrate-report-anonymization`

Prepare and review the MR-RATE Turkish radiology report anonymization stage,
including token mapping outputs and PHI validation.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-report-anonymization

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
Medical Imaging, Privacy, Data Preprocessing

Collection context:
This is the first stage skill in the MR-RATE report preprocessing family.

## What This Skill Does

This skill helps Codex prepare source-supported anonymization and anonymization
QC commands for MR-RATE Turkish report CSVs. It explains required columns,
per-rank outputs, token mapping behavior, validation outputs, and safe merge
handoff.

## Why You Would Call It

Call this skill when:

- You have raw Turkish report CSVs and need anonymized outputs.
- You need to verify that anonymized reports do not obviously leak PHI.
- You want to understand `anonymized_rank`, `mapping_rank`, or validation shards.

Use it to:

- Check anonymization input columns.
- Prepare vLLM anonymization or validation commands.
- Route merged outputs to translation QC.

Do not use it when:

- Reports are already anonymized and ready for translation.
- You need to publish or inspect raw PHI-bearing content.

## Keywords

MR-RATE, anonymization, PHI, Turkish reports, radiology reports, token mapping,
Qwen, vLLM, SLURM, validation.

## Search Terms

anonymize MR-RATE reports, validate anonymized reports, PHI QC for Turkish
radiology reports, MR-RATE token mapping, anonymized_rank CSV.

## How It Works

The source anonymizer reads `AccessionNo` and `RaporText`, runs Qwen through
vLLM, writes anonymized report shards and token mappings, and supports resume by
skipping already processed accessions. The validation script reads
`Anonymized_Rapor` and writes per-rank PHI review results.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE anonymization" --json
python -m skillforge evaluate mrrate-report-anonymization --json
```

Source commands:

```text
srun python 01_anonymization/anonymize_reports_parallel.py --input_file merged_filtered_with_uid.csv --output_dir anonymized_shards
```

```text
srun python utils/validate_anonymization_parallel.py --input_file anonymized_reports.csv --output_dir validation_shards
```

Configuration:

- Uses Qwen/Qwen3.5-35B-A3B-FP8 in the inspected source.
- Uses SLURM rank variables when available, otherwise local single-rank defaults.

## Inputs And Outputs

Inputs can include:

- Raw Turkish CSV with `AccessionNo` and `RaporText`.
- Anonymized CSV with `Anonymized_Rapor`.
- Output directory for shard files.

Outputs can include:

- `anonymized_rank_{RANK}.csv`
- `mapping_rank_{RANK}.csv`
- `validation_rank_{RANK}.csv`

Output locations:

- User-supplied `--output_dir`.
- Merged outputs through `mrrate-report-shard-operations`.

## Limitations

Known limitations:

- LLM anonymization is not a formal de-identification guarantee.
- Token mappings are sensitive and should not be published.
- No public sample PHI fixtures are packaged with this skill.

Choose another skill when:

- You need translation or retranslation.
- You need generic shard merging.

## Examples

Beginner example:

```text
Use mrrate-report-anonymization to check the required columns for my raw reports CSV.
```

Task-specific example:

```text
Prepare anonymization and validation commands for this MR-RATE reports file, but do not run vLLM yet.
```

Safety-aware example:

```text
Summarize validation failures by count only. Do not print leaked items or report text.
```

## Help And Getting Started

Start with:

```text
Use mrrate-report-anonymization to check my raw report CSV schema and prepare safe anonymization commands.
```

Provide:

- The local CSV path.
- The intended output directory.
- Whether Codex may inspect row content or only column names and counts.

Ask for help when:

- Validation output contains failures.
- Token mappings need to be protected before sharing logs.
- Existing rank files may be resumed or overwritten.

## How To Call From An LLM

Direct prompt:

```text
Use mrrate-report-anonymization to plan anonymization for this MR-RATE report CSV.
```

Guarded prompt:

```text
Use mrrate-report-anonymization, but do not print PHI, token mappings, or report text.
```

## How To Call From The CLI

Search for the skill:

```text
python -m skillforge search "MR-RATE anonymization" --json
```

Show skill metadata:

```text
python -m skillforge info mrrate-report-anonymization --json
```

Evaluate the skill:

```text
python -m skillforge evaluate mrrate-report-anonymization --json
```

Source anonymization command:

```text
srun python 01_anonymization/anonymize_reports_parallel.py --input_file merged_filtered_with_uid.csv --output_dir anonymized_shards
```

Source validation command:

```text
srun python utils/validate_anonymization_parallel.py --input_file anonymized_reports.csv --output_dir validation_shards
```

## Trust And Safety

Risk level:
Medium

Permissions:

- Reads local CSV schemas and source scripts.
- Proposes commands that write anonymization and validation outputs.
- Requires approval before reading PHI rows or running model jobs.

Data handling:
Raw reports, token mappings, and validation failures may contain PHI.

Writes vs read-only:
Planning is read-only. Source scripts write CSV shards when run.

External services:
The source scripts may access Hugging Face model files if not cached locally.

Credentials:
No credentials for planning. Model access depends on local environment.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes missing column checks, unsafe examples, or unclear PHI
handling guidance.

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

- `mrrate-report-preprocessing`: family-level stage routing.
- `mrrate-report-shard-operations`: merge anonymization and validation shards.
- `mrrate-report-translation-qc`: next stage after anonymization.
