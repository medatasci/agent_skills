# MR-RATE Report Shard Operations

Skill ID: `mrrate-report-shard-operations`

Merge, deduplicate, and inspect MR-RATE report preprocessing per-rank CSV and
pathology JSON outputs.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-report-shard-operations

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
Data Engineering, Medical Imaging

Collection context:
This utility skill supports every MR-RATE report preprocessing stage that writes
per-rank outputs.

## What This Skill Does

This skill helps Codex safely merge source-script shard outputs, inspect status
distributions, and prepare handoffs to the next report preprocessing stage.

## Why You Would Call It

Call this skill when:

- You have `*_rank_*.csv` files from an MR-RATE report preprocessing stage.
- You want to deduplicate by `AccessionNo`.
- You need to merge `labels_rank_*.json` pathology outputs.

Use it to:

- Prepare deterministic merge commands.
- Report row counts and status distributions.
- Avoid accidental overwrite or deletion.

Do not use it when:

- You need to generate new LLM outputs.
- You want to delete shards without an explicit cleanup request.

## Keywords

MR-RATE, shard merge, SLURM, per-rank CSV, labels_rank JSON, deduplication,
parse_status, verdict, qc_status.

## Search Terms

merge MR-RATE shards, combine anonymized_rank CSV files, merge labels_rank JSON,
MR-RATE parse_status summary, SLURM report preprocessing shards.

## How It Works

The CSV merge utility finds matching rank CSVs, concatenates them, optionally
deduplicates on `AccessionNo`, prints status distributions when status columns
exist, and writes one merged CSV. The pathology merge utility reads
`labels_rank_*.json` and writes one label CSV.

## API And Options

Source commands:

```text
python utils/merge_shards.py --shard_dir anonymized_shards --output anonymized_reports.csv --shard_prefix anonymized_rank_ --dedup_col AccessionNo
```

```text
python utils/merge_shards.py --shard_dir structure_shards --output structured_reports.csv --shard_prefix structure_rank_ --dedup_col AccessionNo
```

```text
python 06_pathology_classification/merge_labels.py --input_dir pathology_output --output labels.csv
```

Configuration:

- Default CSV shard prefix pattern: `*_rank_`.
- Default deduplication column: `AccessionNo`.

## Inputs And Outputs

Inputs can include:

- Directory containing `*_rank_*.csv`.
- Directory containing `labels_rank_*.json`.
- Output file path.

Outputs can include:

- Merged CSV.
- Status distribution summary.
- Pathology labels CSV.

Output locations:

- User-supplied `--output` path.
- Existing shards remain untouched unless explicitly deleted by the user.

## Limitations

Known limitations:

- The source CSV merge utility does not check for missing expected ranks.
- It keeps the last duplicate by default.
- It does not validate medical content.

Choose another skill when:

- You need to run anonymization, translation, structuring, or labeling.
- You need a non-MR-RATE generic data engineering workflow.

## Examples

Beginner example:

```text
Use mrrate-report-shard-operations to explain how to merge these MR-RATE rank CSVs.
```

Task-specific example:

```text
Prepare a merge command for structure_rank files and summarize parse_status counts.
```

Safety-aware example:

```text
Check whether the merged output already exists before writing it.
```

## Help And Getting Started

Start with:

```text
Use mrrate-report-shard-operations to inspect this shard directory and prepare a safe merge command.
```

Provide:

- The shard directory.
- The expected filename prefix.
- The desired merged output path.

Ask for help when:

- The output file already exists.
- Rank files appear to be missing.
- Status distributions show unexpected `parse_failed`, `fail`, or `error` rows.

## How To Call From An LLM

Direct prompt:

```text
Use mrrate-report-shard-operations to merge these MR-RATE report preprocessing shards.
```

Guarded prompt:

```text
Use mrrate-report-shard-operations, but ask before overwriting any merged output file.
```

## How To Call From The CLI

Search for the skill:

```text
python -m skillforge search "MR-RATE shard merge" --json
```

Show skill metadata:

```text
python -m skillforge info mrrate-report-shard-operations --json
```

Evaluate the skill:

```text
python -m skillforge evaluate mrrate-report-shard-operations --json
```

Source CSV merge command:

```text
python utils/merge_shards.py --shard_dir structure_shards --output structured_reports.csv --shard_prefix structure_rank_ --dedup_col AccessionNo
```

Source pathology label merge command:

```text
python 06_pathology_classification/merge_labels.py --input_dir pathology_output --output labels.csv
```

## Trust And Safety

Risk level:
Low

Permissions:

- Reads local CSV or JSON shard files.
- Writes one requested merged output file.
- Requires approval before overwriting outputs or deleting shards.

Data handling:
Shard files may contain sensitive reports or labels; summaries should avoid
printing report text.

Writes vs read-only:
Inspection is read-only. Merge commands write the requested output path.

External services:
None.

Credentials:
None.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes missing shard prefix examples, weak overwrite checks,
or insufficient downstream handoff guidance.

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

- `mrrate-report-preprocessing`: family-level routing.
- `mrrate-report-pathology-labeling`: source of label JSON outputs.
- `mrrate-report-structuring-qc`: common source of parse-status CSV shards.
