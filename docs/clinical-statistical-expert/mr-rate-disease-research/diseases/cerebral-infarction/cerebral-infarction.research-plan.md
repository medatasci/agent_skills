# Cerebral infarction Research Plan

Status: existing_chapter_needs_cross_disease_update

## Scope Definition

- Disease or finding: Cerebral infarction
- MR-RATE original name: Ischemic infarct
- Ontology source: snomed
- SNOMED CT: 432504007 (Cerebral infarction)
- Cluster: ischemic_vascular
- Primary imaging modality: MRI
- Intended use: research planning, known-diagnosis imaging characterization, report-language extraction, differential/mimic-aware review, and clinical-statistical translation.
- Explicit non-use: final diagnosis, treatment recommendation, triage, or unsupported claims.

## Chapter Goals

1. Describe how Cerebral infarction is expected to present on diagnostic imaging, especially MRI, using radiology-report style language.
2. Identify findings that support or argue against Cerebral infarction relative to common mimics and relevant MR-RATE categories.
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

## Research And Writing Checkpoint

Date/time: 2026-05-08T02:57:27Z

Current phase: maturity expansion, below final thorough-research target

### What Has Been Done

- Reinterpreted `ready_for_expert_review` as draft status rather than final
  status because it does not meet the new final 50/25/15 target.
- Expanded the source manifest to 24 records.
- Expanded the figure manifest to 19 records.
- Created a starter video evidence manifest with 10 records.
- Added template-style artifact aliases so `disease-preview` and
  `disease-template-check` can find the source and figure manifests.

### What Worked

- Additional open-access review sources strengthened DWI/ADC/FLAIR timing,
  CT/MR perfusion, vascular-territory lesion patterns, acute CT signs, and
  stroke mimic context.
- Video sources are useful for human and agent onboarding because they explain
  workflow and cases more intuitively than the source manifest alone.

### What Did Not Work

- The disease is still below final target. It needs more source, image, and
  video evidence before being final-ready.
- Several strong figures are link-only because reuse rights were not reviewed
  at the image-file level.

### Problems Or Risks Before Continuing

- The source list is becoming broad. Future passes should prioritize source
  quality and coverage gaps rather than adding duplicates.
- Treatment-pathway statements should remain research context and should defer
  to the latest AHA/ASA, ACR, ESO, and NICE guidance.

### What Needs To Change

- Add at least 26 more source records, 6 more figure records, and 5 more video
  records or explicitly justify a lower target.
- Review video transcripts and mark which ones are high authority versus
  teaching-only.
- Add final source-review notes for lacunar, watershed, posterior circulation,
  hemorrhagic transformation, venous infarct, seizure/migraine mimic, and tumor
  mimic coverage.

### Current Confidence

Strong source-backed draft, not final mature.

### Next Action

Continue expanding cerebral infarction until the final target is met, then
return to rank 2 and repeat the maturity pass.

## Research And Writing Checkpoint

Date/time: 2026-05-08T03:38:03Z

Current phase: final evidence-count target met; human expert review needed

### What Has Been Done

- Expanded the source manifest to 50 records.
- Expanded the figure manifest to 25 records.
- Expanded the video evidence manifest to 15 records.
- Added evidence from newer textbook-style stroke-and-mimics chapters,
  non-contrast MRI sequence review, DWI-FLAIR mismatch literature, Canadian
  Stroke Best Practices, vascular-territory atlas papers, and additional
  stroke imaging teaching videos.
- Updated the manifest and task list so the next automation cycle can move to
  the next disease needing maturity expansion.

### What Worked

- The strongest new sources improved coverage of MRI sequence timing,
  DWI/ADC/FLAIR mismatch, CT/MR perfusion, stroke mimics, vascular-territory
  localization, low-field MRI caveats, and practical video case teaching.
- The evidence package now reaches the requested numeric maturity target
  without downloading restricted images or using private data.

### What Did Not Work

- Most new figures remain link-only because reuse rights were not reviewed at
  the image-file level.
- Video evidence is still candidate evidence until transcripts or full video
  content are reviewed.

### Problems Or Risks Before Continuing

- The disease has enough evidence records, but source extraction is uneven.
  Future refinement should prioritize claim-quality review over adding more
  sources.
- Treatment-selection and reperfusion statements must stay in research-context
  language and be checked against current professional guidance.

### What Needs To Change

- Review source claims and video transcripts before publication.
- Grade figure reuse status and embed only assets with clear reuse permission.
- Add more realistic report-language examples from reviewed cases or MR-RATE
  reports when available.

### Current Confidence

Evidence-count target met; ready for human expert review, not final clinical
publication.

### Next Action

Move to rank 2 in the MR-RATE queue and apply the same maturity-target pass to
`lacunar-infarct`.

## Expert-Framed Source Discovery

Basic prompt:

```text
As a radiology expert, given a diagnosis of Cerebral infarction, what would you look for in MRI images to confirm?
```

Advanced prompt:

```text
As a neuroradiologist, given a diagnosis of Cerebral infarction, what sequence-specific MRI signal characteristics, lesion morphology, anatomic distribution, chronicity features, volume-loss patterns, and associated findings would you expect to see on MRI?
```

Search variants:

- Cerebral infarction MRI imaging characteristics
- Cerebral infarction MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics
- Cerebral infarction MRI lesion morphology anatomic distribution
- Cerebral infarction MRI chronicity features structural patterns
- Cerebral infarction MRI associated findings radiology
- Cerebral infarction MRI differential diagnosis mimics
- Cerebral infarction MRI report language findings impression
- Cerebral infarction clinical course progression stable treatment response
- Cerebral infarction cohort definition endpoint misclassification adjudication

## Differential Matrix Placeholder

Complete `differential-matrix.md` before drafting the disease chapter. Include relevant contrasts to the other MR-RATE categories, ordered roughly from most common to least common in the relevant imaging context.
