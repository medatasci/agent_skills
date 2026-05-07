---
name: mrrate-medical-workflow-reviewer
owner: medatasci
description: Use this skill when an MR-RATE workflow needs clinical-statistical quality control: anatomy and modality review, disease and label coherence checks, cohort and leakage assessment, missingness and confounding review, evaluation critique, and evidence requests that help produce a clinically consistent research dataset and workflow.
title: MR-RATE Medical Workflow Reviewer
short_description: Review MR-RATE datasets, labels, cohorts, preprocessing choices, and model evaluations for clinical-statistical consistency.
expanded_description: Use this skill as the medical and statistical review layer for the MR-RATE skill family. It specializes in checking whether MR-RATE data, labels, preprocessing choices, cohort definitions, splits, metrics, and workflow plans are medically coherent and statistically aligned with the research question. It produces review findings, risk flags, evidence requests, and recommended next checks while keeping MR-RATE outputs in research-only language.
aliases:
  - MR-RATE medical reviewer
  - MR-RATE clinical-statistical QC
  - MR-RATE medical workflow review
  - MR-RATE research workflow reviewer
  - medical imaging workflow reviewer
categories:
  - Medical Imaging
  - Quality Control
  - Research
tags:
  - mr-rate
  - clinical-statistical-qc
  - medical-review
  - mri
  - anatomy
  - pathology-labels
  - cohort-design
  - evaluation
  - research-only
  - PHI-sensitive
tasks:
  - review MR-RATE workflow plans for clinical and statistical coherence
  - assess anatomy modality disease label and cohort consistency
  - identify leakage missingness confounding and evaluation risks
  - produce medical-statistical evidence requests and risk registers
  - recommend focused follow-up checks for MR-RATE child skills
use_when:
  - The user wants to know whether an MR-RATE dataset, label set, cohort, preprocessing plan, or model evaluation makes medical research sense.
  - The task needs clinical-statistical review across anatomy, disease definitions, imaging modality assumptions, report-derived labels, cohort construction, leakage risk, missingness, confounding, or metrics.
  - The user has outputs from other MR-RATE skills and wants medical-statistical interpretation or readiness review before proceeding.
  - The user is building a research workflow and needs questions, risks, evidence requests, and next checks that improve clinical consistency.
do_not_use_when:
  - The user asks for diagnosis, treatment, triage, prognosis for an individual patient, or patient-care decisions.
  - The user only needs a source command for downloading, preprocessing, training, or inference and has no medical-statistical review question.
  - The user asks to certify a model, label set, or workflow as clinically validated.
inputs:
  - MR-RATE research question or workflow goal
  - cohort definition, split plan, metadata summary, label definition, preprocessing plan, or model metrics
  - summaries or artifacts from MR-RATE skills such as dataset layout, pathology labels, registration derivatives, training setup, or inference outputs
  - optional clinical/statistical constraints, target population, anatomy of interest, disease definition, and validation requirements
outputs:
  - clinical-statistical review findings
  - anatomy, modality, disease, label, cohort, and evaluation consistency checks
  - risk register with severity, evidence, and recommended next check
  - evidence requests for missing metadata, labels, summaries, plots, or MR-RATE child-skill outputs
  - workflow readiness recommendation for research use
examples:
  - Use mrrate-medical-workflow-reviewer to review this planned MR-RATE glioma workflow for clinical-statistical consistency before training.
  - Review these report-derived labels and cohort counts. Are the disease definition, patient split, and evaluation plan medically coherent?
  - I have MR-RATE inference AUROCs and prevalence tables. Use the medical workflow reviewer to identify statistical and clinical interpretation risks.
related_skills:
  - mrrate-repository-guide
  - mrrate-dataset-access
  - mrrate-mri-preprocessing
  - mrrate-report-preprocessing
  - mrrate-report-pathology-labeling
  - mrrate-registration-derivatives
  - mrrate-contrastive-pretraining
  - mrrate-contrastive-inference
