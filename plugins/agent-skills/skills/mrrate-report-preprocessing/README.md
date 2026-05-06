# MR-RATE Report Preprocessing

Skill ID: `mrrate-report-preprocessing`

Plan and operate the MR-RATE radiology report preprocessing workflow as a
source-grounded sequence of stages, without guessing commands or overclaiming
clinical validity.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-report-preprocessing

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
Medical Imaging, Data Preprocessing, Agent Workflows

Collection context:
This is the umbrella skill for the MR-RATE `reports_preprocessing` skill family.
Use child skills for narrow execution planning.

## What This Skill Does

This skill helps Codex map the MR-RATE report preprocessing source tree into a
safe runbook: anonymization, translation, translation QC, structuring,
structure QC, pathology labeling, and shard merging.

## Why You Would Call It

Call this skill when:

- You want to understand the whole MR-RATE report preprocessing pipeline.
- You need to decide which stage or child skill applies next.
- You want source-supported commands and approval gates before model jobs run.

Use it to:

- Build a staged run plan.
- Check inputs and outputs for each report preprocessing stage.
- Route to narrower skills for stage-specific details.

Do not use it when:

- A single child skill directly matches the task.
- The task is clinical diagnosis, treatment, triage, or patient management.

## Keywords

MR-RATE, radiology reports, report preprocessing, Turkish reports, Qwen, vLLM,
SLURM, anonymization, translation QC, report structuring, pathology labels.

## Search Terms

MR-RATE reports pipeline, plan MR-RATE report preprocessing, run Turkish MRI
report preprocessing, source-grounded MR-RATE report workflow, reports_preprocessing.

## How It Works

Codex reads the README chain and source script contracts, identifies the current
artifact, and routes to the correct child skill. It keeps the source loop intact:
run, automated QC, retry or fallback, re-QC, then manual review.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE reports preprocessing" --json
python -m skillforge info mrrate-report-preprocessing --json
python -m skillforge evaluate mrrate-report-preprocessing --json
```

Important source context:

- MR-RATE repo commit inspected: `e02b4ed79ff427fb3578f03242de2d9d51dc709d`.
- Source path: `data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing`.
- Report environment: `environment_reports.yml` with Python 3.11, PyTorch CUDA
  12.6, vLLM, Transformers, Pandas, tqdm, and Hugging Face Hub.

## Inputs And Outputs

Inputs can include:

- Local MR-RATE checkout path.
- Current stage and available CSV/shard directories.
- Runtime constraints such as SLURM ranks, GPUs, model cache, and output paths.

Outputs can include:

- Stage run plan.
- Command sequence.
- Input/output checklist.
- Child skill recommendation.

Output locations:

- Chat response unless the user asks to write a runbook.
- SkillForge report artifacts under `docs/reports/` when generated.

## Limitations

Known limitations:

- The skill plans and explains; it does not itself wrap the MR-RATE scripts.
- It does not validate clinical correctness.
- The source tree does not include redistributable sample report fixtures.

Choose another skill when:

- You need a narrow stage: use a child skill.
- You need dataset download guidance: use a dataset or Hugging Face skill.

## Examples

Beginner example:

```text
Use mrrate-report-preprocessing to explain the MR-RATE reports_preprocessing stages.
```

Task-specific example:

```text
Plan a safe command sequence from anonymized Turkish reports to pathology labels, but do not run GPU jobs.
```

Troubleshooting example:

```text
I have structure shards and QC shards. Which MR-RATE report skill should I use next?
```

## Trust And Safety

Risk level:
Medium

Permissions:

- Reads local source files and user-provided file metadata.
- Proposes commands that may write outputs when run.
- Requires explicit approval before running GPU/vLLM jobs, downloading models,
  or processing PHI-bearing report text.

Data handling:
Treat raw reports, token mappings, translated reports, structured reports, and
labels as sensitive research artifacts.

Writes vs read-only:
Read-only by default unless the user asks to write a runbook or generated files.

External services:
The source scripts may use Hugging Face model access depending on local cache.

Credentials:
No credentials are needed for planning. Running source scripts may require model
or dataset access configured outside this skill.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes missing stage routing, weak command examples, or
insufficient safety guidance around PHI or model downloads.

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
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/

## Related Skills

- `mrrate-report-anonymization`: anonymization and PHI QC stage.
- `mrrate-report-translation-qc`: translation, language detection, and retranslation.
- `mrrate-report-structuring-qc`: section extraction and structure QC.
- `mrrate-report-pathology-labeling`: 37-label pathology classification.
- `mrrate-report-shard-operations`: merge and inspect per-rank outputs.

