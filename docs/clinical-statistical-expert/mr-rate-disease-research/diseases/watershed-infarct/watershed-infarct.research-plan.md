# Watershed infarct Research Plan

Status: ready_for_expert_review

## Scope Definition

- Disease or finding: Watershed infarct
- MR-RATE original name: Watershed infarct
- Ontology source: snomed
- SNOMED CT: 47559000 (Watershed infarct)
- Cluster: ischemic_vascular
- Primary imaging modality: MRI
- Intended use: research planning, known-diagnosis imaging characterization, report-language extraction, differential/mimic-aware review, and clinical-statistical translation.
- Explicit non-use: final diagnosis, treatment recommendation, triage, or unsupported claims.

## Chapter Goals

1. Describe how Watershed infarct is expected to present on diagnostic imaging, especially MRI, using radiology-report style language.
2. Identify findings that support or argue against Watershed infarct relative to common mimics and relevant MR-RATE categories.
3. Translate imaging appearance, uncertainty, and report language into cohort definition, endpoint, covariate, adjudication, and misclassification implications.
4. Extract Findings-style and Impression-style report-language patterns when sources support them.

## Research And Writing Checkpoint

Date/time: 2026-05-08T01:55:31Z

Current phase: evaluate-and-gap-list

### What Has Been Done

- Created initial scope from the MR-RATE pathology/SNOMED mapping file.
- Generated an expert-framed source discovery query pack in `../../query-packs.json`.
- Reviewed watershed-specific and stroke-imaging sources.
- Drafted the disease chapter from the template method.
- Recorded source evidence, figure candidates, and a cross-disease differential matrix.
- Rendered the HTML preview for human expert review.

### What Worked

- The source category is mapped to an ontology concept in the MR-RATE source file.
- Watershed infarct has strong subtype-specific imaging language: cortical/external border zones, internal/deep border zones, ACA/MCA and MCA/PCA distributions, deep lesions parallel to the lateral ventricles, and string-of-pearls pattern.
- The contrast with lacunar infarct, cerebral infarction, embolic infarcts, chronic gliosis/encephalomalacia, and demyelinating disease is clinically useful.

### What Did Not Work

- Several source pages were browser-challenge or abstract/landing-page accessible in this environment, so full local source caching was not completed.
- Figure evidence remains link-only; no figure reuse rights were cleared for local embedding.

### Problems Or Risks Before Continuing

- Mechanism should not be overcalled from imaging pattern alone because watershed infarcts can involve hypoperfusion, embolism, or mixed mechanisms.
- Chronic watershed sequelae should not be counted as acute stroke endpoints without interval or DWI evidence.

### What Needs To Change

- Expert review should confirm differential ordering, treatment/outcome framing, and wording for internal watershed versus lacunar infarct.
- Additional image candidates should be reviewed before mature publication.

### Current Confidence

Ready for expert review.

### Next Action

Move to the next disease in sequence after regenerating HTML and validating artifacts.

## Expert-Framed Source Discovery

Basic prompt:

```text
As a radiology expert, given a diagnosis of Watershed infarct, what would you look for in MRI images to confirm?
```

Advanced prompt:

```text
As a neuroradiologist, given a diagnosis of Watershed infarct, what sequence-specific MRI signal characteristics, lesion morphology, anatomic distribution, chronicity features, volume-loss patterns, and associated findings would you expect to see on MRI?
```

Search variants:

- Watershed infarct MRI imaging characteristics
- Watershed infarct MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics
- Watershed infarct MRI lesion morphology anatomic distribution
- Watershed infarct MRI chronicity features structural patterns
- Watershed infarct MRI associated findings radiology
- Watershed infarct MRI differential diagnosis mimics
- Watershed infarct MRI report language findings impression
- Watershed infarct clinical course progression stable treatment response
- Watershed infarct cohort definition endpoint misclassification adjudication

## Differential Matrix Placeholder

Complete `differential-matrix.md` before drafting the disease chapter. Include relevant contrasts to the other MR-RATE categories, ordered roughly from most common to least common in the relevant imaging context.

## Research And Writing Checkpoint

Date/time: 2026-05-08T05:38:07Z

Current phase: final evidence-count target met; human expert review needed

### What Has Been Done

- Expanded the source manifest to 50 records.
- Expanded the figure manifest to 25 records.
- Created and expanded the video evidence manifest to 15 records.
- Added evidence for hemodynamic and embolic watershed mechanisms, carotid
  stenosis and collateral status, perfusion and vascular imaging context,
  internal versus cortical border-zone patterns, arterial-territory mapping,
  stroke mimics, and general acute-stroke imaging workflow.
- Added template-style source, figure, video, research-plan, and source-review
  aliases so the disease preview and template checks can find the supporting
  artifacts.
- Updated the manifest and task list so the next automation cycle can move to
  `cerebral-hemorrhage`.

### What Worked

- The watershed literature has strong pattern language: external cortical
  border zones, internal deep border zones, ACA/MCA and MCA/PCA junctions,
  linear deep lesions, rosary-like pattern, and string-of-pearls pattern.
- Added hemodynamic, carotid/collateral, and perfusion sources support
  mechanism uncertainty and covariate selection.
- The chapter body now includes the missing template-required human/agent
  sections and passes strict heading checks.

### What Did Not Work

- Most figures remain link-only because reuse rights were not reviewed at the
  image-file level.
- Video evidence remains candidate evidence until transcripts are reviewed.

### Problems Or Risks Before Continuing

- Mechanism should remain probabilistic unless vascular, perfusion, and
  clinical context support a hypoperfusion, embolic, or mixed classification.
- Internal watershed infarcts can be confused with lacunar infarcts, embolic
  shower patterns, chronic gliosis, demyelination, or broad cerebral infarction
  labels.

### What Needs To Change

- Review source claims and video transcripts before publication.
- Grade figure reuse status and embed only assets with clear permission.
- Reconcile report-language examples with MR-RATE report phrases when available.

### Current Confidence

Evidence-count target met; ready for human expert review, not final clinical
publication.

### Next Action

Move to rank 4 in the MR-RATE queue and apply the same maturity-target pass to
`cerebral-hemorrhage`.
