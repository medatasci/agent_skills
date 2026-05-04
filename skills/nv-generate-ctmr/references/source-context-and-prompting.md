# NV-Generate-CTMR Source Context And Prompting

This reference gives agents the source-grounded context needed to route and
prompt NV-Generate-CTMR workflows without inventing capabilities.

## Authoritative Sources

Use these sources before making detailed claims:

- NV-Generate-CTMR repository:
  https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/tree/main
- Upstream inference guide:
  https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/blob/main/docs/inference.md
- Upstream setup guide:
  https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/blob/main/docs/setup.md
- Upstream training guide:
  https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/blob/main/docs/training.md
- NV-Generate-CT model card:
  https://huggingface.co/nvidia/NV-Generate-CT
- NV-Generate-MR model card:
  https://huggingface.co/nvidia/NV-Generate-MR
- NV-Generate-MR-Brain model card:
  https://huggingface.co/nvidia/NV-Generate-MR-Brain
- MAISI-v1 paper:
  https://arxiv.org/abs/2409.11169
- MAISI-v2 paper:
  https://arxiv.org/abs/2508.05772

## Source Version

The first SkillForge interface was built from local clone commit:

```text
40f5109dc77eaf01fbc5741809003f89ca3a36c7
```

Pin source and model-card revisions before making reproducibility or benchmark
claims beyond planning and adapter behavior.

## Source Facts To Preserve

- NV-Generate-CTMR generates high-resolution synthetic 3D CT and MRI volumes
  with latent diffusion and rectified-flow MAISI models.
- The repository advertises four model variants: `rflow-mr-brain`, `rflow-mr`,
  `rflow-ct`, and `ddpm-ct`.
- `rflow-ct` supports CT image/mask pair generation and CT image-only
  generation.
- `ddpm-ct` is a legacy CT DDPM path with 1000 inference steps.
- `rflow-mr-brain` supports brain MRI image-only generation, including
  whole-brain and skull-stripped contrast codes.
- `rflow-mr` supports MRI image-only generation and the upstream README
  recommends `rflow-mr-brain` for brain MRI.
- The upstream README says quick start requires at least a 16 GB GPU.
- The setup guide says Python 3.11+, CUDA 11.8+ or CUDA 12.x, and CUDA-capable
  PyTorch are needed for execution.
- The inference guide explains parameters such as `num_output_samples`,
  `spacing`, `output_size`, `controllable_anatomy_size`, `body_region`,
  `anatomy_list`, `autoencoder_sliding_window_infer_size`,
  `autoencoder_sliding_window_infer_overlap`, and
  `autoencoder_tp_num_splits`.
- The modality mapping includes CT codes and MRI contrast codes such as
  `mri_t1`, `mri_t2`, `mri_flair`, `mri_swi`, and skull-stripped variants.
- Full execution can download model weights and CT mask assets from Hugging
  Face.
- Source code is Apache 2.0; model weights have separate terms, including an
  NVIDIA Non-Commercial license for NV-Generate-MR according to the upstream
  README.
- Local WSL2 acceptance on 2026-05-04 succeeded for `rflow-ct`, `ct-paired`,
  output size `[256, 256, 128]`, spacing `[1.5, 1.5, 2.0]`, chest/lung tumor,
  on an NVIDIA RTX 3500 Ada 12 GB GPU. Peak GPU memory was 10.36 GB.

## Intent Routing

Use these routing patterns:

| User intent | Preferred route |
| --- | --- |
| "Generate a CT with a mask" | `rflow-ct`, `ct-paired` workflow. |
| "Generate CT only" | `rflow-ct`, `image-only`; mention `ddpm-ct` as legacy. |
| "Generate brain MRI" | `rflow-mr-brain`, `image-only`; ask for contrast. |
| "Generate non-brain MRI" | `rflow-mr`, `image-only`; ask for contrast/anatomy and warn about model terms. |
| "Use TensorRT" | Only discuss as an optional CT paired inference acceleration path. |
| "Train or fine tune" | Keep planning-first; route to training docs and require dataset/license/config review. |
| "Segment this existing image" | Route to `nv-segment-ctmr`. |
| "Use report text to create an ROI" | Route to `radiological-report-to-roi`. |

## Clarifying Questions

Ask only the questions needed for the next safe step:

- Do you want CT, MRI, or brain MRI generation?
- Do you need a paired CT segmentation mask, or image only?
- Which contrast do you want for MRI?
- How many samples, what output size, and what voxel spacing?
- Do you want a plan only, a config preview, or an approved run?
- Do you already have a local NV-Generate-CTMR checkout and model weights?
- Is Hugging Face download allowed?
- Is CUDA/GPU execution allowed on this machine?
- Where should generated outputs be written?

## LLM Versus Deterministic Split

LLM responsibilities:

- Interpret user intent.
- Choose likely workflow and ask clarifying questions.
- Explain model variant tradeoffs, side effects, and license implications.
- Summarize source context in plain language.
- Ask before side-effectful work.

Deterministic adapter responsibilities:

- Return model and modality metadata.
- Check local source checkout and dependency presence.
- Produce setup plans and command plans.
- Produce configuration preview JSON and source-compatible config files.
- Refuse execution without explicit confirmation.
- Run approved commands from a source checkout.
- Verify generated NIfTI files.

## Response Shape

For planning responses, return:

- selected model variant
- workflow route
- assumptions
- missing information
- configuration preview
- planned commands
- expected outputs
- side effects
- approval needed before execution
- source URLs and license notes
- next step the user can choose
