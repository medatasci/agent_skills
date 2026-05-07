# Collaborative Clinical-Statistical Review Checklist

This checklist supports `mrrate-medical-workflow-reviewer`. It is designed as a
living review surface for clinicians, statisticians, ML researchers, data
engineers, and workflow owners who are trying to produce a clinically
consistent MR-RATE research dataset and workflow.

Use this checklist to make the review explicit: what evidence exists, what is
assumed, what remains unresolved, and what should be checked next.

## How To Edit This Checklist

This checklist may be edited collaboratively.

When editing:

- Put high-risk and commonly applicable checks near the top of each section.
- Keep questions concrete enough that another reviewer can answer them with an
  artifact, summary, table, plot, or source reference.
- Preserve the distinction between evidence, assumption, concern, and
  recommendation.
- Add project-specific notes when a rule applies only to a disease target,
  anatomy, cohort, or study design.
- Prefer aggregate and de-identified review artifacts.
- Do not add patient-care instructions.
- Do not claim MR-RATE labels, models, segmentations, reports, or metrics are
  clinically validated.
- Leave unresolved questions visible until evidence resolves them.

Recommended reviewer note format:

```text
Reviewer:
Date:
Workflow or disease target:
Evidence reviewed:
Assumptions:
Unresolved questions:
Recommended next check:
```

## 1. Research Question And Intended Use

- Is the anatomy of interest stated clearly: brain, spine, intracranial
  structure, spinal region, lesion compartment, or other target?
- Is the disease, finding, or condition defined in clinically meaningful terms?
- Is the workflow for research cohort construction, model training, model
  evaluation, exploratory analysis, or another research use?
- Is the unit of analysis clear: patient, study, series, report, image volume,
  registered derivative, or model score?
- Is the intended comparison clear: disease vs no disease, one label among many,
  subgroup comparison, longitudinal change, or zero-shot score evaluation?
- Are inclusion and exclusion criteria explicit enough that another reviewer
  could reproduce the cohort definition?
- Are there any claims being implied that would require clinical validation,
  external validation, regulatory review, or prospective evaluation?

Evidence to request when unclear:

- One-paragraph research question.
- Target anatomy and disease definition.
- Inclusion/exclusion criteria.
- Intended use statement.
- Unit-of-analysis table.

## 2. Anatomy, Modality, And Image-Space Consistency

- Does the workflow use imaging that can plausibly show the anatomy and disease
  signal of interest?
- Are brain and spine studies handled separately when the disease target or
  model input requires that distinction?
- Are modality and sequence assumptions stated, such as T1, T2, FLAIR,
  contrast-enhanced imaging, diffusion, or other MRI sequence groups?
- Does modality filtering remove studies that may be clinically important for
  the disease question?
- Does native-space, coregistered, or atlas-space processing match the planned
  model or analysis?
- Could registration, resampling, cropping, masking, or defacing remove or
  distort the anatomy or disease signal being studied?
- Are segmentations or derived masks being treated as research derivatives
  rather than clinical annotations?
- Are there known failure modes for the chosen anatomy, such as postoperative
  anatomy, hardware, motion, severe mass effect, incomplete field of view, or
  unusual spine coverage?

Evidence to request when unclear:

- Modality and sequence counts by cohort and split.
- Native/coreg/atlas-space choice and rationale.
- Example preprocessing metadata summary.
- Failure-rate summary for registration, segmentation, or defacing.
- Counts of excluded studies and exclusion reasons.

## 3. Disease Definition And Label Coherence

- Does the label name match a specific clinical concept, or is it too broad for
  the research question?
- Is the positive label based on current findings, historical findings,
  impressions, report language, structured labels, model outputs, or another
  source?
- Does the label definition handle negation, uncertainty, history, differential
  diagnosis, postoperative findings, treated disease, and incidental findings?
- Are related labels clinically separable enough for the intended model or
  analysis?
- Are multi-label interactions expected, such as tumor with edema, hemorrhage
  with mass effect, or degenerative spine findings with stenosis?
- Does the label source support the intended unit of analysis?
- Are labels being used for training, evaluation, cohort selection, or
  descriptive analysis? Each use may require a different evidence threshold.
- Does label prevalence make clinical sense for the cohort and split?

Evidence to request when unclear:

- Label ontology or pathology list.
- Label generation method and source stage.
- Prevalence by split, batch, anatomy, and subgroup.
- Examples summarized without raw PHI-bearing text.
- Ambiguous or low-confidence label counts.

## 4. Report-Derived Label Review

- Were reports anonymized, translated, structured, and quality-checked before
  label generation?
- Are report sections used consistently, such as findings vs impression?
- Are labels derived from structured findings, free-text findings, or another
  intermediate artifact?
- Could translation or structuring errors change label meaning?
- Are report-derived labels being treated as weak research labels rather than
  clinical ground truth?
- Is there a verification or QC step for positive labels?
- Are label failures likely to be systematic for certain anatomy, language,
  disease classes, or report templates?
- Are labels joined to imaging by `study_uid` or another intended key without
  accidental patient or report leakage?

Evidence to request when unclear:

- Report preprocessing stage summary.
- Structuring QC output.
- Label generation command and pathology JSON.
- Merge report and label counts.
- Positive-label verification statistics.

## 5. Cohort Construction

- Are patient, study, series, report, and derivative identifiers used
  consistently?
