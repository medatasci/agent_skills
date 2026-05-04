# Medical AI Skill Candidate Inventory

Status: first-pass discovery  
Date: 2026-05-04

This inventory collects potential agentic skills from medical AI codebases for
later review. The first source is NVIDIA-Medtech/NV-Segment-CTMR. Future passes
should add more NVIDIA-Medtech repositories and Project MONAI/MONAI functional
blocks.

The working assumption for this pass is that **functional blocks can be skills**.
A block does not need to be a perfect final skill package yet. It needs a clear
user need, source provenance, an execution surface, and enough input/output
shape to judge whether an agentic wrapper is useful.

HTML report:
[NV-Segment-CTMR Skill Discovery Report](reports/nv-segment-ctmr-skill-discovery.html)

## Review Criteria

For each candidate, capture:

- what the skill is
- how a user or agent would call it
- source repository and full entrypoint URLs
- required inputs and produced outputs
- deterministic command, script, config, or API surface
- dependencies, credentials, GPU, Docker, model weights, and operating system
- safety, license, data-use, and clinical-use boundaries
- whether it should be a standalone skill or part of a larger workflow
- recommendation: `make-skill-now`, `needs-adapter-first`,
  `needs-docs-or-examples`, `needs-license-review`, or `not-a-good-skill-yet`

## Source 1: NVIDIA-Medtech / NV-Segment-CTMR

Repository:
https://github.com/NVIDIA-Medtech/NV-Segment-CTMR

Main implementation directory:
https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR

Model card:
https://huggingface.co/nvidia/NV-Segment-CTMR

Existing local readiness card:
[docs/readiness-cards/nv-segment-ctmr.md](readiness-cards/nv-segment-ctmr.md)

Existing related SkillForge exemplar:
[skills/radiological-report-to-roi](../skills/radiological-report-to-roi/README.md)

### Source Notes

- The GitHub README describes NV-Segment-CTMR as a unified CT and MRI
  segmentation foundation model based on VISTA3D.
- The README documents three segment-everything modes:
  `CT_BODY`, `MRI_BODY`, and `MRI_BRAIN`.
- The Hugging Face model card describes two automated workflows: Segment
  Everything and Segment by Class.
- The Hugging Face model card says the model is for research and development
  only, uses MONAI Core, supports NIfTI inputs/outputs, and is tested on A100
  and H100 class hardware.
- The VISTA3D CVPR paper is the method/paper lineage for this model family.
- No `NV-Segment-CTMR/scripts/files.py` was found in the first-pass upstream
  `scripts/` directory listing. The listed scripts are `__init__.py`,
  `batch_inference_utils.py`, `early_stop_score_function.py`, `evaluator.py`,
  `inferer.py`, and `trainer.py`.

### Candidate Skills

| Candidate skill | What the skill would do | Sample prompt call | SkillForge CLI contract | Key source entrypoints | Recommended next step |
|---|---|---|---|---|---|
| `ct-mri-segmentation-map` | Segment one CT or MRI NIfTI volume using a predefined modality mode. | Create a segmentation map from this MRI. | `python scripts/nv_segment_ctmr.py run --image scan.nii.gz --mode MRI_BODY --output-dir results --json` | README quick start; `configs/inference.json`; MONAI bundle command. | `needs-adapter-first` |
| `ct-mri-anatomy-specific-segmentation` | Segment one or more selected anatomy classes by label ID. | Create a segmentation mask for the spleen in this CT scan. | `python scripts/nv_segment_ctmr.py run --image scan.nii.gz --label-id 3 --output-dir results --json` | README label-prompt example; `configs/label_dict.json`; `configs/metadata.json`; Hugging Face pipeline example. | `needs-adapter-first` |
| `ct-mri-segmentation-label-finder` | Search/resolve anatomical labels, class IDs, modality coverage, and evaluation notes. | Find the segmentation labels that match brain stem anatomy. | `python scripts/nv_segment_ctmr.py labels --query "brain stem" --json` | `configs/label_dict.json`; `configs/metadata.json`; `configs/label_mappings.json`. | `make-skill-now` |
| `ct-mri-batch-segmentation` | Build a resumable input list and run folder-level NIfTI segmentation. | Create segmentation maps for every NIfTI image in this folder and skip completed cases. | `python scripts/nv_segment_ctmr.py batch-plan --input-dir cohort --output-dir results --mode MRI_BODY --json` | `configs/batch_inference.json`; `scripts/batch_inference_utils.py`. | `needs-adapter-first` |
| `ct-mri-cohort-segmentation` | Run cohort segmentation through `torchrun` with multi-GPU config and resume behavior. | Segment this imaging cohort across available GPUs and make the run resumable. | `python scripts/nv_segment_ctmr.py batch-run --input-dir cohort --output-dir results --mode MRI_BODY --gpus 2 --json` | README multi-GPU example; `configs/mgpu_inference.json`; `scripts/batch_inference_utils.py`. | `needs-adapter-first` |
| `brain-mri-segmentation-map` | Run the brain MRI script that skull strips, preprocesses, segments, and reverts masks. | Create a brain structure segmentation map from this MRI and keep provenance. | `python scripts/nv_segment_ctmr.py brain-run --image brain_t1.nii.gz --output-dir results --json` | `brain_t1_preprocess/run_brain_segmentation.sh`; `preprocess.py`; `revert_preprocess.py`. | `needs-adapter-first` |
| `brain-mri-preprocessing` | Run or validate skull stripping, affine alignment, template preprocessing, and native-space reversion. | Prepare this brain MRI for segmentation and tell me what changed. | `python scripts/nv_segment_ctmr.py brain-preprocess --image brain_t1.nii.gz --output-dir work --json` | `brain_t1_preprocess/preprocess.py`; `revert_preprocess.py`; `synthstrip-docker`; `LUMIR_template.nii.gz`. | `needs-adapter-first` |
| `ct-mri-segmentation-evaluation` | Run or explain evaluation workflows and prompt formatting for label/point prompts. | Evaluate this medical image segmentation model on my validation set. | `python scripts/nv_segment_ctmr.py evaluate-plan --config configs/evaluate.json --json` | `configs/evaluate.json`; `configs/mgpu_evaluate.json`; `scripts/evaluator.py`; `scripts/early_stop_score_function.py`. | `needs-docs-or-examples` |
| `ct-mri-accelerated-segmentation` | Run TensorRT inference when a TensorRT environment/model is available. | Check whether this segmentation workflow can run with TensorRT acceleration here. | `python scripts/nv_segment_ctmr.py trt-check --json` | README TensorRT section; `configs/inference_trt.json`. | `needs-license-review` |
| `ct-mri-segmentation-finetuning-helper` | Guide or automate continual learning/fine-tuning setup. | Help me prepare a fine-tuning run for this segmentation model and label mapping. | `python scripts/nv_segment_ctmr.py finetune-plan --train-config configs/train_continual.json --json` | README finetuning note; `configs/train.json`; `configs/train_continual.json`; `configs/multi_gpu_train.json`; `scripts/trainer.py`. | `needs-docs-or-examples` |

