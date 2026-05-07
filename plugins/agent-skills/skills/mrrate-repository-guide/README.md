# MR-RATE Repository Guide

Skill ID: `mrrate-repository-guide`

Navigate the full MR-RATE repository and route work to the right specialized
skill without running downloads, uploads, training, inference, or PHI-sensitive
processing by accident.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-repository-guide

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
Medical Imaging, Agent Workflows, Research

Collection context:
This is the top-level skill for the MR-RATE whole-repository skill family.

## What This Skill Does

This skill helps Codex explain the MR-RATE repository structure and decide
which child skill applies to a user task: dataset access, MRI preprocessing,
report preprocessing, registration derivatives, contrastive pretraining, or
contrastive inference.

## Why You Would Call It

Call this skill when:

- You want a whole-repo MR-RATE overview.
- You have an MR-RATE task but are not sure which workflow branch applies.
- You need source-grounded routing before any expensive or sensitive action.

Use it to:

- Choose a child skill.
- Build a whole-repo runbook.
- Explain how dataset, preprocessing, training, and inference pieces connect.

Do not use it when:

- A narrower MR-RATE skill directly matches the task.
- The task is clinical diagnosis, treatment, triage, or patient management.

## Keywords

MR-RATE, repository guide, whole repo, MRI dataset, radiology reports,
contrastive pretraining, zero-shot inference, SkillForge skill family.

## Search Terms

MR-RATE whole repo, MR-RATE repository guide, MR-RATE dataset and model,
MR-RATE workflow router, MR-RATE skill family.

## How It Works

Codex reads the root README, data-preprocessing docs, reports preprocessing
README, dataset guide, backfilled registration guide, and contrastive
pretraining README. It then routes the user to the narrowest source-supported
skill and names side effects before any command is proposed for execution.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE whole repo" --json
python -m skillforge info mrrate-repository-guide --json
python -m skillforge evaluate mrrate-repository-guide --json
```

Important source context:

- MR-RATE source commit inspected: `e02b4ed79ff427fb3578f03242de2d9d51dc709d`.
- Source URL: https://github.com/forithmus/MR-RATE
- Repository license stated in source: CC BY-NC-SA 4.0.

## How To Call From An LLM

Ask for the skill by name when the task spans the whole repository or when the
right MR-RATE child skill is unclear:

```text
Use mrrate-repository-guide to route this MR-RATE task to the right skill.
```

## How To Call From The CLI

Use SkillForge discovery and evaluation commands:

```text
python -m skillforge search "MR-RATE whole repo" --json
python -m skillforge info mrrate-repository-guide --json
python -m skillforge evaluate mrrate-repository-guide --json
```

## Inputs And Outputs

Inputs can include:

- MR-RATE checkout path or GitHub URL.
- User goal and current local artifacts.
- Dataset, preprocessing, training, inference, or report-processing constraints.

Outputs can include:

- Whole-repo orientation.
- Child skill recommendation.
- Source-grounded workflow checklist.
- Safety, data, compute, and license notes.

Output locations:

- Chat response unless the user asks to write a runbook.
- SkillForge report artifacts under `docs/reports/` when generated.

## Limitations

Known limitations:

- This skill routes and explains; it does not wrap MR-RATE source scripts.
- It does not validate clinical correctness.
- It does not grant access to gated datasets or model weights.

Choose another skill when:

- The task is already specific enough for a child skill.
- The user wants to run a source command with stage-specific arguments.

## Examples

Beginner example:

```text
Use mrrate-repository-guide to explain the MR-RATE repo and choose the right child skill.
```

Task-specific example:

```text
Build a source-grounded MR-RATE workflow from dataset download to zero-shot evaluation, but do not run anything.
```

Troubleshooting example:

```text
I have MR-RATE metadata, images, reports, and a checkpoint. Which skill should I use first?
```

## Trust And Safety

Risk level:
Medium

Permissions:

- Reads local source files and user-provided metadata.
- Proposes commands and routes to child skills.
- Requires explicit approval before downloads, uploads, GPU jobs, model access,
  or PHI-sensitive report processing.

Data handling:
Treat local MR-RATE data, reports, mappings, imaging derivatives, checkpoints,
and labels as sensitive research artifacts.

Writes vs read-only:
Read-only by default unless the user asks for generated planning artifacts.

External services:
Child workflows may use Hugging Face, W&B, torch hub, or SLURM.

Credentials:
No credentials are needed for planning. Dataset/model workflows may require
credentials configured outside this skill.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes missing child routing, weak source citations, or
insufficient warnings around gated datasets and model jobs.

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

- `mrrate-dataset-access`: dataset downloads, merges, and local layout.
- `mrrate-mri-preprocessing`: raw MRI and metadata preprocessing.
- `mrrate-report-preprocessing`: radiology report preprocessing skill family.
- `mrrate-registration-derivatives`: coreg and atlas derivatives.
- `mrrate-contrastive-pretraining`: model training.
- `mrrate-contrastive-inference`: zero-shot pathology scoring and evaluation.
