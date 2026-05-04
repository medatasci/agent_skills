# NV-Generate-CTMR Requirements And Development Plan

## Goal

Expose NVIDIA-Medtech NV-Generate-CTMR as a SkillForge agentic interface for
research synthetic CT and MRI generation workflows.

The first implementation should help users and agents plan model selection,
setup, configuration, command execution, and output verification without
silently downloading weights, running expensive GPU work, or writing generated
medical image volumes.

## Scope

Included:

- Model variant explanation for `rflow-mr-brain`, `rflow-mr`, `rflow-ct`, and
  `ddpm-ct`.
- Read-only setup planning for Linux/WSL2, Windows, and macOS.
- Read-only source checkout and dependency checks.
- CT paired image/mask command planning.
- CT, MR, and MR brain image-only command planning.
- Configuration preview for output size, spacing, sample count, anatomy, body
  region, modality/contrast, and random seed.
- Guarded execution with explicit confirmation.
- NIfTI output verification.
- Source URLs, source commit, model-card URLs, and license notes in public docs.

Deferred:

- Quality evaluation of generated images.
- Training and fine-tuning adapters.
- TensorRT acceptance testing.
- Multi-GPU orchestration beyond command planning.
- Automatic model-card revision pinning.
- Public sample-output galleries.

## Runtime And Deployment Plan

Install location:

- Recommended runtime checkout:
  `~/.skillforge/runtime/nv-generate-ctmr`

OS/runtime target:

- Preferred execution target: Linux or WSL2/Linux with NVIDIA CUDA.
- Native Windows and macOS should be planning-first until the local runtime is
  explicitly verified.

Dependency setup:

- Python 3.11+
- CUDA 11.8+ or CUDA 12.x
- CUDA-enabled PyTorch
- MONAI
- numpy
- scipy
- scikit-image
- nibabel
- matplotlib
- einops
- huggingface_hub
- tqdm
- fire
- tensorboard
- PyYAML

Model/data download policy:

- Do not download weights or CT mask assets by default.
- Model/data download requires explicit user approval.
- Guarded execution requires `--confirm-execution` and `--confirm-downloads`.

License review:

- Source code: Apache 2.0 according to the upstream repository.
- NV-Generate-CT weights: NVIDIA Open Model terms according to the upstream
  README.
- NV-Generate-MR weights: NVIDIA Non-Commercial terms according to the upstream
  README.
- NV-Generate-MR-Brain weights: NVIDIA Open Model terms according to the
  upstream README.
- Agents must not imply commercial, clinical, or redistribution permissions
  without reviewing the current model-card terms.

Environment checks:

- Check Python, platform, `git`, `python`, `nvidia-smi`, and `torchrun`.
- Check importability for `torch`, `monai`, `nibabel`, `huggingface_hub`, and
  `numpy`.
- Check source checkout for `scripts/inference.py`, `scripts/diff_model_infer.py`,
  and `configs/`.

Smoke-test data:

- CI tests should use read-only adapter commands and optional tiny synthetic
  NIfTI files for `verify-output`.
- Do not commit generated medical image volumes, model weights, or large
  outputs.
- Full CUDA acceptance tests require an approved local machine and approved
  model/data downloads.

## WSL2 Runtime Smoke Test Status

Local WSL2 preflight performed on 2026-05-04:

- WSL2 Ubuntu is available.
- CUDA is visible from WSL through `nvidia-smi`.
- Runtime checkout exists at `~/.skillforge/runtime/nv-generate-ctmr`.
- Runtime checkout source commit:
  `40f5109dc77eaf01fbc5741809003f89ca3a36c7`.
- Local GPU visible to WSL: NVIDIA RTX 3500 Ada with 12 GB VRAM.
- Upstream quick-start guidance says at least 16 GB GPU VRAM is required, so
  full-size inference on this workstation may require a smaller validated
  config or a different GPU.
- WSL has `python3-venv` and `python3-pip` installed.
- Runtime virtual environment exists at
  `~/.skillforge/runtime/nv-generate-ctmr/.venv`.
- Runtime dependency install completed with CUDA-capable PyTorch 2.11.0+cu130,
  MONAI 1.5.2, nibabel 5.4.2, Hugging Face Hub, and upstream requirements.

Smoke tests completed:

- Source checkout clone and source commit verification.
- WSL CUDA visibility check with `nvidia-smi`.
- Read-only adapter plan against the WSL runtime checkout:

```text
python3 skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py plan \
  --generate-version rflow-ct \
  --workflow ct-paired \
  --source-dir ~/.skillforge/runtime/nv-generate-ctmr \
  --output-size 256,256,128 \
  --spacing 1.5,1.5,2.0 \
  --output-dir ~/skillforge-smoke/nv-generate-ctmr \
  --json
```

- Source-compatible config writing with `config-template --config-dir`.
- Guarded run refusal without execution confirmation:

```text
python3 skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py run \
  --generate-version rflow-ct \
  --workflow ct-paired \
  --source-dir ~/.skillforge/runtime/nv-generate-ctmr \
  --output-size 256,256,128 \
  --spacing 1.5,1.5,2.0 \
  --output-dir ~/skillforge-smoke/nv-generate-ctmr \
  --json
```

Full CUDA inference smoke test status:
Accepted for a small CT paired smoke test on this workstation.

Runtime setup commands used:

```text
sudo apt install python3-venv python3-pip
cd ~/.skillforge/runtime/nv-generate-ctmr
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

Config generation and guarded run command used:

```text
python3 /mnt/c/Users/medgar/OneDrive\ -\ NVIDIA\ Corporation/Documents/New\ project/agent_skills/skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py config-template \
  --source-dir ~/.skillforge/runtime/nv-generate-ctmr \
  --generate-version rflow-ct \
  --workflow ct-paired \
  --output-size 256,256,128 \
  --spacing 1.5,1.5,2.0 \
  --body-region chest \
  --anatomy "lung tumor" \
  --config-dir ~/skillforge-smoke/nv-generate-ctmr/configs \
  --output-dir ~/skillforge-smoke/nv-generate-ctmr/output \
  --json

python3 /mnt/c/Users/medgar/OneDrive\ -\ NVIDIA\ Corporation/Documents/New\ project/agent_skills/skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py run \
  --source-dir ~/.skillforge/runtime/nv-generate-ctmr \
  --generate-version rflow-ct \
  --workflow ct-paired \
  --output-size 256,256,128 \
  --spacing 1.5,1.5,2.0 \
  --body-region chest \
  --anatomy "lung tumor" \
  --config-dir ~/skillforge-smoke/nv-generate-ctmr/configs \
  --output-dir ~/skillforge-smoke/nv-generate-ctmr/output \
  --python-executable .venv/bin/python \
  --confirm-execution \
  --confirm-downloads \
  --json
```

Accepted smoke-test outputs:

- `/home/marc/skillforge-smoke/nv-generate-ctmr/output/sample_20260504_134014_319438_image.nii.gz`
- `/home/marc/skillforge-smoke/nv-generate-ctmr/output/sample_20260504_134014_319438_label.nii.gz`

Verification result:

- Both outputs are readable NIfTI files.
- Both outputs have shape `[256, 256, 128]` and voxel spacing `[1.5, 1.5, 2.0]`.
- The run completed with peak GPU memory usage of 10.36 GB.

Do not treat this as clinical validation. It is a runtime integration smoke
test only.

## Skill Split Decision

Decision:
Keep `nv-generate-ctmr` as one umbrella algorithm-interface skill for the MVP.
Do not split it into separate installable skills yet.

Rationale:

- The model variants share the same source repository, setup path, dependency
  stack, model-download behavior, safety boundaries, and provenance needs.
- Most users will begin with an intent such as "generate synthetic CT" or
  "generate brain MRI" and need routing before they know which variant applies.
- One skill is easier to discover, install, and maintain while runtime
  execution is still being hardened.
- The current adapter already exposes model/workflow routing in deterministic
  commands.

Future split candidates:

| Candidate skill | Split when | Why |
| --- | --- | --- |
| `nv-generate-ctmr-ct-paired` | CT paired config writing and CUDA smoke tests are working. | CT image/mask generation has distinct outputs, configs, and side effects. |
| `nv-generate-ctmr-mr-brain` | MR brain model-card revision pinning and MR-specific config writing are working. | Brain MRI contrast selection and skull-stripped variants deserve focused prompts. |
| `nv-generate-ctmr-image-only` | Image-only CT/MR runs have separate accepted smoke tests. | Image-only runs use `diff_model_infer.py` and different config files from CT paired generation. |
| `synthetic-medical-image-evaluation` | Quality metrics and report outputs are implemented. | Evaluation is a downstream workflow with different inputs, outputs, and interpretation risks. |
| `nv-generate-ctmr-training` | Training/fine-tuning requirements, data contracts, and safety review are ready. | Training is higher risk, higher compute, and should not be bundled with inference planning. |

Rule:
Split only when a candidate has a distinct user workflow, a distinct
deterministic adapter surface, separate smoke-test evidence, and enough search
demand to justify another skill in the catalog.

Backlog:
Detailed split candidates and acceptance tasks are tracked in
`docs/backlog/nv-generate-ctmr-split-roadmap.md`.

Rollback/cleanup notes:

- Remove runtime checkout when no longer needed.
- Remove Hugging Face caches, downloaded models, generated outputs, and
  temporary config files when appropriate.
- Keep provenance for any generated research artifact that is retained.

## Adapter Commands

Required commands:

- `schema`
- `check`
- `setup-plan`
- `models`
- `modalities`
- `config-template`
- `plan`
- `run`
- `verify-output`

## Safety Gates

The adapter must refuse execution unless:

- `--confirm-execution` is provided.
- `--confirm-downloads` is provided when upstream commands may download
  weights or data.
- A valid source checkout exists.
- The selected model/workflow combination is supported.

## Publication Checks

Before publishing:

- Run `python -m skillforge build-catalog --json`.
- Run `python -m skillforge evaluate nv-generate-ctmr --json`.
- Confirm generated catalog, static site, and plugin bundle files are
  committed.
- Confirm public docs preserve model/license limitations and do not include
  NVIDIA-internal data.
