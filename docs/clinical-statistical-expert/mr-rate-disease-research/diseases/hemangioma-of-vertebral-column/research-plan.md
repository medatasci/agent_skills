# Hemangioma of vertebral column Research Plan

Status: not_started

## Scope Definition

- Disease or finding: Hemangioma of vertebral column
- MR-RATE original name: Vertebral hemangioma
- Ontology source: snomed
- SNOMED CT: 448232005 (Hemangioma of vertebral column)
- Cluster: spine
- Primary imaging modality: MRI
- Intended use: research planning, known-diagnosis imaging characterization, report-language extraction, differential/mimic-aware review, and clinical-statistical translation.
- Explicit non-use: final diagnosis, treatment recommendation, triage, or unsupported claims.

## Chapter Goals

1. Describe how Hemangioma of vertebral column is expected to present on diagnostic imaging, especially MRI, using radiology-report style language.
2. Identify findings that support or argue against Hemangioma of vertebral column relative to common mimics and relevant MR-RATE categories.
3. Translate imaging appearance, uncertainty, and report language into cohort definition, endpoint, covariate, adjudication, and misclassification implications.
4. Extract Findings-style and Impression-style report-language patterns when sources support them.

## Research And Writing Checkpoint

Date/time: 2026-05-07T23:39:48Z

Current phase: scope-and-query-pack

### What Has Been Done

- Created initial scope from the MR-RATE pathology/SNOMED mapping file.
- Generated an expert-framed source discovery query pack in `../../query-packs.json`.

### What Worked

- The source category is mapped to an ontology concept or RadLex concept in the MR-RATE source file.

### What Did Not Work

- No authoritative disease-specific source review has been completed yet in this batch workspace.

### Problems Or Risks Before Continuing

- Risk of using broad category labels too loosely; source review must distinguish finding, diagnosis, etiology, acuity, and incidental variant language.
- Differential ordering must be disease-specific and imaging-context-specific, not copied mechanically from the global source list.

### What Needs To Change

- Add authoritative sources, source notes, image evidence candidates, and a disease-specific differential matrix.

### Current Confidence

Draft

### Next Action

Run authoritative source discovery and record source evidence.

## Expert-Framed Source Discovery

Basic prompt:

```text
As a radiology expert, given a diagnosis of Hemangioma of vertebral column, what would you look for in MRI images to confirm?
```

Advanced prompt:

```text
As a neuroradiologist, given a diagnosis of Hemangioma of vertebral column, what sequence-specific MRI signal characteristics, lesion morphology, anatomic distribution, chronicity features, volume-loss patterns, and associated findings would you expect to see on MRI?
```

Search variants:

- Hemangioma of vertebral column MRI imaging characteristics
- Hemangioma of vertebral column MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics
- Hemangioma of vertebral column MRI lesion morphology anatomic distribution
- Hemangioma of vertebral column MRI chronicity features structural patterns
- Hemangioma of vertebral column MRI associated findings radiology
- Hemangioma of vertebral column MRI differential diagnosis mimics
- Hemangioma of vertebral column MRI report language findings impression
- Hemangioma of vertebral column clinical course progression stable treatment response
- Hemangioma of vertebral column cohort definition endpoint misclassification adjudication

## Differential Matrix Placeholder

Complete `differential-matrix.md` before drafting the disease chapter. Include relevant contrasts to the other MR-RATE categories, ordered roughly from most common to least common in the relevant imaging context.
