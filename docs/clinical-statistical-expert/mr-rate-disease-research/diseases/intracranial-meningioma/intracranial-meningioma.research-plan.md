# Intracranial meningioma Research Plan

Status: final_thorough_research_target_met_needs_human_review

## Scope Definition

- Disease or finding: Intracranial meningioma
- MR-RATE original name: Meningioma
- Ontology source: snomed
- SNOMED CT: 302820008 (Intracranial meningioma)
- Cluster: neoplasm_mass
- Primary imaging modality: MRI
- Intended use: research planning, known-diagnosis imaging characterization, report-language extraction, differential/mimic-aware review, and clinical-statistical translation.
- Explicit non-use: final diagnosis, treatment recommendation, triage, or unsupported claims.

## Chapter Goals

1. Describe how Intracranial meningioma is expected to present on diagnostic imaging, especially MRI, using radiology-report style language.
2. Identify findings that support or argue against Intracranial meningioma relative to common mimics and relevant MR-RATE categories.
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
As a radiology expert, given a diagnosis of Intracranial meningioma, what would you look for in MRI images to confirm?
```

Advanced prompt:

```text
As a neuroradiologist, given a diagnosis of Intracranial meningioma, what sequence-specific MRI signal characteristics, lesion morphology, anatomic distribution, chronicity features, volume-loss patterns, and associated findings would you expect to see on MRI?
```

Search variants:

- Intracranial meningioma MRI imaging characteristics
- Intracranial meningioma MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics
- Intracranial meningioma MRI lesion morphology anatomic distribution
- Intracranial meningioma MRI chronicity features structural patterns
- Intracranial meningioma MRI associated findings radiology
- Intracranial meningioma MRI differential diagnosis mimics
- Intracranial meningioma MRI report language findings impression
- Intracranial meningioma clinical course progression stable treatment response
- Intracranial meningioma cohort definition endpoint misclassification adjudication

## Differential Matrix Placeholder

Complete `differential-matrix.md` before drafting the disease chapter. Include relevant contrasts to the other MR-RATE categories, ordered roughly from most common to least common in the relevant imaging context.


## Research And Writing Checkpoint

Date/time: 2026-05-08T10:31:50Z

Current phase: final-thorough-research-target-met

### What Has Been Done

- Continued the queue from the manifest and selected `intracranial-meningioma`.
- Expanded the evidence pack to 50 source records, 25 figure evidence records,
  and 15 video or teaching evidence records.
- Drafted a template-conformant disease chapter.
- Updated source review, differential matrix, JSON manifests, alias files,
  manifest, TODO table, and HTML index.
- Rendered the disease HTML preview with `python -m skillforge disease-preview`.

### What Worked

- Guideline, textbook-style, radiology, response-assessment, PET, and molecular
  sources were available.
- The template separated typical imaging, atypical grade-risk clues, mimics,
  treatment context, response assessment, and research design.

### What Did Not Work

- Figure reuse rights were not reviewed.
- Video transcripts were not reviewed.
- Molecular and PET details need expert review before publication-grade claims.

### Problems Or Risks Before Continuing

- Do not treat every dural-based enhancing lesion as meningioma.
- Do not infer WHO grade from imaging alone.
- Do not overstate DOTATATE PET or molecular findings without pathology context.

### What Needs To Change

- Review figure reuse rights and video transcripts.
- Add compact tables for report-language adjudication, grade-risk imaging
  features, and follow-up/treatment-response endpoints if publication-bound.

### Current Confidence

Evidence-count target met; needs human expert review.

### Next Action

Continue the MR-RATE queue with `glioma`, unless a human review pass on
intracranial meningioma is requested first.
