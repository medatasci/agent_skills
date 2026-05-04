---
name: nv-segment-ctmr
owner: medatasci
description: >
  Plan and guide research-only NVIDIA-Medtech NV-Segment-CTMR CT/MRI
  segmentation workflows, including CT_BODY, MRI_BODY, MRI_BRAIN, anatomy label
  lookup, command planning, output verification, and explicitly approved guarded
  execution. Do not use for diagnosis, treatment, triage, or clinical
  decision-making.
---

# NV-Segment-CTMR

## What This Skill Does

Use this skill when a user asks for research-only CT/MRI segmentation planning,
label lookup, output verification, or explicitly approved NV-Segment-CTMR
execution.

This skill helps an agent turn high-level user requests such as "create a
segmentation map from this MRI" into a safe, reproducible workflow grounded in
the NV-Segment-CTMR source documentation, MONAI bundle conventions, local input
files, and explicit user approval for any execution.

## Safe Default Behavior

Default to planning and inspection.

Do not run inference unless the user has explicitly approved local medical image
processing, output writes, runtime requirements, and the adapter command includes
`--confirm-execution`.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Create a segmentation map from a body CT | Use `CT_BODY` planning or guarded execution. |
| Create a segmentation map from a body MRI | Use `MRI_BODY` planning or guarded execution. |
| Create a segmentation map from a brain MRI | Use `MRI_BRAIN` planning or guarded execution. |
| Find labels for an anatomy phrase | Use the `labels` adapter command. |
| Check whether an existing output is valid | Use the `verify-output` adapter command. |
| Generate an ROI from a report and segmentation | Route to `radiological-report-to-roi`. |

## SkillForge Discovery Metadata

This section is written as Markdown so people can read it, while SkillForge can
still extract the same discovery fields for catalogs, search, and generated
pages.

### Title

NV-Segment-CTMR

### Short Description

Plan and guide research CT/MRI segmentation workflows with NV-Segment-CTMR,
MONAI bundle commands, label prompts, and provenance.

### Expanded Description

Use this skill to help an agent turn user intent into a safe, source-grounded
NV-Segment-CTMR segmentation workflow. The skill helps clarify modality, choose
`CT_BODY`, `MRI_BODY`, or `MRI_BRAIN`, resolve anatomy labels from authoritative
label maps or a built-in cited snapshot, explain setup requirements, plan MONAI
bundle commands, plan brain and batch workflows, verify existing segmentation
outputs, route report-guided requests to Radiological Report to ROI, and preserve
research-only safety boundaries. The bundled Python adapter implements `schema`,
`check`, `labels`, `plan`, `brain-plan`, `batch-plan`, `verify-output`, and
guarded `run`, `brain-run`, and `batch-run` commands. Direct execution requires
explicit approval and local prerequisites.

### Aliases

- NV-Segment-CTMR
- nv-segment-ctmr
- NVIDIA-Medtech NV-Segment-CTMR
- VISTA3D CT MRI segmentation
- MONAI bundle medical segmentation
- CT MRI segmentation map
- Create a segmentation map from this MRI
- Create a segmentation map from this CT
- MRI_BRAIN segmentation
- MRI_BODY segmentation
- CT_BODY segmentation

### Categories

- Medical Imaging
- Research
- Agent Workflows
- AI ML

### Tags

- nv-segment-ctmr
- medical-image-segmentation
- nifti
- monai
- vista3d
- ct
- mri
- brain-mri
- label-prompt
- segmentation

### Tasks

- plan an NV-Segment-CTMR segmentation run
- choose CT_BODY MRI_BODY or MRI_BRAIN mode
- resolve anatomy names to segmentation label candidates
- explain NV-Segment-CTMR setup and model weight requirements
- plan MONAI bundle inference commands
- run guarded single-volume, brain MRI, or batch segmentation after explicit approval
- plan brain MRI preprocessing and native-space output handling
- plan batch or cohort segmentation with resume behavior
- verify segmentation output provenance

### Use When

