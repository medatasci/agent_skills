# MR-RATE MRI Preprocessing

Skill ID: `mrrate-mri-preprocessing`

Plan and inspect the MR-RATE native MRI and metadata preprocessing pipeline
from raw DICOM and PACS exports to defaced NIfTI study folders and upload-ready
metadata.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-mri-preprocessing

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
Medical Imaging, Data Preprocessing, Privacy

Collection context:
This skill is the raw MRI and metadata preprocessing branch of the MR-RATE
skill family.

## What This Skill Does

This skill helps Codex plan the YAML-driven MR-RATE preprocessing pipeline:
DICOM-to-NIfTI conversion, PACS metadata filtering, series classification,
modality filtering, HD-BET brain segmentation, Quickshear defacing, study
zipping, metadata preparation, and optional Hugging Face upload.

## Why You Would Call It

Call this skill when:

- You have raw DICOM folder paths and PACS metadata.
- You need to review or fill a MR-RATE batch YAML config.
- You want to understand which source step creates each intermediate artifact.

Use it to:

- Plan `run_mri_preprocessing.py`.
- Plan `run_mri_upload.py`.
- Explain expected outputs and side effects.

Do not use it when:

- You only want to download already-preprocessed MR-RATE data.
- You are working with report preprocessing or contrastive model training.

## Keywords

MR-RATE, DICOM, NIfTI, PACS metadata, modality filtering, HD-BET, Quickshear,
defacing, batch YAML, Hugging Face upload.

## Search Terms

MR-RATE MRI preprocessing, MR-RATE DICOM to NIfTI, MR-RATE defacing,
MR-RATE metadata filtering, MR-RATE run_mri_preprocessing.

## How It Works

Codex reads the batch YAML and source script contracts, then maps user inputs
to steps 1 through 7. It names every side effect before execution: DICOM reads,
NIfTI writes, metadata writes, GPU brain segmentation, defacing, zipping, and
Hugging Face upload.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE MRI preprocessing" --json
python -m skillforge info mrrate-mri-preprocessing --json
python -m skillforge evaluate mrrate-mri-preprocessing --json
```

Important source commands:

```text
python run/run_mri_preprocessing.py --config run/configs/mri_batch00.yaml
python run/run_mri_upload.py --config run/configs/mri_batch00.yaml
```

Important source context:

- `data-preprocessing/run/configs/mri_batch00.yaml`
- `data-preprocessing/environment.yml`
- `data-preprocessing/src/mr_rate_preprocessing/mri_preprocessing/`

## How To Call From An LLM

Ask for the skill by name when planning or reviewing the raw MRI preprocessing
pipeline:

```text
Use mrrate-mri-preprocessing to review this batch YAML before execution.
```

## How To Call From The CLI

Use SkillForge commands for the skill and MR-RATE source commands only after
approving local data processing side effects:

```text
python -m skillforge info mrrate-mri-preprocessing --json
python -m skillforge evaluate mrrate-mri-preprocessing --json
```

## Inputs And Outputs

Inputs can include:

- Batch YAML config.
- DICOM folder path CSV with `FolderPath`.
- PACS metadata CSV.
- Patient mapping and anonymized study-date mapping files.
- Output dirs, GPU device, repo ID, upload flags, and log dir.

Outputs can include:

- Preprocessing plan.
- Config checklist.
- Expected intermediate layout.
- Upload handoff plan.

Output locations:

- Chat response unless the user asks to write a runbook.
- Source pipeline outputs under user-configured raw, interim, processed, and
  log directories when commands are approved.

## Limitations

Known limitations:

- The skill does not execute preprocessing by default.
- It does not prove defacing completeness.
- It does not infer missing metadata columns outside source configs.

Choose another skill when:

- You want dataset consumption rather than raw preprocessing.
- You want registration derivatives after native outputs are ready.

## Examples

Beginner example:

```text
Use mrrate-mri-preprocessing to explain the seven MR-RATE MRI preprocessing steps.
```

Task-specific example:

```text
Review this batch YAML and tell me what will be written before I run it.
```

Troubleshooting example:

```text
Which MR-RATE step creates the classified metadata CSV and which creates the modalities JSON?
```

## Trust And Safety

Risk level:
Medium

Permissions:

- Reads local source files and user-provided config metadata.
- Proposes commands that write NIfTI, masks, metadata, zips, logs, and uploads.
- Requires explicit approval before DICOM processing, GPU work, uploads, or
  data deletion.

Data handling:
Treat raw DICOMs, PACS metadata, accession numbers, mapping spreadsheets, and
intermediate outputs as sensitive.

Writes vs read-only:
Read-only by default. Source commands write many files when run.

External services:
Hugging Face upload is optional and requires credentials outside the skill.

Credentials:
No credentials are needed for planning. Uploads require authenticated Hugging
Face access.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes missing config checks, unclear upload warnings, or
weak explanations of preprocessing outputs.

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
- HD-BET: https://github.com/MIC-DKFZ/HD-BET
- Quickshear: https://github.com/nipy/quickshear
- BrainLesion preprocessing: https://github.com/BrainLesion/preprocessing
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/

## Related Skills

- `mrrate-repository-guide`: whole-repo routing.
- `mrrate-dataset-access`: download already-preprocessed data.
- `mrrate-registration-derivatives`: generate coreg and atlas derivatives.
- `mrrate-report-preprocessing`: process radiology reports.