### Recommended First Skill Package

Start with a reusable algorithm skill:

```text
skills/nv-segment-ctmr/
  SKILL.md
  README.md
  references/
    source-summary.md
    label-map.md
    execution.md
    safety-and-license.md
  scripts/
    nv_segment_ctmr.py
```

The adapter should support:

```text
python scripts/nv_segment_ctmr.py check --json
python scripts/nv_segment_ctmr.py schema --json
python scripts/nv_segment_ctmr.py labels --query "brain stem" --json
python scripts/nv_segment_ctmr.py plan --image image.nii.gz --mode MRI_BODY --json
python scripts/nv_segment_ctmr.py run --image image.nii.gz --mode MRI_BODY --output-dir results --json
```

The first implementation should probably make `labels`, `check`, `schema`, and
`plan` work before direct model execution. Direct execution needs careful
environment handling, model weight resolution, GPU checks, and provenance.

### Agent Value

The agentic layer is useful because users should not need to memorize:

- which mode to use for CT body, MRI body, or brain MRI
- whether brain MRI requires preprocessing
- where the model weights should live
- how label IDs map to anatomical terms
- how batch resume and skip rules work
- when a precomputed segmentation is preferable to running the model
- what safety, license, and research-only limitations apply

### LLM Semantic Processing Opportunities

LLM semantic processing should help users find and compose the right capability,
but deterministic code should still verify labels, files, commands, outputs, and
provenance.

Useful semantic processing tasks:

- Map broad user intent to candidate skills, such as "create a segmentation
  map" to `ct-mri-segmentation-map`.
- Ask clarifying questions when modality, anatomy, image type, or batch scope is
  unclear.
- Expand anatomy synonyms, acronyms, and report language into likely label-map
  search terms.
- Route report-guided requests to the Radiological Report to ROI workflow
  instead of generic segmentation.
- Read README files, papers, model cards, configs, and scripts to propose new
  candidate functional blocks.
- Summarize outputs and warnings in user language after deterministic code has
  verified the artifacts.

Deterministic code must still verify:

- exact label IDs and source label-map files
- supported modalities and model modes
- file existence and NIfTI readability
- dependency availability
- output paths and non-empty output artifacts
- provenance fields, command logs, and safety warnings

### Safety And Product Notes

- Treat the model as research/development only.
- Do not claim diagnosis, treatment, triage, clinical validation, or clinical
  decision support.
- Require explicit user confirmation before network downloads, Docker,
  GPU-heavy model execution, or processing files that may contain PHI.
- Preserve source repo URL, model card URL, model version/ref, command,
  environment summary, input paths, output paths, label map source, and warnings
  in provenance.
- Separate generic segmentation from Radiological Report to ROI. The latter
  composes report interpretation, label selection, segmentation provenance, and
  deterministic ROI extraction.

## Source Links

- NV-Segment-CTMR repository:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR
- Main implementation README:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR
- Quick start:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR#quick-start
- Scripts directory:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR/scripts
- Brain MRI segmentation:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR#brain-mri-segmentation-any-mri-sequence
- Model card:
  https://huggingface.co/nvidia/NV-Segment-CTMR
- VISTA3D CVPR paper:
  https://openaccess.thecvf.com/content/CVPR2025/html/He_VISTA3D_A_Unified_Segmentation_Foundation_Model_For_3D_Medical_Imaging_CVPR_2025_paper.html
