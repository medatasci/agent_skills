# Gliosis Build Retrospective

This file records how the `gliosis.md` disease chapter was actually built and
what that experience implies for the next prospective disease-chapter workflow.

It is intentionally not a reconstructed research plan. Gliosis was created as a
prototype while the `clinical-statistical-expert` process, templates, review
criteria, and evidence records were still being designed. Creating a
`gliosis.research-plan.md` after the fact could imply more reproducibility than
the current history supports.

## Retrospective Summary

Gliosis was useful as a first disease chapter because it forced the workflow to
handle a clinically messy topic. Gliosis is usually a tissue response or imaging
finding rather than a single disease entity. That exposed the need for a
structured source hierarchy, figure evidence records, mimic-aware comparison,
report-language extraction, disease-course framing, treatment/outcome context,
and a content reviewer.

## What Was Actually Done

1. A prototype `gliosis.md` chapter was drafted before a complete prospective
   disease research plan existed.
2. The chapter revealed gaps in the original disease template, especially around
   known-diagnosis review, report-like imaging descriptions, differential
   diagnosis, longitudinal disease course, treatment response, covariates,
   confounders, and statistical translation.
3. The disease chapter template was expanded while the gliosis chapter was being
   improved.
4. A source review artifact, source evidence record, figure evidence record, and
   content review artifact were created to support the chapter.
5. Source collection used authoritative, relevant sources where possible:
   textbook-style NCBI Bookshelf/Springer chapters, professional criteria,
   radiology teaching resources, broad reviews, and narrow technical studies
   only for narrow claims.
6. Image evidence was added after the initial chapter draft. Three reusable
   local images were saved from sources with explicit CC BY 4.0 reuse permission,
   and additional candidates were recorded as link-only evidence.
7. The content reviewer marked the chapter as developing and needing expert
   review rather than mature.

## What Worked

- The book-and-chapter model worked: the expert role belongs at the book level,
  while disease-specific knowledge belongs in chapter files.
- The disease chapter became much stronger after adding explicit sections for
  what to look for, report language, locations, mimics, disease course,
  treatment/outcome context, covariates, and statistical implications.
- The source review artifact helped separate broad support from narrow support.
- The figure evidence record prevented local image reuse from being assumed.
- The content reviewer made it possible to preserve a developing maturity state
  instead of treating a large chapter as complete.

## What Did Not Work

- The research plan did not exist before the chapter. This means gliosis proves
  that the workflow is needed, but it does not prove that the workflow can
  reproduce a high-quality chapter from scratch.
- Some source discovery was opportunistic rather than driven by a pre-existing
  plan.
- The source review includes research-plan-like material, but it is not a clean
  prospective plan.
- The current chapter still needs a deeper source-to-report-language extraction
  pass for vascular, demyelinating, postoperative, posttreatment, radiation, and
  tumor-mimic contexts.
- Some useful image sources remain link-only or need reuse review.

## Reproducibility Risk

The main risk is provenance inversion: writing a research plan after the
chapter can make the workflow look more reproducible than it was. The honest
claim is:

> Gliosis is a prototype chapter that helped discover the workflow. The next
> disease should be the prospective test of the workflow.

## Backward Check Against `disease-research-plan.md.tmpl`

This check asks whether the current research-plan template would reasonably
cause a future author or agent to create the material that appears in
`gliosis.md`.

