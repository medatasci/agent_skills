# Radiological Report to ROI

Skill ID: `radiological-report-to-roi`

Generate research ROI masks and summaries from a radiology report, image
volume, segmentation mask, and selected anatomy labels.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/radiological-report-to-roi

Parent package:
SkillForge Agent Skills Marketplace

Parent package repo URL:
https://github.com/medatasci/agent_skills

Distribution or marketplace:
SkillForge local catalog and Codex skill install workflow

Version or release channel:
Repository `main` branch when published

## Parent Collection

Parent collection:
SkillForge Agent Skills Marketplace

Collection URL:
https://github.com/medatasci/agent_skills

Categories:
Medical Imaging, Research, Agent Workflows

Collection context:
This skill is the first medical-imaging exemplar for the
codebase-to-agentic-skills project. It demonstrates how a report,
image volume, segmentation model or segmentation output, and deterministic ROI
adapter can become an agentic workflow.

## What This Skill Does

This skill helps an agent generate a research region of interest from a medical
image volume and a corresponding radiology report. The current executable MVP
accepts a local image volume, a local segmentation mask, and label IDs, then
writes a binary ROI mask, ROI summary JSON, provenance JSON, and optional HTML
report with slice previews.

The broader workflow is radiological report to ROI: the agent can use report
text to identify candidate anatomy, ask clarifying questions, select or verify
segmentation labels, and explain the result. The deterministic CLI performs the
fragile file and mask operations.

## Why You Would Call It

Call this skill when:

- You have a medical image volume, segmentation mask, and label IDs and need an
  ROI mask.
- You have an MR-RATE MRI volume and matching report and want a report-to-ROI
  ROI workflow.
- You want an agent to connect radiology report evidence, anatomy labels,
  segmentation outputs, and ROI provenance.

Use it to:

- Extract label IDs from a segmentation as a binary ROI mask.
- Produce machine-readable ROI summaries for downstream analysis.
- Keep report evidence, segmentation labels, and output files connected through
  provenance.

Do not use it when:

- You need diagnosis, treatment, triage, or clinical decision-making.
- You want to redistribute restricted medical data or derived outputs without
  permission.
- You only need generic segmentation with no radiological report-to-ROI step.

## Keywords

Radiological report to ROI, radiology report to ROI, report-guided ROI, medical
image ROI, radiology report, segmentation mask, NIfTI, MRI, brain MRI, MR-RATE,
MR-RATE-nvseg-ctmr, NV-Segment-CTMR, MONAI bundle, NiBabel, label IDs, ROI
summary, provenance, research workflow.

## Search Terms

Generate ROI from a radiological report, radiology report to ROI, extract ROI
from segmentation labels, medical image ROI generator, MR-RATE ROI analysis,
MRI report guided ROI, anatomy guided segmentation, NIfTI ROI mask, create ROI
summary JSON, use NV-Segment-CTMR for ROI, MR-RATE-nvseg-ctmr brain
segmentation, MONAI medical image segmentation, NiBabel NIfTI mask extraction,
report guided medical imaging workflow.

## How It Works

The skill separates agent reasoning from deterministic execution:

1. The agent clarifies the target anatomy and segmentation source.
2. The agent verifies that exact label IDs are available from a trusted label
   map or user input.
3. The Python CLI loads local NIfTI image and segmentation files.
4. The CLI validates shape compatibility and records affine warnings.
5. The CLI selects the requested label IDs and writes a binary ROI mask.
6. The CLI writes summary and provenance JSON for agents and downstream tools.
7. The CLI can render a human-readable HTML report with raw data,
   intermediate results, final outputs, and representative slice previews.

The MVP does not download MR-RATE data and does not run NV-Segment-CTMR. Those
steps are planned follow-ons that require explicit user confirmation because
they can involve gated data, large downloads, GPU execution, Conda, Docker, and
model-weight terms.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "radiological report to ROI"
python -m skillforge info radiological-report-to-roi --json
python -m skillforge install radiological-report-to-roi --scope global
python -m skillforge evaluate radiological-report-to-roi --json
```

Agent CLI:

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py check --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py schema --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py prepare-mrrate-case --study-uid 22B7CXEZ6T --image-zip 22B7CXEZ6T.zip --segmentation-zip 22B7CXEZ6T_nvseg-ctmr.zip --reports-csv batch00_reports.csv --labels-csv mrrate_labels.csv --output-dir test-data/radiological-report-to-roi --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py extract-roi --image image.nii.gz --segmentation segmentation.nii.gz --labels 10,11 --output-dir output --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py report-html --manifest manifest.json --roi-summary roi_summary.json --provenance provenance.json --output-html roi_report.html --json
```

Options:

- `prepare-mrrate-case`: unpack and pair local MR-RATE image/segmentation ZIPs
  with report and label CSV rows.
- `report-html`: write a human-facing HTML report and PNG ROI overlay slices
  from a prepared case and ROI outputs.
- `--image`: local NIfTI image path.
- `--segmentation`: local NIfTI segmentation path.
- `--labels`: comma-separated label IDs.
- `--output-dir`: output directory for ROI mask and JSON files.
- `--name`: optional output name stem.
- `--anatomy`: optional anatomy phrase for provenance.
- `--report`: optional local report text or CSV path for provenance.
- `--manifest`: prepared MR-RATE case manifest for report generation.
- `--roi-summary`: ROI summary JSON for report generation.
- `--provenance`: provenance JSON for report generation.
- `--output-html`: output HTML report path.
- `--json`: emit machine-readable output.

## Inputs And Outputs

Inputs:

- Local image volume path.
- Local segmentation mask path.
- Label IDs for the target ROI.
- Optional radiology report path.
- Optional anatomy phrase.
- Optional output directory.

Outputs:

- `roi_mask.nii.gz`
- `roi_summary.json`
- `provenance.json`
- `roi_report.html`
- `roi_report_assets/*.png`
- JSON command response for agents.

## Examples

Promptable:

```text
Use radiological-report-to-roi to extract labels 10 and 11 from this segmentation and summarize the ROI.
```

```text
I have an MR-RATE MRI volume and matching report. Help me generate an ROI for the anatomy discussed in the report.
```

CLI:

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py check --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py prepare-mrrate-case --study-uid 22B7CXEZ6T --image-zip "C:\Users\medgar\Downloads\22B7CXEZ6T.zip" --segmentation-zip "C:\Users\medgar\Downloads\22B7CXEZ6T_nvseg-ctmr.zip" --reports-csv "C:\Users\medgar\Downloads\batch00_reports.csv" --labels-csv "C:\Users\medgar\Downloads\mrrate_labels.csv" --output-dir "test-data\radiological-report-to-roi" --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py extract-roi --image image.nii.gz --segmentation segmentation.nii.gz --labels 10,11 --output-dir output --anatomy "left temporal lobe" --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py report-html --manifest manifest.json --roi-summary roi_summary.json --provenance provenance.json --output-html roi_report.html --title "Research ROI Report" --json
```

## Help

Start with the read-only checks:

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py check --json
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py schema --json
```

If dependencies are missing, install or activate an environment with `numpy` and
`nibabel` before running `extract-roi`.

Use `prepare-mrrate-case` before `extract-roi` when the inputs are MR-RATE ZIP
and CSV downloads rather than already-extracted NIfTI files.

Use `report-html` after `extract-roi` when a human-readable audit report is
needed. The report embeds static 2D slices. For interactive 3D review, use an
existing NIfTI viewer such as NiiVue or Papaya rather than custom viewer code.

## Optional Local Integration Test

Use MR-RATE case `22B7CXEZ6T` as the preferred local integration test when the
files are available on the machine. The data is not packaged with SkillForge and
should not be committed to the public repository.

Expected local files:

```text
test-data/radiological-report-to-roi/22B7CXEZ6T.zip
test-data/radiological-report-to-roi/22B7CXEZ6T_nvseg-ctmr.zip
test-data/radiological-report-to-roi/batch00_reports.csv
test-data/radiological-report-to-roi/mrrate_labels.csv
```

