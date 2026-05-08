# Cerebral hemorrhage Research Plan

Status: final_thorough_research_target_met_needs_human_review

## Scope Definition

- Disease or finding: Cerebral hemorrhage
- MR-RATE original name: Intracerebral hemorrhage
- Ontology source: snomed
- SNOMED CT: 274100004 (Cerebral hemorrhage)
- Cluster: hemorrhagic_vascular
- Primary imaging modality: MRI
- Intended use: research planning, known-diagnosis imaging characterization, report-language extraction, differential/mimic-aware review, and clinical-statistical translation.
- Explicit non-use: final diagnosis, treatment recommendation, triage, or unsupported claims.

## Chapter Goals

1. Describe how Cerebral hemorrhage is expected to present on diagnostic imaging, especially MRI, using radiology-report style language.
2. Identify findings that support or argue against Cerebral hemorrhage relative to common mimics and relevant MR-RATE categories.
3. Translate imaging appearance, uncertainty, and report language into cohort definition, endpoint, covariate, adjudication, and misclassification implications.
4. Extract Findings-style and Impression-style report-language patterns when sources support them.

## Research And Writing Checkpoint

Date/time: 2026-05-08T01:59:47Z

Current phase: evaluate-and-gap-list

### What Has Been Done

- Created initial scope from the MR-RATE pathology/SNOMED mapping file.
- Generated an expert-framed source discovery query pack in `../../query-packs.json`.
- Reviewed broad imaging, guideline, and radiology reference sources.
- Drafted the disease chapter from the template method.
- Recorded source evidence, figure candidates, and a cross-disease differential matrix.
- Rendered the HTML preview for human expert review.

### What Worked

- The source category is mapped to an ontology concept in the MR-RATE source file.
- The topic has a strong authoritative source base for CT/MRI appearance, blood-product evolution, location patterns, complications, and etiologic clues.
- The MR-RATE contrasts with cerebral infarction, microhemorrhage, subdural hemorrhage, cavernous malformation, tumor, and edema are clinically useful.

### What Did Not Work

- Some PubMed and journal pages are abstract-only or browser-challenge accessible in this environment.
- Figure evidence remains link-only; no figure reuse rights were cleared for local embedding.

### Problems Or Risks Before Continuing

- Risk of mixing primary intraparenchymal hemorrhage with hemorrhagic transformation, subdural hemorrhage, microbleeds, or hemorrhagic tumor.
- Treatment pathway context should not be turned into patient-level treatment recommendations.

### What Needs To Change

- Expert review should confirm treatment/outcome wording and whether a compact MRI blood-product table should be added.
- Additional image candidates should be reviewed before mature publication.

### Current Confidence

Ready for expert review.

### Next Action

Move to the next disease in sequence after regenerating HTML and validating artifacts.

## Research And Writing Checkpoint

Date/time: 2026-05-08T06:21:10Z

Current phase: final-thorough-research-target-met

### What Has Been Done

- Expanded the evidence package to the current target of 50 sources, 25 figure
  evidence records, and 15 video evidence records.
- Added source coverage for spontaneous ICH imaging, CT/MRI blood-product
  interpretation, SWI/GRE, CTA spot sign, noncontrast CT expansion markers,
  ABC/2 volume measurement, perihematomal edema, outcome predictors,
  neuroprognostication, CAA/Boston criteria context, and radiology teaching
  resources.
- Updated the disease chapter to expose template-required differential,
  endpoint, covariate, confounder, source-breadth, and claim-boundary sections.
- Added slug-prefixed evidence aliases for restart-safe validation.

### What Worked

- The source base has enough broad material to support imaging appearance,
  modality choice, report-language patterns, and key cohort-design variables.
- Hemorrhagic-vascular contrasts with silent micro-hemorrhage, subdural
  hemorrhage, cavernous malformation, infarction, tumor, and cerebral edema are
  actionable for MR-RATE-style labeling.
- URL-only figure and video evidence allowed safe progress without downloading
  assets or using credentials.

### What Did Not Work

- Figure reuse rights were not cleared, so no local figure images were embedded.
- Video transcripts were not reviewed, so videos remain teaching evidence rather
  than extracted source text.
- Some sources are URL-only because full text or journal pages may require
  access patterns outside this local automation.

### Problems Or Risks Before Continuing

- Acute primary intraparenchymal hemorrhage can be mislabeled if mixed with
  hemorrhagic transformation, microbleeds, extra-axial hemorrhage, cavernous
  malformation, hemorrhagic tumor, or CAA-marker burden.
- Treatment and outcome statements need stroke-domain expert review before
  publication.

### What Needs To Change

- Review the generated HTML preview, figure evidence, and video evidence.
- Decide whether to add a compact blood-product evolution table in a later
  refinement pass.
- Continue the queue with `silent-micro-hemorrhage-of-brain`.

### Current Confidence

Final evidence-count target met; ready for human expert review.

### Next Action

Continue with `silent-micro-hemorrhage-of-brain`, which is the next disease in
the manifest below target.

## Expert-Framed Source Discovery

Basic prompt:

```text
As a radiology expert, given a diagnosis of Cerebral hemorrhage, what would you look for in MRI images to confirm?
```

Advanced prompt:

```text
As a neuroradiologist, given a diagnosis of Cerebral hemorrhage, what sequence-specific MRI signal characteristics, lesion morphology, anatomic distribution, chronicity features, volume-loss patterns, and associated findings would you expect to see on MRI?
```

Search variants:

- Cerebral hemorrhage MRI imaging characteristics
- Cerebral hemorrhage MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics
- Cerebral hemorrhage MRI lesion morphology anatomic distribution
- Cerebral hemorrhage MRI chronicity features structural patterns
- Cerebral hemorrhage MRI associated findings radiology
- Cerebral hemorrhage MRI differential diagnosis mimics
- Cerebral hemorrhage MRI report language findings impression
- Cerebral hemorrhage clinical course progression stable treatment response
- Cerebral hemorrhage cohort definition endpoint misclassification adjudication

## Differential Matrix Placeholder

Complete `differential-matrix.md` before drafting the disease chapter. Include relevant contrasts to the other MR-RATE categories, ordered roughly from most common to least common in the relevant imaging context.
