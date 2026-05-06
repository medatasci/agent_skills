# MR-RATE Medical Workflow Reviewer

Skill ID: `mrrate-medical-workflow-reviewer`

## Most Important Context

This skill provides medical and statistical review for MR-RATE research
workflows. It helps agents and researchers build clinically consistent datasets
and workflows by checking anatomy, disease definitions, imaging modality
assumptions, report-derived labels, cohort design, missingness, confounding,
leakage risk, preprocessing choices, and evaluation validity.

The skill's specialty is clinical-statistical quality control: making sure the
dataset, labels, workflow steps, and evaluation plan remain medically coherent
from raw MR-RATE inputs through derived artifacts and model results.

Use this skill when a workflow needs medical research judgment: whether a label
definition is clinically meaningful, whether a cohort matches the disease
question, whether preprocessing choices preserve the anatomy of interest,
whether disease labels are usable for the intended analysis, whether model
outputs are being evaluated with appropriate statistics, or what
medical/statistical issues must be resolved before proceeding.

This skill contributes to MR-RATE workflows by reviewing evidence and producing
clinically meaningful findings, risk flags, evidence requests, and recommended
next checks. It works best alongside the MR-RATE dataset, preprocessing, report,
registration, training, and inference skills because those skills can produce
the source-grounded artifacts this reviewer evaluates.

This is a research workflow review skill. It must not diagnose patients,
recommend treatment, triage care, or certify model outputs as clinically valid.
It should prefer aggregate summaries and de-identified evidence when reviewing
data.

The review checklist for this skill is intentionally collaborative. Medical,
statistical, ML, and data-engineering reviewers may edit it as the workflow
evolves, as long as edits preserve evidence, assumptions, unresolved questions,
and research-only safety boundaries.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-medical-workflow-reviewer

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
Medical Imaging, Quality Control, Research

Collection context:
This skill belongs to the MR-RATE skill family. It is the
clinical-statistical review layer for workflows that use MR-RATE dataset access,
MRI preprocessing, report preprocessing, pathology labeling, registration
derivatives, contrastive pretraining, or contrastive inference.

Related skills are usually used to produce evidence. This skill reviews whether
that evidence supports a clinically consistent research dataset and workflow.

## What This Skill Does

This skill helps Codex review MR-RATE research workflows through a medical and
statistical lens. It looks at the clinical meaning of the data and workflow:
the anatomy being represented, the disease definition, the imaging modality and
space, the label source, the cohort design, the split policy, and the metrics
used to evaluate model behavior.

It produces review findings rather than pipeline outputs. Typical products are
clinical-statistical summaries, risk registers, evidence requests, recommended
next checks, and research-readiness notes.

Use it to check whether:

- a disease label is clinically meaningful for the intended question
- a cohort actually represents the target population or anatomy
- report-derived labels are appropriate for model training or evaluation
- patient/study/series joins preserve the intended unit of analysis
- preprocessing and registration preserve the anatomy or disease signal
- train/validation/test splits avoid patient-level or report-level leakage
- missingness, confounding, class imbalance, or subgroup coverage may distort
  results
- AUROC, sensitivity, specificity, calibration, thresholds, and confidence
  intervals are appropriate for the research claim

## Why You Would Call It

Call this skill when:

- You have an MR-RATE workflow plan and want to know whether it is medically
  coherent before running expensive preprocessing, training, or inference.
- You have labels, cohort counts, split tables, metrics, or derived artifacts
  and want clinical-statistical review.
- You need concrete medical/statistical questions that must be answered before
  treating a dataset as ready for research modeling.
- You want a risk register that connects medical concerns to specific evidence
  requests and next checks.

Use it to:

- Review dataset and workflow consistency from a medical research perspective.
- Identify label, cohort, leakage, confounding, missingness, and evaluation
  problems early.
- Decide which evidence should be requested from MR-RATE child skills before a
  workflow proceeds.

Do not use it when:

- The user needs diagnosis, treatment, triage, prognosis, or individual patient
  care guidance.
