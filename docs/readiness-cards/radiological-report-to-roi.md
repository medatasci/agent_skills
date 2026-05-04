# Radiological Report to ROI Readiness Card

## Summary

Name:
Radiological Report to ROI

Source:
MR-RATE, MR-RATE-nvseg-ctmr, NV-Segment-CTMR, MONAI, and NiBabel public
sources.

Workflow goal:
Turn a radiology report, matching medical image volume, and segmentation source
into a research ROI mask, summary JSON, provenance JSON, and optional HTML
report.

Primary users:
Researchers and agents working with local medical imaging research data.

Recommendation:
Keep `radiological-report-to-roi` as a workflow skill separate from
`nv-segment-ctmr`.

Recommendation rationale:
The workflow composes report interpretation, local file preparation,
segmentation provenance, label selection, deterministic ROI extraction, and
human-readable reporting. That scope is broader than a model wrapper and should
remain a higher-level workflow skill.

## Candidate Scope

Proposed skill type:

- Workflow skill

Proposed skill ID:
`radiological-report-to-roi`

Should this be one skill or multiple skills?
One workflow skill for report-to-ROI orchestration, with `nv-segment-ctmr` kept
as the lower-level segmentation algorithm skill.

Why this scope:
Users ask for a region of interest grounded in report evidence, not just model
execution. The workflow should decide when an existing segmentation is enough
and when a lower-level segmentation skill is needed.

## Source Inventory

Repository or codebase URL:
https://github.com/medatasci/agent_skills/tree/main/skills/radiological-report-to-roi

Model card URL:
https://huggingface.co/nvidia/NV-Segment-CTMR

Documentation URLs:

- https://huggingface.co/datasets/Forithmus/MR-RATE
- https://huggingface.co/datasets/Forithmus/MR-RATE-nvseg-ctmr
- https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR
- https://docs.monai.io/en/stable/bundle_intro.html
- https://nipy.org/nibabel/

Example or quick-start URLs:

- https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR
- https://github.com/medatasci/agent_skills/blob/main/docs/radiological-report-to-roi.md

License URLs:

- https://huggingface.co/datasets/Forithmus/MR-RATE
- https://huggingface.co/datasets/Forithmus/MR-RATE-nvseg-ctmr
- https://huggingface.co/nvidia/NV-Segment-CTMR

Relevant files or commands:

- `skills/radiological-report-to-roi/SKILL.md`
- `skills/radiological-report-to-roi/README.md`
- `skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py`
- `docs/radiological-report-to-roi.md`
- `skills/nv-segment-ctmr/SKILL.md`
- `docs/readiness-cards/nv-segment-ctmr.md`

Source version status:
Unpinned with risk. Public source URLs are recorded, but the exact upstream
commits or dataset revisions should be pinned before claims about reproducible
external-source behavior are published as production-ready.

Version, commit, tag, or release to pin:
Pin MR-RATE dataset revision, MR-RATE-nvseg-ctmr dataset revision,
NV-Segment-CTMR source commit, NV-Segment-CTMR model revision, MONAI version,
and NiBabel version when preparing a reproducible release.

## Source Context Map

For each important source artifact, this map records how the source affects the
skill design, adapter behavior, LLM prompting, safety, tests, and publication
claims.

