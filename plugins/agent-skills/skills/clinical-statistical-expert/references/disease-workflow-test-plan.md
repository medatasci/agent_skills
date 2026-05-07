# Disease Chapter Workflow Test Plan

Use this plan to test whether the `clinical-statistical-expert` disease
research workflow is reproducible and generalizable.

The central question is:

> Can the disease research plan template lead to high-quality disease chapters,
> rather than merely documenting chapters after they already exist?

## Validation Strategy

Test the workflow in two ways:

1. Backtest against the prototype gliosis chapter.
2. Prospectively build chapters for common gliosis differentials.

The gliosis backtest checks whether the template can produce a useful blinded
research plan. The prospective differential builds check reproducibility and
generalization.

## Backtest Blinding Rule

The gliosis backtest must start with a blinded research-plan draft. During that
drafting phase, the author or agent must not read or use the existing
`gliosis.md` chapter or derivative review artifacts.

Allowed during blinded drafting:

- the research-plan template
- the disease/finding name and user-supplied scope
- newly collected authoritative sources
- newly created source and figure evidence records

Not allowed during blinded drafting:

- `gliosis.md`
- `gliosis.review.md`
- `gliosis.source-review.md`
- `gliosis.build-retrospective.md`
- prior summaries of the current gliosis chapter

The blinded output should be saved as `gliosis.research-plan.blinded.md`.
Only after that file is frozen should a separate reviewer open `gliosis.md` and
write `gliosis.research-plan.backtest-comparison.md`.

## Test Artifacts

| Artifact | Purpose | Status |
| --- | --- | --- |
| `gliosis.build-retrospective.md` | Records what actually happened during the prototype build. | created |
| `gliosis.research-plan.backtest.md` | Defines the blinded backtest protocol and forbids use of the current gliosis chapter during plan drafting. | created |
| `gliosis.research-plan.blinded.md` | Blinded plan created from the template without access to the current gliosis chapter. | pending |
| `gliosis.research-plan.backtest-comparison.md` | Separate unblinded reviewer comparison after the blinded plan is frozen. | pending |
| `chronic-infarct-encephalomalacia.research-plan.md` | Starts the first prospective differential workflow. | created |
| `<disease>.sources.json` | Records structured source evidence for each prospective disease. | pending |
| `<disease>.figures.json` | Records structured figure evidence for each prospective disease. | pending |
| `<disease>.source-review.md` | Summarizes source review and evidence extraction. | pending |
| `<disease>.md` | Disease chapter generated from the plan and evidence. | pending |
| `<disease>.review.md` | Content reviewer output. | pending |
| `<disease>.html` | Human-readable preview. | pending |

## Candidate Differential Diseases

| Priority | Disease or finding | Why this tests the workflow |
| --- | --- | --- |
| 1 | Chronic infarct / encephalomalacia | Closest practical differential for chronic gliotic change; tests tissue loss, vascular context, chronicity, and report-language distinctions. |
| 2 | Chronic demyelinating plaque / multiple sclerosis | Tests inflammatory mimic handling, lesion distribution, dissemination concepts, and guideline-driven MRI interpretation. |
| 3 | Low-grade glioma | Tests mass-like mimic handling, growth, enhancement, perfusion, spectroscopy, and uncertainty language. |
| 4 | Radiation necrosis / treatment effect | Tests posttreatment context, recurrence versus treatment effect, response/progression criteria, and longitudinal imaging. |
| 5 | Hippocampal sclerosis / mesial temporal sclerosis | Tests a narrower disease where gliosis is part of the disease concept and epilepsy-protocol MRI matters. |

## Prospective Workflow

For each disease, follow the files in this order:

1. Create `<disease>.research-plan.md`.
2. Create `<disease>.sources.json`.
3. Create `<disease>.figures.json`.
4. Fill source and figure evidence records using the research plan.
5. Write `<disease>.source-review.md`.
6. Draft `<disease>.md` from the evidence.
7. Run the content reviewer into `<disease>.review.md`.
8. Render `<disease>.html`.
9. Compare the final chapter against the research plan and record whether the
   template caused the needed material to be created.

## Success Criteria

The workflow is successful when a prospective disease chapter:

- starts from a research plan rather than a freeform draft
- records authoritative sources before broad claims are written
- separates broad claims from narrow technical claims
- includes figure evidence with reuse status
- includes known-diagnosis review guidance
- includes report-language examples that distinguish Findings-style description
  from Impression-style synthesis
- includes a differential diagnosis matrix when mimics matter
- includes disease-course, treatment-response, and interval-change context when
  relevant
- includes clinical, imaging, treatment/temporal, acquisition/protocol, and
  research-design confounders
- translates disease knowledge into cohort, endpoint, adjudication,
  misclassification, and claims-language implications
- preserves uncertainty and source gaps
- receives a content reviewer rating that honestly marks mature, developing,
  or draft status

## Failure Signals

The workflow needs revision if:

- the disease chapter is mostly written before source evidence is recorded
- broad disease claims are supported only by narrow papers
- the chapter has polished prose but weak report-language extraction
- the chapter omits mimics or treats mimics as a generic list
- treatment or outcome context is missing when it affects interpretation
- covariates and confounders are vague or not actionable
- the content reviewer finds major gaps that the research plan should have
  anticipated
- the template coverage check marks many chapter sections as missing or partial

## Review Questions After Each Disease

- Which template sections produced useful content?
- Which template sections were ignored, confusing, or too broad?
- Which final chapter sections were not clearly prompted by the research plan?
- Did the workflow overfit to gliosis?
- Did the workflow help distinguish the disease from gliosis and other mimics?
- Did the workflow support both human review and agent use?
- What template changes should be made before the next disease?

## Recommended First Test

Start with chronic infarct / encephalomalacia because it is close enough to
gliosis to make differences visible, but distinct enough to test whether the
template can avoid collapsing related chronic injury concepts.