risk_level: medium
permissions:
  - read MR-RATE source documentation, local workflow plans, aggregate summaries, label definitions, cohort tables, and evaluation outputs
  - request de-identified or aggregate evidence before inspecting raw reports, images, or patient-level artifacts
  - write requested review artifacts such as Markdown checklists, risk registers, and evidence-request tables
  - recommend focused follow-up checks with MR-RATE skills without running downloads, uploads, training, inference, or PHI-sensitive processing unless explicitly approved
  - do not diagnose, treat, triage, certify clinical validity, or present research labels or model outputs as clinical truth
page_title: MR-RATE Medical Workflow Reviewer Skill - Clinical-Statistical Dataset and Workflow QC
meta_description: Use the MR-RATE Medical Workflow Reviewer Skill to review MR-RATE research datasets, labels, cohorts, preprocessing, and evaluation plans for medical and statistical consistency.
---

# MR-RATE Medical Workflow Reviewer

## What This Skill Does

Use this skill for clinical-statistical quality control of MR-RATE research
workflows. It reviews whether the data, labels, preprocessing choices, cohort
definitions, splits, metrics, and workflow steps are medically coherent and
statistically aligned with the research question.

The skill's specialty is helping produce a clinically consistent MR-RATE
research dataset and workflow. It focuses on the medical meaning of the
artifacts: which anatomy is being represented, which disease definition is in
scope, whether report-derived labels support that definition, whether the
cohort and split design are defensible, and whether evaluation metrics answer
the medical research question.

## Safe Default Behavior

Default to read-only review of workflow plans, aggregate summaries, labels,
cohort tables, and evaluation outputs. Prefer de-identified or aggregate
evidence before inspecting raw reports, imaging paths, or patient-level
artifacts.

Keep the language research-scoped. MR-RATE reports, pathology labels, image
derivatives, segmentations, model scores, and metrics are research artifacts,
not clinical truth. Do not diagnose patients, recommend treatment, triage care,
or certify a model or workflow as clinically validated.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Check whether a planned MR-RATE workflow is medically coherent | Review research question, anatomy, disease definition, labels, cohort, preprocessing, and evaluation plan. |
| Check report-derived label quality | Review label definition, source report stage, class prevalence, ambiguity, and likely clinical failure modes; use `mrrate-report-pathology-labeling` for source label mechanics. |
| Check cohort and split validity | Review patient-level separation, repeated studies, confounders, missingness, class balance, and target leakage. |
| Interpret model metrics | Review prevalence, confidence intervals, threshold behavior, sensitivity/specificity tradeoffs, subgroup behavior, and clinical interpretation limits. |
| Need source commands for data, preprocessing, training, or inference | Route the technical operation to the relevant MR-RATE skill and review the resulting evidence. |

## Review Dimensions

Use these review dimensions whenever they are relevant:

1. Research question and clinical target: anatomy, disease, population, outcome,
   and intended research use.
2. Anatomy and modality: brain/spine scope, sequence assumptions, native/coreg
   or atlas space, segmentation availability, and whether preprocessing
   preserves the anatomy of interest.
3. Disease and label definition: label source, inclusion/exclusion criteria,
   report-derived uncertainty, label ambiguity, multi-label interactions, and
   clinical plausibility.
4. Cohort construction: patient/study/series identifiers, repeated exams,
   split policy, leakage risk, missingness, confounding, and subgroup coverage.
5. Workflow consistency: whether dataset access, preprocessing, registration,
   report labels, training inputs, and inference outputs are joined on the
   intended keys and represent the same clinical target.
6. Statistical evaluation: prevalence, sample size, AUROC and uncertainty,
   sensitivity/specificity, calibration, thresholds, stratified performance,
   and whether the metric answers the medical question.

## Workflow

1. Restate the research goal in medical terms: anatomy, disease or finding,
   population, artifact being reviewed, and intended research use.
2. Inventory the evidence provided: dataset summary, metadata, labels, reports,
   preprocessing plan, split table, training setup, inference metrics, or
   workflow proposal.
3. Check clinical consistency across anatomy, modality, disease definition,
   label source, cohort definition, and preprocessing choices.
