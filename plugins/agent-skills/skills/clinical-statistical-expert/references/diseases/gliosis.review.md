# Gliosis Disease Chapter Review

Review artifact for `docs/clinical-statistical-expert/diseases/gliosis.md`.

Date/time: 2026-05-07

## Overall Rating

- Draft: no.
- Developing: yes.
- Mature: no.
- Needs expert review: yes.

The chapter is now a stronger evidence-backed draft. It has goals, source
status, a source-review artifact, a source manifest, three locally saved figures
with machine-readable metadata, 54 recorded image candidates, and clearer
source stratification. It should not yet be called mature because the source set
still needs a deeper source-to-report-language extraction pass and expert
review, even though the numeric image-candidate target has now been met.

## Source Quality

Rating: developing.

Strengths:

- Broad claims are increasingly grounded in textbook-style NCBI Bookshelf /
  Springer chapters, ACR criteria, and radiology teaching material.
- The chapter now separates broad sources from narrow technical sources.
- Narrow studies are labeled as narrow and are not used to support broad
  routine-MRI claims.
- Source review is documented in `gliosis.source-review.md`.
- Source URLs, local cache status, and reuse notes are now tracked in
  `gliosis.sources.json`.
- The current source manifest records 38 sources, including 28 locally cached
  source pages and 9 URL-first or failed-download records.

Gaps:

- Complete the deeper 100-page-equivalent source extraction before maturity.
- Review Radiopaedia, MRI Online, and Radiology Assistant reuse terms before
  local image storage.
- Convert the expanded source set into more source-derived report language for
  vascular, demyelinating, postsurgical, radiation, and postoperative contexts.
- Review the 51 link-only figure candidates qualitatively before calling figure
  evidence mature.

## Report-Language Extraction

Rating: developing.

Strengths:

- The chapter now distinguishes findings-style language from impression-style
  language.
- Findings examples use radiology-report conventions such as nonexpansile
  T2/FLAIR hyperintensity, volume loss, ex vacuo change, enhancement status,
  diffusion status, and interval stability.
- Impression examples synthesize chronicity, likely etiology, stability, and
  exclusions.
- The source-review artifact now has specific rows for findings-style language,
  impression-style language, and uncertainty/cohort-label language.

Gaps:

- The examples are clinically plausible and source-informed, but more should be
  extracted from real report-style teaching cases and curated imaging examples.
- Vascular, demyelinating, postoperative, and posttreatment contexts need more
  source-derived report phrases.
- A formal label hierarchy is still needed for strong, probable, nonspecific,
  and excluded gliosis labels.

## Clinical Characterization

Rating: developing to strong.

Strengths:

- The chapter frames gliosis as a tissue response/finding rather than a single
  disease.
- It tells the reviewer what to look for: FLAIR/T2 signal, volume loss,
  encephalomalacia, DWI/ADC, SWI/GRE, enhancement, perfusion, and stability.
- It includes a known-diagnosis review frame and missing-information prompts.

Gaps:

- Add more source-backed examples by etiology.
- Add clearer distinction between nonspecific white matter hyperintensity,
  vascular gliosis, demyelinating scar, and posttreatment change.

## Imaging And Modality Coverage

Rating: developing.

Strengths:

- MRI is justified as the primary modality.
- T1, T2, FLAIR, DWI/ADC, SWI/GRE, contrast, perfusion, and spectroscopy are
  separated.
- CT, EEG, PET/SPECT, MEG, pathology, angiography, and vascular imaging are
  discussed as context-dependent adjuncts.
- Figure evidence now includes local CC BY examples for posttraumatic
  encephalomalacia/gliosis, hippocampal sclerosis, and chronic hemorrhagic
  traumatic encephalomalacia.
- The figure manifest now records 54 total candidates, including trauma,
  epilepsy, vascular/perinatal stroke, demyelinating/MS, tumor-mimic,
  posttreatment/radiation, and postoperative contexts.

Gaps:

- Add more formal source support for perfusion, spectroscopy, and PET/MR use.
- Add more detailed protocol requirements for specific use cases such as
  epilepsy, posttreatment tumor, and demyelination.

## Locations And Structural Appearance

Rating: developing.

Strengths:

- The chapter covers cortical/subcortical, deep white matter, periventricular,
  callosal, deep gray, brainstem/cerebellar, hippocampal, tract-like, and
  postoperative/posttreatment patterns.
- It emphasizes morphology and location rather than signal intensity alone.

Gaps:

- Add more source-backed examples for each location.
- Add structured location-specific mimic guidance.

## Disease Course And Interval Change

Rating: developing.

Strengths:

- The chapter uses clinical disease-course headings:
  Natural History And Clinical Course; Evidence Of Active Disease,
  Progression, Or Recurrence; Stable Or Chronic Residual Findings;
  Improvement, Treatment Response, Or Resolution; Serial Imaging Assessment And
  Interval Change.
- It separates chronic gliotic scar from edema, enhancement, diffusion
  abnormality, and active treatment effect.

Gaps:

- Add stronger source-backed disease-course language for each etiology.
- Add prior/current image examples when reusable sources are available.

## Treatment, Response, And Outcome Context

Rating: developing.

Strengths:

- The chapter now states that gliosis is usually not a standalone treatment
  target and organizes treatment context by underlying cause.
- Guideline and criteria sources have been added for tumor-treatment, vascular,
  demyelinating, seizure/epilepsy, and posttreatment contexts.
- The chapter separates posttreatment imaging appearance, treatment response,
  progression/recurrence/treatment failure, expected outcomes, and statistical
  implications.

Gaps:

- The new section still needs deeper source-derived extraction for each
  underlying cause.
- More concrete examples are needed for how treatment history changes report
  language and endpoint definitions.
- Guideline details such as recommendation strength, population, and
  jurisdiction should be filled in when each disease context becomes central to
  a specific study.

## Differential Diagnosis And Mimics

Rating: developing to strong.

Strengths:

- The chapter now has an easy-to-find `## Differential Diagnosis And Mimics`
  section.
- It includes a quick guide, key imaging discriminators, a differential
  diagnosis matrix, report-language cues, and context prompts.
- The matrix includes low-grade glioma, encephalomalacia, acute/subacute
  infarct, demyelinating plaque, tumefactive demyelination, radiation necrosis
  or treatment effect, infection or abscess, cavernous malformation or prior
  hemorrhage, chronic small vessel ischemic disease, and seizure-related or
  postictal signal abnormality.
- Each comparator now includes why it can look similar, features supporting
  gliosis, features arguing against gliosis, helpful sequences or context,
  example report language, and statistical or cohort implications.
- Each matrix row now has source anchors so readers can see which references
  support the comparator framing.

Gaps:

- Add more source-specific extraction on gliosis versus low-grade glioma,
  radiation necrosis, chronic demyelinating plaque, and postoperative
  treatment-bed change.
- Add high-yield embedded or link-only example figures for the most important
  mimic categories.

## Covariates And Confounders

Rating: developing to strong.

Strengths:

- `## Common Covariates And Confounders` is easy to find.
- The section now separates clinical covariates, imaging covariates, treatment
  and temporal confounders, acquisition/protocol confounders, and research
  design implications.
- It explicitly calls out etiology, treatment history, time from event,
  scanner/protocol, clinical indication, prior imaging, reader expertise, and
  adjudication.
- It connects covariates to adjustment, stratification, adjudication,
  sensitivity analysis, and claims language.

Gaps:

- Add example case-report-form fields for gliosis extraction.
- Add source-backed measurement reliability and inter-reader variability
  references.
- Add disease-specific covariate tables for vascular, demyelinating,
  posttreatment tumor, epilepsy, and trauma contexts.

## Statistical Translation

Rating: developing to strong.

Strengths:

- The chapter identifies label uncertainty, etiologic heterogeneity,
  misclassification, confounding, endpoint ambiguity, inter-reader variability,
  longitudinal bias, and sensitivity analysis.
- It proposes structured labels for etiology, region, lesion type, stability,
  adjudication, and mimic concern.

Gaps:

- Add source-backed measurement reliability, inter-reader, and protocol
  variability references.
- Add example case-report-form fields or cohort-definition variables.

## Expert Use And Claim Boundaries

Rating: developing.

Strengths:

- The chapter preserves expert-facing boundaries around claims language and
  etiology, prognosis, and cohort-label inference.
- It flags growth, enhancement, restricted diffusion, mass effect, and missing
  history as limits on confident "stable gliosis" language.

Gaps:

- Consider whether this section should be shorter and more expert-facing in the
  next pass.

## Missing Information And Open Gaps

Rating: developing.

Strengths:

- The chapter lists missing clinical, imaging, timing, and study-design
  information.
- The source-review file lists explicit research and image gaps.

Gaps:

- Add an evidence-gap table keyed to specific chapter sections.
- Review link-only figure metadata for postoperative/posttreatment examples and
  decide whether any can be converted to local embeddable figures.

## Recommended Next Action

Run a second focused source extraction pass on:

1. Vascular/postischemic gliosis and chronic infarct.
2. Demyelinating plaque versus nonspecific gliosis.
3. Radiation necrosis, treatment effect, and postoperative gliosis.
4. Gliosis versus low-grade glioma and other mass-like mimics.
