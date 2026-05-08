# Lacunar infarct Research Plan

Status: not_started

## Scope Definition

- Disease or finding: Lacunar infarct
- MR-RATE original name: Lacunar infarct
- Ontology source: snomed
- SNOMED CT: 81037000 (Lacunar infarct)
- Cluster: ischemic_vascular
- Primary imaging modality: MRI
- Intended use: research planning, known-diagnosis imaging characterization, report-language extraction, differential/mimic-aware review, and clinical-statistical translation.
- Explicit non-use: final diagnosis, treatment recommendation, triage, or unsupported claims.

## Chapter Goals

1. Describe how Lacunar infarct is expected to present on diagnostic imaging, especially MRI, using radiology-report style language.
2. Identify findings that support or argue against Lacunar infarct relative to common mimics and relevant MR-RATE categories.
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
As a radiology expert, given a diagnosis of Lacunar infarct, what would you look for in MRI images to confirm?
```

Advanced prompt:

```text
As a neuroradiologist, given a diagnosis of Lacunar infarct, what sequence-specific MRI signal characteristics, lesion morphology, anatomic distribution, chronicity features, volume-loss patterns, and associated findings would you expect to see on MRI?
```

Search variants:

- Lacunar infarct MRI imaging characteristics
- Lacunar infarct MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics
- Lacunar infarct MRI lesion morphology anatomic distribution
- Lacunar infarct MRI chronicity features structural patterns
- Lacunar infarct MRI associated findings radiology
- Lacunar infarct MRI differential diagnosis mimics
- Lacunar infarct MRI report language findings impression
- Lacunar infarct clinical course progression stable treatment response
- Lacunar infarct cohort definition endpoint misclassification adjudication

## Differential Matrix Placeholder

Complete `differential-matrix.md` before drafting the disease chapter. Include relevant contrasts to the other MR-RATE categories, ordered roughly from most common to least common in the relevant imaging context.

## Research And Writing Checkpoint

Date/time: 2026-05-08T04:21:04Z

Current phase: maturity expansion, below final thorough-research target

### What Has Been Done

- Reinterpreted `ready_for_expert_review` as draft status rather than final
  status because it does not meet the final 50/25/15 target.
- Expanded the source manifest to 30 records.
- Expanded the figure manifest to 15 records.
- Created a video evidence manifest with 8 records.
- Added template-style artifact aliases so `disease-preview` and
  `disease-template-check` can find the source and figure manifests.
- Left the existing MR-RATE-aware differential matrix in place because it
  already contrasts lacunar infarct with cerebral infarction, watershed
  infarct, silent micro-hemorrhage, gliosis/white matter disease,
  demyelinating disease, and other common mimics.

### What Worked

- New source material strengthened recent small subcortical infarct morphology,
  branch atheromatous disease, enlarged perivascular-space mimics, chronic
  lacune evolution, SPS3 outcome/covariate context, and video teaching support.
- The chapter body already followed the disease template well, so the safest
  path was to expand evidence and status tracking rather than rewrite it.

### What Did Not Work

- The disease remains below final target. It needs more source, image, and
  video evidence before being final-ready.
- No local figure assets were copied because reuse rights were not reviewed at
  the image-file level.

### Problems Or Risks Before Continuing

- Lacunar infarct overlaps heavily with broader cerebral infarction and
  cerebral small vessel disease. Future passes should keep acute lacunar
  infarct, chronic lacune, diffuse white matter disease, microbleeds, and
  enlarged perivascular spaces as distinct labels.
- Treatment and prevention statements should remain research-context language
  and should be checked against current professional guidance.

### What Needs To Change

- Add at least 20 more source records, 10 more figure records, and 7 more video
  records or explicitly justify a lower target.
- Review video transcripts and mark which ones are high authority versus
  teaching-only.
- Review figure reuse rights and embed only assets with clear permission.

### Current Confidence

Strong source-backed draft, not final mature.

### Next Action

Continue expanding `lacunar-infarct` until the final target is met, then return
to rank 3 and repeat the maturity pass for `watershed-infarct`.

## Research And Writing Checkpoint

Date/time: 2026-05-08T04:59:06Z

Current phase: final evidence-count target met; human expert review needed

### What Has Been Done

- Expanded the source manifest to 50 records.
- Expanded the figure manifest to 25 records.
- Expanded the video evidence manifest to 15 records.
- Added evidence for incident lacunes, recurrent lacunar infarction,
  domain-specific cognitive impairment, long-term outcomes, perivascular-space
  mimics, MRI-based mechanism classification, perfusion status, capillary
  small-vessel disease mechanisms, and additional lacunar/small-vessel disease
  teaching videos.
- Updated the manifest and task list so the next automation cycle can move to
  `watershed-infarct`.

### What Worked

- The new evidence closed the numeric maturity gap without downloading
  restricted figures, using private data, installing large dependencies, or
  running expensive compute.
- The added sources improve clinical-statistical endpoint support for
  recurrence, cognition, mortality, disability, vascular events, and imaging
  progression.

### What Did Not Work

- Most new figures remain link-only because reuse rights were not reviewed at
  the image-file level.
- Video evidence remains candidate evidence until transcripts are reviewed.

### Problems Or Risks Before Continuing

- The evidence-count target is met, but source extraction is uneven. Future
  lacunar work should prioritize claim review and human expert adjudication
  over adding more sources.
- The chapter must continue distinguishing acute lacunar infarct, chronic
  lacune, enlarged perivascular space, white matter disease, microbleed,
  watershed infarct, embolic infarct, and branch atheromatous disease.

### What Needs To Change

- Review source claims and video transcripts before publication.
- Grade figure reuse status and embed only assets with clear permission.
- Reconcile report-language examples with MR-RATE report phrases when available.

### Current Confidence

Evidence-count target met; ready for human expert review, not final clinical
publication.

### Next Action

Move to rank 3 in the MR-RATE queue and apply the same maturity-target pass to
`watershed-infarct`.
