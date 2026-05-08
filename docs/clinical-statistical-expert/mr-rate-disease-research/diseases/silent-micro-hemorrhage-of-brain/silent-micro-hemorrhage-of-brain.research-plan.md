# Silent micro-hemorrhage of brain Research Plan

Status: final_thorough_research_target_met_needs_human_review

## Scope Definition

- Disease or finding: Silent micro-hemorrhage of brain
- MR-RATE original name: Cerebral microbleeds
- Ontology source: snomed
- SNOMED CT: 723857007 (Silent micro-hemorrhage of brain)
- Cluster: hemorrhagic_vascular
- Primary imaging modality: MRI
- Intended use: research planning, known-diagnosis imaging characterization, report-language extraction, differential/mimic-aware review, and clinical-statistical translation.
- Explicit non-use: final diagnosis, treatment recommendation, triage, or unsupported claims.

## Chapter Goals

1. Describe how Silent micro-hemorrhage of brain is expected to present on diagnostic imaging, especially MRI, using radiology-report style language.
2. Identify findings that support or argue against Silent micro-hemorrhage of brain relative to common mimics and relevant MR-RATE categories.
3. Translate imaging appearance, uncertainty, and report language into cohort definition, endpoint, covariate, adjudication, and misclassification implications.
4. Extract Findings-style and Impression-style report-language patterns when sources support them.

## Research And Writing Checkpoint

Date/time: 2026-05-07T23:39:48Z

Current phase: source-backed draft and target expansion

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

## Research And Writing Checkpoint

Date/time: 2026-05-08T02:13:54Z

Current phase: source-backed draft, below final thorough-research target

### What Has Been Done

- Expanded the source manifest from 2 starter sources to a broader source pack covering cerebral microbleed definition, SWI/GRE detection, STRIVE-style small-vessel-disease terminology, CAA distribution context, hypertensive microangiopathy distribution context, rating/scoring issues, and selected treatment-risk context.
- Created a source-backed disease chapter draft, source-review artifact, link-only figure manifest, video evidence manifest, refreshed differential matrix, and HTML preview.
- Recorded the new final-readiness target: 50 sources, 25 image or figure evidence records, and 15 YouTube/video evidence records.

### What Worked

- Broad review and consensus sources support core imaging language: small round or ovoid punctate susceptibility foci, most conspicuous on T2* GRE or SWI, representing chronic hemosiderin from prior microscopic hemorrhage.
- The source set supports high-yield distribution contrasts: strictly lobar/cortical-subcortical microbleeds suggest CAA context; deep gray, brainstem, and cerebellar microbleeds suggest hypertensive arteriopathy context.
- MR-RATE-relevant mimics are clear enough for a first differential matrix: cerebral hemorrhage, cavernous malformation, lacunar infarct, gliosis/white matter disease, calcification, hemorrhagic metastasis, diffuse axonal injury, and treatment-related ARIA/radiation effects.

### What Did Not Work

- PMC pages opened through the browser with a client challenge in this environment, so the first pass records them as URL-only evidence rather than locally cached source pages.
- The image review is link-only; no figure assets were stored locally because reuse rights were not reviewed at image-file level.
- YouTube/video evidence discovery found a few strong educational candidates, but not the full 15-video target in one cycle.

### Problems Or Risks Before Continuing

- The chapter should not be treated as final-ready until it reaches the 50 source / 25 figure / 15 video target or a disease-specific lower target is explicitly justified.
- Microbleed count and distribution are highly protocol dependent; cohort use must record SWI/GRE availability, field strength, slice thickness, echo time, and reader method where possible.
- "Silent" should not be overinterpreted from imaging alone; many imaging datasets lack symptoms, but report extraction should separate incidental/subclinical wording from clinically silent adjudication.

### What Needs To Change

- Continue source expansion toward 50 records with priority on guideline/consensus, radiology review, rating-scale, CAA, hypertensive arteriopathy, trauma, ARIA, radiation, and research-method sources.
- Continue image evidence toward 25 records, reviewing source credibility and reuse status before any local image storage.
- Continue video evidence toward 15 records and prefer clinician/radiologist educational sources over general patient-oriented videos.

