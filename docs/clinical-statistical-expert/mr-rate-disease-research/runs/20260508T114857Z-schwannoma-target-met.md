# Schwannoma Disease Research Cycle

Run timestamp: 2026-05-08T11:48:57Z

## Selected Focus

Schwannoma was selected because it was the first MR-RATE disease queue item
whose evidence artifacts had not reached the final thorough-research target.
The previous completed item was glioma; the next queued item is pituitary
adenoma.

## Work Performed

- Expanded the schwannoma evidence package to 50 source records, 25 figure
  evidence records, and 15 video or teaching evidence records.
- Drafted a template-conformant `schwannoma.md` disease chapter for clinical
  and statistical review.
- Updated source review, differential matrix, research-plan checkpoint, JSON
  evidence manifests, alias manifests, disease queue manifest, TODO table, and
  disease research index.
- Rendered the HTML preview for human review.

## Source Areas Reviewed

- Vestibular schwannoma diagnosis, MRI appearance, management, and follow-up.
- CPA/IAC differential diagnosis, including meningioma, epidermoid cyst,
  arachnoid cyst, metastasis, lipoma, and nonvestibular cranial nerve
  schwannomas.
- Observation, microsurgery, stereotactic radiosurgery, post-SRS enlargement,
  volumetric measurement, hearing preservation, quality of life, and NF2 or
  schwannomatosis context.

## Commands And Checks

```powershell
python docs/clinical-statistical-expert/mr-rate-disease-research/runs/_tmp_build_schwannoma.py
```

Result: passed after adding one missing source record; generated 50 sources, 25
figures, and 15 videos.

```powershell
python -c "import json, pathlib; ..."
```

Result: passed for `sources.json`, `figures.json`, `videos.json`,
`schwannoma.sources.json`, `schwannoma.figures.json`, and
`schwannoma.videos.json`.

```powershell
python -c "import json, pathlib; ..."
```

Result: passed for `manifest.json`.

```powershell
python -m skillforge disease-template-check schwannoma --disease-dir ... --json
```

Result: passed. Required conceptual headings are present, longitudinal
`What To Look For` subsections are present, strict template headings match,
50 sources are recorded, 25 figures are recorded, and supporting artifacts are
present.

```powershell
python -m skillforge disease-preview schwannoma --disease-dir ... --output ... --json
```

Result: passed. HTML preview rendered to
`reports/diseases/schwannoma.html`.

## What Worked

- Guideline, imaging-review, radiology-reference, treatment, syndrome, and
  location-specific sources were available.
- The template structure worked well for separating vestibular schwannoma,
  nonvestibular cranial nerve schwannomas, CPA/IAC mimics, posttreatment
  imaging, and endpoint/statistical implications.

## What Could Be Improved

- Figure reuse rights were not reviewed; all figure records remain link-only.
- Video transcripts were not reviewed.
- Some nonvestibular cranial nerve schwannoma sources remain search-level or
  reference-level and should be deepened if the chapter is prepared for
  publication.
- A future expert pass should add compact tables for Koos/Hannover grading,
  hearing endpoints, post-SRS pseudoprogression, and report-language
  adjudication.

## Gaps And Blockers

- No private clinical data was used.
- No large dependencies, model downloads, credentials, GPU jobs, pushes, or
  merges were used.
- The chapter is evidence-count complete but still needs human expert review
  before publication.

## Files Changed

- `diseases/schwannoma/schwannoma.md`
- `diseases/schwannoma/research-plan.md`
- `diseases/schwannoma/schwannoma.research-plan.md`
- `diseases/schwannoma/source-review.md`
- `diseases/schwannoma/schwannoma.source-review.md`
- `diseases/schwannoma/differential-matrix.md`
- `diseases/schwannoma/sources.json`
- `diseases/schwannoma/schwannoma.sources.json`
- `diseases/schwannoma/figures.json`
- `diseases/schwannoma/schwannoma.figures.json`
- `diseases/schwannoma/videos.json`
- `diseases/schwannoma/schwannoma.videos.json`
- `reports/diseases/schwannoma.html`
- `reports/index.html`
- `manifest.json`
- `TODO.md`

## Recommended Next Action

Continue the MR-RATE queue with `pituitary-adenoma`, unless a human review pass
on schwannoma is requested first.
