# NV-Generate-CTMR Split Roadmap

## Decision

Keep `nv-generate-ctmr` as one umbrella SkillForge skill for the MVP.

Split only when a candidate workflow has:

- a distinct user-facing job to be done
- a distinct deterministic adapter surface
- separate smoke-test or runtime acceptance evidence
- enough search and install value to justify another catalog entry
- clear safety, license, and provenance boundaries

## Backlog Candidates

### 1. CT Paired Synthetic Image And Mask Generation

Potential skill ID:
`nv-generate-ctmr-ct-paired`

User prompt:
`Create a synthetic CT image and paired segmentation mask for this research scenario.`

CLI direction:
`python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py run --generate-version rflow-ct --workflow ct-paired ...`

Why split:
CT paired generation has distinct outputs, config files, mask assets, and
side effects.

Current evidence:
Small local WSL2 CUDA smoke test succeeded for `rflow-ct`, `ct-paired`, chest,
lung tumor, output size `256,256,128`, spacing `1.5,1.5,2.0`.

Acceptance tasks:

- Add named preset support for small, standard, and large CT paired configs.
- Record model-card revision and source commit in provenance.
- Add output manifest generation after `run`.
- Add cleanup guidance for downloaded mask assets and generated volumes.

### 2. MR Brain Synthetic Image Generation

Potential skill ID:
`nv-generate-ctmr-mr-brain`

User prompt:
`Create a synthetic brain MRI volume with this contrast for research.`

CLI direction:
`python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py run --generate-version rflow-mr-brain --workflow image-only ...`

Why split:
Brain MRI contrast selection, skull-stripped variants, and model-card terms
are different enough from CT paired generation to deserve focused prompts.

Acceptance tasks:

- Write and test image-only source-compatible config files.
- Run a small accepted MR brain smoke test.
- Verify output shape, spacing, contrast code, and provenance.
- Add model-card revision pinning for `nvidia/NV-Generate-MR-Brain`.

### 3. Image-Only Synthetic CT/MR Generation

Potential skill ID:
`nv-generate-ctmr-image-only`

User prompt:
`Create a synthetic medical image volume without a paired segmentation mask.`

CLI direction:
`python skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py run --workflow image-only ...`

Why split:
Image-only generation uses `scripts.diff_model_infer`, model-only downloads,
and model/environment configs rather than the CT paired inference path.

Acceptance tasks:

- Validate generated model/environment configs for CT and MR image-only paths.
- Run one CT image-only and one MR image-only smoke test.
- Document naming conventions for output files.
- Keep `rflow-mr` non-commercial model terms prominent.

### 4. Synthetic Medical Image Evaluation

Potential skill ID:
`synthetic-medical-image-evaluation`

User prompt:
`Evaluate these generated CT volumes against a reference set and explain the limits.`

CLI direction:
Future `evaluate` wrapper around upstream evaluation scripts.

Why split:
Evaluation has different inputs, outputs, interpretation risks, and user intent
from generation.

Acceptance tasks:

- Wrap FID or quality-check scripts with a deterministic adapter.
- Require reference dataset provenance and license review.
- Produce a human-readable metric report with caveats.
- Avoid clinical quality claims.

### 5. NV-Generate-CTMR Training And Fine-Tuning

Potential skill ID:
`nv-generate-ctmr-training`

User prompt:
`Help me plan fine-tuning or training for this synthetic medical imaging workflow.`

CLI direction:
Future `training-plan`, `data-check`, and config review commands.

Why split:
Training is higher risk, higher compute, dataset-dependent, and should not be
bundled with inference planning.

Acceptance tasks:

- Inventory upstream training scripts, configs, notebooks, and data contracts.
- Define dataset and license checks.
- Add GPU, multi-GPU, checkpoint, and storage planning.
- Add strong safety language around data handling and permitted use.

## Next Recommendation

Harden the umbrella `nv-generate-ctmr` skill first by adding named config
presets and output manifests. Then split `nv-generate-ctmr-ct-paired` only if
users repeatedly search for CT paired generation as a standalone task.
