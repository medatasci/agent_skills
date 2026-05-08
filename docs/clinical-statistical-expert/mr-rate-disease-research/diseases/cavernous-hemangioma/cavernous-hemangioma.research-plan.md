# Cavernous hemangioma Research Plan

Status: final_thorough_research_target_met_needs_human_review

## Scope Definition

- Disease or finding: Cavernous hemangioma
- MR-RATE original name: Cavernous malformation
- Ontology source: snomed
- SNOMED CT: 416824008 (Cavernous hemangioma)
- Cluster: hemorrhagic_vascular
- Primary imaging modality: MRI
- Intended use: research planning, known-diagnosis imaging characterization, report-language extraction, differential/mimic-aware review, and clinical-statistical translation.
- Explicit non-use: final diagnosis, treatment recommendation, triage, or unsupported claims.

## Chapter Goals

1. Describe how Cavernous hemangioma is expected to present on diagnostic imaging, especially MRI, using radiology-report style language.
2. Identify findings that support or argue against Cavernous hemangioma relative to common mimics and relevant MR-RATE categories.
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
As a radiology expert, given a diagnosis of Cavernous hemangioma, what would you look for in MRI images to confirm?
```

Advanced prompt:

```text
As a neuroradiologist, given a diagnosis of Cavernous hemangioma, what sequence-specific MRI signal characteristics, lesion morphology, anatomic distribution, chronicity features, volume-loss patterns, and associated findings would you expect to see on MRI?
```

Search variants:

- Cavernous hemangioma MRI imaging characteristics
- Cavernous hemangioma MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics
- Cavernous hemangioma MRI lesion morphology anatomic distribution
- Cavernous hemangioma MRI chronicity features structural patterns
- Cavernous hemangioma MRI associated findings radiology
- Cavernous hemangioma MRI differential diagnosis mimics
- Cavernous hemangioma MRI report language findings impression
- Cavernous hemangioma clinical course progression stable treatment response
- Cavernous hemangioma cohort definition endpoint misclassification adjudication

## Differential Matrix Placeholder

Complete `differential-matrix.md` before drafting the disease chapter. Include relevant contrasts to the other MR-RATE categories, ordered roughly from most common to least common in the relevant imaging context.

## Research And Writing Checkpoint

Date/time: 2026-05-08T07:44:12Z

Current phase: final-thorough-research-target-met

### What Has Been Done

- Expanded the evidence package to the current target of 50 sources, 25 figure
  evidence records, and 15 video evidence records.
- Drafted the disease chapter from the clinical-statistical template.
- Created source review, source manifest, figure manifest, video evidence
  manifest, differential matrix, slug-prefixed restart aliases, HTML preview,
  manifest updates, TODO updates, and run log.
- Added coverage for guidelines, MRI appearance, Zabramski categories, DVA
  association, natural history, seizures, brainstem lesions, pediatric lesions,
  familial genetics, radiation context, surgery/radiosurgery, and mimics.

### What Worked

- Current 2025 consensus guidelines and 2017 guideline synopsis provide strong
  disease-specific clinical and imaging scaffolding.
- GeneReviews and StatPearls provide clear public-safe explanations of
  Zabramski classification, familial disease, and MRI sequence use.
- Radiology and natural-history sources support actionable cohort variables and
  endpoints.

### What Did Not Work

- Some articles are abstract-only or publisher pages; the package records them
  as URL-only evidence.
- Figure evidence remains link-only because reuse rights were not reviewed.
- Video records are not transcribed.

### Problems Or Risks Before Continuing

- Risk of overcalling nonspecific punctate susceptibility foci as cavernous
  malformation without family, DVA, radiation, or larger-lesion context.
- Risk of mixing CCM-related hemorrhage with primary ICH, tumor hemorrhage,
  AVM/fistula, or traumatic microhemorrhage.
- Treatment comparisons are confounded by indication and should be interpreted
  as research context, not patient-level guidance.

### What Needs To Change

- Human review should inspect report-language examples, treatment/outcome
  statements, and figure candidates.
- Add a compact Zabramski and endpoint table in a later refinement pass if
  useful.
- Continue the queue with `subdural-intracranial-hemorrhage`.

### Current Confidence

Final evidence-count target met; ready for human expert review.

### Next Action

Continue with `subdural-intracranial-hemorrhage`, which is the next disease in
the manifest below target.
