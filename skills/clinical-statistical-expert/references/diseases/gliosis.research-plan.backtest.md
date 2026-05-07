# Gliosis Disease Chapter Research Plan Backtest

This is a blinded backtest protocol for the disease research-plan workflow.
It is not the original research plan for the gliosis chapter, and it is not an
unblinded comparison result.

The purpose is to test whether
`skillforge/templates/clinical-statistical-expert/disease-research-plan.md.tmpl`
can guide an agent or human author toward a high-quality gliosis research plan
without reading the current gliosis disease chapter.

## Core Constraint

The drafter must not read, search, summarize, quote, diff, or otherwise use the
current gliosis chapter or any derivative review artifact while creating the
blinded research-plan draft.

Do not use these files during the blinded drafting phase:

- `gliosis.md`
- `gliosis.review.md`
- `gliosis.source-review.md`
- `gliosis.build-retrospective.md`
- previous summaries of the current gliosis chapter

Allowed inputs during blinded drafting:

- `disease-research-plan.md.tmpl`
- the disease or finding name: gliosis in the brain
- user-supplied goals and scope
- newly collected authoritative sources
- newly recorded source evidence created during the backtest
- newly recorded figure evidence created during the backtest

## Required Output Sequence

1. Create a blinded research-plan draft from the template.
2. Save that draft before any comparison work begins.
3. Record the source evidence and figure evidence used by the blinded draft.
4. Mark the blinded draft as frozen with date/time, source list, and known gaps.
5. Only after the blinded draft is frozen, allow a separate reviewer to open the
   existing chapter and create an unblinded comparison artifact.

Recommended filenames:

- Blinded draft: `gliosis.research-plan.blinded.md`
- Blinded source evidence: `gliosis.research-plan.sources.json`
- Blinded figure evidence: `gliosis.research-plan.figures.json`
- Unblinded comparison: `gliosis.research-plan.backtest-comparison.md`

The unblinded comparison file should state clearly that it was written after
the existing chapter became visible.

## Scope Definition

- Disease or finding: gliosis in the brain.
- Primary imaging modality: MRI.
- Secondary modalities to consider when source-supported: CT, SWI/GRE,
  DWI/ADC, contrast-enhanced MRI, perfusion MRI, spectroscopy, PET/SPECT,
  EEG, vascular imaging, pathology, and prior imaging.
- Included contexts to research: posttraumatic, postischemic, postsurgical,
  posttreatment, radiation-related, postinfectious, demyelinating or
  inflammatory, seizure-related, hippocampal sclerosis, chronic white matter
  change, and Wallerian degeneration when source support is present.
- Explicit boundary: do not turn the chapter into patient-specific diagnosis,
  treatment selection, etiology assignment, prognosis assignment, or
  adjudication without clinical context.

## Chapter Goals

1. Describe how gliosis appears on brain MRI when gliosis or a gliotic sequela
   is already suspected or known.
2. Describe what to look for when considering common mimics or differential
   diagnoses with similar imaging presentation.
3. Capture realistic radiology-report language for Findings and Impression
   sections, including uncertainty and interval-change language.
4. Map imaging and report-language patterns to clinical-statistical uses such
   as cohort definitions, endpoints, covariates, adjudication, and claims
   boundaries.
5. Identify reusable or link-only figures that help users recognize structural
   appearance, location patterns, chronicity, mimics, and treatment context.

## Search Plan Starting Points

Use broad, authoritative sources before narrow primary studies:

- medical imaging textbooks or textbook-style chapters available on the web
- professional society guidance and appropriateness criteria
- authoritative radiology training resources with citations or revision history
- broad review articles for natural history, treatment context, and imaging
  progression
- narrow primary studies only for specialized claims, biomarkers, radiomics,
  pathology correlation, or advanced imaging methods

Search terms should evolve based on what the sources reveal. Initial searches
may include:

- gliosis brain MRI
- cerebral gliosis MRI appearance
- encephalomalacia gliosis MRI
- posttraumatic gliosis MRI
- hippocampal sclerosis gliosis MRI
- chronic infarct gliosis MRI
- gliosis differential diagnosis MRI
- gliosis radiology report findings impression

## Blinded Draft Checklist

Before freezing the blinded draft, confirm that it asks for:

- source review status and unresolved source gaps
- terminology, aliases, and realistic report phrases
- structural appearance by imaging sequence and disease-course context
- Findings-style and Impression-style wording
- location and pattern-based differential diagnosis
- mimics and distinguishing features
- treatment, response, outcome, and progression context
- covariates, confounders, and statistical implications
- figure evidence with local-use or link-only rights captured
- related disease chapters and related statistical method files
- claim boundaries and author handoff notes

## Unblinded Comparison Questions

After the blinded plan is frozen, a separate reviewer may compare it to the
existing chapter. The comparison should ask:

- Did the blinded plan anticipate the major content categories needed for the
  chapter?
- Did it ask for source evidence, figure evidence, report language,
  differential diagnosis, treatment/outcome context, confounders, and claim
  boundaries?
- Which useful chapter needs were missed by the blinded plan?
- Which plan sections did not produce useful chapter content?
- What changes should be made to the template before the next prospective
  disease build?

## Current Status

This protocol is ready to be executed as a blinded workflow. It should not be
treated as proof of reproducibility until the blinded draft is actually created
without accessing the current chapter and then reviewed separately.

The next prospective disease workflow should still be run because a backtest,
even when blinded, is weaker evidence than creating a new disease chapter from
the template from the beginning.
