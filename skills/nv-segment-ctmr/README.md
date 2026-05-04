# NV-Segment-CTMR

Skill ID: `nv-segment-ctmr`

Plan and guide research CT/MRI segmentation workflows using NVIDIA-Medtech
NV-Segment-CTMR. This skill helps an agent turn plain-language requests into
source-grounded segmentation plans, label lookup steps, MONAI bundle commands,
output expectations, and safety/provenance checks.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/nv-segment-ctmr

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
Medical Imaging, Research, Agent Workflows, AI ML

Collection context:
This skill is part of the medical AI codebase-to-agentic-skill workstream. It
is the reusable algorithm skill that can support higher-level workflows such as
Radiological Report to ROI, MR-RATE analysis, and future medical imaging
algorithm wrappers.

## What This Skill Does

This skill gives Codex an agentic interface to NVIDIA-Medtech
NV-Segment-CTMR, a CT and MRI 3D medical image segmentation model and MONAI
bundle workflow.

The current version is planning-first by default. It helps with:

- Choosing whether the request is generic segmentation, anatomy-specific
  segmentation, label lookup, brain MRI preprocessing, batch segmentation, or a
  report-guided ROI workflow.
- Choosing among `CT_BODY`, `MRI_BODY`, and `MRI_BRAIN` when enough context is
  available.
- Explaining setup requirements, model weight requirements, and source
  limitations.
- Producing a read-only WSL2/Linux setup plan before cloning source, creating
  environments, or downloading model weights.
- Planning MONAI bundle commands and expected output paths.
- Verifying existing segmentation outputs.
- Running guarded single-volume, brain MRI, or batch segmentation only after
  explicit confirmation and local prerequisite checks.
- Preserving research-only safety language, model/license notes, and
  provenance requirements.

The skill should not silently download model weights, run Docker, launch GPU
jobs, or write segmentation outputs. Execution is behind the deterministic
Python adapter, `--confirm-execution`, and user approval.

## Why You Would Call It

Call this skill when:

- You have a CT or MRI NIfTI volume and want to create a segmentation map.
- You want to segment a specific anatomy such as spleen, liver, brain stem, or
  a supported brain structure.
- You want to understand whether NV-Segment-CTMR is the right source for a
  report-guided ROI workflow.
- You need a reproducible command plan before running an expensive medical
  image segmentation job.
- You need to understand what the WSL2/Linux runtime setup would do before
  approving clone, environment, or model download steps.
- You want an agent to explain setup, modes, label prompts, outputs, and
  limitations without manually reading the upstream repo.

Use it to:

- Plan single-volume CT or MRI segmentation.
- Run guarded single-volume CT or MRI segmentation after explicit approval and
  local readiness checks.
- Resolve anatomy words to candidate label-map searches.
- Plan brain MRI preprocessing and native-space mask handling.
- Plan batch or cohort segmentation with resume behavior.
- Generate a checklist for environment readiness and output verification.

Do not use it when:

- You need diagnosis, treatment, triage, or clinical decision support.
- You only need ROI extraction from an existing segmentation and report. Use
  `radiological-report-to-roi` instead.
- You need generic NIfTI file handling with no NV-Segment-CTMR context.
- You want to execute downloads, Docker, GPU work, or file writes without
  explicit review.

## Keywords

NV-Segment-CTMR, NVIDIA-Medtech, VISTA3D, CT segmentation, MRI segmentation,
medical image segmentation, 3D segmentation, NIfTI, MONAI bundle, CT_BODY,
MRI_BODY, MRI_BRAIN, label prompt, anatomy label lookup, brain MRI
segmentation, batch segmentation, cohort segmentation, TensorRT segmentation,
research medical imaging.

## Search Terms

Create a segmentation map from this MRI, segment this CT scan, segment spleen
in a CT volume, find the NV-Segment-CTMR label for brain stem, plan a MONAI
bundle segmentation run, run CT_BODY segmentation, run MRI_BODY segmentation,
run MRI_BRAIN segmentation, preprocess a brain MRI for segmentation, create a
batch segmentation plan, check whether NV-Segment-CTMR can run on this machine,
medical image segmentation with VISTA3D, research NIfTI segmentation workflow,
agentic medical imaging segmentation skill.

## How It Works

The skill separates agent reasoning from deterministic execution.

1. The agent clarifies the user's segmentation intent.
2. The agent asks for missing information such as modality, local image path,
   target anatomy, model path, output directory, and whether writes are allowed.
3. The agent uses source context from the NV-Segment-CTMR repo, model card, and
   VISTA3D paper to explain supported workflows and limitations.
4. For anatomy-specific requests, the agent treats natural language as a search
   phrase and requires exact label IDs from authoritative label maps before
   execution.
5. For brain MRI, the agent calls out preprocessing and skull-stripping
   assumptions before any model plan.
6. For report-guided requests, the agent routes to Radiological Report to ROI
   and uses NV-Segment-CTMR as the segmentation source when needed.
