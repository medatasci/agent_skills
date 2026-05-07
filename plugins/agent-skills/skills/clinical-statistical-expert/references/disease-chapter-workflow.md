# Disease Chapter Workflow

Use this workflow when creating, updating, or reviewing a disease chapter for
the `clinical-statistical-expert` skill.

## 1. Define Scope

Record:

- disease or finding name
- primary modality, such as MRI
- included anatomy and disease contexts
- excluded contexts
- whether the chapter is known-diagnosis characterization, mimic-aware review,
  report-language extraction, statistical translation, or all of these

## 2. Start With A Research Checkpoint

Before writing or revising, summarize:

- what has been done
- what worked
- what has not worked
- current blockers or evidence risks
- what needs to change before the chapter can be stronger

Repeat this checkpoint periodically as research and writing proceed.

## 3. Search Authoritative Sources

Use authoritative, relevant sources matched to the scope of the claim.

Prefer broad clinical sources for broad claims:

- medical imaging textbooks or textbook-style chapters available on the web,
  such as NCBI Bookshelf chapters or open educational radiology texts
- professional society guidance and appropriateness criteria, such as ACR,
  RSNA, ASNR, AAN, ILAE, NICE, or disease-specific society guidance
- authoritative radiology training resources written for clinicians,
  radiologists, or trainees, such as Radiology Assistant, MRI Online/Medality,
  Radiopaedia reference articles with citations and revision history, or
  accredited professional education material
- broad clinical, radiology, or consensus reviews when they fit the disease
  scope

Use narrow papers only for narrow claims. Label narrow claims clearly.

## 4. Archive Sources

Record source evidence with:

```text
python -m skillforge source-archive <disease> --source-id <id> --title "<title>" --url <url> --source-type "<type>" --claim-breadth "<broad/narrow/scope>" --section "<section>" --download --json
```

Keep downloaded source pages in the ignored local cache. Do not commit full
source pages unless redistribution is explicitly allowed.

Downloaded access-denial pages, login pages, JavaScript challenges, and other
incomplete pages are not source evidence.

## 5. Search Images Iteratively

Start with broad image searches such as:

- `<disease> in MRI`
- `<disease> appearance in MRI`
- `<disease> progression MRI`
- `<disease> radiology case MRI`
- `<disease> FLAIR T1 T2 DWI ADC SWI`
- `<disease> differential diagnosis MRI`

Then refine based on what works:

- search by etiology, stage, anatomic location, or mimic
- search by source type, such as NCBI Bookshelf, Radiology Assistant, ACR, PMC,
  or textbook-style resources
- keep useful thumbnails only when the source page itself is credible

For promising images, save the image only when reuse is explicitly allowed.
Otherwise record link-only figure evidence.

## 6. Record Figure Evidence

Use:

```text
python -m skillforge figure-evidence <disease> --figure-id <id> --source-title "<title>" --source-url <url> --figure-label "<figure>" --license "<license>" --reuse-status link-only --clinical-point "<point>" --section "<section>" --json
```

For imaging-heavy chapters, review at least 50 image candidates before calling
figure evidence mature. The target is not just a count: confirm source quality,
clinical point, reuse status, and where each figure improves the chapter.

## 7. Write Or Revise The Disease Chapter

Start from:

```text
skillforge/templates/clinical-statistical-expert/disease.md.tmpl
```

The chapter should include:

- goals near the top
- figure evidence and image reuse status
- disease aliases and scope
- known-diagnosis review framing
- what to look for, grouped by longitudinal presentation when useful
- modality-specific appearance
- locations and structural appearance
- differential diagnosis and mimics, including quick guide, imaging
  discriminators, matrix, report-language cues, and context prompts
- Findings-style and Impression-style report-language patterns
- treatment, response, and outcome context when treatment history, guidelines,
  progression criteria, response criteria, or expected outcomes affect imaging
  interpretation or endpoints
- disease course and interval change
- endpoints, structured covariates and confounders, adjudication, and
  statistical implications
- missing information
- expert claim boundaries
- authoritative sources

Descriptions should sound like radiology-report language when the user needs
report-language support. Distinguish findings from impressions.

## 8. Review Weaknesses

Use:

```text
skillforge/templates/clinical-statistical-expert/disease-review-criteria.md.tmpl
```

Review for weak source quality, incomplete modality coverage, vague visual
description, missing differential diagnosis or mimic details, missing
disease-course language, missing treatment/response/outcome context, missing
structured covariates/confounders, unsupported statistical implications,
unclear claim boundaries, and missing information.

## 9. Render HTML Preview

Use:

```text
python -m skillforge disease-preview <disease> --json
```

Review the generated HTML for readability, figure rendering, source counts,
image-candidate counts, and obvious gaps.

## 10. Evaluate Publication Readiness

Use:

```text
python -m skillforge evaluate clinical-statistical-expert --json
```

Before publication, make sure `SKILL.md`, `README.md`, references, source
manifests, figure manifests, generated catalog files, and static pages are
consistent.
