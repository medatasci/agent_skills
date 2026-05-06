# MR-RATE Registration Derivatives

Skill ID: `mrrate-registration-derivatives`

Plan and inspect MR-RATE co-registration and atlas-registration derivative
workflows, including partitioned runs, upload zipping, and backfilled study
recovery.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-registration-derivatives

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
Medical Imaging, Registration, Data Preprocessing

Collection context:
This skill is the registration-derivatives branch of the MR-RATE skill family.

## What This Skill Does

This skill helps Codex plan MR-RATE coreg and atlas derivative generation. The
source registration script uses ANTs to align moving modalities to a T1w center
modality and map volumes into MNI152 atlas space.

## Why You Would Call It

Call this skill when:

- You have native processed study folders and metadata with center modality flags.
- You need to run or split a registration job.
- You need to zip/upload coreg or atlas derivative outputs.
- You need to recover backfilled registration studies.

Use it to:

- Plan `registration.py`.
- Plan `registration/upload.py`.
- Explain coreg, atlas, and transform output layouts.

Do not use it when:

- Native preprocessed data does not exist yet.
- You only want to consume downloaded derivatives.

## Keywords

MR-RATE, registration, ANTs, co-registration, coreg, atlas, MNI152, transforms,
backfilled registration studies.

## Search Terms

MR-RATE registration, MR-RATE coreg upload, MR-RATE atlas registration,
MR-RATE backfilled coreg atlas, MR-RATE registration partition.

## How It Works

Codex checks the source input contract, metadata requirements, and output
layout before proposing commands. It separates compute-heavy registration from
upload/zipping and names cleanup or delete behavior before execution.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE registration" --json
python -m skillforge info mrrate-registration-derivatives --json
python -m skillforge evaluate mrrate-registration-derivatives --json
```

Important source commands:

```text
python src/mr_rate_preprocessing/registration/registration.py --input-dir data/MR-RATE/mri/batchXX --metadata-csv data/MR-RATE/metadata/batchXX_metadata.csv --output-dir data/MR-RATE-reg --num-processes 4 --threads-per-process 4
python src/mr_rate_preprocessing/registration/upload.py --input-dir data/MR-RATE-reg/MR-RATE-coreg_batchXX --zip-suffix _coreg --repo-id Forithmus/MR-RATE-coreg
python scripts/hf/download_backfilled_reg_studies.py --json-path scripts/hf/backfilled_reg_study_ids.json --output-base ./data --coreg --atlas
```

## How To Call From An LLM

Ask for the skill by name when planning registration, upload, or backfill
recovery:

```text
Use mrrate-registration-derivatives to plan this coreg and atlas registration run.
```

## How To Call From The CLI

Use SkillForge commands for the skill and MR-RATE source commands only after
approving registration, upload, or download side effects:

```text
python -m skillforge info mrrate-registration-derivatives --json
python -m skillforge evaluate mrrate-registration-derivatives --json
```

## Inputs And Outputs

Inputs can include:

- Native processed study input directory.
- Metadata CSV with `study_uid`, `series_id`, and `is_center_modality`.
- Output directory, process count, thread count, and partition settings.
- Upload repo ID, zip suffix, worker counts, and Xet setting.

Outputs can include:

- Registration command plan.
- Partitioned run plan.
- Coreg and atlas output checklist.
- Upload or backfilled recovery plan.

Output locations:

- Chat response unless the user asks to write a runbook.
- Source pipeline outputs under user-specified registration and zip dirs.

## Limitations

Known limitations:

- The skill does not run ANTs by default.
- It does not validate image registration quality.
- It does not assume credentials or atlas resources are available.

Choose another skill when:

- You need raw preprocessing.
- You need dataset download and merge guidance only.

## Examples

Beginner example:

```text
Use mrrate-registration-derivatives to explain the coreg and atlas output folders.
```

Task-specific example:

```text
Plan a partitioned MR-RATE registration run with eight partitions and no upload.
```

Troubleshooting example:

```text
I downloaded MR-RATE-coreg before the backfill. How do I get the missing studies?
```

## Trust And Safety

Risk level:
Medium

Permissions:

- Reads source files and user-provided registration metadata.
- Proposes commands that write registered images, transforms, zips, and uploads.
- Requires approval before ANTs runs, uploads, or deleting zips.

Data handling:
Treat registered images, masks, and transforms as sensitive research artifacts.

Writes vs read-only:
Read-only by default. Source commands write large derivative datasets.

External services:
Hugging Face upload or download when requested.

Credentials:
Uploads and gated downloads require authenticated Hugging Face access.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes missing partition examples, unclear output checks, or
insufficient warnings about upload/delete side effects.

## Contributing

Contributions are welcome by pull request. Update `SKILL.md`, this README, run
`python -m skillforge build-catalog`, and evaluate the changed skill before PR.

## Author

medatasci

Maintainer status:
Draft source-derived SkillForge skill for review.

## Citations

- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- MR-RATE coreg dataset: https://huggingface.co/datasets/Forithmus/MR-RATE-coreg
- MR-RATE atlas dataset: https://huggingface.co/datasets/Forithmus/MR-RATE-atlas
- ANTs: https://github.com/ANTsX/ANTs
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/

## Related Skills

- `mrrate-repository-guide`: whole-repo routing.
- `mrrate-mri-preprocessing`: native preprocessing before registration.
- `mrrate-dataset-access`: consume downloaded derivatives.
- `mrrate-contrastive-pretraining`: train on available image spaces.