| Source artifact | What it provides | Skill design impact | Adapter or deterministic-code impact | LLM context impact | Safety/license/publication impact | Open questions |
| --- | --- | --- | --- | --- | --- | --- |
| MR-RATE dataset card | Dataset purpose, report/image pairing, gated access context, MRI volume/report organization. | Makes local image plus report the core input pair and keeps dataset download out of MVP. | `prepare-mrrate-case` reads local ZIP/CSV files instead of fetching data. | Agent should ask for local files or confirm dataset access rather than assuming download rights. | Public docs must not include private local report text or redistributed gated data. | Pin dataset revision and clarify whether future download helpers are allowed. |
| MR-RATE reports and labels CSV | Report rows, study IDs, report sections, label CSV used in local tests. | Supports report evidence extraction and label-summary report sections. | Parser reads local CSV and writes manifest, report text, report JSON, and label summary. | Agent can explain evidence from a local report but should not turn patient-specific content into public SEO. | Local test data remains ignored by Git. | Decide whether deterministic anatomy extraction should precede LLM extraction. |
| MR-RATE-nvseg-ctmr dataset card | Precomputed NV-Segment-CTMR segmentation derivatives for MR-RATE. | MVP should prefer existing segmentations when they match the image and study. | `prepare-mrrate-case` selects matching image and segmentation entries from local ZIP files. | Agent should distinguish "use existing segmentation" from "run the model." | Derived segmentation access and redistribution follow dataset terms. | Pin derivative dataset revision and document matching rules. |
| NV-Segment-CTMR source repo | Supported modes, label dictionary, MRI_BRAIN preprocessing, MONAI bundle context. | Keeps model execution delegated to `nv-segment-ctmr`; this skill consumes outputs or plans routing. | Future direct model execution should call the lower-level skill or adapter, not duplicate model-running code. | Agent can choose when `MRI_BRAIN`, `MRI_BODY`, or `CT_BODY` likely matters. | Research-only and model-license language must be preserved. | Decide whether future report-to-ROI should invoke model execution directly or only route. |
| NV-Segment-CTMR model card | Model purpose, NIfTI input expectation, VISTA3D reference, use restrictions. | Grounds segmentation-source description and research-only limitations. | Runtime checks should require explicit model/download approval if direct execution is added. | Agent should not imply clinical readiness or unsupported interactive segmentation. | Model terms must be reviewed before distribution or execution helpers expand. | Pin model revision and accepted terms workflow. |
| MONAI docs | Bundle execution conventions and medical imaging workflow context. | Explains why lower-level model execution is a separate skill surface. | Future model-run adapter may need MONAI bundle checks and command planning. | Agent can explain bundle context without inventing runtime success. | MONAI docs are public authoritative context, not patient data. | Decide whether a future shared MONAI bundle runner skill is needed. |
| NiBabel docs | NIfTI load/save behavior, affine/header access, array handling. | Supports deterministic local ROI extraction instead of LLM-written image code. | `extract-roi` loads image and segmentation, checks shape, writes ROI NIfTI, JSON, and provenance. | Agent should describe NIfTI compatibility warnings and not calculate volume in prose. | Local file reads/writes require user-provided paths and output approval. | Add stronger affine/spacing validation policy if needed. |
| Local SkillForge docs and tests | Implemented CLI contract, local MR-RATE smoke-test path, HTML report behavior. | Defines what is actually implemented today versus future MR-RATE download/model execution. | Tests cover missing inputs, CLI schema, ROI extraction, report generation, and local integration when data is present. | Agent should report exact commands and generated file paths. | Test data is local and must not be committed. | Add CI-safe fixture with synthetic NIfTI and synthetic report text. |

## Candidate Skill Table

| Candidate Skill | What It Does | Likely Entry Point | Sample Prompt Call | CLI For Prompt | Source Evidence | Inputs | Outputs | Agent Role | Deterministic Role | Safety Notes | Test Evidence | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `radiological-report-to-roi` | Generate a research ROI from a report, image volume, segmentation, and selected labels. | `skills/radiological-report-to-roi/SKILL.md` and `scripts/radiological_report_to_roi.py`. | "Create an ROI from this report, image, and segmentation, and show evidence and provenance." | `python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py extract-roi --image image.nii.gz --segmentation segmentation.nii.gz --labels 220 --output-dir output --json` | MR-RATE, MR-RATE-nvseg-ctmr, NV-Segment-CTMR, NiBabel, local skill docs. | Local image, segmentation, labels, optional report/anatomy, output dir. | ROI mask, summary JSON, provenance JSON, optional HTML report. | Interpret report/anatomy, ask clarifying questions, explain results and limits. | Parse files, resolve exact inputs, load NIfTI, extract mask, compute stats, write outputs. | Research-only; no diagnosis or redistribution of restricted data. | Unit tests and local `22B7CXEZ6T` integration path. | Keep and improve as the workflow exemplar. |
| `nv-segment-ctmr` | Plan and optionally run guarded CT/MRI segmentation. | `skills/nv-segment-ctmr/SKILL.md`. | "Create a segmentation map from this MRI, but ask before running anything." | `python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-plan --image brain.nii.gz --output-dir results --json` | NV-Segment-CTMR repo and model card. | Local CT/MRI NIfTI, mode, optional model path, output dir. | Segmentation plan or guarded segmentation output. | Choose mode and explain setup/safety. | Check environment, plan commands, verify outputs, run only after approval. | Model execution needs explicit approval and runtime readiness. | Separate readiness card and WSL2 smoke test. | Use as lower-level algorithm skill. |
| `mrrate-report-search` | Search local or authorized MR-RATE reports for anatomy or pathology phrases. | Future script or `huggingface-datasets` plus local CSV parser. | "Find MR-RATE reports mentioning brain stem and return matching study IDs." | Future: `python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py search-reports --query "brain stem" --json` | MR-RATE dataset card and local reports CSV. | Authorized report CSV or local report folder, query, max results. | Matching study IDs, evidence snippets, report metadata. | Expand query synonyms and explain ambiguity. | Search text/CSV deterministically and return evidence. | Gated data; no public redistribution of report text. | Not implemented as separate command yet. | Defer until repeated use justifies a separate skill or subcommand. |
| `medical-image-roi-report-html` | Generate a static report with raw data, intermediate outputs, final ROI results, and slice previews. | Existing `report-html` command. | "Make an HTML report showing the ROI extraction evidence and commands." | `python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py report-html --manifest manifest.json --roi-summary roi_summary.json --provenance provenance.json --output-html report.html --json` | Local generated reports and ROI generator script. | Manifest, ROI summary, provenance, image/seg/ROI files. | HTML report and PNG slice previews. | Explain report sections and caveats. | Render slices, tables, commands, and missing-mask audit. | Do not write a custom 3D viewer; use existing viewers for interaction. | Local generated report for `22B7CXEZ6T`. | Keep as part of this workflow skill for now. |

