# Experiment Design And Reproducibility Checklist

This checklist supports `mrrate-clinical-ai-researcher`. It is designed for
planning and reviewing MR-RATE clinical AI experiments before expensive runs
and after results arrive.

## 1. Experiment Card

Fill this out before running:

```text
Experiment name:
Research hypothesis:
Expected contribution:
Baseline:
Primary comparison:
Data version:
Source commit:
Training split:
Validation split:
Test split:
Model-selection rule:
Primary metric:
Secondary metrics:
Ablations:
Failure analyses:
Compute budget:
Stopping rule:
Owner:
```

## 2. Pre-Run Checks

- Is the hypothesis specific enough to test?
- Is the baseline already runnable and comparable?
- Is the proposed change isolated from unrelated config changes?
- Are data, reports, labels, and splits fixed before training?
- Are patient-level split rules and leakage checks documented?
- Are source commit, environment, and command template recorded?
- Are W&B, checkpoint, and output paths named safely and clearly?
- Is the compute budget adequate for the planned baselines and ablations?
- Are side effects approved: GPU jobs, downloads, W&B logging, checkpoint
  writes, and output directories?

## 3. Model/Data Contract

Record:

- Data folder.
- Image space.
- Reports JSONL.
- Labels CSV.
- Splits CSV.
- Pathologies or prompt file.
- Encoder.
- Fusion mode.
- Pooling strategy.
- Normalizer.
- Batch size and number of train steps.
- Checkpoint and resume behavior.
- Output directory.

Questions:

- Do all artifacts use the same cohort and join keys?
- Are training, validation, and test inputs separated as intended?
- Are labels used only in the stages where they are allowed?
- Are prompt and label names stable across runs?

## 4. Baseline Plan

A baseline is credible when it is:

- run on the same cohort and split
- evaluated with the same code and prompts
- selected using the same validation policy
- given a comparable compute budget
- reproducible from recorded configs

Recommended baseline table:

| Baseline | Purpose | Same data? | Same evaluation? | Notes |
| --- | --- | --- | --- | --- |

## 5. Ablation Matrix

Use this table before running ablations:

| Experiment | Change | Held constant | Expected signal | Metric | Decision rule |
| --- | --- | --- | --- | --- | --- |

Checklist:

- Does each ablation change one thing?
- Does the ablation remove or isolate the claimed contribution?
- Are seeds and compute budgets comparable?
- Are evaluation prompts and labels unchanged?
- Are expected outcomes written down before results arrive?
- Is there a plan for negative or inconclusive results?

## 6. Evaluation Plan

Before test evaluation:

- Is the test split untouched by model selection?
- Are positive and negative counts known for each pathology?
- Is AUROC appropriate for the claim?
- Is AUPRC needed for rare labels?
- Are sensitivity, specificity, threshold, or calibration analyses needed?
- Are confidence intervals or bootstrap summaries planned?
- Are subgroup analyses planned?
- Are failure examples summarized without exposing PHI?

Recommended result table:

| Label or subgroup | N positive | N negative | Metric | CI or uncertainty | Notes |
| --- | --- | --- | --- | --- | --- |

## 7. Failure Analysis

Plan failure analysis before looking at examples:

- Which labels regress?
- Which labels improve?
- Are failures concentrated by anatomy, image space, sequence count, modality,
  batch, preprocessing status, or cohort subgroup?
- Are failures related to label ambiguity or prompt wording?
- Are false positives clinically plausible unlabeled positives?
- Are false negatives due to missing sequence, poor coverage, small lesions,
  postoperative anatomy, motion, or report-label mismatch?
- Is model behavior different between native, coregistered, and atlas inputs?

Evidence to request:

- Score distributions.
- Per-label confusion or threshold summaries.
- Subgroup metric table.
- Failure case summaries with de-identified or aggregate descriptors.
- Comparison against baseline failures.

## 8. Reproducibility Package

A reproducibility package should include:

- Source commit.
- Skill and MR-RATE source context.
- Environment summary.
- Commands or configs.
- Data version and artifact manifest.
- Split and label files.
- Prompt/pathology files.
- Random seeds.
- Checkpoint map.
- Training logs.
- Evaluation outputs.
- Result summary.
- Known failed runs and excluded runs.

## 9. Post-Run Review

After results arrive:

- Did the primary metric improve over the baseline?
- Did clinically important labels or subgroups regress?
- Are improvements larger than expected run-to-run variance?
- Are confidence intervals compatible with the claim?
- Do ablations support the proposed mechanism?
- Could leakage, preprocessing differences, prompts, or label changes explain
  the result?
- Are failure cases consistent with the hypothesis?
- What is the next experiment: replicate, ablate further, fix data, change
  objective, or stop?

## 10. Decision Summary

Use this short summary when closing an experiment:

```text
Decision:
Evidence supporting the decision:
Evidence against the decision:
Most important unresolved risk:
Next experiment:
Artifacts to preserve:
```
