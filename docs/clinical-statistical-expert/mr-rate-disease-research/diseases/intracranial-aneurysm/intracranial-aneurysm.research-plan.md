# Intracranial aneurysm Research Plan

Status: final_thorough_research_target_met_needs_human_review

## Scope Definition

- Disease or finding: Intracranial aneurysm
- MR-RATE original name: Intracranial aneurysm
- Ontology source: snomed
- SNOMED CT: 128609009 (Intracranial aneurysm)
- Cluster: hemorrhagic_vascular
- Primary imaging modality: MRI
- Intended use: research planning, known-diagnosis imaging characterization, report-language extraction, differential/mimic-aware review, and clinical-statistical translation.
- Explicit non-use: final diagnosis, treatment recommendation, triage, or unsupported claims.

## Chapter Goals

1. Describe how Intracranial aneurysm is expected to present on diagnostic imaging, especially MRI, using radiology-report style language.
2. Identify findings that support or argue against Intracranial aneurysm relative to common mimics and relevant MR-RATE categories.
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
As a radiology expert, given a diagnosis of Intracranial aneurysm, what would you look for in MRI images to confirm?
```

Advanced prompt:

```text
As a neuroradiologist, given a diagnosis of Intracranial aneurysm, what sequence-specific MRI signal characteristics, lesion morphology, anatomic distribution, chronicity features, volume-loss patterns, and associated findings would you expect to see on MRI?
```

Search variants:

- Intracranial aneurysm MRI imaging characteristics
- Intracranial aneurysm MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics
- Intracranial aneurysm MRI lesion morphology anatomic distribution
- Intracranial aneurysm MRI chronicity features structural patterns
- Intracranial aneurysm MRI associated findings radiology
- Intracranial aneurysm MRI differential diagnosis mimics
- Intracranial aneurysm MRI report language findings impression
- Intracranial aneurysm clinical course progression stable treatment response
- Intracranial aneurysm cohort definition endpoint misclassification adjudication

## Differential Matrix Placeholder

Complete `differential-matrix.md` before drafting the disease chapter. Include relevant contrasts to the other MR-RATE categories, ordered roughly from most common to least common in the relevant imaging context.


## Research And Writing Checkpoint

Date/time: 2026-05-08T09:14:19Z

Current phase: final-thorough-research-target-met

### What Has Been Done

- Continued the queue from the manifest and selected `intracranial-aneurysm`.
- Expanded the evidence pack to 50 source records, 25 figure evidence records,
  and 15 video or teaching evidence records.
- Drafted a template-conformant disease chapter.
- Updated source review, differential matrix, JSON manifests, alias files,
  manifest, TODO table, and HTML index.
- Rendered the disease HTML preview with `python -m skillforge disease-preview`.

### What Worked

- Broad guideline and review sources were available for unruptured aneurysm,
  ruptured aneurysmal SAH, imaging modality selection, natural history, and
  treatment context.
- Radiology training resources gave practical search-pattern and report
  language cues.
- The template workflow separated clinical imaging appearance, differential
  diagnosis, treatment context, endpoints, covariates, and claim boundaries.

### What Did Not Work

- Figure reuse rights were not reviewed in this cycle.
- Video transcripts were not reviewed in this cycle.
- Some treatment and advanced imaging claims require periodic refresh because
  device and vessel-wall MRI evidence is evolving.

### Problems Or Risks Before Continuing

- Do not conflate subarachnoid hemorrhage with aneurysm unless the aneurysm is
  identified or explicitly favored.
- Do not include infundibula, vascular loops, or ruled-out aneurysm language as
  positive labels.
- Do not overstate vessel-wall enhancement as a definitive predictor of
  rupture.

### What Needs To Change

- Add local figure assets only after reuse rights are reviewed.
- Add compact risk-model and report-language tables if the chapter becomes
  publication-bound.
- Review video transcripts and decide which are strong enough to support
  educational claims.

### Current Confidence

Evidence-count target met; needs human expert review.

### Next Action

Continue the MR-RATE queue with `metastatic-malignant-neoplasm-to-brain`,
unless a human review pass on intracranial aneurysm is requested first.
