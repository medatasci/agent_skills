# Subdural intracranial hemorrhage Research Plan

Status: final_thorough_research_target_met_needs_human_review

## Scope Definition

- Disease or finding: Subdural intracranial hemorrhage
- MR-RATE original name: Extra-axial hematoma
- Ontology source: snomed
- SNOMED CT: 35486000 (Subdural intracranial hemorrhage)
- Cluster: hemorrhagic_vascular
- Primary imaging modality: MRI
- Intended use: research planning, known-diagnosis imaging characterization, report-language extraction, differential/mimic-aware review, and clinical-statistical translation.
- Explicit non-use: final diagnosis, treatment recommendation, triage, or unsupported claims.

## Chapter Goals

1. Describe how Subdural intracranial hemorrhage is expected to present on diagnostic imaging, especially MRI, using radiology-report style language.
2. Identify findings that support or argue against Subdural intracranial hemorrhage relative to common mimics and relevant MR-RATE categories.
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
As a radiology expert, given a diagnosis of Subdural intracranial hemorrhage, what would you look for in MRI images to confirm?
```

Advanced prompt:

```text
As a neuroradiologist, given a diagnosis of Subdural intracranial hemorrhage, what sequence-specific MRI signal characteristics, lesion morphology, anatomic distribution, chronicity features, volume-loss patterns, and associated findings would you expect to see on MRI?
```

Search variants:

- Subdural intracranial hemorrhage MRI imaging characteristics
- Subdural intracranial hemorrhage MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics
- Subdural intracranial hemorrhage MRI lesion morphology anatomic distribution
- Subdural intracranial hemorrhage MRI chronicity features structural patterns
- Subdural intracranial hemorrhage MRI associated findings radiology
- Subdural intracranial hemorrhage MRI differential diagnosis mimics
- Subdural intracranial hemorrhage MRI report language findings impression
- Subdural intracranial hemorrhage clinical course progression stable treatment response
- Subdural intracranial hemorrhage cohort definition endpoint misclassification adjudication

## Differential Matrix Placeholder

Complete `differential-matrix.md` before drafting the disease chapter. Include relevant contrasts to the other MR-RATE categories, ordered roughly from most common to least common in the relevant imaging context.


## Research And Writing Checkpoint

Date/time: 2026-05-08T08:28:15Z

Current phase: final-thorough-research-target-met

### What Has Been Done

- Continued the queue from the manifest and selected `subdural-intracranial-hemorrhage`.
- Expanded the evidence pack to 50 source records, 25 figure evidence records,
  and 15 video or interactive teaching evidence records.
- Drafted a template-conformant disease chapter.
- Updated the source review, differential matrix, JSON manifests, alias files,
  manifest, TODO table, and HTML index.
- Rendered the disease HTML preview with `python -m skillforge disease-preview`.

### What Worked

- The source hierarchy produced broad clinical, guideline, radiology, chronic
  SDH, surgical, embolization, and differential sources.
- Existing template checks support a restartable disease-chapter workflow.
- Link-only figure evidence allowed image concepts to be captured without
  violating reuse-rights uncertainty.

### What Did Not Work

- Figure reuse rights were not reviewed in this cycle.
- Video transcripts were not reviewed in this cycle.
- Some evidence records are teaching cases or abstracts and should only
  support narrow, labeled claims.

### Problems Or Risks Before Continuing

- Do not overstate the ability of imaging to precisely date subdural hematoma.
- Do not merge nonspecific `extra-axial collection`, hygroma, empyema, or
  postoperative fluid labels into SDH cohorts without adjudication.
- MMA embolization evidence is changing quickly and should be refreshed before
  publication or claims about comparative effectiveness.

### What Needs To Change

- Add local figure assets only after reuse rights are reviewed.
- Add a compact acute/subacute/chronic imaging table and treatment-endpoint
  table if the chapter becomes publication-bound.
- Review video transcripts and decide which are strong enough to support
  educational claims.

### Current Confidence

Evidence-count target met; needs human expert review.

### Next Action

Continue the MR-RATE queue with `intracranial-aneurysm`, unless a human review
pass on subdural hemorrhage is requested first.