- The task is only to run a known MR-RATE command and no medical/statistical
  review is needed.
- The user wants to claim a model, label set, segmentation, or report pipeline
  is clinically validated.

## What Clinically Consistent Means Here

For this skill, a clinically consistent MR-RATE dataset and workflow means:

- The research question names the anatomy, disease or finding, population, and
  intended research use clearly enough to audit the data choices.
- The imaging modality, sequence, native/coreg/atlas space, segmentation, and
  preprocessing choices preserve the anatomy and disease signal needed for the
  research question.
- Report-derived labels are defined in a way that matches the clinical concept
  being modeled, including reasonable treatment of ambiguity, negation,
  historical findings, incidental findings, and multi-label overlap.
- Cohort construction respects the unit of analysis: patient, study, series,
  report, or derived image artifact.
- Splits avoid patient-level leakage and obvious shortcuts such as repeated
  studies, report text artifacts, scanner/site artifacts, or preprocessing
  artifacts that encode the target.
- Evaluation metrics match the medical question and are interpreted with
  prevalence, uncertainty, thresholds, calibration, subgroup behavior, and
  validation limits in view.

This skill does not require the workflow to be perfect. It helps make the
workflow reviewable, evidence-based, and medically coherent enough to support
research decisions.

## How It Works

The skill uses a structured review method rather than a source-code wrapper. It
starts by restating the research question in medical terms, then checks whether
the available data artifacts support that question across anatomy, modality,
disease definition, labels, cohort construction, preprocessing, splits, and
evaluation.

The review is evidence-driven. The skill should name the artifact or summary
that supports each finding, distinguish evidence from assumptions, and request
the smallest useful additional artifact when the available evidence is not
enough. A good review does not simply say that a workflow is risky; it explains
what clinical or statistical consistency issue exists and what evidence would
resolve it.

The skill is also collaborative. It can use outputs from MR-RATE child skills,
such as cohort counts, pathology label definitions, preprocessing summaries,
registration notes, training plans, or inference metrics. It then interprets
those outputs from a medical research perspective and turns them into review
findings, risk flags, evidence requests, and recommended next checks.

The default mode is read-only. When the user asks for a durable artifact, the
skill can write a Markdown review, risk register, or checklist update. It does
not require external services, credentials, model downloads, GPU jobs, or MR-RATE
source execution for its normal review behavior.

## How This Skill Works With MR-RATE Skills

This skill reviews the medical and statistical meaning of artifacts produced by
other MR-RATE skills. It can inspect cohort summaries, preprocessing plans,
report-label definitions, registration assumptions, training designs, inference
metrics, and workflow proposals, then explain what those artifacts imply from a
medical research perspective.

It helps decide what evidence is needed next, which assumptions are fragile,
and which technical skill can produce the missing information.

| MR-RATE skill | Evidence this reviewer may use | Medical-statistical review focus |
| --- | --- | --- |
| `mrrate-repository-guide` | Whole-repo map, workflow branch, source context | Whether the proposed workflow uses the right MR-RATE branch for the clinical question. |
| `mrrate-dataset-access` | Batches, metadata, reports, labels, splits, local layout | Cohort availability, patient/study/series relationships, batch coverage, missing artifacts, and join keys. |
| `mrrate-mri-preprocessing` | DICOM/PACS filtering plan, modality classification, native-space outputs, defacing, metadata | Whether preprocessing preserves anatomy and disease signal, and whether filtering choices bias the cohort. |
| `mrrate-report-preprocessing` | Anonymization, translation, structuring, QC, report batches | Whether reports are usable as research evidence and whether preprocessing introduces label or language artifacts. |
| `mrrate-report-pathology-labeling` | Pathology ontology, LLM labeling plan, merged labels, prevalence | Whether labels are clinically meaningful for the research target and suitable for training or evaluation. |
| `mrrate-registration-derivatives` | Coreg/atlas derivative plan, registration outputs, backfilled studies | Whether image-space assumptions match the anatomy, disease signal, and model workflow. |
| `mrrate-contrastive-pretraining` | Training cohort, JSONL/report inputs, split plan, objective, checkpoints | Leakage risk, label/report coupling, cohort representativeness, and training/evaluation alignment. |
| `mrrate-contrastive-inference` | Scores, AUROCs, labels CSV, splits, prompts, predictions | Metric validity, uncertainty, prevalence effects, threshold behavior, and research-only interpretation. |