| Gliosis chapter content | Current research-plan support | Would it reasonably be created? | Suggested change |
| --- | --- | --- | --- |
| Goals | Scope definition and required clinical/statistical questions partially support this. | Partial. | Add explicit "Chapter Goals" fields for known-diagnosis characterization, differential review, and statistical translation. |
| Source Review Status | Source archive, source review log, and maturity decision support this. | Yes. | No major change. |
| Figure Evidence | Minimum image depth, adaptive image search, image log, and image checkpoint support this. | Yes. | No major change. |
| Common Names And Aliases | Search strategy mentions disease name and aliases. | Partial. | Add an explicit alias/terminology extraction row. |
| Scope | Scope definition directly supports this. | Yes. | No major change. |
| Clinical Context | Required clinical extraction questions support mechanism and clinical relevance. | Yes. | No major change. |
| Known-Diagnosis Review Frame | Clinical extraction questions support this indirectly. | Partial. | Add an explicit known-diagnosis review question: what to look for when the diagnosis is known, and what cannot be inferred. |
| What To Look For | Required clinical, disease-course, and report-language questions support this. | Yes. | No major change. |
| Acute, subacute, chronic, progressive, improving phases | Required disease-course questions support this. | Yes. | No major change. |
| Report Language Patterns | Required report-language questions support this. | Yes. | No major change. |
| Primary Imaging Modality | Scope definition and required clinical questions support this. | Yes. | No major change. |
| Other Modalities | Scope definition and modality search terms support this. | Yes. | No major change. |
| Locations And Structural Appearance | Search strategy and required clinical questions support this. | Yes. | No major change. |
| Typical Appearance | Required clinical questions support typical and atypical appearance. | Yes. | No major change. |
| Atypical Or Red-Flag Appearance | Required clinical questions support atypical and missing-context concerns. | Yes. | No major change. |
| Differential Diagnosis And Mimics | Mimic search terms and mimic-aware questions support this. | Yes. | No major change. |
| Differential Diagnosis Matrix | Mimic questions support this, but not the matrix structure. | Partial. | Add an explicit differential matrix extraction target with comparator, similar appearance, discriminators, report language, and research implication. |
| Natural History And Clinical Course | Required disease-course questions support this. | Yes. | No major change. |
| Treatment, Response, And Outcome Context | Disease-course questions mention treatment response, but not full treatment/outcome context. | Partial. | Add required treatment/outcome extraction questions for guideline context, treatment pathways, posttreatment imaging, progression/failure, expected outcomes, and statistical implications. |
| Evidence Of Active Disease, Progression, Or Recurrence | Required disease-course questions support this. | Yes. | No major change. |
| Stable Or Chronic Residual Findings | Required disease-course questions support this. | Yes. | No major change. |
| Improvement, Treatment Response, Or Resolution | Required disease-course questions support this. | Yes. | No major change. |
| Serial Imaging Assessment And Interval Change | Required disease-course questions support interval change. | Yes. | No major change. |
| Clinical Endpoints | Required statistical translation questions support endpoints. | Yes. | No major change. |
| Imaging, Biomarker, And Measurement Endpoints | Required statistical translation questions support endpoints and biomarkers. | Yes. | No major change. |
| Common Covariates And Confounders | Required statistical questions ask about covariates and confounders. | Partial. | Add structured extraction for clinical, imaging, treatment/temporal, acquisition/protocol, and research-design confounders. |
| Statistical Implications | Required statistical translation questions support this. | Yes. | No major change. |
| Missing Information To Ask For | Required clinical questions include missing information. | Yes. | No major change. |
| Expert Use And Claim Boundaries | Maturity decision and source principles support this indirectly. | Partial. | Add explicit claim-boundary extraction: what claims are supported, uncertain, exploratory, confirmatory, or out of scope. |
| Related Disease Files | Not meaningfully covered. | No. | Add a related-files planning step for disease chapters and statistical method files. |
| Related Statistical Method Files | Not meaningfully covered. | No. | Add a related-files planning step for statistical methods needed by the chapter. |
| Authoritative Sources | Source selection principle and source review log support this. | Yes. | No major change. |
| Notes For Skill Authors | Not directly covered. | Partial. | Add a final author-notes section for workflow learnings, unresolved template gaps, and handoff notes. |

## Recommended Template Improvements For Review

These changes would make `disease-research-plan.md.tmpl` a stronger prospective
driver for the next disease.

1. Add `## Chapter Goals`.
   - Capture known-diagnosis characterization.
   - Capture differential or mimic-aware review.
   - Capture clinical-statistical translation.

2. Add explicit terminology extraction.
   - Disease names and aliases.
   - Synonyms used in radiology reports.
   - Ambiguous terms that need mapping rules.

3. Add known-diagnosis review extraction.
   - What should be reviewed when the diagnosis is already known?
   - What findings support the diagnosis?
   - What findings argue for a mimic or alternate explanation?
   - What cannot be inferred from imaging alone?

4. Add differential diagnosis matrix extraction.
   - Comparator condition.
   - Why it looks similar.
   - Features supporting the target disease.
   - Features arguing against the target disease.
   - Helpful sequences or clinical context.
   - Report language.
   - Statistical or cohort implications.

5. Add treatment, response, and outcome extraction.
   - Guideline-based management context.
   - Common treatment pathways.
   - Imaging appearance after treatment.
   - Evidence of treatment response.
   - Evidence of progression, recurrence, or treatment failure.
   - Expected outcomes and prognostic factors.
   - Statistical implications of treatment and progression.

6. Strengthen covariate and confounder extraction.
   - Clinical covariates.
   - Imaging covariates.
   - Treatment and temporal confounders.
   - Acquisition and protocol confounders.
   - Research design implications.

7. Add claim-boundary extraction.
   - Supported claims.
   - Uncertain claims.
   - Narrow technical claims.
   - Exploratory versus confirmatory claims.
   - Claims that require expert adjudication.

8. Add related-file planning.
   - Related disease chapters to create or cross-reference.
   - Related statistical method files to create or cross-reference.
   - Related evidence records or previews to update.

9. Add a template coverage check.
   - Before drafting, list expected chapter sections.
   - After drafting, mark each section as supported, partial, missing, or not
     applicable.
   - Preserve gaps rather than filling them with weak claims.

## Recommended Prospective Test

The next disease should be built from the templates in this order:

1. Create `<disease>.research-plan.md`.
2. Create `<disease>.sources.json`.
3. Create `<disease>.figures.json`.
4. Research and fill the source and figure evidence records.
5. Write `<disease>.source-review.md`.
6. Draft `<disease>.md`.
7. Run the content reviewer into `<disease>.review.md`.
8. Render `<disease>.html`.
9. Compare the final chapter to the research plan and record whether the
   template actually caused the needed material to be created.

Only the next prospective disease can validate reproducibility. Gliosis can
serve as the prototype, the backtest, and the benchmark.
