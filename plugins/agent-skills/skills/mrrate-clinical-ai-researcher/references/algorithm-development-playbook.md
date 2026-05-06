# Collaborative Algorithm Development Playbook

This playbook supports `mrrate-clinical-ai-researcher`. It is a living research
document for designing, critiquing, and iterating MR-RATE clinical AI
algorithms.

Use it when an idea needs to become a testable experiment: a model change,
training objective, fusion strategy, prompt design, supervised head, retrieval
task, representation-learning method, or evaluation improvement.

## How To Edit This Playbook

This playbook may be edited collaboratively by clinical AI researchers, ML
engineers, clinicians, statisticians, and data engineers.

When editing:

- Put high-value design questions near the top of each section.
- Keep guidance concrete enough to become an experiment, ablation, or evidence
  request.
- Preserve assumptions, unresolved questions, negative results, and failed
  ideas when they are useful.
- Add source references, config names, or artifact paths when a rule depends on
  MR-RATE implementation details.
- Keep patient-care and clinical-validation claims out of the playbook.
- Prefer aggregate or de-identified research artifacts.

Recommended research note format:

```text
Research idea:
Clinical AI hypothesis:
Expected contribution:
Data contract:
Architecture change:
Objective or supervision:
Baselines:
Ablations:
Evaluation:
Risks:
Evidence needed before execution:
```

## 1. Research Hypothesis

- What representation, signal, or inductive bias should improve?
- What is the medical imaging problem the algorithm is trying to solve?
- Is the method intended to improve retrieval, zero-shot classification,
  pathology scoring, multi-sequence fusion, robustness, calibration,
  efficiency, or transfer?
- What specific result would support the hypothesis?
- What result would falsify it?
- Is the claim distinguishable from data scale, preprocessing, prompt wording,
  label quality, or training stability?

Evidence to request:

- One-paragraph algorithm hypothesis.
- Baseline being improved.
- Expected improvement target.
- Failure case the method is designed to address.

## 2. Model And Data Contract

- Which image artifacts are inputs: native, coregistered, atlas, segmentation,
  or another derivative?
- Which anatomy and modality/sequence groups are expected?
- How are variable numbers of volumes represented?
- Which report text is used for supervision?
- Are report sentences, full findings, labels, prompts, or structured outputs
  used?
- Which identifiers join images, reports, labels, splits, and outputs?
- Which split is used for training, validation, model selection, and final
  evaluation?
- What files should the experiment produce?

Evidence to request:

- Data layout summary.
- Reports JSONL contract.
- Labels CSV or pathology prompt contract.
- Split table summary.
- Output artifact manifest.

## 3. Architecture Design

- Which image encoder is used and why?
- Which text encoder is used and why?
- Which parts are frozen, adapted with LoRA, or fully trained?
- How does the method handle depth: temporal CNN, sliding chunks, resampling, or
  another design?
- How does the method handle multiple MRI volumes: early, mid, late, learned
  attention, cross attention, gating, or another fusion?
- Are projection heads, latent dimensions, and temperature parameters matched
  across comparisons?
- Is memory behavior understood for the planned batch size and volume count?
- Does the architecture create a path for leakage or shortcut learning?

Evidence to request:

- Architecture diagram or short description.
- Trainable parameter counts.
- Encoder/fusion/pooling settings.
- Memory estimate or small smoke-test result.
- Config diff from baseline.

## 4. Objective And Supervision

- What objective is optimized?
- Does the objective match the research claim?
- Are reports used as weak supervision, labels used as targets, prompts used for
  evaluation, or multiple signals combined?
- Could report-derived labels leak into evaluation?
- Are negative examples reliable enough for the intended loss or metric?
- Does the loss handle multiple report sentences per study correctly?
- Are positives and negatives balanced or sampled in a way that changes the
  clinical target?
- Is the objective robust to noisy report text or uncertain labels?

Evidence to request:

- Loss definition.
- Supervision source.
- Sampling strategy.
- Positive/negative construction.
- Label and report provenance.

## 5. Baselines

- What is the minimal source-supported baseline?
- Is there a no-change baseline using the existing MR-RATE configuration?
- Is there a simpler baseline that would explain the same improvement?
- Are baselines run with the same data, split, seeds, compute budget, and
  evaluation code?
- Are baseline checkpoints selected using the same rule?
- Are negative results preserved?

Common baseline types:

- Existing MR-RATE contrastive configuration.
- Simpler fusion method.
- Frozen encoder vs LoRA-adapted encoder.
- Native vs coregistered or atlas-space input.
- Prompt-only or label-frequency baseline for evaluation context.
- Supervised linear probe or simple classifier when appropriate.

## 6. Ablation Design

- Which component is the proposed contribution?
- Which variables must be held constant to isolate it?
- What ablation removes the new component?
- What ablation changes only one design choice?
- What ablation tests whether the method is robust to prompt, split, or
  preprocessing changes?
- How many seeds are needed for the decision?
- What metric and decision rule determine whether the ablation supports the
  claim?

Recommended matrix:

| Experiment | Change | Held constant | Expected signal | Metric | Decision rule |
| --- | --- | --- | --- | --- | --- |

## 7. Evaluation And Failure Analysis

- Which metrics directly test the research claim?
- Are pathology-level metrics reported, not only averages?
- Are confidence intervals or bootstrap summaries needed?
- Are rare labels treated carefully?
- Are thresholds, calibration, sensitivity, specificity, or AUPRC relevant?
- Are failure cases inspected by cohort, anatomy, modality, sequence count,
  image space, label prevalence, or report characteristics?
- Are improvements concentrated in easy or confounded cases?
- Are subgroup regressions visible?

Evidence to request:

- Per-label metric table.
- Prevalence by split and label.
- Confidence intervals where possible.
- Score distributions.
- Failure case summaries.
- Subgroup metrics.

## 8. Reproducibility

- Is the MR-RATE source commit recorded?
- Are data version, batch list, labels, reports, splits, and preprocessing
  artifacts recorded?
- Are configs, command lines, environment, package versions, and seeds recorded?
- Are checkpoints and logs named with enough context?
- Are model-selection and stopping rules stated before test evaluation?
- Are result tables traceable to specific runs?
- Are failed runs and excluded runs documented?

Evidence to request:

- Run manifest.
- Config file or command.
- Source commit.
- Environment summary.
- Checkpoint map.
- Result table with run IDs.

## 9. Research Risk Register

Use this table when the algorithm design has multiple open risks:

| Risk | Why it matters | Evidence needed | Next check | Owner |
| --- | --- | --- | --- | --- |

Common risks:

- Apparent improvement is caused by leakage.
- The method improves average AUROC but hurts clinically important rare labels.
- Evaluation prompts changed between runs.
- Preprocessing or image-space choice changed the cohort.
- Training instability explains the result.
- Baseline is under-tuned.
- Compute constraints prevent fair comparison.
- Results are not reproducible from recorded artifacts.

## 10. Open Research Additions

Use this section for ideas that should be discussed before they become standard
playbook guidance.

Suggested addition:
Rationale:
Applies to:
Evidence needed:
Reviewer:
Date:
