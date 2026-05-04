# NV-Segment-CTMR Skill Requirements And Development Plan

This reference mirrors the project-level requirements for implementing the
`nv-segment-ctmr` SkillForge skill.

Canonical project document:
`docs/nv-segment-ctmr-skill-requirements-and-plan.md`

## Product Goal

Create an agentic SkillForge skill that lets Codex help users safely plan,
review, and eventually run NVIDIA-Medtech NV-Segment-CTMR research
segmentation workflows.

The skill should reduce the need for users to memorize model setup, mode
selection, label prompt syntax, MONAI bundle commands, brain MRI preprocessing,
batch resume behavior, and provenance requirements.

## MVP Scope

MVP is planning-first and guarded-execution capable:

- skill trigger and README
- source-grounded workflow guidance
- label lookup requirements
- deterministic adapter for schema, check, labels, plan, brain-plan, batch-plan, output verification, and guarded run
- safety and provenance requirements
- clear execution gates

MVP must not silently:

- download model weights
- run Docker
- run GPU inference
- write segmentation outputs
- process PHI without explicit user approval

## Implemented Read-Only Python Adapter

Preferred command shape:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py schema --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py check --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py setup-plan --target wsl2-linux --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py labels --query "brain stem" --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py plan --image scan.nii.gz --mode MRI_BODY --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-plan --image brain_t1.nii.gz --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py batch-plan --input-dir cohort --mode MRI_BODY --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py verify-output --segmentation results/scan_trans.nii.gz --json
```

Implemented guarded execution command:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py run --image scan.nii.gz --mode MRI_BODY --output-dir results --confirm-execution --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-run --image brain_t1.nii.gz --output-dir results --confirm-execution --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py batch-run --input-dir cohort --mode MRI_BODY --output-dir results --confirm-execution --json
```

The implemented planning adapter returns stable JSON and separates planning
from writes. The guarded run commands refuse execution without
`--confirm-execution`, local source, model weights, an input NIfTI, writable
output directory, and MONAI/PyTorch runtime dependencies.

## Development Phases

1. Package the planning skill. Done.
2. Implement read-only adapter commands: `schema`, `check`, `setup-plan`,
   `labels`, `plan`. Done.
3. Implement output verification. Done.
4. Add guarded single-volume execution. Done.
5. Add brain MRI planning and execution wrappers. Done.
6. Add batch planning. Done.
7. Add guarded batch execution. Done.
8. Add optional TensorRT and fine-tuning planning after license/runtime review.

## Acceptance Criteria

- Skill is discoverable by NV-Segment-CTMR, VISTA3D, CT segmentation, MRI
  segmentation, MONAI bundle, and label prompt queries.
- Skill clearly distinguishes planning from execution.
- Agent asks for modality or anatomy only when needed.
- Label IDs come from source label files, not memory.
- Execution commands require explicit user approval.
- Output verification records file existence, size, NIfTI readability, shape,
  affine, and provenance.
- Safety text always says research only and not clinical decision support.

## Optional Local Smoke Test Data

Use `22B7CXEZ6T` as a local manual smoke-test case when the user's machine still
has the MR-RATE image and segmentation files. In this workspace, the direct
runtime smoke-test input is
`test-data/nv-segment-ctmr/22B7CXEZ6T/img/22B7CXEZ6T_t1w-raw-axi.nii.gz`.
The generated smoke-test output is
`test-output/nv-segment-ctmr/22B7CXEZ6T/22B7CXEZ6T_t1w-raw-axi_trans.nii.gz`.
Existing precomputed ROI workflow segmentations may also be checked under
`test-data/radiological-report-to-roi/22B7CXEZ6T/segmentation/` when
available.

Do not commit new MR-RATE files to the SkillForge repository without reviewing
license, privacy, and size constraints; keep automated tests on small synthetic
NIfTI fixtures.

## WSL2 Runtime Smoke Test

The first accepted local runtime target is WSL2 Ubuntu with a CUDA-visible GPU.
The local source checkout lives at
`~/.skillforge/runtime/nv-segment-ctmr/repo/NV-Segment-CTMR` and was tested at
upstream commit `4046a027492266f22872880fea665ffd6aba1e36`.

Runtime setup used:

- Miniforge conda environment `nvseg-ctmr`
- Python 3.11.15
- upstream `requirements.txt`
- `models/model.pt` from `nvidia/NV-Segment-CTMR`

The accepted smoke-test command shape is:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-run \
  --source-dir ~/.skillforge/runtime/nv-segment-ctmr/repo/NV-Segment-CTMR \
  --image test-data/nv-segment-ctmr/22B7CXEZ6T/img/22B7CXEZ6T_t1w-raw-axi.nii.gz \
  --output-dir test-output/nv-segment-ctmr/22B7CXEZ6T \
  --no-skullstrip \
  --confirm-execution \
  --json
```

Observed output verification:

- `brain-run` returned `ok: true`.
- Output NIfTI was readable.
- Shape was `512 x 512 x 252`.
- Labels included `0`, `220`, `223`, `227`, `228`, `276`, and `284`.
- Non-zero voxel count was `3,752,025`.

Remaining runtime gaps:

- Docker/SynthStrip skull-stripping path was not tested because Docker was not
  installed in WSL2.
- CT_BODY execution, MRI_BODY execution, and batch execution still need
  separate acceptance tests with approved data.

Rollback and cleanup notes:

- The SkillForge adapter writes runtime outputs only under the requested
  output directory.
- Runtime logs and provenance live under `_nv_segment_ctmr_logs/` inside the
  requested output directory.
- Temporary upstream brain MRI files should be removed by the upstream script
  unless `--keep-temp` is selected.
- To clean a failed smoke test, remove the selected output directory after
  confirming it does not contain user data that should be preserved.
- Do not delete the WSL2 source checkout, conda environment, or downloaded
  model weights automatically; those are shared runtime assets and should be
  removed only after explicit user approval.
