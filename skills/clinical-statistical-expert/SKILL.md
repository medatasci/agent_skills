---
name: clinical-statistical-expert
owner: medatasci
description: Use this skill when a user wants clinical research reasoning that connects disease-specific clinical and imaging knowledge with statistical design, cohort definitions, endpoints, covariates, adjudication, bias, uncertainty, and claims language. Use for disease chapter creation, known-diagnosis image characterization, differential or mimic-aware review, report-language extraction, and clinical-statistical study planning. Do not use for final clinical diagnosis, treatment, triage, or unsupported medical claims.
---

# Clinical Statistical Expert

## What This Skill Does

Use this skill when a user asks for clinical-statistical reasoning that connects
clinical disease knowledge, imaging appearance, report language, cohort
definition, endpoint selection, bias, uncertainty, and statistical implications.

The skill is designed to be progressively loaded. Start with the routing logic
and only load disease-specific or statistical-method references when the user
needs them.

## Safe Default Behavior

Default to research, study-design, and evidence-review support.

Do not make final clinical diagnoses, treatment decisions, triage decisions, or
unsupported claims. Keep claims tied to the user's context, the available
evidence, and the relevant disease or method reference.

Before downloading source material, storing images, modifying skill files, or
publishing catalog changes, confirm that the behavior is expected and allowed.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| "Given this diagnosis, what should I look for on MRI?" | Load `references/disease-index.md`, then the relevant disease chapter. |
| "How is this different from similar diseases?" | Use the disease chapter's Differential Diagnosis And Mimics section, then check missing information. |
| "Create or update a disease chapter" | Follow `references/disease-chapter-workflow.md`, the packaged `references/templates/`, and `disease-template-check`. |
| "Turn report language into cohort labels or endpoints" | Use disease report-language patterns plus statistical implications. |
| "Help with statistical design" | Load the relevant statistical method reference when one exists; otherwise provide conservative study-design reasoning. |

## SkillForge Discovery Metadata

This section is written as Markdown so people can read it, while SkillForge can
still extract the same discovery fields for catalogs, search, and generated
pages.

### Title

Clinical Statistical Expert

### Short Description

Connect disease-specific clinical and imaging knowledge with statistical study
design, cohort labels, endpoints, adjudication, uncertainty, and claims
language.

### Expanded Description

Use this skill for clinical research reasoning that needs both clinical context
and statistical discipline. It helps an agent characterize a known or suspected
disease on imaging, identify similar-appearing conditions, extract
radiology-report style language, translate uncertainty into cohort and endpoint
implications, and create source-grounded disease chapters. The first packaged
disease reference is a brain MRI chapter on gliosis.

### Aliases

- clinical statistical expert
- clinical-statistical-expert
- clinical statistics expert
- disease imaging expert
- medical imaging study design
- disease chapter generator
- radiology report language extraction
- clinical endpoint reviewer

### Categories

- Healthcare
- Clinical Research
- Medical Imaging
- Statistical Review

### Tags

- clinical-research
- statistics
- medical-imaging
- radiology
- MRI
- disease-chapters
- cohort-definition
- endpoints
- differential-diagnosis
- report-language
- evidence-review

### Tasks

- characterize known-diagnosis disease appearance on diagnostic imaging
- explain what to look for on MRI for a disease or finding
- compare a disease with similar-appearing mimics
- map radiology report language to cohort labels and endpoint implications
- identify missing clinical or imaging information
- review misclassification, confounding, and adjudication risks
- create or update source-grounded disease chapters
- render disease chapter HTML previews for human review

### Use When

- The user asks how a known diagnosis or finding appears on diagnostic imaging.
- The user wants disease-specific imaging features, locations, structural patterns, report phrases, or mimic-aware comparison.
- The user asks how clinical uncertainty should affect cohort definition, endpoints, covariates, sensitivity analysis, or claims.
- The user wants to create, review, or improve a disease chapter such as `gliosis.md`.
- The user asks for a clinical-statistical research plan or study-design review.

### Do Not Use When

- The user asks for final clinical diagnosis, treatment recommendations, triage, or emergency guidance.
- The user needs a generic literature review with no clinical-statistical or imaging interpretation task.
- The request depends on private medical data that has not been approved for local processing.
- The user wants unsupported conclusions from narrow studies or image examples.

### Inputs

- disease name, diagnosis, finding, report phrase, or clinical research question
- optional imaging modality, anatomy, disease stage, treatment history, and report text
- optional cohort, endpoint, covariate, adjudication, or claims-review context
- optional disease chapter path when creating or updating a chapter

### Outputs

- clinical-statistical interpretation plan
- imaging feature checklist and missing-information list
- mimic-aware comparison and uncertainty framing
- report-language patterns for Findings and Impression sections
- cohort, endpoint, covariate, adjudication, bias, and sensitivity-analysis implications
- source-grounded disease chapter updates and HTML previews

### Examples

