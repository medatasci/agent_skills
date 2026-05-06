# MR-RATE Dataset Access

Skill ID: `mrrate-dataset-access`

Plan and inspect MR-RATE Hugging Face dataset downloads, derivative repository
merges, backfilled registration study recovery, and local dataset structure.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-dataset-access

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
Medical Imaging, Data Access, Research

Collection context:
This skill is the dataset-consumption branch of the MR-RATE skill family.

## What This Skill Does

This skill helps Codex plan source-supported MR-RATE downloads from the four
gated Hugging Face repositories and explain the local file layout keyed by
`study_uid`, `series_id`, `patient_uid`, and `batch00` through `batch27`.

## Why You Would Call It

Call this skill when:

- You want to download native, coreg, atlas, nvseg, metadata, or reports.
- You need to merge downloaded derivative repositories into `MR-RATE/`.
- You need to recover backfilled registration studies.
- You want to understand the local dataset layout before training or inference.

Use it to:

- Select batches and repositories.
- Plan download, unzip, delete-zips, and Xet settings.
- Explain metadata, reports, splits, pathology labels, and derivative joins.

Do not use it when:

- You are generating MR-RATE from raw DICOM/PACS exports.
- You are training or running a model after data is already available.

## Keywords

MR-RATE, Hugging Face, gated dataset, native MRI, coreg, atlas, nvseg,
download.py, merge_downloaded_repos.py, backfilled registration.

## Search Terms

MR-RATE download, MR-RATE dataset access, MR-RATE Hugging Face batches,
MR-RATE merge derivative repos, MR-RATE backfilled studies.

## How It Works

Codex uses the dataset guide and source downloader scripts to choose a safe
command plan. It calls out the large-data consequences of MRI downloads, the
gated-access requirement, whether zips are kept or deleted, and whether a merge
will move derivative folders into the base native repository.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE dataset download" --json
python -m skillforge info mrrate-dataset-access --json
python -m skillforge evaluate mrrate-dataset-access --json
```

Important source commands:

```text
python scripts/hf/download.py --batches 00,01 --native --metadata --reports --unzip
python scripts/hf/download.py --batches all --no-mri --no-metadata --no-reports
python scripts/hf/merge_downloaded_repos.py --coreg --atlas --nvseg --batches 00,01
python scripts/hf/download_backfilled_reg_studies.py --json-path scripts/hf/backfilled_reg_study_ids.json --output-base ./data --coreg --atlas
```

## How To Call From An LLM

Ask for the skill by name when planning a dataset download, merge, or layout
check:

```text
Use mrrate-dataset-access to plan a safe MR-RATE dataset download.
```

## How To Call From The CLI

Use SkillForge commands for the skill and MR-RATE source commands only after
approving download or filesystem side effects:

```text
python -m skillforge info mrrate-dataset-access --json
python -m skillforge evaluate mrrate-dataset-access --json
```

## Inputs And Outputs

Inputs can include:

- Repository selection: native, coreg, atlas, nvseg.
- Batch selector: `all` or comma-separated batch numbers.
- Output base directory.
- Metadata, reports, unzip, delete-zips, and Xet preferences.
- Hugging Face access status.

Outputs can include:

- Download plan.
- Merge plan.
- Backfilled study recovery plan.
- Local structure and join-key explanation.

Output locations:

- Chat response unless the user asks to write a runbook.
- Local dataset paths only when supplied by the user.

## Limitations

Known limitations:

- The skill does not grant gated dataset access.
- It does not verify every file inside an interrupted unzip.
- It does not run network commands unless approved.

Choose another skill when:

- You need raw preprocessing from DICOMs.
- You need model training or inference commands.

## Examples

Beginner example:

```text
Use mrrate-dataset-access to explain the four MR-RATE Hugging Face repositories.
```

Task-specific example:

```text
Plan a metadata-and-reports-only MR-RATE download for batches 00 and 01.
```

Troubleshooting example:

```text
I downloaded coreg and atlas before the backfill. Which recovery path should I use?
```

## Trust And Safety

Risk level:
Medium

Permissions:

- Reads local dataset folder metadata and source docs.
- Proposes commands that may download, unzip, merge, or delete zip archives.
- Requires explicit approval before network downloads or zip deletion.

Data handling:
Treat study folders, metadata, reports, labels, and splits as sensitive
research artifacts even when de-identified.

Writes vs read-only:
Read-only by default. Download, unzip, merge, and delete-zips are side-effectful.

External services:
Hugging Face dataset repositories and optional Xet transfer backend.

Credentials:
The datasets are gated and require authenticated Hugging Face access.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes missing download scenarios, weak status-check guidance,
or unclear storage warnings.

## Contributing

Contributions are welcome by pull request. Update `SKILL.md`, this README, run
`python -m skillforge build-catalog`, and evaluate the changed skill before PR.

## Author

medatasci

Maintainer status:
Draft source-derived SkillForge skill for review.

## Citations

- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- MR-RATE dataset: https://huggingface.co/datasets/Forithmus/MR-RATE
- MR-RATE coreg dataset: https://huggingface.co/datasets/Forithmus/MR-RATE-coreg
- MR-RATE atlas dataset: https://huggingface.co/datasets/Forithmus/MR-RATE-atlas
- MR-RATE nvseg dataset: https://huggingface.co/datasets/Forithmus/MR-RATE-nvseg-ctmr
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/

## Related Skills

- `mrrate-repository-guide`: whole-repo routing.
- `mrrate-registration-derivatives`: registration derivative generation.
- `mrrate-contrastive-pretraining`: training after data is present.
- `mrrate-contrastive-inference`: inference after data and checkpoint are present.
