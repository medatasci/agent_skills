# Pituitary adenoma Research Plan

Status: final_thorough_research_target_met_needs_human_review

## Scope Definition

- Disease or finding: Pituitary adenoma
- MR-RATE original name: Pituitary adenoma
- Ontology source: snomed
- SNOMED CT: 254956000 (Pituitary adenoma)
- Cluster: neoplasm_mass
- Primary imaging modality: MRI
- Intended use: research planning, known-diagnosis imaging characterization, report-language extraction, differential/mimic-aware review, and clinical-statistical translation.
- Explicit non-use: final diagnosis, treatment recommendation, triage, or unsupported claims.

## Chapter Goals

1. Describe how Pituitary adenoma is expected to present on diagnostic imaging, especially MRI, using radiology-report style language.
2. Identify findings that support or argue against Pituitary adenoma relative to common mimics and relevant MR-RATE categories.
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
As a radiology expert, given a diagnosis of Pituitary adenoma, what would you look for in MRI images to confirm?
```

Advanced prompt:

```text
As a neuroradiologist, given a diagnosis of Pituitary adenoma, what sequence-specific MRI signal characteristics, lesion morphology, anatomic distribution, chronicity features, volume-loss patterns, and associated findings would you expect to see on MRI?
```

Search variants:

- Pituitary adenoma MRI imaging characteristics
- Pituitary adenoma MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics
- Pituitary adenoma MRI lesion morphology anatomic distribution
- Pituitary adenoma MRI chronicity features structural patterns
- Pituitary adenoma MRI associated findings radiology
- Pituitary adenoma MRI differential diagnosis mimics
- Pituitary adenoma MRI report language findings impression
- Pituitary adenoma clinical course progression stable treatment response
- Pituitary adenoma cohort definition endpoint misclassification adjudication

## Differential Matrix Placeholder

Complete `differential-matrix.md` before drafting the disease chapter. Include relevant contrasts to the other MR-RATE categories, ordered roughly from most common to least common in the relevant imaging context.


## Research And Writing Checkpoint

Date/time: 2026-05-08T12:26:59Z

Current phase: final-thorough-research-target-met

### What Has Been Done

- Continued the queue from the manifest and selected `pituitary-adenoma`.
- Expanded evidence to 50 source records, 25 figure evidence records, and 15
  video or teaching evidence records.
- Drafted a template-conformant disease chapter and updated source review,
  differential matrix, JSON manifests, alias files, manifest, TODO table, and
  HTML index.
- Rendered the disease HTML preview.

### What Worked

- Strong source coverage exists across radiology, endocrinology, neurosurgery,
  pituitary society guidance, NCBI/Endotext chapters, and sellar differential
  references.
- The template separated microadenoma, macroadenoma, functioning subtype,
  nonfunctioning adenoma, apoplexy, postoperative residual tumor, and mimics.

### What Did Not Work

- Figure reuse rights and video transcripts were not reviewed.
- Some functional subtype and postoperative imaging details remain high-level
  and should be deepened before publication.

### Problems Or Risks Before Continuing

- Do not treat every sellar mass as pituitary adenoma.
- Preserve microadenoma versus macroadenoma and functioning versus
  nonfunctioning distinctions.
- Separate imaging response from biochemical remission.

### What Needs To Change

- Add compact tables for endocrine subtype, Knosp/cavernous sinus invasion,
  postoperative residual tumor, and report-language adjudication if
  publication-bound.

### Current Confidence

Evidence-count target met; needs human expert review.

### Next Action

Continue the MR-RATE queue with `lipoma-of-brain`, unless a human review pass
on pituitary adenoma is requested first.
