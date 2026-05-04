# Radiological Report to ROI

Status: exemplar design draft  
Date: 2026-05-03

## Purpose

This exemplar shows how to turn a medical-imaging algorithm and dataset workflow
into an agentic skill. The immediate goal is to use a radiology report and its
corresponding MRI volume to guide segmentation and generate a region of
interest.

The larger goal is to learn a repeatable pattern for converting algorithm
codebases from NVIDIA-Medtech, MONAI, and similar sources into safe, useful,
discoverable Codex skills.

## Decisions So Far

- Frame this exemplar as Radiological Report to ROI, not just a segmentation wrapper.
- Use the radiology report plus matching MRI volume as the core input pair.
- Use NV-Segment-CTMR as the segmentation capability.
- Prefer precomputed MR-RATE-nvseg-ctmr segmentations for the MVP when they
  match the image and study.
- Treat direct NV-Segment-CTMR execution as Phase 2 because it adds environment,
  model-weight, GPU, Conda, Docker/SynthStrip, and preprocessing complexity.
- Keep LLM responsibilities focused on report interpretation, anatomy
  disambiguation, mode choice, and explanation.
- Keep deterministic Python responsible for file resolution, NIfTI loading,
  label ID resolution, ROI extraction, summary JSON, and provenance.
- Include an agent-callable Python CLI so agents can inspect the command schema,
  check dependencies, and run ROI extraction without rewriting fragile NIfTI
  code in chat.
- Use conservative medical-imaging safety language: research workflow only, not
  diagnosis, treatment, triage, or clinical decision-making.

## User Story

As a researcher, I have:

- an MRI image volume from MR-RATE
- the corresponding MR-RATE radiology report
- a target anatomy question, such as "find the brain anatomy location mentioned
  in this report"

I want an agent to:

1. Read the report.
2. Identify relevant anatomy or a likely region of interest.
3. Choose the right NV-Segment-CTMR segmentation strategy.
4. Use precomputed MR-RATE NV-Segment-CTMR segmentations when available, or run
   NV-Segment-CTMR when needed.
5. Extract an ROI mask from the image volume.
6. Return evidence, labels, files, commands, and limitations.

## Source Context

MR-RATE contains native-space brain and spine MRI volumes with corresponding
radiology reports and metadata:

https://huggingface.co/datasets/Forithmus/MR-RATE

MR-RATE-nvseg-ctmr contains derivative segmentations predicted with
NV-Segment-CTMR:

https://huggingface.co/datasets/Forithmus/MR-RATE-nvseg-ctmr

NV-Segment-CTMR supports CT and MRI segmentation modes, including `CT_BODY`,
`MRI_BODY`, and `MRI_BRAIN`. The repository notes that brain MRI segmentation
requires preprocessing and provides a brain segmentation script:

https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR

## Inputs

The workflow should support these input modes:

### Direct Local Inputs

```text
image_volume: /path/to/image.nii.gz
radiology_report: /path/to/report.txt or /path/to/report.csv
anatomy_query: optional, such as "left temporal lobe"
output_dir: /path/to/output
```

### MR-RATE Inputs

```text
study_uid: MR-RATE study identifier
series_id: optional MRI series identifier
batch: optional batch hint
anatomy_query: optional anatomy or report-search term
hf_token: optional, supplied through environment or authenticated HF CLI
output_dir: /path/to/output
```

### Search Inputs

```text
report_search_query: anatomy phrase or clinical phrase
max_studies: maximum matching studies to inspect
preferred_modality: optional, such as T1, T2, FLAIR
```

## Outputs

The workflow should produce:

```text
roi_mask.nii.gz
segmentation_mask.nii.gz or path to source segmentation
roi_summary.json
report_evidence.json
provenance.json
optional_preview.png
optional_roi_report.html
optional_roi_report_assets/*.png
```

`roi_summary.json` should include:

- selected anatomy terms
- selected segmentation labels
- label IDs
- voxel count
- physical volume when voxel spacing is available
- bounding box in voxel coordinates
- source image shape
- source segmentation shape
- warnings or mismatches

`provenance.json` should include:

- image source
- report source
- segmentation source
- model or derivative source
- commands run
- label map source
- timestamp
- software versions when available

`optional_roi_report.html` should include:

- raw source files and prepared file paths
- available image and segmentation entries
- radiology report text and parsed sections
- anatomy mentioned in the impression, including evidence text and segmentation
  availability
- a list of impression-mentioned regions where no segmentation mask exists
- MR-RATE label CSV summary
- segmentation labels present in the selected mask
- selected ROI label IDs and label names
- ROI metrics, bounding box, warnings, and provenance
- reproducibility commands for dependency checking, case preparation, ROI
  extraction, and report generation
- representative 2D slices with ROI overlays
- notes about using existing 3D NIfTI viewers for interactive review

## Optional Local Integration Case

Use MR-RATE case `22B7CXEZ6T` as the preferred local integration test when the
user has the MR-RATE files locally. The test data should live under
`test-data/radiological-report-to-roi/` and remain ignored by Git.

Required local files:

```text
22B7CXEZ6T.zip
22B7CXEZ6T_nvseg-ctmr.zip
batch00_reports.csv
mrrate_labels.csv
```

The smoke-test path prepares the case, extracts label `220` for `Brain-Stem`,
and generates an HTML report. This validates the real MR-RATE/NV-Segment-CTMR
file pairing, NIfTI loading, ROI extraction, impression anatomy audit, and
report generation without publishing the restricted data.

## Authoritative Source Chain

The skill's public search and SEO language should be grounded in authoritative
upstream sources:

- NVIDIA-Medtech/NV-Segment-CTMR for model capabilities, supported modes,
  label dictionaries, and MRI_BRAIN preprocessing expectations.
- nvidia/NV-Segment-CTMR on Hugging Face for model-card language, research-only
  terms, supported inputs, and license references.
- Forithmus/MR-RATE for MRI volumes, report sections, dataset organization,
  access terms, privacy restrictions, and pathology-label context.
- Forithmus/MR-RATE-nvseg-ctmr for native-space brain and body segmentation
  derivatives generated with NV-Segment-CTMR.
- MONAI for bundle execution context and NiBabel for deterministic NIfTI
  handling in the local Python CLI.

The report text and image data for individual studies are local analysis
artifacts. They can appear in generated private reports, but they must not be
used as public SEO content.

## Pipeline

### 1. Confirm Access And Use Boundaries

MR-RATE is gated and released for research, educational, and non-commercial use.
The workflow should confirm that the user has accepted dataset terms before
downloading data.

The skill must not make diagnostic, treatment, triage, or clinical
decision-making claims.

### 2. Resolve The Study

For MR-RATE workflows:

1. Search reports or accept an explicit `study_uid`.
2. Resolve the matching report row.
3. Resolve candidate MRI series for that `study_uid`.
4. Prefer the center modality when brain segmentation is needed and the
   precomputed MR-RATE-nvseg-ctmr brain segmentation is available.

### 3. Read The Report

Parse report sections such as:

- clinical information
- technique
- findings
- impression
- full report text

Use the LLM to identify anatomy mentions and ambiguity. The agent should ask a
clarifying question if multiple anatomical targets are plausible.

### 4. Choose Segmentation Strategy

Prefer precomputed MR-RATE-nvseg-ctmr outputs when they match the image volume
and study.

Use NV-Segment-CTMR directly when:

- no precomputed segmentation exists
- the user provides a local image outside MR-RATE
- the user explicitly wants to run the model
- a different mode or label set is needed

Mode selection:

```text
brain anatomy -> MRI_BRAIN
body/spine anatomy -> MRI_BODY
CT anatomy -> CT_BODY
```

For brain MRI, use the NV-Segment-CTMR brain segmentation script because the
upstream repo requires preprocessing for `MRI_BRAIN`.

### 5. Map Anatomy To Labels

The LLM may propose candidate label names, but deterministic code must resolve
exact labels and IDs from an approved label map.

The workflow should record:

- anatomy phrase from the report
- normalized anatomy term
- candidate labels
- final selected labels
- label IDs
- label map source

### 6. Extract ROI

Python should:

1. Load image and segmentation NIfTI files.
2. Verify shape and affine compatibility.
3. Create a binary ROI mask for selected label IDs.
4. Compute voxel count, physical volume, and bounding box.
5. Save ROI mask and summary outputs.

### 7. Generate Human Report

Python should optionally render a static HTML report from the prepared case
manifest and ROI outputs. The report should embed representative sagittal,
coronal, and axial PNG slice previews through the ROI center.

Do not write a custom 3D viewer for the MVP. If interactive 3D review is
needed, use an existing NIfTI-capable viewer such as NiiVue or Papaya and serve
the report folder through a local HTTP server when browser file restrictions
block direct local loading.

### 8. Explain Result

The agent should return:

- report snippets that motivated the ROI
- selected label names and IDs
- output file paths
- segmentation source
- important warnings
- HTML report path when generated
- statement that this is research output, not a clinical interpretation