## Review Flow

1. Define the clinical research question.
   Capture the anatomy, disease or finding, target population, unit of
   analysis, intended use, and what decision the workflow is supposed to
   support.
2. Inventory available evidence.
   List dataset summaries, labels, reports, preprocessing outputs, split files,
   model outputs, metrics, or source context already available.
3. Review clinical coherence.
   Check whether anatomy, modality, disease definition, label source, cohort,
   and preprocessing choices support the same research question.
4. Review statistical coherence.
   Check sample size, prevalence, split policy, missingness, confounding,
   leakage, metric choice, uncertainty, thresholds, and subgroup behavior.
5. Request missing evidence.
   Ask for the smallest useful artifact or summary needed to resolve each
   issue. Prefer aggregate summaries and de-identified outputs.
6. Recommend focused next checks.
   Point to the MR-RATE skill or source artifact that can produce the needed
   evidence.
7. Produce a review result.
   Summarize findings, risks, assumptions, evidence requests, and workflow
   readiness for research use.

## What This Skill Produces

Typical outputs include:

- Clinical-statistical review summary.
- Anatomy, modality, and disease-coherence notes.
- Label validity and label-source concerns.
- Cohort design, missingness, confounding, and leakage review.
- Statistical evaluation critique.
- Evidence-request table.
- Risk register with severity and next check.
- Recommended follow-up with MR-RATE child skills.
- Research-readiness status such as `ready for next technical check`,
  `blocked pending evidence`, or `not aligned with stated research question`.

Recommended compact review table:

| Finding | Evidence | Risk | Recommended next check |
| --- | --- | --- | --- |
| Specific medical/statistical concern | Artifact, summary, or assumption supporting the concern | Low/medium/high | Summary, analysis, source file, or MR-RATE skill output needed next |

## Collaborative Checklist

The checklist lives at:

```text
skills/mrrate-medical-workflow-reviewer/references/clinical-statistical-review-checklist.md
```

It is a living review document. It may be edited by clinicians, statisticians,
ML researchers, data engineers, and workflow owners as MR-RATE use cases grow.
Edits should make the checklist more precise, easier to apply, and better
grounded in evidence.

When editing the checklist:

- Put the highest-risk, most generally useful checks near the top of each
  section.
- Preserve the distinction between evidence, assumption, concern, and
  recommendation.
- Add reviewer notes when a rule is project-specific or site-specific.
- Prefer aggregate/de-identified review artifacts over patient-level details.
- Do not add patient-care instructions or claims that MR-RATE outputs are
  clinically validated.
- Leave unresolved questions visible instead of smoothing them away.

The collaboration map lives at:

```text
skills/mrrate-medical-workflow-reviewer/references/mrrate-skill-collaboration-map.md
```

Use it when the reviewer needs to decide which MR-RATE skill can produce the
missing evidence for a medical-statistical review.

## Keywords

MR-RATE, medical workflow reviewer, clinical-statistical quality control,
medical imaging, MRI, anatomy, disease definition, pathology labels, report
labels, cohort design, leakage, missingness, confounding, AUROC, sensitivity,
specificity, calibration, research workflow.

## Search Terms