### Current Confidence

Source-backed draft, not final mature.

### Next Action

Continue the same disease in the next automation cycle unless the user chooses a two-pass strategy that drafts all diseases first and matures targets later.

## Research And Writing Checkpoint

Date/time: 2026-05-08T07:02:41Z

Current phase: final-thorough-research-target-met

### What Has Been Done

- Expanded the evidence package to the current target of 50 sources, 25 image
  or figure evidence records, and 15 YouTube/video evidence records.
- Added evidence coverage for spontaneous microbleed study standards, the
  Microbleed Study Group detection guide, BOMBS and MARS rating frameworks,
  QSM and automated detection methods, Rotterdam population imaging,
  CAA/hypertensive topography, ARIA-H monitoring, antithrombotic/thrombolysis
  outcome context, traumatic microbleed/DAI mimics, cortical superficial
  siderosis, and histopathology correlation.
- Updated the chapter status and source review to reflect evidence-count
  maturity while preserving human expert review, transcript review, and figure
  reuse review as remaining gates.
- Updated `manifest.json` and `TODO.md` so restart logic can move to the next
  below-target disease.

### What Worked

- The existing chapter already passed the template checker, so this cycle could
  focus on evidence depth, source breadth, and artifact maturity.
- The source set now covers the main clinical-statistical risks: protocol
  dependence, rating reliability, burden thresholds, etiologic distribution,
  treatment exposure, longitudinal comparability, and mimic separation.
- Link-only figure and video records allowed safe progress without downloading
  images, using credentials, or processing private clinical data.

### What Did Not Work

- PMC and PubMed pages intermittently showed client-challenge pages in this
  environment, so many records remain URL-only rather than locally cached.
- Figure reuse rights were not reviewed; no local figure assets were embedded.
- Video transcripts were not reviewed, so video evidence remains candidate
  teaching evidence.

### Problems Or Risks Before Continuing

- Microbleed burden is highly sequence-dependent; apparent count changes can be
  artifacts of SWI/GRE availability, field strength, slice thickness, echo time,
  reader method, or automated detection threshold.
- Etiology should remain distribution-informed and probabilistic unless clinical
  context, vascular imaging, pathology, amyloid biomarkers, or treatment context
  support a narrower claim.
- Treatment-risk and ARIA-H statements need expert review before publication.

### What Needs To Change

- Review the generated HTML preview and evidence manifests.
- Consider adding a compact burden/categorization table using MARS, BOMBS, and
  ARIA-H severity references.
- Continue the queue with `cavernous-hemangioma`.

### Current Confidence

Final evidence-count target met; ready for human expert review.

### Next Action

Continue with `cavernous-hemangioma`, which is the next disease in the manifest
below target.

## Expert-Framed Source Discovery

Basic prompt:

```text
As a radiology expert, given a diagnosis of Silent micro-hemorrhage of brain, what would you look for in MRI images to confirm?
```

Advanced prompt:

```text
As a neuroradiologist, given a diagnosis of Silent micro-hemorrhage of brain, what sequence-specific MRI signal characteristics, lesion morphology, anatomic distribution, chronicity features, volume-loss patterns, and associated findings would you expect to see on MRI?
```

Search variants:

- Silent micro-hemorrhage of brain MRI imaging characteristics
- Silent micro-hemorrhage of brain MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics
- Silent micro-hemorrhage of brain MRI lesion morphology anatomic distribution
- Silent micro-hemorrhage of brain MRI chronicity features structural patterns
- Silent micro-hemorrhage of brain MRI associated findings radiology
- Silent micro-hemorrhage of brain MRI differential diagnosis mimics
- Silent micro-hemorrhage of brain MRI report language findings impression
- Silent micro-hemorrhage of brain clinical course progression stable treatment response
- Silent micro-hemorrhage of brain cohort definition endpoint misclassification adjudication

## Differential Matrix Placeholder

Complete `differential-matrix.md` before drafting the disease chapter. Include relevant contrasts to the other MR-RATE categories, ordered roughly from most common to least common in the relevant imaging context.
