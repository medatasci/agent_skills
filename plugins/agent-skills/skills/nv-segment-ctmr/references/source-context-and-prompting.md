# NV-Segment-CTMR Source Context And Prompting

This reference gives agents the source-grounded context needed to prompt and
route NV-Segment-CTMR workflows without inventing capabilities.

## Authoritative Sources

Use these sources before making detailed claims:

- NV-Segment-CTMR implementation README:
  https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR
- NV-Segment-CTMR model card:
  https://huggingface.co/nvidia/NV-Segment-CTMR
- VISTA3D CVPR 2025 paper:
  https://openaccess.thecvf.com/content/CVPR2025/html/He_VISTA3D_A_Unified_Segmentation_Foundation_Model_For_3D_Medical_Imaging_CVPR_2025_paper.html
- VISTA3D arXiv record:
  https://arxiv.org/abs/2406.05285
- Project MONAI VISTA source lineage:
  https://github.com/Project-MONAI/VISTA

## Source Facts To Preserve

- NV-Segment-CTMR is a CT and MRI 3D medical image segmentation model based on
  VISTA3D.
- The implementation README describes three segment-everything modes:
  `CT_BODY`, `MRI_BODY`, and `MRI_BRAIN`.
- The repository points to label metadata files including `metadata.json`,
  `label_dict.json`, and `label_mappings.json`.
- The model card describes label-prompt and modality-prompt workflows.
- The model card says NV-Segment-CTMR does not support point-based interactive
  segmentation and points users to VISTA3D for interactive use.
- The model card says this model is for research and development only.
- The model card says NIfTI is the input format and MONAI Core is the software
  integration.
- The repository README describes brain MRI preprocessing with skull stripping,
  affine alignment to a LUMIR template, MONAI bundle inference, and native-space
  mask reversion.
- The repository README states code is Apache License 2.0 and model weights
  are under an NVIDIA non-commercial license.

## VISTA3D Paper Context For Prompting

The VISTA3D paper matters because it explains why a medical-imaging agent
should not treat this like a generic 2D image segmentation problem.

Prompting implications:

- Ask whether the user needs automatic segmentation of supported structures or
  a different workflow. Automatic segmentation is the main practical path for
  large cohorts.
- Treat 3D medical image volumes as volumetric inputs, not independent 2D image
  slices.
- Distinguish supported-class segmentation from novel or unsupported anatomy.
  Unsupported anatomy should trigger label-map review, limitation language, or
  a different workflow.
- Do not imply open-vocabulary text segmentation. Anatomy language must be
  resolved to supported label IDs or known modes.
- Do not imply point-click interactive correction through NV-Segment-CTMR. The
  interactive lineage belongs to VISTA3D, but the NV-Segment-CTMR model card
  says this model does not expose point-based interactive segmentation.
- Explain that fine-tuning is a separate higher-cost workflow with different
  data, compute, checkpoint, and validation requirements.

## Intent Routing

Use these routing patterns:

| User intent | Preferred route |
|---|---|
| "Create a segmentation map from this MRI" | Ask body vs brain if unclear, then plan `MRI_BODY` or `MRI_BRAIN`. |
| "Segment this CT scan" | Plan `CT_BODY` unless the user requests specific labels. |
| "Segment the spleen" | Resolve anatomy to label candidates first, then plan label-prompt segmentation. |
| "Find the label for brain stem" | Use label lookup, not model execution. |
| "Use the report to find the ROI" | Route to `radiological-report-to-roi`; use this skill only for segmentation source planning. |
| "Run this on a folder" | Plan batch segmentation, resume rules, output paths, and resource checks. |
| "Can it run faster?" | Treat TensorRT as optional and environment-specific. |
| "Train or fine tune this" | Keep planning-first and require data/config/checkpoint review. |

## Clarifying Questions

Ask only the questions needed for the next safe step:

- Is the image CT or MRI?
- Is this body imaging or brain MRI?
- Do you want all supported structures or a specific anatomy?
- Do you already have an NV-Segment-CTMR checkout and model weights?
- Do you want a plan only, or are you asking me to run inference?
- Where should outputs be written?
- Is Docker allowed for brain MRI skull stripping?
- Is the data allowed to be processed locally for this workflow?

## Response Shape

For planning responses, return:

- selected workflow
- assumptions
- missing information
- source URLs
- planned command
- expected outputs
- side effects
- approval needed before execution
- provenance fields to capture

For execution requests before the adapter exists, say that the current
SkillForge skill is planning-first and that direct execution depends on the
local upstream NV-Segment-CTMR setup.
