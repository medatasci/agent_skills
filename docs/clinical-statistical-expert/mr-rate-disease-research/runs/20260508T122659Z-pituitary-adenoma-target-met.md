# Pituitary Adenoma Disease Research Cycle

Run timestamp: 2026-05-08T12:26:59Z

## Selected Focus

Pituitary adenoma was selected because it was the first MR-RATE disease queue
item whose evidence artifacts had not reached the final thorough-research
target. The previous completed item was schwannoma; the next queued item is
lipoma of brain.

## Work Performed

- Expanded the pituitary adenoma evidence package to 50 source records, 25
  figure evidence records, and 15 video or teaching evidence records.
- Drafted a template-conformant `pituitary-adenoma.md` disease chapter for
  clinical and statistical review.
- Updated source review, differential matrix, research-plan checkpoint, JSON
  evidence manifests, alias files, disease queue manifest, TODO table, and
  disease research index.
- Rendered the HTML preview for human review.

## Source Areas Reviewed

- Dedicated pituitary MRI, sellar/parasellar MRI anatomy, and microadenoma
  versus macroadenoma imaging.
- Endocrine Society incidentaloma guidance, CNS/AANS nonfunctioning pituitary
  adenoma guidance, Pituitary Society prolactinoma consensus, Endotext, NCBI
  Bookshelf, and WHO/PitNET terminology reviews.
- Functional subtypes including prolactinoma, somatotroph/GH adenoma,
  corticotroph/ACTH adenoma, nonfunctioning adenoma, and apoplexy.
- Sellar/parasellar mimics including Rathke cleft cyst, craniopharyngioma,
  meningioma, aneurysm, hypophysitis, empty sella, arachnoid cyst, lipoma,
  metastasis, and postoperative change.

## Commands And Checks

```powershell
python docs/clinical-statistical-expert/mr-rate-disease-research/runs/_tmp_build_pituitary_adenoma.py
```

Result: passed; generated 50 sources, 25 figures, and 15 videos.

```powershell
python -c "import json, pathlib; ..."
```

Result: passed for `sources.json`, `figures.json`, `videos.json`,
`pituitary-adenoma.sources.json`, `pituitary-adenoma.figures.json`, and
`pituitary-adenoma.videos.json`.

```powershell
python -c "import json, pathlib; ..."
```

Result: passed for `manifest.json`.

```powershell
python -m skillforge disease-template-check pituitary-adenoma --disease-dir ... --json
```

Result: passed. Required conceptual headings are present, longitudinal
`What To Look For` subsections are present, strict template headings match,
50 sources are recorded, 25 figures are recorded, and supporting artifacts are
present.

```powershell
python -m skillforge disease-preview pituitary-adenoma --disease-dir ... --output ... --json
```

Result: passed. HTML preview rendered to
`reports/diseases/pituitary-adenoma.html`.

## What Worked

- Source coverage was strong across radiology, endocrinology, neurosurgery,
  guideline, textbook-style, and sellar differential sources.
- The disease template worked well for separating microadenoma, macroadenoma,
  functioning subtype, nonfunctioning adenoma, apoplexy, postoperative
  residual tumor, treatment response, and mimic-aware interpretation.

## What Could Be Improved

- Figure reuse rights were not reviewed; all figure records remain link-only.
- Video transcripts were not reviewed.
- A future expert pass should add compact tables for endocrine subtype,
  Knosp/cavernous sinus invasion, postoperative residual tumor, dynamic
  contrast protocol, and report-language adjudication.

## Gaps And Blockers

- No private clinical data was used.
- No large dependencies, model downloads, credentials, GPU jobs, pushes, or
  merges were used.
- The chapter is evidence-count complete but still needs human expert review
  before publication.

## Files Changed

- `diseases/pituitary-adenoma/pituitary-adenoma.md`
- `diseases/pituitary-adenoma/research-plan.md`
- `diseases/pituitary-adenoma/pituitary-adenoma.research-plan.md`
- `diseases/pituitary-adenoma/source-review.md`
- `diseases/pituitary-adenoma/pituitary-adenoma.source-review.md`
- `diseases/pituitary-adenoma/differential-matrix.md`
- `diseases/pituitary-adenoma/sources.json`
- `diseases/pituitary-adenoma/pituitary-adenoma.sources.json`
- `diseases/pituitary-adenoma/figures.json`
- `diseases/pituitary-adenoma/pituitary-adenoma.figures.json`
- `diseases/pituitary-adenoma/videos.json`
- `diseases/pituitary-adenoma/pituitary-adenoma.videos.json`
- `reports/diseases/pituitary-adenoma.html`
- `reports/index.html`
- `manifest.json`
- `TODO.md`

## Recommended Next Action

Continue the MR-RATE queue with `lipoma-of-brain`, unless a human review pass
on pituitary adenoma is requested first.