- Clinical Statistical Expert, for gliosis on brain MRI, what should I look for and how would it be described in a radiology report?
- Given a cohort labeled "chronic gliosis", what misclassification risks should I consider?
- Create a disease chapter for multiple sclerosis using authoritative imaging sources and figure evidence.
- Render the gliosis disease chapter preview and show me remaining evidence gaps.

### Related Skills

- codebase-to-agentic-skills
- skill-discovery-evaluation
- radiological-report-to-roi
- nv-segment-ctmr

### Authoritative Sources

- NCBI Bookshelf medical imaging and clinical training chapters
- ACR Appropriateness Criteria and other professional society guidance
- Radiology Assistant and other clinician-facing radiology training resources
- Broad clinical or radiology review articles
- Narrow primary studies only when the claim is narrow and labeled as such

### Citations

- Disease-specific citations live in `references/diseases/<disease>.md` and the corresponding source manifest.
- The gliosis chapter includes NCBI Bookshelf/Springer, ACR, Radiology Assistant, and PMC review sources.

### Risk Level

medium

### Permissions

- read user-provided clinical research questions, public source URLs, local disease chapters, and local evidence manifests
- write local draft disease chapters, review artifacts, manifests, and HTML previews when the user asks for development work
- do not download source material, store image assets, process private clinical data, publish changes, or make external network calls without explicit approval

### Page Title

Clinical Statistical Expert Skill - Disease Imaging And Study Design Reasoning

### Meta Description

Use the Clinical Statistical Expert Skill to connect disease-specific imaging
knowledge with clinical research statistics, cohort definitions, endpoints,
mimic-aware review, report language, and evidence-grounded disease chapters.

## Workflow

1. Classify the request: known-diagnosis characterization, mimic-aware review,
   report-language extraction, clinical-statistical design, disease chapter
   creation, or disease chapter review.
2. Load `references/disease-index.md` if the request is disease-specific.
3. Load only the relevant disease chapter and method references needed for the
   task.
4. For disease chapter creation or revision, follow
   `references/disease-chapter-workflow.md`.
5. For differential diagnosis questions, use the disease chapter's Differential
   Diagnosis And Mimics section first so the answer includes likely mimics,
   discriminating imaging features, report-language cues, and the context needed
   to resolve uncertainty.
6. When treatment history, guidelines, response criteria, progression criteria,
   or expected outcomes affect imaging interpretation or research endpoints,
   use the disease chapter's Treatment, Response, And Outcome Context section
   instead of burying those details in general disease-course prose.
7. For cohort, endpoint, or model-design questions, use Common Covariates And
   Confounders before making statistical recommendations.
8. Keep broad claims supported by broad authoritative sources, and label narrow
   technical claims as narrow.
9. Return the answer with assumptions, missing information, source grounding,
   clinical-statistical implications, and practical next steps.

## Method

Use the LLM to:

- map the user's question to the right disease or method reference
- identify imaging features, locations, morphology, disease course, and mimics
- write Findings-style and Impression-style report language examples
- translate clinical uncertainty into study-design and statistical implications
- decide where source support is broad enough and where claims must stay narrow

Use deterministic SkillForge helpers to:

- record figure evidence with `python -m skillforge figure-evidence`
- record source evidence with `python -m skillforge source-archive`
- render chapter previews with `python -m skillforge disease-preview`
- check disease chapter template conformance with `python -m skillforge disease-template-check`
- evaluate publication readiness with `python -m skillforge evaluate`

## Inputs

- Disease, finding, diagnosis, or clinical research question.
- Imaging modality, anatomy, disease stage, treatment history, report text, or
  cohort definition when available.
- Source URLs and image candidates when creating or updating disease chapters.

## Outputs

- Disease-specific imaging checklist.
- Mimic-aware comparison.
- Report-language patterns.
- Statistical implications for cohort, endpoint, covariate, adjudication, bias,
  and sensitivity analysis.
- Updated disease chapter, review artifact, manifests, and HTML preview when
  performing development work.

## Boundaries

- Keep clinical claims source-grounded and scoped.
- Do not infer general disease behavior from scattered narrow papers.
- Do not store source pages or images in the public repo unless reuse terms
  explicitly allow it.
- Do not process private clinical data unless the user has confirmed it is
  approved for local use.

## Runtime And Deployment Notes

This skill is mostly guidance plus deterministic SkillForge helpers. It does
not require a model download or medical image processing runtime.

When creating disease chapters, use:

```text
python -m skillforge source-archive <disease> --source-id <id> --title "<title>" --url <url> --source-type "<type>" --claim-breadth "<broad/narrow/scope>" --section "<section>" --download --json
python -m skillforge figure-evidence <disease> --figure-id <id> --source-title "<title>" --source-url <url> --figure-label "<figure>" --license "<license>" --reuse-status link-only --clinical-point "<point>" --section "<section>" --json
python -m skillforge disease-preview <disease> --json
python -m skillforge disease-template-check <disease> --json
python -m skillforge evaluate clinical-statistical-expert --json
```
