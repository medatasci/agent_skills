# Metastatic malignant neoplasm to brain Research Plan

Status: final_thorough_research_target_met_needs_human_review

## Scope Definition

- Disease or finding: Metastatic malignant neoplasm to brain
- MR-RATE original name: Brain metastasis
- Ontology source: snomed
- SNOMED CT: 94225005 (Metastatic malignant neoplasm to brain)
- Cluster: neoplasm_mass
- Primary imaging modality: MRI
- Intended use: research planning, known-diagnosis imaging characterization, report-language extraction, differential/mimic-aware review, and clinical-statistical translation.
- Explicit non-use: final diagnosis, treatment recommendation, triage, or unsupported claims.

## Chapter Goals

1. Describe how Metastatic malignant neoplasm to brain is expected to present on diagnostic imaging, especially MRI, using radiology-report style language.
2. Identify findings that support or argue against Metastatic malignant neoplasm to brain relative to common mimics and relevant MR-RATE categories.
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
As a radiology expert, given a diagnosis of Metastatic malignant neoplasm to brain, what would you look for in MRI images to confirm?
```

Advanced prompt:

```text
As a neuroradiologist, given a diagnosis of Metastatic malignant neoplasm to brain, what sequence-specific MRI signal characteristics, lesion morphology, anatomic distribution, chronicity features, volume-loss patterns, and associated findings would you expect to see on MRI?
```

Search variants:

- Metastatic malignant neoplasm to brain MRI imaging characteristics
- Metastatic malignant neoplasm to brain MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics
- Metastatic malignant neoplasm to brain MRI lesion morphology anatomic distribution
- Metastatic malignant neoplasm to brain MRI chronicity features structural patterns
- Metastatic malignant neoplasm to brain MRI associated findings radiology
- Metastatic malignant neoplasm to brain MRI differential diagnosis mimics
- Metastatic malignant neoplasm to brain MRI report language findings impression
- Metastatic malignant neoplasm to brain clinical course progression stable treatment response
- Metastatic malignant neoplasm to brain cohort definition endpoint misclassification adjudication

## Differential Matrix Placeholder

Complete `differential-matrix.md` before drafting the disease chapter. Include relevant contrasts to the other MR-RATE categories, ordered roughly from most common to least common in the relevant imaging context.


## Research And Writing Checkpoint

Date/time: 2026-05-08T09:51:49Z

Current phase: final-thorough-research-target-met

### What Has Been Done

- Continued the queue from the manifest and selected
  `metastatic-malignant-neoplasm-to-brain`.
- Expanded the evidence pack to 50 source records, 25 figure evidence records,
  and 15 video or teaching evidence records.
- Drafted a template-conformant disease chapter.
- Updated source review, differential matrix, JSON manifests, alias files,
  manifest, TODO table, and HTML index.
- Rendered the disease HTML preview with `python -m skillforge disease-preview`.

### What Worked

- Guideline and consensus sources were available across oncology,
  neuro-oncology, radiation oncology, and imaging.
- Broad neuroradiology reviews supported MRI appearance, treatment monitoring,
  and differential diagnosis.
- The template structure worked well for separating untreated disease,
  posttreatment response, radiation necrosis, and research endpoints.

### What Did Not Work

- Figure reuse rights were not reviewed in this cycle.
- Video transcripts were not reviewed in this cycle.
- Primary-cancer-specific screening and systemic therapy details could not be
  fully captured in a single general chapter.

### Problems Or Risks Before Continuing

- Do not count generic `enhancing lesion` or differential-only report language
  as positive brain metastasis without adjudication.
- Do not merge treatment effect, radiation necrosis, pseudoprogression, and
  progression into one endpoint.
- Do not overstate advanced imaging certainty; perfusion, spectroscopy, and PET
  help but are not universally definitive.

### What Needs To Change

- Add local figure assets only after reuse rights are reviewed.
- Add compact report-language, RANO-BM, and treatment-effect adjudication tables
  if the chapter becomes publication-bound.
- Consider subchapters for lung, breast, melanoma, renal cell carcinoma, and
  leptomeningeal metastasis.

### Current Confidence

Evidence-count target met; needs human expert review.

### Next Action

Continue the MR-RATE queue with `intracranial-meningioma`, unless a human
review pass on brain metastasis is requested first.
