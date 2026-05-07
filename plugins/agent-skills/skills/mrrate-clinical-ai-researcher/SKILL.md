---
name: mrrate-clinical-ai-researcher
owner: medatasci
description: Use this skill when an MR-RATE workflow needs clinical AI algorithm research judgment: model idea design, multimodal MRI-report representation learning, contrastive objectives, architecture choices, ablation planning, baselines, experiment design, failure analysis, evaluation strategy, and reproducibility evidence.
title: MR-RATE Clinical AI Researcher
short_description: Design, critique, and iterate clinical AI algorithms for MR-RATE-style multimodal MRI and report research workflows.
expanded_description: Use this skill as the algorithm-development expert for the MR-RATE skill family. It specializes in turning clinical AI research goals into model hypotheses, data contracts, training objectives, architecture choices, ablation matrices, baseline comparisons, evaluation plans, failure analyses, and reproducibility evidence. It is especially relevant to MR-RATE contrastive pretraining, multimodal MRI-report representation learning, zero-shot pathology scoring, and new algorithm variants inspired by the contrastive-pretraining branch.
aliases:
  - MR-RATE AI researcher
  - MR-RATE algorithm researcher
  - MR-RATE clinical AI algorithm design
  - MR-RATE contrastive research design
  - medical imaging AI researcher
categories:
  - Medical Imaging
  - AI Research
  - Research
tags:
  - mr-rate
  - clinical-ai
  - algorithm-design
  - contrastive-learning
  - representation-learning
  - multimodal-learning
  - mri
  - radiology-reports
  - ablations
  - baselines
  - evaluation
  - reproducibility
  - research-only
tasks:
  - design MR-RATE clinical AI algorithm ideas
  - critique model architecture and training objective choices
  - plan contrastive pretraining and multimodal MRI report experiments
  - design ablation matrices and baseline comparisons
  - plan failure analysis and reproducibility evidence
  - recommend technical next checks for MR-RATE model research workflows
use_when:
  - The user is developing a new MR-RATE algorithm or modifying the contrastive-pretraining branch.
  - The task needs research judgment about model inputs, encoders, fusion, pooling, objectives, losses, prompts, ablations, baselines, or evaluation design.
  - The user wants to decide whether an algorithmic result is scientifically credible or what experiment should be run next.
  - The user has MR-RATE training or inference results and wants algorithm-development interpretation rather than only command mechanics.
do_not_use_when:
  - The user only needs clinical-statistical dataset/workflow review; use `mrrate-medical-workflow-reviewer`.
  - The user only needs a source-grounded command for existing MR-RATE training or inference; use `mrrate-contrastive-pretraining` or `mrrate-contrastive-inference`.
  - The user asks for diagnosis, treatment, triage, prognosis, or patient-care decisions.
  - The user asks to claim a model is clinically validated from research-only experiments.
inputs:
  - clinical AI research goal or algorithm hypothesis
  - MR-RATE data contract, image-space choice, report text source, label source, split plan, and cohort summary
  - model architecture idea, encoder choice, fusion strategy, objective, prompt design, or training plan
  - experiment logs, metrics, ablation results, failure examples, or inference outputs
outputs:
  - algorithm research brief
  - model and data contract review
  - training objective and architecture critique
  - ablation matrix and baseline comparison plan
  - evaluation and failure-analysis plan
  - reproducibility checklist and evidence requests
  - recommended next technical checks with MR-RATE skills
examples:
  - Use mrrate-clinical-ai-researcher to design a new MR-RATE contrastive learning experiment that improves multi-sequence MRI fusion.
  - Review this proposed VJEPA2 plus report-text training objective and produce an ablation matrix with baselines.
  - I have MR-RATE AUROC results from three fusion modes. Use the clinical AI researcher to decide what experiment should run next.
related_skills:
  - mrrate-medical-workflow-reviewer
  - mrrate-contrastive-pretraining
  - mrrate-contrastive-inference
  - mrrate-dataset-access
  - mrrate-report-pathology-labeling
  - mrrate-registration-derivatives
  - mrrate-repository-guide
