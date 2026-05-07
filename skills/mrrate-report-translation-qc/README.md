# MR-RATE Report Translation QC

Skill ID: `mrrate-report-translation-qc`

Guide Turkish-to-English translation of anonymized MR-RATE radiology reports,
translation QC, language detection, and retranslation loops.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-report-translation-qc

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
Medical Imaging, Translation, Quality Control

Collection context:
This skill covers the translation and translation-QC stages in the MR-RATE
report preprocessing family.

## What This Skill Does

This skill helps Codex plan and explain the MR-RATE source scripts for
translation, LLM translation QC, remaining-Turkish detection, and retranslation
of failed or non-English outputs.

## Why You Would Call It

Call this skill when:

- You have anonymized Turkish reports and need English translations.
- You need translation QC verdicts and issue summaries.
- You need to detect or retranslate reports that remain Turkish or mixed.

Use it to:

- Prepare source-supported translation commands.
- Check required columns for QC and detection.
- Plan the run-QC-retry-manual-review loop.

Do not use it when:

- Reports still contain PHI and need anonymization first.
- You need structured sections or pathology labels.

## Keywords

MR-RATE, translation, translation QC, Turkish, English radiology reports,
remaining Turkish detection, retranslation, Qwen, vLLM.

## Search Terms

translate MR-RATE reports, MR-RATE translation quality check, detect Turkish in
translated reports, retranslate MR-RATE report failures.

## How It Works

The translation script translates `Anonymized_Rapor` into English. QC compares
Turkish and English versions for high-confidence clinical meaning errors.
Language detection checks whether English outputs remain Turkish or mixed.
Retranslation can filter non-English rows from a detection file.

## API And Options

Source commands:

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

Configuration:

- Translation uses Qwen/Qwen3.5-35B-A3B-FP8 in the inspected source.
- Retranslation uses a stricter terminology prompt and retry pass.

## Inputs And Outputs

Inputs can include:

- `Anonymized_Rapor` for translation.
- `turkish_anonymized_report` and `english_anonymized_report` for QC.
- `detected_language` for retranslation filtering.

Outputs can include:

- `translated_rank_{RANK}.csv`
- `qc_rank_{RANK}.csv`
- `detect_rank_{RANK}.csv`
- `retranslate_rank_{RANK}.csv`

Output locations:

- User-supplied `--output_dir`.
- Merged outputs through `mrrate-report-shard-operations`.

## Limitations

Known limitations:

- QC is conservative and still needs manual review for remaining failures.
- Translation outputs are research artifacts, not clinical translations for care.
- Source scripts may require cached or accessible model files.

Choose another skill when:

- You need anonymization first.
- You need structuring after translation passes.

## Examples

Beginner example:

```text
Use mrrate-report-translation-qc to tell me which translation script applies to this CSV.
```

Task-specific example:

```text
Prepare translation, QC, Turkish detection, and retranslation commands for these MR-RATE report artifacts.
```

Safety-aware example:

```text
Summarize QC verdict counts without quoting report text.
```

## Trust And Safety

Risk level:
Medium

Permissions:

- Reads local CSV schemas and source scripts.
- Proposes commands that write translation and QC outputs.
- Requires approval before running vLLM or printing report text.

Data handling:
Translated and source report text may still be sensitive even after tokenization.

Writes vs read-only:
Planning is read-only. Source scripts write CSV shards when run.

External services:
The source scripts may access Hugging Face model files if not cached.

Credentials:
No credentials for planning. Runtime access depends on local environment.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes missing QC columns, weak retry guidance, or unsafe
examples.

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

- `mrrate-report-anonymization`: previous stage.
- `mrrate-report-structuring-qc`: next stage.
- `mrrate-report-shard-operations`: merge translation and QC shards.