7. The bundled read-only Python adapter performs schema reporting,
   environment checks, label lookup, command planning, brain planning, batch
   planning, and existing output verification. The guarded `run` command
   `brain-run`, and `batch-run` commands refuse execution unless explicit
   confirmation and local prerequisites are present.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "NV-Segment-CTMR"
python -m skillforge info nv-segment-ctmr --json
python -m skillforge install nv-segment-ctmr --scope global
python -m skillforge evaluate nv-segment-ctmr --json
```

Promptable examples:

```text
Use NV-Segment-CTMR to plan a segmentation map for this MRI: scan.nii.gz.
```

```text
Find the NV-Segment-CTMR label candidates for brain stem and show the source label map.
```

```text
Plan a CT_BODY segmentation run for scan.nii.gz and include expected outputs, side effects, and provenance.
```

Implemented read-only adapter commands:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py check --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py schema --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py setup-plan --target wsl2-linux --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py labels --query "brain stem" --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py plan --image scan.nii.gz --mode MRI_BODY --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-plan --image brain_t1.nii.gz --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py batch-plan --input-dir cohort --mode MRI_BODY --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py verify-output --segmentation results/scan_trans.nii.gz --json
```

Guarded execution commands:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py run --image scan.nii.gz --mode MRI_BODY --output-dir results --confirm-execution --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-run --image brain_t1.nii.gz --output-dir results --confirm-execution --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py batch-run --input-dir cohort --mode MRI_BODY --output-dir results --confirm-execution --json
```

The planning and verification commands are read-only. They do not download
model weights, run Docker, launch GPU inference, create output folders, or
write segmentation files. The `setup-plan` command is also read-only: it
returns the commands, side effects, approvals, and prerequisites for WSL2/Linux
setup without executing the clone, environment creation, dependency install, or
model download. The `verify-output` command reads an existing NIfTI file to
report shape, affine, file size, and label-value counts when `nibabel` and
`numpy` are available. The guarded `run`, `brain-run`, and `batch-run` commands
can write outputs, logs, and provenance only after `--confirm-execution` and
prerequisite checks.

## Runtime Status

Current development status:

- SkillForge unit tests pass.
- SkillForge publication evaluation passes for this skill.
- A local WSL2 Ubuntu GPU smoke test successfully ran `brain-run` against the
  `22B7CXEZ6T` MRI test case and verified the generated NIfTI output.
- The smoke test used `--no-skullstrip` because Docker/SynthStrip was not
  installed in that WSL2 environment.
- Docker/SynthStrip brain preprocessing, `CT_BODY`, `MRI_BODY`, and batch
  runtime execution still need separate acceptance tests with approved data.

The runtime acceptance details are recorded in
`docs/nv-segment-ctmr-skill-requirements-and-plan.md`.

## Inputs And Outputs

Inputs:

- Local CT or MRI NIfTI image path.
- Intended segmentation mode: `CT_BODY`, `MRI_BODY`, or `MRI_BRAIN`.
- Optional target anatomy phrase.
- Optional exact label IDs.
- Optional local NV-Segment-CTMR source checkout.
- Optional model weight path.
- Optional output directory.
- Optional batch input folder, file list, or root path.

Outputs:

- Segmentation plan.
- Candidate upstream command.
- Label lookup plan or candidate label notes.
- Environment readiness checklist.
- Expected output path pattern.
- Provenance requirements.
- Safety and setup warnings.

Guarded execution adapter outputs:

- Segmentation NIfTI path.
- Command log path.
- Provenance JSON.
- Output verification JSON.
- Structured warnings and suggested fixes.

## Examples

Promptable:

```text
Use NV-Segment-CTMR to create a segmentation map from this MRI. Ask me before running anything.
```

```text
I want to segment the spleen in this CT volume. Help me find the right NV-Segment-CTMR label and plan the run.
```

```text
Check whether this machine is ready to run NV-Segment-CTMR for MRI_BODY segmentation.
```

```text
I have a radiology report and MRI volume. Should this workflow use Radiological Report to ROI, NV-Segment-CTMR, or both?
```

CLI:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py check --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py setup-plan --target wsl2-linux --json
```

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py labels --query "brain stem" --json
```

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py plan --image scan.nii.gz --mode MRI_BODY --output-dir results --json
```

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py batch-plan --input-dir cohort --mode MRI_BODY --output-dir results --json
```

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py run --image scan.nii.gz --mode MRI_BODY --output-dir results --confirm-execution --json
```

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-run --image brain_t1.nii.gz --output-dir results --confirm-execution --json
```

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py batch-run --input-dir cohort --mode MRI_BODY --output-dir results --confirm-execution --json
```

## Help

Start with a planning prompt:

```text
Use NV-Segment-CTMR to help me decide how to segment this medical image.
```

Be ready to provide:

- Whether the input is CT or MRI.
- Whether it is body or brain imaging.
- The local image path.
- The anatomy of interest, if any.
- Whether you want a plan only or are asking to run model inference.
- Whether the local NV-Segment-CTMR repo and model weights already exist.

Use `radiological-report-to-roi` when your goal is to combine a radiology
report, image volume, segmentation mask, and ROI extraction.

## How To Call From An LLM

Use this skill when the user asks for NV-Segment-CTMR, VISTA3D CT/MR
segmentation, MONAI bundle segmentation, CT_BODY, MRI_BODY, MRI_BRAIN, or
anatomy-specific segmentation labels.

Good LLM call:

```text
Use nv-segment-ctmr to plan a research-only MRI_BODY segmentation run for scan.nii.gz.
```

Guardrail:

```text
Before execution, confirm writes, downloads, Docker, GPU use, model terms, and output directory.
```

## How To Call From The CLI

Current SkillForge commands:

```text
python -m skillforge info nv-segment-ctmr --json
python -m skillforge evaluate nv-segment-ctmr --json
```

Skill-specific CLI:

```text
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py check --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py schema --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py setup-plan --target wsl2-linux --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py labels --query "brain stem" --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py plan --image scan.nii.gz --mode MRI_BODY --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-plan --image brain_t1.nii.gz --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py batch-plan --input-dir cohort --mode MRI_BODY --output-dir results --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py verify-output --segmentation results/scan_trans.nii.gz --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py run --image scan.nii.gz --mode MRI_BODY --output-dir results --confirm-execution --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py brain-run --image brain_t1.nii.gz --output-dir results --confirm-execution --json
python skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py batch-run --input-dir cohort --mode MRI_BODY --output-dir results --confirm-execution --json
```

The full CLI roadmap is described in:
https://github.com/medatasci/agent_skills/blob/main/docs/nv-segment-ctmr-skill-requirements-and-plan.md

## Trust And Safety

Risk level:
Medium.

Permissions:

- Planning and label lookup should be read-only.
- Direct execution may read medical images and write segmentation masks, logs,
  and provenance JSON.
- Model setup may require network downloads.
- Brain MRI preprocessing may require Docker/SynthStrip.
- Batch/cohort segmentation may consume significant GPU and storage resources.

Data handling:
Medical images, reports, paths, and derived segmentation masks may be sensitive.
Do not upload, share, or redistribute them without explicit permission and
appropriate rights.

Writes vs read-only:
The current skill should default to read-only planning. Execution and output
writes require an explicit output directory and user approval.

External services:
The upstream setup may use GitHub and Hugging Face for source code and model
weights. The skill should not call them unless the user approves a setup or
download step.

Credential requirements:
Hugging Face authentication may be required depending on access state and model
terms. The skill should not ask for secrets in chat.

Approval gates:

- Before downloading source code or model weights.
- Before running Docker, GPU jobs, or long-running inference.
- Before writing outputs.
- Before processing data that may contain PHI.

Limitations:

- The inference adapters are guarded and depend on the user's local
  NV-Segment-CTMR checkout, model weights, MONAI/PyTorch environment, input
  image, writable output directory, and explicit execution confirmation.
- NV-Segment-CTMR is research/development oriented, not clinical decision
  support.
- Label IDs must come from source label maps, not LLM memory.
- Brain MRI workflows have preprocessing assumptions that differ from body
  CT/MRI workflows.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues/new/choose

Useful feedback:

- The skill was hard to find.
- The skill chose the wrong workflow or asked the wrong clarifying question.
- A source command or limitation was unclear.
- A needed adapter command is missing.
- A prompt should route to Radiological Report to ROI instead.

Promptable feedback:

```text
Please help me send feedback on nv-segment-ctmr. I tried to plan MRI_BRAIN segmentation and the setup guidance was confusing.
```

## Contributing

For normal users, submit a pull request rather than pushing directly to `main`.

Suggested contribution prompt:

```text
SkillForge, help me prepare a PR that improves the nv-segment-ctmr skill.
```

Developer path:

```text
python -m skillforge contribute "Improve nv-segment-ctmr adapter planning" --type skill --user-type developer --json
```

## Author

Maintainer:
medatasci

Maintainer status:
Draft SkillForge skill package for review and implementation.

## Citations

- NVIDIA-Medtech NV-Segment-CTMR repository:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR
- NV-Segment-CTMR Hugging Face model card:
  https://huggingface.co/nvidia/NV-Segment-CTMR
- He et al. VISTA3D: A Unified Segmentation Foundation Model For 3D Medical
  Imaging. CVPR 2025:
  https://openaccess.thecvf.com/content/CVPR2025/html/He_VISTA3D_A_Unified_Segmentation_Foundation_Model_For_3D_Medical_Imaging_CVPR_2025_paper.html
- VISTA3D arXiv record:
  https://arxiv.org/abs/2406.05285

## Related Skills

- `radiological-report-to-roi`: Use after or alongside segmentation when a
  radiology report should guide ROI selection and extraction.
- `huggingface-datasets`: Use when working with public Hugging Face datasets
  such as MR-RATE metadata and splits.
- `skill-discovery-evaluation`: Use to improve this skill's discoverability,
  trigger coverage, README, and publication metadata.