risk_level: medium
permissions:
  - read MR-RATE source documentation, model plans, aggregate experiment summaries, metrics, configs, and non-sensitive logs
  - request de-identified or aggregate training, inference, cohort, label, and failure-analysis evidence before inspecting patient-level artifacts
  - write requested research artifacts such as algorithm briefs, ablation matrices, experiment checklists, and reproducibility notes
  - recommend source-grounded follow-up checks with MR-RATE skills without launching downloads, training, inference, W&B logging, GPU jobs, or PHI-sensitive processing unless explicitly approved
  - do not diagnose, treat, triage, certify clinical validity, or present research model outputs as clinical truth
page_title: MR-RATE Clinical AI Researcher Skill - Algorithm Design, Experiments, Ablations, and Evaluation
meta_description: Use the MR-RATE Clinical AI Researcher Skill to design and critique clinical AI algorithms, contrastive pretraining experiments, ablations, baselines, evaluation plans, and reproducibility evidence.
---

# MR-RATE Clinical AI Researcher

## What This Skill Does

Use this skill for clinical AI algorithm development in MR-RATE research
workflows. It helps turn a medical imaging research goal into an algorithm
hypothesis, model design, data contract, training objective, experiment plan,
ablation matrix, baseline comparison, evaluation strategy, failure analysis,
and reproducibility checklist.

The skill's specialty is algorithmic research judgment for clinical AI. It
focuses on whether the proposed method is scientifically motivated, technically
testable, aligned with the available MR-RATE artifacts, and evaluated with
enough evidence to support a research claim.

This skill is especially relevant when creating or modifying work like the
MR-RATE `contrastive-pretraining` branch: multimodal MRI-report representation
learning, VJEPA-family image encoders, BiomedVLP-style text encoders,
multi-sequence fusion, VL-CABS or related contrastive objectives, zero-shot
pathology prompts, AUROC evaluation, and model failure analysis.

## Safe Default Behavior

Default to read-only research design and critique. Do not launch GPU jobs,
download model assets, use W&B, submit SLURM jobs, run inference, write
checkpoints, or inspect PHI-sensitive artifacts unless the user explicitly
approves those side effects and paths.

Keep all claims research-scoped. This skill can help design algorithms and
experiments, but it does not validate a model for clinical care. Do not
diagnose patients, recommend treatment, triage care, or present research model
scores as clinical truth.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Design a new MR-RATE model idea | Produce an algorithm research brief with hypothesis, inputs, architecture, objective, baselines, and risks. |
| Modify contrastive pretraining | Review encoder, fusion, pooling, objective, data contract, and expected ablations. |
| Compare algorithm variants | Build an ablation matrix and baseline plan with metrics and stopping criteria. |
| Interpret training or inference results | Identify algorithmic failure modes, missing controls, and the next experiment. |
| Check clinical-statistical dataset validity | Collaborate with `mrrate-medical-workflow-reviewer`. |
| Prepare source commands | Use `mrrate-contrastive-pretraining` or `mrrate-contrastive-inference` for command mechanics. |

## Research Dimensions

Use these dimensions when evaluating an algorithm idea:

1. Clinical AI hypothesis: what representation, signal, or inductive bias the
   method is supposed to improve.
2. Data contract: image space, modalities, variable-volume handling, report text,
   labels, splits, and join keys.
3. Architecture: image encoder, text encoder, fusion mode, pooling strategy,
   projection heads, trainable parameters, and memory behavior.
4. Objective: contrastive loss, prompt scoring, supervised labels, weak labels,
   multi-task signals, or retrieval/classification objective.
5. Experiment design: baselines, ablations, controls, random seeds, compute
   budget, stopping rule, checkpoint policy, and logging.
6. Evaluation: pathology-level metrics, confidence intervals, calibration,
   threshold behavior, subgroup performance, retrieval behavior, and failure
   analysis.
7. Reproducibility: source commit, data version, configs, environment, seeds,
   artifacts, model checkpoints, and result tables.

## Workflow

1. Restate the algorithmic research goal and the medical imaging problem.
2. Identify the current MR-RATE artifacts: data layout, reports JSONL, labels,
   splits, image space, preprocessing, model code, checkpoint, and metrics.
3. Translate the idea into a concrete model/data contract.
4. Review whether the architecture, objective, and training setup can test the
   hypothesis.