Smoke-test commands:

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py prepare-mrrate-case --study-uid 22B7CXEZ6T --image-zip test-data/radiological-report-to-roi/22B7CXEZ6T.zip --segmentation-zip test-data/radiological-report-to-roi/22B7CXEZ6T_nvseg-ctmr.zip --reports-csv test-data/radiological-report-to-roi/batch00_reports.csv --labels-csv test-data/radiological-report-to-roi/mrrate_labels.csv --output-dir test-output/radiological-report-to-roi-integration --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py extract-roi --image test-output/radiological-report-to-roi-integration/22B7CXEZ6T/image/22B7CXEZ6T_t1w-raw-axi.nii.gz --segmentation test-output/radiological-report-to-roi-integration/22B7CXEZ6T/segmentation/22B7CXEZ6T_t1w-raw-axi_nvseg-ctmr-brain.nii.gz --labels 220 --output-dir test-output/radiological-report-to-roi-integration/22B7CXEZ6T/brain-stem --anatomy Brain-Stem --report test-output/radiological-report-to-roi-integration/22B7CXEZ6T/report.txt --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py report-html --manifest test-output/radiological-report-to-roi-integration/22B7CXEZ6T/manifest.json --roi-summary test-output/radiological-report-to-roi-integration/22B7CXEZ6T/brain-stem/roi_summary.json --provenance test-output/radiological-report-to-roi-integration/22B7CXEZ6T/brain-stem/provenance.json --output-html test-output/radiological-report-to-roi-integration/22B7CXEZ6T/22B7CXEZ6T_roi_report.html --title "Radiological Report to ROI: 22B7CXEZ6T" --json
```

Expected ROI summary for label `220` includes anatomy `Brain-Stem`, image and
segmentation shape `[512, 512, 252]`, and no extraction warnings.

The HTML report also audits anatomy mentioned in the impression. It lists each
detected region, the evidence line from the impression, whether a corresponding
segmentation mask exists, label IDs and voxel counts when available, and a
separate table for regions mentioned in the impression but absent from the
selected segmentation.

The report includes a reproducibility section with the Python commands used to
check dependencies, prepare the case, extract the ROI, and regenerate the HTML.

## How To Call From An LLM

Use this pattern:

```text
Use radiological-report-to-roi.
Image: <path>
Segmentation: <path>
Labels: <ids>
Anatomy: <optional phrase>
Return ROI mask, summary JSON, and provenance.
```

The calling agent should inspect the CLI schema, confirm side effects, and then
call the deterministic CLI for extraction and optional HTML report generation.

## How To Call From The CLI

Run the script from the SkillForge repository root or pass absolute paths:

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py extract-roi --image <image.nii.gz> --segmentation <seg.nii.gz> --labels <ids> --output-dir <dir> --json
```

```text
python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py report-html --manifest <manifest.json> --roi-summary <roi_summary.json> --provenance <provenance.json> --output-html <report.html> --json
```

## Trust And Safety

Risk level:
Medium.

Permissions:

- Reads local medical image, segmentation, and optional report files.
- Writes ROI and JSON files to the requested output directory.
- Does not use network for the MVP local ROI extraction command.
- Future MR-RATE download or NV-Segment-CTMR execution requires explicit user
  confirmation.

Data handling:
Medical images and reports can be sensitive or restricted. Keep data local
unless the user explicitly requests an allowed transfer. Do not add PHI,
restricted data, or proprietary clinical data to public SkillForge content.

Writes vs read-only:
`check` and `schema` are read-only. `prepare-mrrate-case`, `extract-roi`, and
`report-html` write output files.

## Authority Sources And Provenance

This skill is intentionally tied to authoritative upstream sources rather than
generic SEO language. Discovery text, examples, safety notes, and limitations
should stay aligned with these sources.

Core upstream sources:

- [NVIDIA-Medtech/NV-Segment-CTMR](https://github.com/NVIDIA-Medtech/NV-Segment-CTMR):
  upstream source repo for the NV-Segment CT and CT/MR medical image
  segmentation foundation models. The repo describes NV-Segment-CTMR as a CT
  and MRI segmentation model that follows the MONAI bundle architecture,
  supports CT_BODY, MRI_BODY, and MRI_BRAIN modes, and links the model weights,
  label dictionary, and VISTA3D paper.
- [NV-Segment-CTMR model card](https://huggingface.co/nvidia/NV-Segment-CTMR):
  authoritative model card for model purpose, research-only use, NIfTI input,
  CT/MR modality support, label prompts, MRI_BRAIN preprocessing expectations,
  license terms, and VISTA3D reference.
- [MR-RATE dataset card](https://huggingface.co/datasets/Forithmus/MR-RATE):
  authoritative source for the MRI volumes, radiology reports, metadata,
  pathology labels, access terms, privacy restrictions, and dataset
  organization used by this workflow.
- [MR-RATE-nvseg-ctmr dataset card](https://huggingface.co/datasets/Forithmus/MR-RATE-nvseg-ctmr):
  authoritative source for the native-space NV-Segment-CTMR brain and body
  segmentation derivatives used for ROI extraction and downstream analysis.
- [MONAI](https://github.com/Project-MONAI/MONAI): upstream healthcare-imaging
  AI framework referenced by NV-Segment-CTMR and used as the bundle execution
  layer for segmentation workflows.
- [NiBabel](https://nipy.org/nibabel/): Python neuroimaging library used by the
  SkillForge CLI to read/write NIfTI images, inspect image metadata, preserve
  affine/header context, and work with voxel arrays.

Linked source chain:

- MR-RATE reports are structured into clinical information, technique,
  findings, and impression sections; the ROI report audit uses those fields
  rather than private free-text SEO content.
- MR-RATE native images are released as NIfTI volumes and the dataset card
  identifies [dcm2niix](https://github.com/rordenlab/dcm2niix) as the DICOM to
  NIfTI conversion tool.
- MR-RATE describes defacing and brain-mask preprocessing that link to
  [HD-BET](https://github.com/MIC-DKFZ/HD-BET), Quickshear, and related
  preprocessing tools.
- MR-RATE describes co-registration and atlas registration that link to
  [ANTs](https://github.com/ANTsX/ANTs) and the MNI152 atlas.
- NV-Segment-CTMR brain segmentation documentation links MRI_BRAIN processing
  to skull stripping, LUMIR-template alignment, MONAI bundle inference, and
  restoring masks to original image space.

## Limitations

- The MVP requires exact label IDs. It does not yet resolve label IDs from
  anatomy text automatically.
- The MVP does not download MR-RATE files.
- The MVP does not run NV-Segment-CTMR.
- Output is a research artifact, not a clinical interpretation.
- Shape and affine compatibility are checked, but the user remains responsible
  for validating scientific appropriateness.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

CLI feedback draft:

```text
python -m skillforge feedback "radiological-report-to-roi" --trying "extract an ROI" --happened "describe what worked, failed, or was confusing"
```

## Contributing

Contributions are welcome through GitHub pull requests. Useful next
contributions include label-map resolution, MR-RATE file resolution,
NV-Segment-CTMR execution adapters, and small reproducible smoke tests.

## Author

Marc Edgar / medatasci

## Citations

Relevant sources:

- NV-Segment-CTMR:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR
- NV-Segment-CTMR model card:
  https://huggingface.co/nvidia/NV-Segment-CTMR
- NV-Segment-CTMR label dictionary:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/blob/main/NV-Segment-CTMR/configs/label_dict.json
- VISTA3D paper:
  https://arxiv.org/abs/2406.05285
- MR-RATE:
  https://huggingface.co/datasets/Forithmus/MR-RATE
- MR-RATE-nvseg-ctmr:
  https://huggingface.co/datasets/Forithmus/MR-RATE-nvseg-ctmr
- MONAI:
  https://github.com/Project-MONAI/MONAI
- NiBabel:
  https://nipy.org/nibabel/

## Related Skills

- `nv-segment-ctmr`: planned lower-level segmentation algorithm skill.
- `huggingface-datasets`: inspect Hugging Face dataset metadata and rows.
- `skillforge`: find, inspect, install, and evaluate SkillForge skills.