## LLM Versus Python Responsibilities

| Step | LLM | Deterministic Code |
| --- | --- | --- |
| Understand user goal | Interpret request and target anatomy | Validate required fields |
| Report analysis | Extract anatomy mentions, synonyms, ambiguity | Parse CSV/text sections |
| Study resolution | Explain candidate choices | Join `study_uid`, batch, series, file paths |
| Segmentation choice | Choose mode and ask clarifying questions | Check whether segmentation files exist |
| Model execution | Explain prerequisites and plan | Run NV-Segment-CTMR command or adapter |
| Label mapping | Propose candidate labels | Resolve exact label IDs from label map |
| ROI extraction | Explain outputs | Load NIfTI, mask labels, compute stats |
| Safety | Explain limits | Enforce required confirmations and metadata |

## Skill Package Shape

Recommended initial skill:

```text
skills/radiological-report-to-roi/
  SKILL.md
  README.md
  references/
    mrrate-data-contract.md
    nv-segment-ctmr-execution.md
    label-mapping.md
    safety-and-license.md
  scripts/
    search_reports.py
    resolve_mrrate_inputs.py
    run_nvseg_ctmr.py
    extract_roi.py
```

Recommended reusable lower-level skill:

```text
skills/nv-segment-ctmr/
  SKILL.md
  README.md
  references/
    quick-start.md
    labels.md
    environment.md
  scripts/
    run_segmentation.py
    check_environment.py
```

## Deterministic Adapter Commands

Implemented MVP commands:

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py check --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py schema --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py extract-roi --image image.nii.gz --segmentation segmentation.nii.gz --labels 10,11 --output-dir output --json
```

Future MR-RATE/NV-Segment-CTMR commands:

```text
python scripts/search_reports.py --dataset Forithmus/MR-RATE --query "temporal lobe" --max-studies 10 --json
```

```text
python scripts/resolve_mrrate_inputs.py --study-uid <study_uid> --prefer center-t1 --json
```

```text
python scripts/run_nvseg_ctmr.py --image image.nii.gz --mode MRI_BRAIN --output-dir output/
```

```text
python scripts/extract_roi.py --image image.nii.gz --seg segmentation.nii.gz --labels 10,11 --output-dir output/ --json
```

The final command names may change, but the responsibilities should remain
separate.

## MVP

The MVP should avoid unnecessary model-running complexity. Use precomputed
MR-RATE-nvseg-ctmr segmentations first.

MVP workflow:

```text
MR-RATE report + MR-RATE image volume + MR-RATE-nvseg-ctmr segmentation
-> anatomy extraction
-> label mapping
-> ROI extraction
-> evidence-grounded summary
```

MVP acceptance criteria:

- Accept a `study_uid` or local report/image/segmentation paths.
- Parse a report and identify candidate anatomy.
- Resolve labels from a local label map.
- Extract an ROI mask from an existing segmentation through a Python CLI.
- Produce `roi_summary.json` and `provenance.json`.
- Avoid diagnostic language.

## Phase 2

Run NV-Segment-CTMR directly when a precomputed segmentation is unavailable.

Phase 2 acceptance criteria:

- Check environment and model-weight availability.
- Support `MRI_BRAIN`, `MRI_BODY`, and `CT_BODY` routing.
- Use the brain segmentation script for `MRI_BRAIN`.
- Capture commands, logs, and output paths.
- Fail with actionable setup guidance when dependencies are missing.

## Phase 3

Generalize the pattern into the codebase-to-agentic-skill generator.

Phase 3 acceptance criteria:

- Create a readiness card for this workflow.
- Extract reusable adapter and data-contract templates.
- Use the same pattern on at least one additional NVIDIA-Medtech repo and one
  MONAI workflow.

## Safety Baseline

The skill should always say:

- This is for research workflows.
- Outputs are model-derived or algorithm-derived artifacts.
- Outputs are not medical advice, diagnosis, triage, or treatment guidance.
- Dataset access and use must comply with MR-RATE terms.
- Restricted or gated data should not be redistributed.
- The user is responsible for appropriate data governance and approvals.

## Open Questions

- Should the MVP support direct Hugging Face download, or require local files
  first?
- Which MR-RATE metadata file is the source of truth for center modality and
  series selection?
- Which NV-Segment-CTMR label map should be pinned for the first workflow?
- Should report anatomy extraction use deterministic term matching first, LLM
  extraction first, or both?
- Should ROI previews be generated as static PNG slices in the first MVP?
