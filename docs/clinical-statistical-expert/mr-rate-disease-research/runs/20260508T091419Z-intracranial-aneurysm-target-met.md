# Intracranial Aneurysm Disease Research Run

Run timestamp: 2026-05-08T09:14:19Z

## Selected Focus

Intracranial aneurysm.

## Why This Was Selected

The MR-RATE disease research manifest showed `intracranial-aneurysm` as the
first disease category that had not reached the final thorough-research target
after subdural intracranial hemorrhage.

## Work Performed

- Expanded the disease evidence pack to the thorough-research target:
  - 50 source records.
  - 25 figure or image evidence records.
  - 15 video or teaching evidence records.
- Created the disease chapter:
  - `intracranial-aneurysm.md`
- Updated supporting research artifacts:
  - `research-plan.md`
  - `source-review.md`
  - `differential-matrix.md`
  - `sources.json`
  - `figures.json`
  - `videos.json`
- Created disease-specific alias artifacts:
  - `intracranial-aneurysm.research-plan.md`
  - `intracranial-aneurysm.source-review.md`
  - `intracranial-aneurysm.sources.json`
  - `intracranial-aneurysm.figures.json`
  - `intracranial-aneurysm.videos.json`
- Updated restart and review surfaces:
  - `manifest.json`
  - `TODO.md`
  - `reports/index.html`
- Rendered the disease HTML preview:
  - `reports/diseases/intracranial-aneurysm.html`

## Source Areas Reviewed

- AHA/ASA guidance for unruptured intracranial aneurysm.
- AHA/ASA guidance for aneurysmal subarachnoid hemorrhage.
- ESO guidance for unruptured intracranial aneurysm.
- ACR cerebrovascular imaging appropriateness context.
- NCBI Bookshelf / StatPearls clinical overview.
- Neuroradiology reviews comparing CTA, MRA, and DSA.
- Radiology training resources for aneurysm search pattern and report language.
- Vessel-wall MRI and aneurysm wall enhancement reviews.
- Natural history and risk-model sources including UCAS Japan, PHASES, ELAPSS,
  and UIATS.
- Academic medical center pages and videos for treatment-context framing.

## Commands And Checks

Generated artifacts:

```powershell
python docs/clinical-statistical-expert/mr-rate-disease-research/runs/_tmp_build_intracranial_aneurysm.py
```

Result:

```json
{
  "ok": true,
  "disease": "intracranial-aneurysm",
  "counts": {
    "sources": 50,
    "figures": 25,
    "videos": 15
  },
  "status": "final_thorough_research_target_met_needs_human_review"
}
```

Validated disease JSON artifacts:

```powershell
python -c "load sources.json, figures.json, videos.json, and disease-specific aliases"
```

Result:

```text
json ok: sources.json, figures.json, videos.json, intracranial-aneurysm.sources.json, intracranial-aneurysm.figures.json, intracranial-aneurysm.videos.json
```

Validated manifest JSON:

```powershell
python -c "load manifest.json"
```

Result:

```text
json ok: manifest.json
```

Checked disease chapter against the clinical-statistical-expert disease
template:

```powershell
python -m skillforge disease-template-check intracranial-aneurysm --disease-dir docs/clinical-statistical-expert/mr-rate-disease-research/diseases/intracranial-aneurysm --json
```

Result:

```text
ok: true
required conceptual headings present
all template headings match exactly
50 sources recorded
25 figures recorded
```

Rendered HTML preview:

```powershell
python -m skillforge disease-preview intracranial-aneurysm --disease-dir docs/clinical-statistical-expert/mr-rate-disease-research/diseases/intracranial-aneurysm --output docs/clinical-statistical-expert/mr-rate-disease-research/reports/diseases/intracranial-aneurysm.html --json
```

Result:

```text
ok: true
sources_total: 50
figures_total: 25
local_figures: 0
```

## What Worked

- The manifest-driven queue correctly selected the next below-target disease.
- The disease chapter passed the template conformance check, including strict
  heading matching.
- The source set is anchored in broad guideline, radiology review, and clinical
  review sources, with narrower material labeled as teaching, procedure, or
  biomarker support.
- The chapter separates aneurysm detection, rupture, growth, treatment,
  recurrence, and mimic adjudication, which matters for cohort labels.

## What Could Be Improved

- Figure evidence remains link-only until reuse rights are reviewed.
- Video and teaching evidence records were curated, but transcripts were not
  reviewed in this cycle.
- The chapter would benefit from compact tables for aneurysm reporting fields,
  PHASES/ELAPSS/UIATS-related variables, and post-treatment recurrence
  endpoints.
- Vessel-wall MRI and flow-diverter evidence should be periodically refreshed
  before publication-grade claims.

## Blockers Or Gaps

- No private clinical data was processed.
- No large dependencies, models, GPU jobs, credentials, merge, or push were
  used.
- Human expert review is still needed before treating this as final
  clinical-statistical content.

## Next Action

Continue the MR-RATE queue with `metastatic-malignant-neoplasm-to-brain`,
unless the user wants a human review pass on intracranial aneurysm first.