- Is the cohort defined at the right level for the medical question?
- Are repeated studies from the same patient handled explicitly?
- Are multiple series from the same study handled in a way that avoids
  over-counting?
- Are inclusion and exclusion reasons medically defensible?
- Are excluded studies summarized, not silently dropped?
- Are missing reports, missing labels, missing images, failed preprocessing, or
  failed registration counted?
- Are batches, acquisition sources, anatomy groups, and time periods balanced or
  at least described?

Evidence to request when unclear:

- Cohort flow table.
- Patient/study/series count table.
- Inclusion/exclusion reason counts.
- Missingness table by artifact type.
- Batch and split distribution table.

## 6. Leakage And Split Review

- Are train, validation, and test splits separated at the patient level when
  patient-level generalization is intended?
- Are repeated studies from the same patient prevented from crossing splits?
- Could reports, labels, accession metadata, filenames, preprocessing outputs,
  or batch artifacts encode the target?
- Are near-duplicate series or derivative copies separated consistently?
- Are labels generated using information from a split that should remain held
  out?
- Does any preprocessing, normalization, threshold selection, prompt tuning, or
  model selection use test-set information?
- Are prevalence, anatomy, modality, and acquisition distributions described by
  split?

Evidence to request when unclear:

- Split table with patient/study/series counts.
- Duplicate/repeated patient check.
- Label generation timing relative to split construction.
- Prevalence and modality distribution by split.
- Description of any tuning decisions and data used.

## 7. Missingness, Confounding, And Bias

- Are missing images, reports, labels, derivatives, or metrics counted and
  explained?
- Is missingness related to anatomy, disease severity, modality, acquisition
  source, batch, scanner, language, or clinical workflow?
- Could site, scanner, protocol, batch, report template, or preprocessing
  success act as a proxy for disease?
- Are important subgroups represented, such as age bands, sex, anatomy groups,
  disease classes, postoperative cases, or acquisition protocols when available?
- Are negative cases clinically appropriate controls, or are they merely
  unlabeled positives?
- Are there disease definitions where the absence of a report mention is a weak
  negative?
- Are class imbalance and rare positive labels handled in metric interpretation?

Evidence to request when unclear:

- Missingness table by split and subgroup.
- Confounder distribution table.
- Positive and negative cohort definitions.
- Class prevalence by subgroup.
- Preprocessing success/failure rates by cohort.

## 8. Workflow And Artifact Consistency

- Do dataset access, preprocessing, reports, labels, registration derivatives,
  training inputs, and inference outputs refer to the same cohort?
- Are join keys explicit, such as `patient_uid`, `study_uid`, and `series_id`?
- Are derived artifacts traceable to source studies?
- Are native, coregistered, atlas, and segmentation artifacts kept distinct when
  their interpretation differs?
- Are source versions, commands, parameters, and commit hashes recorded?
- Are output directories and files named so that a reviewer can tell which
  cohort, split, and label definition produced them?
- Are destructive or large side effects documented, such as deleting zips,
  moving derivatives, uploading outputs, training checkpoints, or writing
  predictions?

Evidence to request when unclear:

- Artifact manifest.
- Join-key summary.
- Command provenance.
- Source commit and branch.
- Output directory map.

## 9. Training And Inference Design

- Does the training objective match the research question?
- Are report text, labels, image inputs, and split design aligned?
- Are pretrained weights, frozen encoders, prompt choices, pooling strategy, and
  fusion mode documented when relevant?
- Could report text or labels leak evaluation targets into training?
- Are checkpoint selection and early stopping based only on appropriate data?
- Are inference prompts clinically meaningful and paired with reasonable
  negative prompts?
- Are score outputs interpreted as model research scores, not probabilities of
  disease unless calibrated and validated for that claim?

Evidence to request when unclear:

- Training config or command.
- Data JSONL and split description.
- Checkpoint selection rule.
- Prompt/pathology JSON.
- Inference output manifest.

## 10. Statistical Evaluation

- Is the metric appropriate for prevalence and intended use?
- Are AUROC, AUPRC, sensitivity, specificity, F1, precision, recall,
  calibration, and threshold metrics interpreted correctly?
- Are confidence intervals or uncertainty estimates needed for the decision?
- Are rare labels evaluated with enough positives to support the claim?
- Are thresholds selected on validation data and evaluated on held-out data?
- Are subgroup metrics reported when cohort structure suggests important
  heterogeneity?
- Are negative labels reliable enough for specificity or false-positive claims?
- Are model results compared to a meaningful baseline?
- Are multiple comparisons or many labels handled carefully?

Evidence to request when unclear:

- Positive/negative counts by split and label.
- AUROC or metric table with confidence intervals when possible.
- Threshold-selection rule.
- Calibration plot or summary when probabilities are interpreted.
- Subgroup performance table.

## 11. Review Output Template

Use this table for compact outputs:

| Finding | Evidence | Risk | Recommended next check |
| --- | --- | --- | --- |
| | | Low/medium/high | |

Use this readiness summary when useful:

```text
Clinical-statistical readiness:
Research question clarity:
Dataset and cohort coherence:
Label coherence:
Preprocessing and artifact coherence:
Leakage and split status:
Evaluation status:
Highest-priority risks:
Evidence needed before proceeding:
Recommended MR-RATE skill follow-up:
```

## 12. Open Collaborative Additions

Use this section for reviewer additions that should be discussed before they
become standard checklist items.

Suggested addition:
Rationale:
Applies to:
Evidence needed:
Reviewer:
Date:
