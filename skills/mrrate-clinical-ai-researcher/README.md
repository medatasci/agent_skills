# MR-RATE Clinical AI Researcher

Skill ID: `mrrate-clinical-ai-researcher`

## Most Important Context

This skill provides clinical AI algorithm-development expertise for MR-RATE
research workflows. It helps agents and researchers design, critique, and
iterate new medical imaging AI methods by connecting the research question to
model architecture, data contracts, training objectives, experiment design,
ablation evidence, evaluation strategy, failure analysis, and reproducibility.

The skill's specialty is algorithmic research judgment for clinical AI: making
sure a proposed method is scientifically motivated, technically testable,
grounded in available MR-RATE artifacts, and evaluated with enough evidence to
support a research claim.

Use this skill when developing or modifying algorithms like the MR-RATE
`contrastive-pretraining` workflow: multimodal MRI-report representation
learning, VJEPA-family vision encoders, BiomedVLP-style text encoders,
multi-sequence MRI fusion, contrastive objectives, prompt-based pathology
scoring, AUROC evaluation, ablation studies, and model failure analysis.

This skill is different from `mrrate-medical-workflow-reviewer`. The medical
workflow reviewer focuses on whether the dataset, labels, cohort, workflow, and
metrics are clinically and statistically coherent. The clinical AI researcher
focuses on the algorithm itself: what to build, why that method might work, how
to test it, which baselines and ablations are needed, and what result evidence
would make the method scientifically credible.

This is a research algorithm-development skill. It must not diagnose patients,
recommend treatment, triage care, or certify model outputs as clinically valid.
It should prefer aggregate summaries, de-identified artifacts, configs, metrics,
and experiment logs when reviewing model behavior.

The research playbook and experiment checklist for this skill are intentionally
collaborative. Clinical AI researchers, ML engineers, clinicians,
statisticians, and data engineers may edit them as MR-RATE experiments evolve,
as long as edits preserve evidence, assumptions, unresolved questions,
reproducibility, and research-only safety boundaries.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-clinical-ai-researcher

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
Medical Imaging, AI Research, Research

Collection context:
This skill belongs to the MR-RATE skill family. It is the algorithm-development
expert for workflows that use MR-RATE dataset access, MRI preprocessing, report
labels, registration derivatives, contrastive pretraining, and zero-shot
inference.

Related skills usually produce evidence or source-grounded command plans. This
skill reviews and designs the algorithmic research strategy that those
technical workflows support.

## What This Skill Does

This skill helps Codex act as a clinical AI researcher for MR-RATE-style
medical imaging research. It reviews model ideas, turns them into testable
research plans, and identifies the algorithmic evidence needed before a result
is scientifically credible.

It works on questions such as:

- What model architecture should we try for variable-volume MRI studies?
- Should the experiment use native, coregistered, or atlas-space inputs?
- How should multiple MRI volumes or sequences be fused?
- What training objective actually tests the research hypothesis?
- Which report text, label source, or prompt set should supervise the model?
- What baselines are required before claiming an algorithmic improvement?
- Which ablations isolate the contribution?
- What failure analysis would explain weak or surprising model behavior?
- What reproducibility evidence is needed for another researcher to rerun the
  experiment?

Typical outputs are algorithm briefs, experiment plans, ablation matrices,
baseline comparison plans, evaluation plans, failure-analysis plans, risk
registers, and reproducibility checklists.

## Why You Would Call It

Call this skill when:

- You are creating a new MR-RATE algorithm or modifying the
  `contrastive-pretraining` branch.
- You have an idea for a model, fusion method, objective, prompt strategy,
  supervised head, retrieval task, or training regime and want a research plan.
- You need to decide what baseline, ablation, or evaluation should run next.
- You have training or inference results and want algorithmic interpretation:
  what failed, what worked, what is missing, and what experiment should follow.
- You want the AI research perspective before asking the technical MR-RATE
  skills to prepare commands.

Use it to:

- Turn an algorithm idea into a testable MR-RATE experiment.
- Critique architecture, objective, data, and evaluation choices.
- Build ablation and baseline plans.
- Plan failure analysis and reproducibility evidence.
- Coordinate with MR-RATE skills that provide data, labels, training, and
  inference mechanics.

Do not use it when:

- The task is only clinical-statistical dataset and workflow coherence. Use
  `mrrate-medical-workflow-reviewer`.
- The task is only to run the existing training CLI. Use
  `mrrate-contrastive-pretraining`.
- The task is only to run inference or AUROC evaluation. Use
  `mrrate-contrastive-inference`.
- The user needs diagnosis, treatment, triage, prognosis, or patient-care
  guidance.

## What Good Algorithm Research Means Here

For this skill, good MR-RATE clinical AI research means:

- The algorithmic hypothesis is explicit. The method says what signal,
  representation, fusion behavior, or inductive bias it is expected to improve.
- The model/data contract is concrete. The plan specifies images, reports,
  labels, splits, image space, join keys, and outputs.
- The architecture is motivated. Encoder, fusion, pooling, projection, prompt,
  and objective choices connect to the medical imaging problem.
- The experiment isolates the contribution. Baselines and ablations distinguish
  the new idea from data scale, preprocessing, prompt changes, label leakage, or
  training instability.
- Evaluation is aligned with the claim. Metrics, confidence intervals,
  subgroup behavior, failure cases, and negative results are used to understand
  the model rather than only maximize a headline score.
- Reproducibility is planned from the start. Configs, source commits, seeds,
  data versions, checkpoints, logs, and result tables are treated as research
  evidence.

## How It Works

The skill uses a structured research-design method rather than wrapping source
code directly. It starts by restating the algorithmic goal, then translates the
idea into a testable model/data contract: what inputs the model sees, what
supervision it uses, what outputs it produces, and what claim the experiment is
supposed to support.

The review then examines architecture, objective, and experiment design. For
MR-RATE contrastive research, that can include VJEPA-family image encoders,
BiomedVLP-CXR-BERT-style text encoders, variable-volume MRI fusion, temporal CNN
vs sliding depth chunks, early/mid/late/attention fusion, contrastive losses,
prompt-based scoring, label-derived evaluation, and checkpointing or logging
choices.

The skill expects evidence. It should name the artifact or result that supports
each recommendation, distinguish assumptions from observed results, and request
the smallest useful additional summary when the evidence is missing. Good
algorithm advice should result in a concrete experiment, not a vague preference.

The default mode is read-only. When the user asks for a durable artifact, the
skill can write an algorithm brief, ablation matrix, experiment checklist, or
reproducibility note. It does not require external services, credentials, model
downloads, GPU jobs, or MR-RATE source execution for normal research design.

## How This Skill Works With MR-RATE Skills

This skill designs and critiques the algorithmic research strategy. Other
MR-RATE skills provide source-grounded artifacts, command plans, and workflow
evidence.

| MR-RATE skill | Evidence this researcher may use | Algorithm-development focus |
| --- | --- | --- |
| `mrrate-medical-workflow-reviewer` | Clinical-statistical review, cohort risks, label validity concerns | Whether the algorithm research plan is medically and statistically coherent enough to test. |
| `mrrate-contrastive-pretraining` | Training arguments, encoder/fusion choices, data JSONL contract, checkpoint behavior | How to convert a research design into source-supported training mechanics. |
| `mrrate-contrastive-inference` | Score artifacts, prompts, labels CSV, AUROC outputs, split filtering | How to evaluate model variants and interpret algorithmic performance patterns. |
| `mrrate-dataset-access` | Dataset layout, batches, reports, labels, splits, local availability | Whether the proposed experiment can be supported by available data. |
| `mrrate-report-pathology-labeling` | Pathology ontology, label generation mechanics, prevalence | Whether labels or prompts are suitable supervision or evaluation signals. |
| `mrrate-registration-derivatives` | Native/coreg/atlas derivatives and registration constraints | Whether image-space choices support the algorithmic hypothesis. |
| `mrrate-repository-guide` | Whole-repo source map and family routing | Where the algorithm idea fits in the MR-RATE source tree and skill family. |

## Research Flow

1. Define the algorithmic hypothesis.
   State what the method should improve: representation quality, fusion,
   retrieval, zero-shot scoring, robustness, efficiency, calibration, or
   transfer.