MR-RATE medical review, MR-RATE clinical-statistical QC, review MR-RATE labels,
MR-RATE cohort leakage, MR-RATE workflow validity, clinically consistent
dataset, medical imaging dataset review, report-derived label validation,
MR-RATE model evaluation review, MR-RATE AUROC interpretation.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE clinical-statistical QC" --json
python -m skillforge info mrrate-medical-workflow-reviewer --json
python -m skillforge evaluate mrrate-medical-workflow-reviewer --json
```

This skill does not wrap MR-RATE source scripts. It is a review skill that
reads plans, summaries, and artifacts and writes review outputs when requested.
Use the related MR-RATE skills for source-grounded commands.

## How To Call From An LLM

Direct prompt:

```text
Use mrrate-medical-workflow-reviewer to review this MR-RATE workflow for clinical-statistical consistency.
```

Task-based prompt:

```text
Use mrrate-medical-workflow-reviewer to review these label definitions, cohort counts, split tables, and AUROC results. Focus on whether the dataset and workflow are clinically consistent for the stated disease question.
```

Guarded prompt:

```text
Use mrrate-medical-workflow-reviewer, but only use aggregate summaries and do not inspect raw reports or patient-level identifiers.
```

Evidence-request prompt:

```text
Use mrrate-medical-workflow-reviewer to tell me what evidence we need from the MR-RATE skills before training a model for this disease target.
```

## Help And Getting Started

Start with a short statement of the research question and the artifacts already
available:

```text
Use mrrate-medical-workflow-reviewer to review this MR-RATE workflow for clinical-statistical consistency. The target is <disease/finding>, the anatomy is <anatomy>, the cohort is <cohort summary>, and the current artifacts are <labels/splits/metrics/preprocessing summary>.
```

Helpful inputs include:

- The anatomy and disease target.
- The intended research use.
- A cohort count table with patient, study, and series counts.
- Label definitions and prevalence by split.
- Preprocessing or registration summaries.
- Training, inference, or metric summaries.

If you do not have those artifacts yet, ask the skill for evidence requests:

```text
Use mrrate-medical-workflow-reviewer to tell me what evidence we need before this workflow can be reviewed medically and statistically.
```

Ask for clarification when:

- the disease target is broad or ambiguous
- the unit of analysis is unclear
- labels and images may not be joined on the intended key
- train/test separation is not clearly patient-level
- model metrics are reported without prevalence or split counts

## How To Call From The CLI

Search for the skill:

```text
python -m skillforge search "MR-RATE medical workflow review" --json
```

Show skill metadata:

```text
python -m skillforge info mrrate-medical-workflow-reviewer --json
```

Install the skill into Codex:

```text
python -m skillforge install mrrate-medical-workflow-reviewer --scope global
```

Evaluate the skill before publishing changes:

```text
python -m skillforge evaluate mrrate-medical-workflow-reviewer --json
```

## Inputs And Outputs

Inputs can include:

- Research question or workflow goal.
- Anatomy and disease target.
- Target population and intended research use.
- Cohort definition, batch list, metadata summary, split table, or inclusion and
  exclusion criteria.
- Report-derived label definitions, pathology ontology, label prevalence, or
  label QC output.
- Preprocessing plan, modality filtering summary, image-space choice, or
  registration derivative summary.
- Training plan, inference outputs, AUROC tables, score distributions,
  threshold analysis, or subgroup summaries.

Outputs can include:

- Clinical-statistical review narrative.
- Risk register.
- Evidence-request table.
- Recommended next checks and relevant MR-RATE skills.
- Research-readiness status.
- Markdown review artifact when the user asks for a written deliverable.

Output locations:

- Chat response by default.
- A user-specified Markdown, CSV, or issue artifact when requested.

## Limitations

Known limitations:

- This skill does not replace clinician, statistician, IRB, privacy, regulatory,
  or safety review.
- It does not run MR-RATE preprocessing, labeling, registration, training, or
  inference jobs.
- It does not grant access to gated datasets, model weights, PHI, or internal
  systems.
- It does not prove that labels or model outputs are clinically valid.
- It depends on the quality and specificity of the evidence provided.

Choose another skill when:

- You need source-grounded commands for downloading data:
  `mrrate-dataset-access`.
- You need raw MRI preprocessing commands: `mrrate-mri-preprocessing`.
- You need report preprocessing mechanics: `mrrate-report-preprocessing`.
- You need pathology label generation mechanics:
  `mrrate-report-pathology-labeling`.
- You need registration derivative commands:
  `mrrate-registration-derivatives`.
- You need model training commands: `mrrate-contrastive-pretraining`.
- You need inference or AUROC command planning:
  `mrrate-contrastive-inference`.

## Examples

Beginner example:

```text
Use mrrate-medical-workflow-reviewer to explain what makes an MR-RATE workflow clinically consistent.
```

Task-specific example:

```text
Use mrrate-medical-workflow-reviewer to review a brain tumor workflow using MR-RATE labels, native MRI data, and contrastive inference. Identify anatomy, label, cohort, leakage, and evaluation risks.
```

Safety-aware example:

```text
Use mrrate-medical-workflow-reviewer to review this cohort summary and AUROC table. Use only aggregate data and do not inspect raw report text.
```

Troubleshooting example:

```text
Our MR-RATE model performs well overall but poorly on one subgroup. Use mrrate-medical-workflow-reviewer to identify clinical, cohort, and statistical explanations we should investigate.
```

## Trust And Safety

Risk level:
Medium

Permissions:

- Reads MR-RATE source documentation, local workflow plans, aggregate summaries,
  labels, cohort tables, and evaluation outputs.
- May request additional summaries or artifacts needed for review.
- May write Markdown review notes, evidence-request tables, or risk registers
  when the user asks.
- Requires explicit approval before inspecting raw reports, patient-level data,
  local image paths, or PHI-sensitive artifacts.

Data handling:
Treat reports, image paths, study IDs, patient IDs, labels, derived artifacts,
checkpoints, predictions, and metrics as sensitive research artifacts. Prefer
aggregate and de-identified review artifacts.

Writes vs read-only:
Read-only by default. Writes only user-requested review artifacts.

External services:
None required for review. Related MR-RATE skills may involve Hugging Face,
W&B, torch hub, SLURM, or local model runtimes when the user separately
approves those workflows.

Credentials:
No credentials are needed for review. Dataset and model access credentials
belong to the relevant MR-RATE child workflows.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes:

- Missing review questions for anatomy, modality, disease labels, cohorts, or
  metrics.
- Places where the checklist is too rigid, too vague, or hard to edit
  collaboratively.
- Additional MR-RATE artifacts that should appear in the collaboration map.
- Safer wording for research-only medical review.

## Contributing

Contributions are welcome by pull request. The most likely files to edit are:

- `skills/mrrate-medical-workflow-reviewer/SKILL.md`
- `skills/mrrate-medical-workflow-reviewer/README.md`
- `skills/mrrate-medical-workflow-reviewer/references/clinical-statistical-review-checklist.md`
- `skills/mrrate-medical-workflow-reviewer/references/mrrate-skill-collaboration-map.md`

Before opening a pull request:

- Preserve the research-only and no-patient-care safety boundary.
- Keep collaborative checklist edits evidence-based and reviewer-friendly.
- Run `python -m skillforge build-catalog`.
- Run `python -m skillforge evaluate mrrate-medical-workflow-reviewer --json`.

## Author

medatasci

Maintainer status:
Draft MR-RATE skill-family member for review.

## Citations

- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- MR-RATE dataset: https://huggingface.co/datasets/Forithmus/MR-RATE
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/

## Related Skills

- `mrrate-repository-guide`: whole-repo orientation and family routing.
- `mrrate-dataset-access`: dataset repositories, metadata, reports, labels,
  splits, and local layout.
- `mrrate-mri-preprocessing`: raw MRI and metadata preprocessing.
- `mrrate-report-preprocessing`: report anonymization, translation,
  structuring, QC, labeling, and shard operations.
- `mrrate-report-pathology-labeling`: pathology label generation and merging.
- `mrrate-registration-derivatives`: coreg and atlas derivatives.
- `mrrate-contrastive-pretraining`: model training workflow planning.
- `mrrate-contrastive-inference`: zero-shot scoring and evaluation review.
