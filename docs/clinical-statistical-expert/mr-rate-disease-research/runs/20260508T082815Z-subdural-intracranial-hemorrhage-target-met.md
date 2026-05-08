# Subdural Intracranial Hemorrhage Disease Research Run

Run timestamp: 2026-05-08T08:28:15Z

## Selected Focus

Subdural intracranial hemorrhage, corresponding to the MR-RATE source label
`Extra-axial hematoma`.

## Why This Was Selected

The MR-RATE disease research manifest showed `subdural-intracranial-hemorrhage`
as the first disease category that had not reached the final thorough-research
target after cavernous hemangioma.

## Work Performed

- Expanded the disease evidence pack to the thorough-research target:
  - 50 source records.
  - 25 figure or image evidence records.
  - 15 video or interactive teaching evidence records.
- Created the disease chapter:
  - `subdural-intracranial-hemorrhage.md`
- Updated supporting research artifacts:
  - `research-plan.md`
  - `source-review.md`
  - `differential-matrix.md`
  - `sources.json`
  - `figures.json`
  - `videos.json`
- Created disease-specific alias artifacts:
  - `subdural-intracranial-hemorrhage.research-plan.md`
  - `subdural-intracranial-hemorrhage.source-review.md`
  - `subdural-intracranial-hemorrhage.sources.json`
  - `subdural-intracranial-hemorrhage.figures.json`
  - `subdural-intracranial-hemorrhage.videos.json`
- Updated restart and review surfaces:
  - `manifest.json`
  - `TODO.md`
  - `reports/index.html`
- Rendered the disease HTML preview:
  - `reports/diseases/subdural-intracranial-hemorrhage.html`

## Source Areas Reviewed

- Broad clinical sources for subdural hematoma anatomy, etiology, risk factors,
  evaluation, and management.
- Brain Trauma Foundation / Congress of Neurological Surgeons acute subdural
  hematoma surgical guidance.
- ACR head trauma imaging-selection context.
- Radiology reviews for CT/MRI appearance, acute/subacute/chronic evolution,
  extra-axial compartment localization, mass effect, and chronic SDH internal
  architecture.
- Chronic SDH reviews covering recurrence, membranes, septations, bilateral
  disease, and treatment pathways.
- Middle meningeal artery embolization reviews and patient-facing academic
  medical center material for treatment-context framing.
- Differential sources for epidural hematoma, subdural hygroma, subdural
  empyema, subarachnoid hemorrhage, cerebral hemorrhage, intracranial
  hypotension, and postoperative extra-axial collections.

## Commands And Checks

Generated artifacts:

```powershell
python docs/clinical-statistical-expert/mr-rate-disease-research/runs/_tmp_build_subdural_intracranial_hemorrhage.py
```

Result:

```json
{
  "ok": true,
  "disease": "subdural-intracranial-hemorrhage",
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
json ok: sources.json, figures.json, videos.json, subdural-intracranial-hemorrhage.sources.json, subdural-intracranial-hemorrhage.figures.json, subdural-intracranial-hemorrhage.videos.json
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
python -m skillforge disease-template-check subdural-intracranial-hemorrhage --disease-dir docs/clinical-statistical-expert/mr-rate-disease-research/diseases/subdural-intracranial-hemorrhage --json
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
python -m skillforge disease-preview subdural-intracranial-hemorrhage --disease-dir docs/clinical-statistical-expert/mr-rate-disease-research/diseases/subdural-intracranial-hemorrhage --output docs/clinical-statistical-expert/mr-rate-disease-research/reports/diseases/subdural-intracranial-hemorrhage.html --json
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
- The evidence pack now separates broad source records, figure evidence,
  video/interactive teaching evidence, source review notes, and differential
  contrasts.
- The chapter captures the important research-design distinction between
  specific subdural hematoma language and nonspecific extra-axial collection
  language.

## What Could Be Improved

- Figure evidence remains link-only until reuse rights are reviewed.
- Video and interactive teaching evidence records were curated, but transcripts
  were not reviewed in this cycle.
- The chapter would benefit from compact tables for acute/subacute/chronic
  imaging appearance, surgical decision variables, and chronic SDH recurrence
  endpoints.
- Middle meningeal artery embolization evidence is changing quickly and should
  be refreshed before publication-grade claims.

## Blockers Or Gaps

- No private clinical data was processed.
- No large dependencies, models, GPU jobs, credentials, merge, or push were
  used.
- Human expert review is still needed before treating this as final
  clinical-statistical content.

## Next Action

Continue the MR-RATE queue with `intracranial-aneurysm`, unless the user wants
a human review pass on subdural intracranial hemorrhage first.