2. Define the model/data contract.
   Specify image inputs, report text, labels, prompts, splits, image space,
   cohort, join keys, outputs, and artifacts.
3. Review architecture choices.
   Identify encoder, fusion, pooling, projection, trainable parameter strategy,
   normalization, and memory behavior.
4. Review objective and supervision.
   Clarify contrastive loss, weak labels, supervised labels, prompts,
   report-derived signals, multi-task losses, or retrieval/classification
   targets.
5. Plan baselines and ablations.
   Hold the right variables constant and isolate each contribution.
6. Plan evaluation and failure analysis.
   Define metrics, uncertainty, subgroup analyses, examples to inspect, and
   decision rules.
7. Plan reproducibility.
   Record source commit, configs, seeds, environment, data version, checkpoint
   policy, and output manifests.
8. Recommend next technical checks.
   Point to the MR-RATE skill or artifact needed before running the experiment.

## What This Skill Produces

Typical outputs include:

- Algorithm research brief.
- Model/data contract.
- Architecture and objective critique.
- Baseline plan.
- Ablation matrix.
- Evaluation plan.
- Failure-analysis plan.
- Reproducibility checklist.
- Research risk register.
- Recommended next technical checks with MR-RATE skills.

Recommended algorithm brief:

| Section | Content |
| --- | --- |
| Research hypothesis | The representation, training, fusion, or evaluation claim being tested. |
| Model/data contract | Inputs, reports, labels, splits, image space, outputs, and artifacts. |
| Proposed method | Encoders, fusion, pooling, objective, prompts, or new module. |
| Baselines | Comparisons needed before claiming improvement. |
| Ablations | Tests that isolate each contribution. |
| Evaluation | Metrics, uncertainty, subgroups, and failure analyses. |
| Risks | Leakage, confounding, overfitting, compute, and interpretation limits. |
| Next checks | Evidence or MR-RATE skill outputs needed before execution. |

Recommended ablation matrix:

| Experiment | Change | Held constant | Expected signal | Metric | Decision rule |
| --- | --- | --- | --- | --- | --- |

## Collaborative Research Docs

The algorithm playbook lives at:

```text
skills/mrrate-clinical-ai-researcher/references/algorithm-development-playbook.md
```

The experiment checklist lives at:

```text
skills/mrrate-clinical-ai-researcher/references/experiment-design-checklist.md
```

The MR-RATE contrastive research map lives at:

```text
skills/mrrate-clinical-ai-researcher/references/mrrate-contrastive-research-map.md
```

These files are living research documents. They may be edited by clinical AI
researchers, ML engineers, clinicians, statisticians, and data engineers as
experiments evolve.

When editing:

- Put the most important design and evidence questions near the top.
- Preserve assumptions, unresolved questions, and negative results.
- Add concrete experiment artifacts rather than broad advice.
- Keep reproducibility details visible.
- Keep patient-care and clinical-validation claims out of the research docs.

## Keywords

MR-RATE, clinical AI researcher, algorithm design, medical imaging AI,
contrastive learning, representation learning, multimodal learning, MRI,
radiology reports, VJEPA2, BiomedVLP, fusion modes, ablation study, baseline,
experiment design, zero-shot pathology, AUROC, reproducibility.

## Search Terms

