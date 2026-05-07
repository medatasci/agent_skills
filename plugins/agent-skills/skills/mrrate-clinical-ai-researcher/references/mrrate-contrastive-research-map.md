# MR-RATE Contrastive Research Map

This map helps `mrrate-clinical-ai-researcher` connect algorithm ideas to the
MR-RATE `contrastive-pretraining` source surfaces and related skills.

The goal is to keep research design grounded: every model idea should map to
source-supported data contracts, configurable training surfaces, evaluation
artifacts, and explicit evidence requests.

## Source Surfaces

| Source surface | Research relevance |
| --- | --- |
| `contrastive-pretraining/README.md` | Architecture overview, encoder choices, fusion modes, data format, training examples, inference format, and tests. |
| `scripts/run_train.py` | Training argument parser, encoder selection, fusion/pooling settings, normalizer, split, resume, W&B, and checkpoint setup. |
| `scripts/data.py` | Dataset loading, report JSONL contract, image layouts, normalization, resampling, crop/pad behavior, split filtering, and variable-volume handling. |
| `mr_rate/mr_rate/mr_rate.py` | MRRATE model, visual/text projections, fusion logic, attention pooling, token masking, and contrastive loss implementation. |
| `vision_encoder/` | VJEPA2, VJEPA 2.1, sliding encoder variants, LoRA and temporal/depth handling. |
| `scripts/mr_rate_trainer.py` | Distributed training, checkpointing, optimizer/scheduler state, W&B logging, and resume behavior. |
| `scripts/inference.py` | Zero-shot pathology scoring, prompt encoding, model loading, prediction outputs, split filtering, and labels handling. |
| `scripts/eval.py` | AUROC and related evaluation mechanics, including confidence interval behavior when supported by source. |
| `data/pathologies.json` | Positive/negative pathology prompts for zero-shot scoring. |
| `tests/` | Source-backed behavior expectations and smoke-test targets for model, fusion, pooling, data, and encoders. |

## Algorithm Ideas To Evidence

| Algorithm idea | Source or skill evidence needed | Review question |
| --- | --- | --- |
| New fusion method | Model change in `mr_rate.py`, baseline fusion settings, ablation matrix | Does the new method outperform simpler fusion when data, objective, and compute are held constant? |
| Text-guided pooling change | Pooling strategy implementation, prompts/report text source, failure analysis | Does text conditioning improve disease-relevant visual token selection or just overfit prompt artifacts? |
| Native vs coreg vs atlas input study | Data layout, registration derivative summaries, same split and labels | Does image-space choice affect representation quality or introduce cohort differences? |
| Sliding encoder vs temporal CNN | Encoder choice, chunk size, memory profile, same training budget | Does depth handling improve relevant pathology performance or only change compute behavior? |
| New contrastive objective | Loss implementation, sampling strategy, sentence validity masking, baseline loss | Does the objective test the intended representation claim without leaking labels? |
| Supervised or multi-task head | Label provenance, split policy, loss weighting, evaluation outputs | Does supervision help without turning weak labels into unexamined ground truth? |
| Prompt design change | Pathology prompt file, fixed checkpoint, fixed labels, prompt ablations | Does prompt wording improve robust scoring or just tune to one label set? |
| External pretrained weights | Weight source, compatibility, initialization rule, baseline comparison | Does initialization improve performance under a fair model-selection policy? |

## Skill Collaboration

| Need | Skill to use | Return to researcher for |
| --- | --- | --- |
| Whole-repo orientation | `mrrate-repository-guide` | Source placement and workflow scope. |
| Dataset availability and layout | `mrrate-dataset-access` | Experiment feasibility and data contract. |
| Clinical-statistical coherence | `mrrate-medical-workflow-reviewer` | Dataset, label, cohort, leakage, and metric validity. |
| Training command mechanics | `mrrate-contrastive-pretraining` | Source-supported execution plan after research design is set. |
| Inference and AUROC mechanics | `mrrate-contrastive-inference` | Source-supported evaluation artifact plan. |
| Pathology labels and prompts | `mrrate-report-pathology-labeling` | Label provenance and supervision/evaluation signal review. |
| Image-space derivatives | `mrrate-registration-derivatives` | Native/coreg/atlas input comparison design. |

## Evidence Request Pattern

When the researcher needs another MR-RATE skill, request a specific artifact:

```text
Use <MR-RATE skill> to produce or explain <artifact>. I need it so
mrrate-clinical-ai-researcher can assess <algorithm-development concern>.
Do not run side-effecting commands unless approved.
```

Examples:

```text
Use mrrate-contrastive-pretraining to explain the source-supported settings for
late_attn with cross_attn pooling. I need it so mrrate-clinical-ai-researcher
can design a fair ablation against late fusion and simple_attn.
```

```text
Use mrrate-contrastive-inference to explain the outputs from this inference run.
I need it so mrrate-clinical-ai-researcher can evaluate whether the new fusion
method improved specific pathologies or only the mean AUROC.
```

```text
Use mrrate-medical-workflow-reviewer to review this cohort and label plan. I
need it so mrrate-clinical-ai-researcher can avoid designing experiments around
a clinically incoherent target.
```

## Research Handoff Template

Use this when handing evidence back to the clinical AI researcher:

```text
Research hypothesis:
Evidence source skill:
Artifacts reviewed:
Model/data contract:
Baseline:
Ablations:
Metrics:
Known missing evidence:
Known side effects:
Questions for algorithm research review:
```