## Workflow Fit

User problem:
The user has a radiology report and a matching image volume and wants a
research ROI grounded in reported anatomy and segmentation labels.

What the codebase does:
The skill currently provides a deterministic Python CLI for dependency checks,
schema reporting, local MR-RATE case preparation, ROI extraction, and HTML
report generation.

What the codebase does not do:
The MVP does not download MR-RATE, authenticate to Hugging Face, run
NV-Segment-CTMR directly, perform clinical interpretation, or decide exact
label IDs without a label source.

Where an agent adds value:
The agent interprets the user request, extracts likely anatomy from report
language, explains ambiguity, chooses whether existing segmentation is enough,
routes to `nv-segment-ctmr` when segmentation is missing, and summarizes
outputs.

What should remain deterministic:
File matching, CSV parsing, NIfTI loading, shape checks, label-mask extraction,
voxel counts, volume estimates, bounding boxes, file writes, and provenance.

## Input Contract

Required inputs:

- Local image NIfTI path.
- Local segmentation NIfTI path.
- Exact label IDs for ROI extraction.
- Output directory.

Optional inputs:

- Local radiology report path.
- Anatomy phrase.
- MR-RATE study UID and local ZIP/CSV files for case preparation.
- HTML report title.

Accepted file formats:

- `.nii`
- `.nii.gz`
- `.zip` for local MR-RATE image and segmentation archives.
- `.csv` for local reports and labels.
- `.txt` or parsed text embedded in generated manifest files.

Required metadata:
Study UID or explicit file paths, label IDs, and segmentation source.

Credentials or access requirements:
No credentials are required for the MVP local commands. Future dataset download
or model execution would require explicit user confirmation and any required
dataset/model access terms.

Expected input size:
3D medical image volumes and segmentation masks. Runtime and storage depend on
volume size.

Validation checks:
Required paths exist, labels parse as integers, image and segmentation shapes
are compatible, output directory is available, and optional dependencies are
importable.

## Output Contract

Primary outputs:

- `roi_mask.nii.gz`
- `roi_summary.json`
- `provenance.json`

Optional outputs:

- `roi_report.html`
- PNG slice previews.
- Manifest, report text, report JSON, and label summary JSON from
  `prepare-mrrate-case`.

Output file formats:
NIfTI, JSON, HTML, PNG, TXT.

Expected output locations:
User-selected output directories under local workspace or test-output paths.

Machine-readable summary:
JSON from every CLI command when `--json` is supplied.

Provenance fields:
Command, timestamp, image path, segmentation path, labels, anatomy, report path,
script path, and generated file paths.

Validation checks:
Shape compatibility, label presence, voxel count, bounding box, and warnings
for missing or empty ROI labels.