MR-RATE algorithm design, MR-RATE clinical AI researcher, MR-RATE contrastive
research, MR-RATE ablation plan, MR-RATE model experiment design, MR-RATE
VJEPA2 research, multimodal MRI report learning, medical imaging AI algorithm
review, MR-RATE baseline comparison, MR-RATE failure analysis.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE clinical AI researcher" --json
python -m skillforge info mrrate-clinical-ai-researcher --json
python -m skillforge evaluate mrrate-clinical-ai-researcher --json
```

This skill does not wrap MR-RATE source scripts. It is an algorithm research
design skill that reads plans, configs, summaries, and results and writes
research artifacts when requested. Use `mrrate-contrastive-pretraining` and
`mrrate-contrastive-inference` for source-grounded training and inference
commands.

Important source context:

- `contrastive-pretraining/README.md`
- `contrastive-pretraining/scripts/run_train.py`
- `contrastive-pretraining/scripts/inference.py`
- `contrastive-pretraining/scripts/eval.py`
- `contrastive-pretraining/scripts/data.py`
- `contrastive-pretraining/mr_rate/mr_rate/mr_rate.py`
- `contrastive-pretraining/vision_encoder/`

## How To Call From An LLM

Direct prompt:

```text
Use mrrate-clinical-ai-researcher to design a new MR-RATE algorithm experiment.
```

Task-based prompt:

```text
Use mrrate-clinical-ai-researcher to review this proposed contrastive MRI-report algorithm. Produce a model/data contract, baselines, ablations, evaluation plan, and reproducibility checklist.
```

Guarded prompt:

```text
Use mrrate-clinical-ai-researcher, but only use aggregate experiment summaries and do not inspect raw reports, local image paths, or patient-level identifiers.
```

Results-analysis prompt:

```text
Use mrrate-clinical-ai-researcher to interpret these MR-RATE ablation results and recommend the next algorithmic experiment.
```

## Help And Getting Started

Start with the algorithm idea and the artifacts already available:

```text
Use mrrate-clinical-ai-researcher to design an MR-RATE experiment. The idea is <algorithm idea>, the input data are <image/report/label artifacts>, the current baseline is <baseline>, and the research claim is <claim>.
```

Helpful inputs include:

- Research hypothesis.
- Anatomy and disease target.
- Image-space choice and modality/sequence assumptions.
- Report text source and label source.
- Encoder, fusion, pooling, objective, prompt, or model-change proposal.
- Baseline results, ablation results, or prior inference metrics.
- Compute, runtime, and reproducibility constraints.

If you do not have those artifacts yet, ask for an experiment-readiness review:

```text
Use mrrate-clinical-ai-researcher to tell me what evidence we need before this algorithm idea is ready to run.
```

Ask for clarification when:

- the algorithmic contribution is not distinguishable from a baseline
- the supervision signal is unclear
- the proposed evaluation does not test the claim
- ablations cannot isolate the new idea
- source artifacts or data contracts are missing
- compute budget or checkpoint policy is not stated

## How To Call From The CLI

Search for the skill:

```text
python -m skillforge search "MR-RATE algorithm design" --json
```

Show skill metadata:

```text
python -m skillforge info mrrate-clinical-ai-researcher --json
```

Install the skill into Codex:

```text
python -m skillforge install mrrate-clinical-ai-researcher --scope global
```

Evaluate the skill before publishing changes:

```text
python -m skillforge evaluate mrrate-clinical-ai-researcher --json
```

## Inputs And Outputs

Inputs can include:

- Clinical AI research goal or algorithm hypothesis.
- Anatomy, disease target, cohort, and intended research claim.
- MR-RATE data layout, image space, reports JSONL, labels CSV, splits CSV, or
  preprocessing summary.
- Model proposal: encoder, fusion mode, pooling strategy, objective, loss,
  prompts, supervised head, or representation-learning method.
- Training plan, inference plan, baseline results, ablation results, logs,
  metrics, or failure-analysis summaries.

Outputs can include:

- Algorithm research brief.
- Model/data contract.
- Baseline and ablation plan.
- Evaluation and failure-analysis plan.
- Reproducibility checklist.
- Research risk register.
- Recommended next MR-RATE skill follow-up.
- Markdown research artifact when the user asks for a written deliverable.

Output locations:

- Chat response by default.
- A user-specified Markdown, CSV, issue, or runbook artifact when requested.

## Limitations

Known limitations:

- This skill does not replace clinical, statistical, IRB, privacy, regulatory,
  or safety review.
- It does not run training, inference, model downloads, W&B logging, or SLURM
  jobs by default.
- It does not guarantee that an algorithm will work or that a result is
  publishable.
- It does not prove that labels, prompts, model scores, or learned
  representations are clinically valid.
- It depends on the quality of the provided experiment evidence.

Choose another skill when:

- You need clinical-statistical dataset and workflow review:
  `mrrate-medical-workflow-reviewer`.
- You need existing MR-RATE training command mechanics:
  `mrrate-contrastive-pretraining`.
- You need existing MR-RATE inference or AUROC command mechanics:
  `mrrate-contrastive-inference`.
- You need dataset download or local layout checks:
  `mrrate-dataset-access`.
- You need report-derived pathology label mechanics:
  `mrrate-report-pathology-labeling`.

## Examples

Beginner example:

```text
Use mrrate-clinical-ai-researcher to explain how to turn an MR-RATE model idea into a testable experiment.
```

Task-specific example:

```text
Use mrrate-clinical-ai-researcher to design an experiment comparing late fusion, late_attn simple attention, and text-guided cross attention for MR-RATE contrastive pretraining.
```

Safety-aware example:

```text
Use mrrate-clinical-ai-researcher to review this ablation table. Use only aggregate metrics and configs; do not inspect raw reports or image paths.
```

Troubleshooting example:

```text
Our new MR-RATE fusion method improves average AUROC but worsens rare labels. Use mrrate-clinical-ai-researcher to propose failure analyses and the next ablations.
```

## Trust And Safety

Risk level:
Medium

Permissions:

- Reads MR-RATE source documentation, model plans, configs, aggregate
  experiment summaries, metrics, and non-sensitive logs.
- May request additional summaries or artifacts needed for algorithm research
  review.
- May write Markdown algorithm briefs, ablation matrices, experiment plans, and
  reproducibility notes when the user asks.
- Requires explicit approval before inspecting raw reports, patient-level data,
  local image paths, PHI-sensitive artifacts, private checkpoints, or
  credential-bearing logs.

Data handling:
Treat reports, image paths, study IDs, patient IDs, labels, derived artifacts,
checkpoints, predictions, logs, and metrics as sensitive research artifacts.
Prefer aggregate and de-identified review artifacts.

Writes vs read-only:
Read-only by default. Writes only user-requested research artifacts.

External services:
None required for algorithm design. Related MR-RATE workflows may involve
Hugging Face, torch hub, W&B, SLURM, GPUs, or local model runtimes when the user
separately approves those operations.

Credentials:
No credentials are needed for research design. Dataset, model, W&B, or cluster
credentials belong to the relevant technical workflows.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Useful feedback includes:

- Missing algorithm-design questions.
- Weak ablation or baseline guidance.
- Better research-output templates.
- Additional MR-RATE source surfaces that should appear in the research map.
- Safer wording for research-only clinical AI algorithm work.

## Contributing

Contributions are welcome by pull request. The most likely files to edit are:

- `skills/mrrate-clinical-ai-researcher/SKILL.md`
- `skills/mrrate-clinical-ai-researcher/README.md`
- `skills/mrrate-clinical-ai-researcher/references/algorithm-development-playbook.md`
- `skills/mrrate-clinical-ai-researcher/references/experiment-design-checklist.md`
- `skills/mrrate-clinical-ai-researcher/references/mrrate-contrastive-research-map.md`

Before opening a pull request:

- Preserve the research-only and no-patient-care safety boundary.
- Keep algorithm guidance evidence-based and reproducible.
- Run `python -m skillforge build-catalog`.
- Run `python -m skillforge evaluate mrrate-clinical-ai-researcher --json`.

## Author

medatasci

Maintainer status:
Draft MR-RATE skill-family member for review.

## Citations

- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- MR-RATE dataset: https://huggingface.co/datasets/Forithmus/MR-RATE
- VJEPA2: https://huggingface.co/facebook/vjepa2-vitg-fpc64-384
- BiomedVLP-CXR-BERT-specialized: https://huggingface.co/microsoft/BiomedVLP-CXR-BERT-specialized
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/

## Related Skills

- `mrrate-medical-workflow-reviewer`: clinical-statistical dataset, label,
  cohort, workflow, and evaluation review.
- `mrrate-contrastive-pretraining`: source-grounded training command planning.
- `mrrate-contrastive-inference`: source-grounded inference and AUROC planning.
- `mrrate-dataset-access`: dataset repositories, metadata, reports, labels,
  splits, and local layout.
- `mrrate-report-pathology-labeling`: pathology label generation and merging.
- `mrrate-registration-derivatives`: coreg and atlas derivatives.
- `mrrate-repository-guide`: whole-repo orientation and family routing.