- The user has a CT or MRI NIfTI volume and wants a segmentation map.
- The user asks for an anatomy-specific CT or MRI segmentation mask.
- The user asks which NV-Segment-CTMR labels match an anatomy phrase.
- The user wants to know how to run or install NV-Segment-CTMR reproducibly.
- The user asks whether NV-Segment-CTMR, VISTA3D, MONAI bundle inference, CT_BODY, MRI_BODY, or MRI_BRAIN applies to a task.
- The user is designing a workflow that may call NV-Segment-CTMR before ROI extraction or analysis.

### Do Not Use When

- The user asks for diagnosis, treatment guidance, triage, or clinical decision-making.
- The user wants a final ROI from a radiology report and an existing segmentation; prefer radiological-report-to-roi for that workflow.
- The user wants generic NIfTI manipulation with no NV-Segment-CTMR or segmentation-model context.
- The user wants to run unreviewed downloads, Docker, GPU jobs, or file writes without explicit approval.

### Inputs

- local CT or MRI NIfTI image path
- intended mode CT_BODY MRI_BODY or MRI_BRAIN
- optional target anatomy or label IDs
- optional output directory
- optional local NV-Segment-CTMR checkout and model path

### Outputs

- source-grounded segmentation plan
- candidate MONAI bundle or brain MRI preprocessing command
- label lookup notes and ambiguity warnings
- expected output paths and provenance requirements
- guarded execution logs and provenance when run is approved
- safety and setup warnings

### Examples

- Use NV-Segment-CTMR to create a segmentation map from this MRI, but ask me before running anything.
- Find the NV-Segment-CTMR label candidates for brain stem and show the source label map.
- Plan a reproducible CT_BODY segmentation run for scan.nii.gz and explain the outputs.
- Does this report-guided ROI workflow need NV-Segment-CTMR or can it use an existing segmentation?

### Related Skills

- radiological-report-to-roi
- huggingface-datasets
- skill-discovery-evaluation

### Authoritative Sources

- NV-Segment-CTMR GitHub source: https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR
- NV-Segment-CTMR Hugging Face model card: https://huggingface.co/nvidia/NV-Segment-CTMR
- VISTA3D CVPR 2025 paper: https://openaccess.thecvf.com/content/CVPR2025/html/He_VISTA3D_A_Unified_Segmentation_Foundation_Model_For_3D_Medical_Imaging_CVPR_2025_paper.html
- VISTA3D arXiv record: https://arxiv.org/abs/2406.05285
- MONAI bundle documentation: https://docs.monai.io/en/stable/bundle_intro.html

### Citations

- He et al. VISTA3D: A Unified Segmentation Foundation Model For 3D Medical Imaging. CVPR 2025.
- NVIDIA-Medtech NV-Segment-CTMR repository and model card.

### Risk Level

medium

### Permissions

- read local source documentation and user-provided medical image paths
- produce command plans and setup guidance
- do not run model inference, Docker, downloads, or large file writes without explicit user approval
- planning adapter commands are read-only; guarded run may write segmentation masks, logs, and provenance JSON to user-selected output directories

### Page Title

NV-Segment-CTMR Skill - Agentic CT And MRI Medical Image Segmentation Planning

### Meta Description

Use the NV-Segment-CTMR Skill to plan research CT and MRI segmentation workflows
with NVIDIA-Medtech NV-Segment-CTMR, MONAI bundles, label prompts, CT_BODY,
MRI_BODY, MRI_BRAIN, and provenance.

## Workflow

1. Clarify the user's goal, inputs, and expected output.
2. Confirm modality and route:
   - `CT_BODY` for body CT segmentation
   - `MRI_BODY` for body MRI segmentation
   - `MRI_BRAIN` for brain MRI segmentation
   - label lookup for anatomy-specific segmentation
   - output verification for an existing segmentation
   - `radiological-report-to-roi` for report-guided ROI extraction
3. Confirm boundaries before any execution: local data permission, output
   directory, model terms, Docker, GPU/runtime use, and file writes.
4. Use the deterministic adapter commands for repeatable checks, plans, runs,
   output verification, logs, and provenance.
5. Return the result with assumptions, warnings, expected outputs, source URLs,
   and next steps.

## Method

This skill separates LLM judgment from deterministic adapter work.

Use the LLM to:

- map broad user intent to the right workflow
- ask concise clarifying questions
- expand anatomy terms into label-search phrases
- explain why `CT_BODY`, `MRI_BODY`, or `MRI_BRAIN` is likely appropriate
- summarize plans, warnings, and verified outputs in user language

Use the adapter to:

- inspect the local environment
- resolve labels
- construct reproducible command plans
- verify existing NIfTI segmentation outputs
- run guarded execution only after explicit approval
- write logs and provenance for guarded execution

Load `references/source-context-and-prompting.md` when source facts, model-card
limits, paper context, or label-prompt caveats matter. Load
`references/requirements-and-development-plan.md` when the user asks about
implementation status, testing, or roadmap.

## Inputs

- Local CT or MRI NIfTI image path.
- Intended segmentation mode: `CT_BODY`, `MRI_BODY`, or `MRI_BRAIN`.
- Optional target anatomy phrase or exact label IDs.
- Optional output directory.
- Optional local NV-Segment-CTMR checkout and model path.
- Optional batch input directory.

## Outputs

- Source-grounded segmentation plan.
- Candidate MONAI bundle or brain MRI preprocessing command.
- Label lookup candidates and ambiguity warnings.
- Expected output paths and provenance requirements.
- Existing segmentation verification JSON.
- Guarded execution logs and provenance when execution is approved.
- Safety, setup, and limitation warnings.

## Adapter Commands

Run the bundled adapter from the repository root:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py schema --json
```

Read-only planning and inspection:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py check --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py labels --query "brain stem" --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py plan --image scan.nii.gz --mode MRI_BODY --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-plan --image brain_t1.nii.gz --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py batch-plan --input-dir cohort --mode MRI_BODY --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py verify-output --segmentation results/scan_trans.nii.gz --json
```

Guarded execution:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py run --image scan.nii.gz --mode MRI_BODY --output-dir results --confirm-execution --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-run --image brain_t1.nii.gz --output-dir results --confirm-execution --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py batch-run --input-dir cohort --mode MRI_BODY --output-dir results --confirm-execution --json
```

Command responsibilities:

- `schema`: report supported commands, modes, sources, and safety boundaries.
- `check`: inspect source paths, model path, optional dependencies, and tools.
- `labels`: resolve anatomy text to candidate label IDs from source metadata or
  the built-in cited snapshot.
- `plan`: build a read-only MONAI bundle command plan for one volume.
- `brain-plan`: build a read-only MRI_BRAIN plan with skull-strip assumptions.
- `batch-plan`: discover NIfTI inputs and build a read-only batch plan.
- `verify-output`: inspect an existing NIfTI segmentation and summarize shape,
  affine, spacing, file size, and label values when possible.
- `run`: execute a guarded single-volume segmentation after approval.
- `brain-run`: execute guarded brain MRI preprocessing and segmentation after
  approval.
- `batch-run`: execute guarded batch segmentation after approval.

## Boundaries

- Do not use this skill for diagnosis, treatment, triage, or clinical decision
  support.
- Do not invent label IDs. Use source label maps or the built-in cited snapshot.
- Do not claim point-click interactive segmentation support for
  NV-Segment-CTMR.
- Do not claim model execution succeeded without output verification.
- Do not upload, share, or redistribute medical images or derived masks unless
  the user has confirmed rights and destination.
- Do not download model weights, clone repositories, use Docker, run GPU-heavy
  jobs, or write large outputs without explicit approval.
- Keep public-safe content public-safe; do not add NVIDIA-internal data,
  private process knowledge, secrets, or privileged automation.
- Preserve provenance: source repo URL, source commit, model card URL, model
  path or version, command, input path, output path, selected mode, label IDs,
  environment summary, and warnings.

## Examples

```text
Use NV-Segment-CTMR to plan a segmentation map for this MRI: scan.nii.gz.
```

```text
Find the NV-Segment-CTMR labels that might match "brain stem" and tell me which source file they came from.
```

```text
Plan a CT_BODY segmentation run for this NIfTI volume and show the expected outputs and provenance.
```

```text
I have a radiology report and MRI volume. Decide whether Radiological Report to ROI should use an existing segmentation or call NV-Segment-CTMR.
```
