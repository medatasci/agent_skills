# MR-RATE Contrastive Pretraining

Skill ID: `mrrate-contrastive-pretraining`

Plan MR-RATE contrastive vision-language training with source-supported
encoders, fusion modes, report JSONL inputs, image spaces, Accelerate launches,
SLURM submission, checkpoints, and logging.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-contrastive-pretraining

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
Medical Imaging, Model Training, Research

Collection context:
This skill is the contrastive training branch of the MR-RATE skill family.

## What This Skill Does

This skill helps Codex plan MR-RATE contrastive pretraining. The source model
aligns variable numbers of MRI volumes per study with radiology report
sentences using VJEPA-family image encoders and a BiomedVLP-CXR-BERT text
encoder.

## Why You Would Call It

Call this skill when:

- You want to train or fine-tune MR-RATE.
- You need to choose `vjepa2`, `vjepa21`, or sliding variants.
- You need to choose fusion mode, pooling strategy, image space, or normalizer.
- You need an Accelerate or SLURM launch plan.

Use it to:

- Build a source-grounded training command.
- Review data contracts before GPU training.
- Explain checkpoint resume and W&B behavior.

Do not use it when:

- You already have a checkpoint and want inference.
- You only need dataset download guidance.

## Keywords

MR-RATE, contrastive pretraining, VJEPA2, VJEPA 2.1, BiomedVLP-CXR-BERT,
VL-CABS, LoRA, Accelerate, SLURM, W&B.

## Search Terms

MR-RATE contrastive training, MR-RATE VJEPA2 pretraining, MR-RATE fusion modes,
MR-RATE submit_train, MR-RATE Accelerate launch.

## How It Works

Codex reads the contrastive pretraining README and training scripts, confirms
data and model settings, and prepares commands without launching GPU work. It
keeps source constraints visible: VJEPA 2.1 needs a checkpoint, sliding
encoders use chunking, and `late_attn` uses a pooling strategy.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE contrastive training" --json
python -m skillforge info mrrate-contrastive-pretraining --json
python -m skillforge evaluate mrrate-contrastive-pretraining --json
```

Important source commands:

```text
accelerate launch --multi_gpu --num_processes 4 scripts/run_train.py --encoder vjepa2 --fusion_mode late --data_folder /path/to/data --jsonl_file /path/to/reports.jsonl --normalizer percentile
FUSION_MODE=late_attn POOLING_STRATEGY=cross_attn NUM_TRAIN_STEPS=50000 sbatch scripts/submit_train.sh
```

Important source context:

- `contrastive-pretraining/scripts/run_train.py`
- `contrastive-pretraining/scripts/submit_train.sh`
- `contrastive-pretraining/scripts/data.py`
- `contrastive-pretraining/mr_rate/mr_rate/mr_rate.py`
- `contrastive-pretraining/vision_encoder/`

## How To Call From An LLM

Ask for the skill by name when planning training or reviewing encoder/fusion
settings:

```text
Use mrrate-contrastive-pretraining to plan a late-fusion VJEPA2 training run.
```

## How To Call From The CLI

Use SkillForge commands for the skill and MR-RATE source training commands only
after approving GPU, model-download, logging, and checkpoint side effects:

```text
python -m skillforge info mrrate-contrastive-pretraining --json
python -m skillforge evaluate mrrate-contrastive-pretraining --json
```

## Inputs And Outputs

Inputs can include:

- Data folder.
- Report JSONL file.
- Encoder, fusion mode, pooling strategy, image space, and normalizer.
- Optional splits CSV, split, VJEPA 2.1 checkpoint, pretrained weights, W&B
  settings, and results folder.

Outputs can include:

- Training command plan.
- SLURM environment-variable plan.
- Data contract checklist.
- Checkpoint and resume explanation.

Output locations:

- Chat response unless the user asks to write a runbook.
- Training outputs under `--results_folder` when source commands are approved.

## Limitations

Known limitations:

- The skill does not launch training by default.
- It does not confirm checkpoint compatibility unless files are provided.
- It does not claim model weights are publicly available; the root README says
  model weights are coming soon.

Choose another skill when:

- You want inference or AUROC evaluation from a checkpoint.
- You want report-derived LLM pathology labels.

## Examples

Beginner example:

```text
Use mrrate-contrastive-pretraining to explain MR-RATE encoders and fusion modes.
```

Task-specific example:

```text
Plan a late-fusion VJEPA2 training command on native-space data with percentile normalization.
```

Troubleshooting example:

```text
Why does vjepa21_sliding require a checkpoint path, and where does chunk_size apply?
```

## Trust And Safety

Risk level:
Medium

Permissions:

- Reads local source files and user-provided training metadata.
- Proposes commands that may download models, run GPUs, write checkpoints, and
  log to W&B.
- Requires approval before training, model downloads, W&B logging, or network
  access.

Data handling:
Treat training images, reports JSONL, splits, checkpoints, and logs as
sensitive research artifacts.

Writes vs read-only:
Read-only by default. Training writes checkpoints and logs.

External services:
Hugging Face, torch hub, W&B, and SLURM may be involved depending on command.

Credentials:
No credentials are needed for planning. Dataset/model access and W&B may
require credentials.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes missing argument coverage, confusing launch examples,
or weak warnings around model downloads and logging.

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
- VJEPA2: https://huggingface.co/facebook/vjepa2-vitg-fpc64-384
- BiomedVLP-CXR-BERT-specialized: https://huggingface.co/microsoft/BiomedVLP-CXR-BERT-specialized
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/

## Related Skills

- `mrrate-repository-guide`: whole-repo routing.
- `mrrate-dataset-access`: get data before training.
- `mrrate-contrastive-inference`: run inference after training.
- `mrrate-report-preprocessing`: produce structured reports and labels.
