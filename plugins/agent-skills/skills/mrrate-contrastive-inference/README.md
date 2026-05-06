# MR-RATE Contrastive Inference

Skill ID: `mrrate-contrastive-inference`

Plan MR-RATE zero-shot pathology inference and evaluation from trained
contrastive checkpoints, including pathology prompt files, labels CSVs, split
filtering, score outputs, and AUROC reports.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-contrastive-inference

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
Medical Imaging, Model Inference, Evaluation

Collection context:
This skill is the contrastive inference and evaluation branch of the MR-RATE
skill family.

## What This Skill Does

This skill helps Codex plan MR-RATE zero-shot pathology scoring. The source
inference script compares positive and negative pathology prompts, writes
per-subject scores, and computes AUROC outputs when labels are supplied.

## Why You Would Call It

Call this skill when:

- You have a trained MR-RATE checkpoint and want pathology scores.
- You need to evaluate scores against a labels CSV.
- You want to understand inference artifacts such as `scores.json` or
  `predicted_scores.npz`.

Use it to:

- Build a source-grounded inference command.
- Check pathology prompt and labels contracts.
- Explain output files and research-only interpretation.

Do not use it when:

- You need to train a checkpoint first.
- You want LLM-derived labels from reports instead of model inference.

## Keywords

MR-RATE, inference, zero-shot pathology, pathology prompts, labels CSV,
predicted_scores.npz, scores.json, AUROC, evaluation.

## Search Terms

MR-RATE inference, MR-RATE zero-shot pathology, MR-RATE AUROC evaluation,
MR-RATE predicted scores, MR-RATE scores json.

## How It Works

Codex reads the inference README section and source scripts, checks the input
contracts, and prepares an inference plan. It keeps the source boundary visible:
the inspected `inference.py` initializes `VJEPA2Encoder` and does not expose a
generic `--encoder` CLI flag.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE zero-shot inference" --json
python -m skillforge info mrrate-contrastive-inference --json
python -m skillforge evaluate mrrate-contrastive-inference --json
```

Important source command:

```text
python scripts/inference.py --fusion_mode late --pooling_strategy simple_attn --weights_path ./mr_rate_results/MrRate.5000.pt --data_folder /path/to/data --jsonl_file /path/to/reports.jsonl --pathologies_file data/pathologies.json --labels_file /path/to/labels.csv --splits_csv /path/to/splits.csv --split test --results_folder ./inference_results
```

Important source context:

- `contrastive-pretraining/scripts/inference.py`
- `contrastive-pretraining/scripts/eval.py`
- `contrastive-pretraining/scripts/data_inference.py`
- `contrastive-pretraining/data/pathologies.json`

## How To Call From An LLM

Ask for the skill by name when planning zero-shot scoring or evaluation:

```text
Use mrrate-contrastive-inference to plan test-split pathology scoring.
```

## How To Call From The CLI

Use SkillForge commands for the skill and MR-RATE source inference commands
only after approving checkpoint loading and output writes:

```text
python -m skillforge info mrrate-contrastive-inference --json
python -m skillforge evaluate mrrate-contrastive-inference --json
```

## Inputs And Outputs

Inputs can include:

- Checkpoint weights path.
- Data folder.
- Report JSONL file.
- Pathology prompts JSON.
- Labels CSV.
- Optional splits CSV, split, image space, normalizer, fusion mode, and pooling
  strategy.

Outputs can include:

- Inference command plan.
- Output artifact checklist.
- AUROC explanation.
- Research-scope interpretation notes.

Output locations:

- Chat response unless the user asks to write a runbook.
- `--results_folder` when source commands are approved.

## Limitations

Known limitations:

- The skill does not run inference by default.
- It does not claim clinical validity.
- It does not assume public model weights are available.
- The inspected source inference CLI is VJEPA2-specific.

Choose another skill when:

- You need to train a checkpoint.
- You need report-derived LLM pathology labels.

## Examples

Beginner example:

```text
Use mrrate-contrastive-inference to explain MR-RATE zero-shot pathology scoring.
```

Task-specific example:

```text
Plan inference for the test split using this checkpoint and data folder, but do not run it.
```

Troubleshooting example:

```text
What is the difference between `scores.json`, `predicted_scores.npz`, and `aurocs.xlsx`?
```

## Trust And Safety

Risk level:
Medium

Permissions:

- Reads local source files and user-provided inference metadata.
- Proposes commands that may run GPU inference and write scores or evaluation
  outputs.
- Requires approval before running inference or loading private checkpoints.

Data handling:
Treat images, reports JSONL, labels, checkpoints, and prediction outputs as
sensitive research artifacts.

Writes vs read-only:
Read-only by default. Inference writes output arrays, JSON, text, and optional
spreadsheet or CSV metrics.

External services:
None required for planning. Runtime may require local model dependencies and
previously downloaded weights.

Credentials:
No credentials are needed for planning. Dataset/model access may require
credentials outside this skill.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes missing artifact explanations, weak labels checks, or
unclear warnings about research-only interpretation.

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
- MR-RATE pathology labels: https://huggingface.co/datasets/Forithmus/MR-RATE/blob/main/pathology_labels/mrrate_labels.csv
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/

## Related Skills

- `mrrate-repository-guide`: whole-repo routing.
- `mrrate-contrastive-pretraining`: train checkpoints.
- `mrrate-dataset-access`: get data and labels.
- `mrrate-report-pathology-labeling`: generate report-derived labels.
