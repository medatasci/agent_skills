# Metastatic Malignant Neoplasm To Brain Disease Research Run

Run timestamp: 2026-05-08T09:51:49Z

## Selected Focus

Metastatic malignant neoplasm to brain, corresponding to the MR-RATE source
label `Brain metastasis`.

## Why This Was Selected

The MR-RATE disease research manifest showed
`metastatic-malignant-neoplasm-to-brain` as the first disease category that had
not reached the final thorough-research target after intracranial aneurysm.

## Work Performed

- Expanded the disease evidence pack to the thorough-research target:
  - 50 source records.
  - 25 figure or image evidence records.
  - 15 video or teaching evidence records.
- Created the disease chapter:
  - `metastatic-malignant-neoplasm-to-brain.md`
- Updated supporting research artifacts:
  - `research-plan.md`
  - `source-review.md`
  - `differential-matrix.md`
  - `sources.json`
  - `figures.json`
  - `videos.json`
- Created disease-specific alias artifacts:
  - `metastatic-malignant-neoplasm-to-brain.research-plan.md`
  - `metastatic-malignant-neoplasm-to-brain.source-review.md`
  - `metastatic-malignant-neoplasm-to-brain.sources.json`
  - `metastatic-malignant-neoplasm-to-brain.figures.json`
  - `metastatic-malignant-neoplasm-to-brain.videos.json`
- Updated restart and review surfaces:
  - `manifest.json`
  - `TODO.md`
  - `reports/index.html`
- Rendered the disease HTML preview:
  - `reports/diseases/metastatic-malignant-neoplasm-to-brain.html`

## Source Areas Reviewed

- ASCO-SNO-ASTRO and ASTRO brain metastasis guidelines.
- NICE adult brain tumors and brain metastases guidance.
- EANO-ESMO brain metastasis guidance.
- NCBI Bookshelf / StatPearls brain metastasis and palliative radiation
  therapy chapters.
- Society for Neuro-Oncology consensus review.
- Broad neuroradiology reviews for MRI appearance, advanced imaging, and
  treatment monitoring.
- RANO-BM, PET RANO-BM, and treatment-response sources.
- Radiation necrosis, pseudoprogression, perfusion MRI, and treatment-effect
  sources.
- Differential sources for glioma, abscess, lymphoma, tumefactive demyelination,
  dural metastasis, meningioma, hemorrhage, and cavernous malformation.

## Commands And Checks

Generated artifacts:

```powershell
python docs/clinical-statistical-expert/mr-rate-disease-research/runs/_tmp_build_brain_metastasis.py
```

Result:

```json
{
  "ok": true,
  "disease": "metastatic-malignant-neoplasm-to-brain",
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
json ok: sources.json, figures.json, videos.json, metastatic-malignant-neoplasm-to-brain.sources.json, metastatic-malignant-neoplasm-to-brain.figures.json, metastatic-malignant-neoplasm-to-brain.videos.json
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
python -m skillforge disease-template-check metastatic-malignant-neoplasm-to-brain --disease-dir docs/clinical-statistical-expert/mr-rate-disease-research/diseases/metastatic-malignant-neoplasm-to-brain --json
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
python -m skillforge disease-preview metastatic-malignant-neoplasm-to-brain --disease-dir docs/clinical-statistical-expert/mr-rate-disease-research/diseases/metastatic-malignant-neoplasm-to-brain --output docs/clinical-statistical-expert/mr-rate-disease-research/reports/diseases/metastatic-malignant-neoplasm-to-brain.html --json
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
- The source set is anchored in broad guideline, consensus, NCBI Bookshelf,
  and neuroradiology review sources.
- The chapter separates untreated metastasis, treated metastasis, progression,
  radiation necrosis, pseudoprogression, leptomeningeal disease, and
  differential-only report language.

## What Could Be Improved

- Figure evidence remains link-only until reuse rights are reviewed.
- Video and teaching evidence records were curated, but transcripts were not
  reviewed in this cycle.
- The chapter would benefit from compact tables for report-language
  adjudication, RANO-BM response categories, treatment-effect mimics, and
  primary-cancer-specific subgroups.
- Primary-cancer-specific screening and systemic therapy details should be
  split into subchapters if this becomes publication-bound.

## Blockers Or Gaps

- No private clinical data was processed.
- No large dependencies, models, GPU jobs, credentials, merge, or push were
  used.
- Human expert review is still needed before treating this as final
  clinical-statistical content.

## Next Action

Continue the MR-RATE queue with `intracranial-meningioma`, unless the user
wants a human review pass on brain metastasis first.