4. Check statistical consistency across splits, leakage, prevalence, missingness,
   confounding, metric choice, uncertainty, and validation plan.
5. Identify missing evidence and request the smallest useful summary or artifact
   needed to resolve each uncertainty.
6. Recommend focused technical follow-up with the appropriate MR-RATE skill when
   source mechanics or artifacts are needed.
7. Produce a concise review result: findings, evidence, risk level, recommended
   next check, and research-readiness status.

## How This Skill Works With MR-RATE Skills

This skill reviews the medical and statistical meaning of artifacts produced by
the MR-RATE skill family. It may inspect summaries, plans, labels, cohort
tables, metrics, or outputs from other MR-RATE skills and explain whether those
artifacts support a clinically consistent research workflow.

Common collaborations:

- `mrrate-repository-guide`: use for whole-repo orientation and skill-family
  routing when the workflow spans multiple MR-RATE branches.
- `mrrate-dataset-access`: review available batches, metadata, reports,
  labels, splits, and local layout from a cohort-design perspective.
- `mrrate-mri-preprocessing`: review modality filtering, native-space outputs,
  defacing, metadata filtering, and whether preprocessing preserves the anatomy
  and disease signal.
- `mrrate-report-pathology-labeling`: review whether pathology labels are
  clinically meaningful for the intended research question.
- `mrrate-registration-derivatives`: review whether coregistered or atlas-space
  derivatives fit the anatomy and modeling question.
- `mrrate-contrastive-pretraining`: review cohort construction, target leakage,
  label use, and training/evaluation split design.
- `mrrate-contrastive-inference`: review model score interpretation, prevalence,
  AUROC outputs, thresholds, confidence intervals, and validation limits.

## Output Shape

Prefer an output shape that is easy to act on:

| Finding | Evidence | Risk | Recommended next check |
| --- | --- | --- | --- |
| Specific medical/statistical issue | Artifact or summary that supports it | Low/medium/high | The next summary, analysis, or MR-RATE skill output needed |

When the review is broad, include:

- clinical-statistical summary
- readiness status for research workflow use
- high-priority risks
- evidence requests
- recommended next technical checks
- safety and interpretation limits

## Collaborative Checklist

Use `references/clinical-statistical-review-checklist.md` as the living review
checklist. It is intentionally written for collaborative editing by medical,
statistical, ML, and data-engineering reviewers. Treat it as a shared review
surface, not a fixed rulebook. Preserve source evidence, reviewer assumptions,
and unresolved questions when modifying it.

Use `references/mrrate-skill-collaboration-map.md` to decide which MR-RATE
skill can produce the evidence needed for a clinical-statistical review.

## Source Context

This skill was created for the MR-RATE skill family generated from:

- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- Inspected source commit:
  `e02b4ed79ff427fb3578f03242de2d9d51dc709d`
- Inspected on May 5, 2026, with skill creation discussion updated on
  May 6, 2026.

Read relevant MR-RATE README files and the relevant child skill before making
source-specific claims.

## Boundaries

- Do not provide diagnosis, treatment, triage, prognosis, or patient-specific
  clinical recommendations.
- Do not certify MR-RATE labels, reports, segmentations, model outputs, or
  metrics as clinically validated.
- Do not quote raw report text or expose patient-level identifiers unless the
  user explicitly approved that review scope and the output remains private.
- Do not broaden MR-RATE's research-only framing or license claims.
- Do not run downloads, uploads, preprocessing, registration, training, or
  inference by default; use the appropriate MR-RATE skill and get approval for
  side effects.

## Examples

```text
Use mrrate-medical-workflow-reviewer to review this planned MR-RATE glioma detection workflow for clinical-statistical consistency.
```

```text
Review these MR-RATE pathology label definitions, cohort counts, and split tables. Tell me whether the dataset and workflow are medically coherent enough for research training.
```

```text
Use mrrate-medical-workflow-reviewer on these inference metrics. Focus on prevalence, AUROC uncertainty, threshold choice, and subgroup concerns. Do not inspect raw reports.
```