## Execution Surface

Execution type:

- Python CLI command
- Local file parser
- NIfTI image processing script
- Static HTML report generator

Setup commands:

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py check --json
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py schema --json
```

Run commands:

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py extract-roi --image image.nii.gz --segmentation segmentation.nii.gz --labels 220 --output-dir output --json
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py report-html --manifest manifest.json --roi-summary roi_summary.json --provenance provenance.json --output-html roi_report.html --json
```

Batch commands:
Not implemented for arbitrary cohorts. The local MR-RATE case-preparation
command prepares one study UID at a time.

Resume or cache behavior:
No cache contract. Existing output files may be overwritten by user-selected
commands.

Expected runtime:
Short for local ROI extraction and HTML reports once input files are available.
Runtime increases with image size and PNG preview rendering.

## Dependencies

Python version:
Python 3.10 or newer is recommended.

Core packages:
`numpy` and `nibabel` for NIfTI processing. Standard library modules are used
for CSV, ZIP, JSON, HTML, and path handling.

External binaries:
None for the MVP local ROI extraction path.

GPU required:
No GPU is required for MVP ROI extraction from existing segmentations.

CUDA or driver requirements:
None for the MVP. Direct NV-Segment-CTMR execution would inherit the lower-level
skill's GPU/runtime requirements.

Docker required:
No for the MVP. Direct brain segmentation preprocessing may involve Docker or
other tools through `nv-segment-ctmr`.

Conda required:
No for the MVP local ROI commands.

Network required:
No for MVP local commands. Future Hugging Face download or model execution
requires explicit approval.

Large downloads:
None by default. MR-RATE data, derivative segmentations, and model weights are
not downloaded silently.

Storage requirements:
Enough local space for image volumes, segmentations, ROI masks, JSON, HTML, and
PNG previews.

## Safety, License, And Data Use

Code license:
SkillForge repository license applies to the local skill code.

Model weights license:
NV-Segment-CTMR model terms must be reviewed before model execution helpers are
used or redistributed.

Dataset terms:
MR-RATE and MR-RATE-nvseg-ctmr terms control access and redistribution of input
data and derivative segmentations.

Permitted use:
Research workflows with local data that the user is allowed to process.

Restricted use:
Diagnosis, treatment, triage, clinical decision-making, re-identification, or
redistribution of restricted medical data.

Privacy concerns:
Radiology reports and medical images may contain sensitive health information.
Keep analysis local unless the user explicitly confirms a compliant destination.

Clinical-use constraints:
Outputs are research artifacts and must not be treated as clinical
interpretations.

Redistribution constraints:
Do not publish MR-RATE files, local report text, images, segmentations, or
generated patient-specific ROI reports in the public SkillForge repo.

Required user confirmations:
Confirm before downloading gated datasets, running model inference, uploading or
sharing data, or writing large outputs outside the requested local directory.

## Agent Decisions

The LLM should decide:

- Which anatomy terms in the report are relevant to the user's question.
- Whether ambiguity requires a clarifying question.
- Whether an existing segmentation is enough or model execution should be
  planned through `nv-segment-ctmr`.
- How to explain limitations and provenance.

The LLM should not decide:

- Exact label IDs without a label map.
- NIfTI mask math.
- Voxel counts, volumes, or bounding boxes.
- Clinical meaning or diagnosis.

Clarifying questions to ask:

- Which anatomy or report finding should define the ROI?
- Do you already have the matching segmentation?
- Are local data terms and output writes approved?
- Should this use existing segmentations only, or plan model execution if
  missing?

Failure modes the agent should recognize:

- Missing files.
- Mismatched image and segmentation shapes.
- Label IDs absent from the segmentation.
- Report mentions anatomy with no available segmentation mask.
- Restricted data cannot be published or redistributed.

## Deterministic Adapter Plan

Adapter files to create:
Already implemented in
`skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py`.

Adapter command shape:

- `check --json`
- `schema --json`
- `prepare-mrrate-case --json`
- `extract-roi --json`
- `report-html --json`

Read-only operations:
Dependency checks and schema reporting.

Write operations:
Case preparation, ROI extraction, provenance JSON, summary JSON, ROI NIfTI,
HTML report, and PNG previews.

Network operations:
None in the MVP.