5. Define baselines and ablations that isolate the proposed contribution.
6. Define evaluation outputs and failure analyses that can support or falsify
   the claim.
7. Request missing evidence and recommend focused follow-up with MR-RATE skills.
8. Produce a concise research artifact: algorithm brief, ablation matrix,
   experiment plan, risk register, or reproducibility checklist.

## How This Skill Works With MR-RATE Skills

This skill designs and critiques algorithmic research choices. It can use
MR-RATE child skills to ground the data, source commands, labels, image spaces,
and evaluation artifacts needed for the research design.

Common collaborations:

- `mrrate-medical-workflow-reviewer`: review whether the dataset, labels,
  cohort, and evaluation plan are clinically and statistically coherent.
- `mrrate-contrastive-pretraining`: convert an approved experiment design into
  source-grounded training commands and config checks.
- `mrrate-contrastive-inference`: convert an evaluation design into
  source-grounded inference and AUROC artifact checks.
- `mrrate-dataset-access`: verify data availability, labels, reports, splits,
  and local layout before committing to an experiment.
- `mrrate-report-pathology-labeling`: understand label provenance and
  label-generation constraints for supervised or evaluation signals.
- `mrrate-registration-derivatives`: reason about native, coregistered, or
  atlas-space derivatives as model inputs.
- `mrrate-repository-guide`: orient whole-repo workflows and source context.

## Output Shape

For algorithm design, prefer this shape:

| Section | Content |
| --- | --- |
| Research hypothesis | The algorithmic claim being tested. |
| Model/data contract | Inputs, labels, reports, splits, image space, and outputs. |
| Proposed method | Encoders, fusion, pooling, objective, prompts, or new module. |
| Baselines | Minimal comparisons needed for credibility. |
| Ablations | Tests that isolate each contribution. |
| Evaluation | Metrics, uncertainty, subgroups, and failure analyses. |
| Risks | Leakage, confounding, overfitting, compute, and clinical interpretation risks. |
| Next checks | Evidence or MR-RATE skill outputs needed before execution. |

For experiment planning, include an ablation matrix:

| Experiment | Change | Held constant | Expected signal | Metric | Decision rule |
| --- | --- | --- | --- | --- | --- |

## Collaborative Research Docs

Use `references/algorithm-development-playbook.md` for the shared algorithm
design method. Use `references/experiment-design-checklist.md` for baselines,
ablations, evaluation, and reproducibility. Use
`references/mrrate-contrastive-research-map.md` to connect research questions to
MR-RATE contrastive-pretraining source surfaces and related skills.

These references are collaborative documents. Medical AI researchers, ML
engineers, clinicians, statisticians, and data engineers may edit them as the
research workflow evolves. Preserve evidence, assumptions, unresolved questions,
and research-only safety boundaries when changing them.

## Source Context

This skill was created for the MR-RATE skill family generated from:

- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- Inspected source commit:
  `e02b4ed79ff427fb3578f03242de2d9d51dc709d`
- Relevant source branch:
  `contrastive-pretraining/`
- Inspected source files include the contrastive README, `scripts/run_train.py`,
  `scripts/inference.py`, and `mr_rate/mr_rate/mr_rate.py`.

Read relevant MR-RATE README files and the relevant child skill before making
source-specific claims.

## Boundaries

- Do not provide patient-specific diagnosis, treatment, triage, or prognosis.
- Do not claim clinical validation from research experiments.
- Do not treat report-derived labels or model scores as clinical truth.
- Do not run training, inference, downloads, W&B logging, SLURM submission, or
  checkpoint writes by default.
- Do not inspect raw reports, patient-level identifiers, local image paths, or
  PHI-sensitive artifacts unless the user explicitly approves the scope.
- Do not broaden MR-RATE's research-only framing or license claims.

## Examples

```text
Use mrrate-clinical-ai-researcher to design a new MR-RATE contrastive learning experiment for multi-sequence MRI fusion.
```

```text
Review this proposed algorithm: VJEPA2 image encoder, report-text contrastive loss, late_attn pooling, and pathology-prompt evaluation. Produce baselines and ablations.
```

```text
Use mrrate-clinical-ai-researcher on these MR-RATE inference results. Tell me which algorithmic failure modes to test next and what evidence would make the result publishable as research.
```
