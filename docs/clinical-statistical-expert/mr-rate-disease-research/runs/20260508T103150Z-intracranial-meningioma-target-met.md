# Intracranial Meningioma Disease Research Run

Run timestamp: 2026-05-08T10:31:50Z

## Selected Focus

Intracranial meningioma, corresponding to the MR-RATE source label
`Meningioma`.

## Why This Was Selected

The MR-RATE disease research manifest showed `intracranial-meningioma` as the
first disease category that had not reached the final thorough-research target
after brain metastasis.

## Work Performed

- Expanded the disease evidence pack to the thorough-research target:
  - 50 source records.
  - 25 figure or image evidence records.
  - 15 video or teaching evidence records.
- Created the disease chapter:
  - `intracranial-meningioma.md`
- Updated supporting research artifacts:
  - `research-plan.md`
  - `source-review.md`
  - `differential-matrix.md`
  - `sources.json`
  - `figures.json`
  - `videos.json`
- Created disease-specific alias artifacts:
  - `intracranial-meningioma.research-plan.md`
  - `intracranial-meningioma.source-review.md`
  - `intracranial-meningioma.sources.json`
  - `intracranial-meningioma.figures.json`
  - `intracranial-meningioma.videos.json`
- Updated restart and review surfaces:
  - `manifest.json`
  - `TODO.md`
  - `reports/index.html`
- Rendered the disease HTML preview:
  - `reports/diseases/intracranial-meningioma.html`

## Source Areas Reviewed

- EANO meningioma diagnosis and management guideline.
- NICE adult brain tumor guidance and meningioma follow-up evidence review.
- NCBI Bookshelf / StatPearls meningioma and location-specific chapters.
- ACR brain tumor imaging appropriateness context.
- Broad meningioma MRI pictorial and imaging-spectrum reviews.
- Molecular classification, WHO 2021, TERT, and molecular-risk sources.
- RANO-Meningioma response-assessment and post-radiotherapy transient
  enlargement sources.
- DOTATATE PET/MRI and PET/CT sources for SSTR-positive disease delineation.
- Differential sources for dural metastasis, solitary fibrous tumor,
  schwannoma, glioma, lymphoma, macroadenoma, epidermoid, and chordoma.

## Commands And Checks

Generated artifacts:

```powershell
python docs/clinical-statistical-expert/mr-rate-disease-research/runs/_tmp_build_intracranial_meningioma.py
```

Result:

```json
{
  "ok": true,
  "disease": "intracranial-meningioma",
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
json ok: sources.json, figures.json, videos.json, intracranial-meningioma.sources.json, intracranial-meningioma.figures.json, intracranial-meningioma.videos.json
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
python -m skillforge disease-template-check intracranial-meningioma --disease-dir docs/clinical-statistical-expert/mr-rate-disease-research/diseases/intracranial-meningioma --json
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
python -m skillforge disease-preview intracranial-meningioma --disease-dir docs/clinical-statistical-expert/mr-rate-disease-research/diseases/intracranial-meningioma --output docs/clinical-statistical-expert/mr-rate-disease-research/reports/diseases/intracranial-meningioma.html --json
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
- The evidence set covers typical imaging, atypical/high-grade features,
  molecular risk, PET, treatment response, and major dural-mass mimics.
- The chapter explicitly warns against treating every dural-based enhancing
  mass as meningioma.

## What Could Be Improved

- Figure evidence remains link-only until reuse rights are reviewed.
- Video and teaching evidence records were curated, but transcripts were not
  reviewed in this cycle.
- The chapter would benefit from compact tables for report-language
  adjudication, imaging grade-risk features, location-specific risks,
  DOTATATE use, and treatment-response endpoints.
- Molecular-risk and PET claims need expert review before publication-grade
  use.

## Blockers Or Gaps

- No private clinical data was processed.
- No large dependencies, models, GPU jobs, credentials, merge, or push were
  used.
- Human expert review is still needed before treating this as final
  clinical-statistical content.

## Next Action

Continue the MR-RATE queue with `glioma`, unless the user wants a human review
pass on intracranial meningioma first.