Error handling:
Return nonzero for missing required inputs, unreadable files, invalid labels, or
failed NIfTI processing. Return warnings for empty labels, affine concerns, or
missing report evidence.

JSON output fields:
`ok`, command-specific output paths, warnings, selected inputs, labels, summary
metrics, provenance, and suggested next command where relevant.

## Smoke Test Plan

Minimal test input:
Use local MR-RATE case `22B7CXEZ6T` when the user has approved local files:

- `22B7CXEZ6T.zip`
- `22B7CXEZ6T_nvseg-ctmr.zip`
- `batch00_reports.csv`
- `mrrate_labels.csv`

Expected command:

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py prepare-mrrate-case --study-uid 22B7CXEZ6T --image-zip test-data/radiological-report-to-roi/22B7CXEZ6T.zip --segmentation-zip test-data/radiological-report-to-roi/22B7CXEZ6T_nvseg-ctmr.zip --reports-csv test-data/radiological-report-to-roi/batch00_reports.csv --labels-csv test-data/radiological-report-to-roi/mrrate_labels.csv --output-dir test-output/radiological-report-to-roi-integration --json
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py extract-roi --image test-output/radiological-report-to-roi-integration/22B7CXEZ6T/image/22B7CXEZ6T_t1w-raw-axi.nii.gz --segmentation test-output/radiological-report-to-roi-integration/22B7CXEZ6T/segmentation/22B7CXEZ6T_t1w-raw-axi_nvseg-ctmr-brain.nii.gz --labels 220 --output-dir test-output/radiological-report-to-roi-integration/22B7CXEZ6T/brain-stem --anatomy Brain-Stem --report test-output/radiological-report-to-roi-integration/22B7CXEZ6T/report.txt --json
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py report-html --manifest test-output/radiological-report-to-roi-integration/22B7CXEZ6T/manifest.json --roi-summary test-output/radiological-report-to-roi-integration/22B7CXEZ6T/brain-stem/roi_summary.json --provenance test-output/radiological-report-to-roi-integration/22B7CXEZ6T/brain-stem/provenance.json --output-html test-output/radiological-report-to-roi-integration/22B7CXEZ6T/22B7CXEZ6T_roi_report.html --title "Radiological Report to ROI: 22B7CXEZ6T" --json
```

Expected outputs:
Prepared manifest, selected image, selected segmentation, report text, label
summary JSON, ROI mask, ROI summary JSON, provenance JSON, HTML report, and PNG
slice previews.

Skip conditions:
Skip the local integration test if MR-RATE files are not present locally, the
user has not confirmed permission to process them, or optional NIfTI
dependencies are not installed.

How to verify output:
Confirm JSON `ok` fields, generated file existence, nonzero ROI voxel count
when the selected label is present, expected label ID `220` for Brain-Stem, and
an HTML report that lists raw data, intermediate results, final ROI output, and
mentioned report anatomy with missing-mask notes when relevant.

Test data license:
The test uses locally provided MR-RATE files and must not commit or publish the
data.

## Skill Package Plan

Suggested files:

```text
skills/radiological-report-to-roi/
  SKILL.md
  README.md
  scripts/
    radiological_report_to_roi.py
```

References to include:
This readiness card plus `docs/radiological-report-to-roi.md` are the public
source-context references. Add skill-local references only when they are needed
by the runtime skill.

Scripts to include:
`scripts/radiological_report_to_roi.py`.

Catalog/search terms:
radiological report to ROI, report-guided ROI, MR-RATE ROI analysis,
NV-Segment-CTMR ROI workflow, NIfTI ROI audit report, anatomy guided
segmentation.

Related skills:

- `nv-segment-ctmr`
- `huggingface-datasets`
- `codebase-to-agentic-skills`

## Known Blockers

- Upstream dataset and model revisions are not pinned.
- Direct model execution remains delegated to `nv-segment-ctmr`.
- Public docs must not include local report/image/segmentation content.

## Open Questions

- Should MR-RATE search become a separate skill or remain a subcommand?
- Should anatomy extraction use deterministic matching first, LLM extraction
  first, or a hybrid?
- Which source revision pins should be used for the first reproducible release?

## Next Action

Next recommended action:
Run evaluation and confirm repo-derived advisory warnings are clear:

```text
python -m skillforge evaluate radiological-report-to-roi --json
```
