# Clinical Statistical Expert

Skill ID: `clinical-statistical-expert`

Clinical Statistical Expert helps connect disease-specific clinical and imaging
knowledge with statistical research design. It is for questions where clinical
meaning, radiology language, cohort labels, endpoints, uncertainty, and claims
all need to line up.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/clinical-statistical-expert

Parent package:
SkillForge

Parent package repo URL:
https://github.com/medatasci/agent_skills

Distribution or marketplace:
Agent Skills Marketplace / SkillForge catalog

Version or release channel:
main

## Parent Collection

Parent collection:
SkillForge clinical research and medical imaging skills

Collection URL:
https://github.com/medatasci/agent_skills

Categories:
Healthcare, Clinical Research, Medical Imaging, Statistical Review

Collection context:
This skill is part of the SkillForge effort to make reusable Codex workflows
discoverable by humans and agents. It pairs well with imaging and repo-derived
skills such as `radiological-report-to-roi`, `nv-segment-ctmr`, and
`codebase-to-agentic-skills`.

## What This Skill Does

Clinical Statistical Expert helps an agent reason about disease-specific
clinical context and statistical consequences at the same time. It can help
describe how a known diagnosis or finding appears on imaging, identify
similar-appearing mimics, write radiology-report-style examples, and translate
uncertainty into cohort, endpoint, covariate, adjudication, bias, and claims
implications.

The first packaged disease reference is a brain MRI chapter for gliosis.

## Why You Would Call It

Call this skill when:

- You know the diagnosis or finding and want to understand what to look for on
  diagnostic imaging.
- You want to distinguish a disease or imaging finding from similar-appearing
  conditions.
- You need to turn clinical or report language into research labels, endpoints,
  covariates, or claims.
- You want to create or review a source-grounded disease chapter.

Use it to:

- Review imaging appearance and report language.
- Identify missing clinical, imaging, timing, or adjudication information.
- Reduce cohort-definition, endpoint, and misclassification risk.
- Build disease chapters that future agents can load efficiently.

Do not use it when:

- You need final clinical diagnosis, treatment guidance, triage, or emergency
  decisions.
- You want broad claims built from narrow or unsupported sources.

## Keywords

clinical research, statistics, medical imaging, radiology, MRI, brain disease,
gliosis, cohort definition, endpoints, imaging biomarkers, differential
diagnosis, mimic-aware review, report language, adjudication, misclassification,
study design, clinical claims

## Search Terms

- clinical statistical expert
- help me design a clinical imaging study
- what should I look for on MRI for this diagnosis
- how would gliosis be described in a radiology report
- compare this imaging finding with similar diseases
- map radiology report language to cohort labels
- create a disease chapter with authoritative sources
- review endpoint and misclassification risk

## How It Works

The skill keeps the main agent contract small and loads disease-specific
knowledge only when needed. For disease questions, it routes to
`references/disease-index.md`, then to the relevant disease chapter.

For disease chapter development, the workflow uses deterministic helpers:

1. Record source evidence with `source-archive`.
2. Record image evidence with `figure-evidence`.
3. Write or update the disease chapter from the packaged templates in
   `references/templates/`.
4. Review the chapter against weakness criteria.
5. Render an HTML preview with `disease-preview`.
6. Check disease chapter template conformance with `disease-template-check`.
7. Evaluate the packaged skill before publication.

The template map in `references/templates/README.md` shows which template
creates each disease chapter artifact.

For disease-chapter source discovery, start with
`references/templates/disease-research-plan.md.tmpl`. Its Expert-Framed Source
Discovery Questions section includes reusable one-shot patterns for clinical,
imaging, and statistical evidence searches.

## API And Options

Search for the skill:

```text
python -m skillforge search "clinical statistical expert" --json
```

Install the skill:

```text
python -m skillforge install clinical-statistical-expert
```

Render the gliosis chapter preview:

```text
python -m skillforge disease-preview gliosis --json
```

Check disease chapter template conformance:

```text
python -m skillforge disease-template-check gliosis --json
```

Generate source-discovery prompt and query variants:

```text
python -m skillforge evidence-query-pack gliosis --modality MRI --json
```

Record a source for a disease chapter:

```text
python -m skillforge source-archive gliosis --source-id <id> --title "<title>" --url <url> --source-type "<type>" --claim-breadth "<broad/narrow/scope>" --section "<section>" --download --json
```

Record figure evidence:

```text
python -m skillforge figure-evidence gliosis --figure-id <id> --source-title "<title>" --source-url <url> --figure-label "<figure>" --license "<license>" --reuse-status link-only --clinical-point "<point>" --section "<section>" --json
```

Evaluate publication readiness:

```text
python -m skillforge evaluate clinical-statistical-expert --json
```

## Inputs And Outputs

Inputs can include:

- disease name, diagnosis, finding, or report phrase
- imaging modality, anatomy, disease stage, treatment history, and report text
- cohort definition, endpoint, covariate, adjudication, or claims-review
  context
- source URLs and image candidates for disease chapter creation

Outputs can include:

- imaging feature checklist
- mimic-aware comparison
- Findings-style and Impression-style report-language examples
- missing-information questions
- clinical-statistical implications for cohorts, endpoints, covariates, bias,
  sensitivity analysis, and claims
- disease chapter updates, source and figure manifests, review artifacts, and
  HTML previews

## Examples

```text
Clinical Statistical Expert, for gliosis on brain MRI, what should I look for and how would it be described in a radiology report?
```

```text
Given a cohort labeled "chronic gliosis", what misclassification risks should I consider?
```

```text
Create a disease chapter for multiple sclerosis using authoritative imaging sources and figure evidence.
```

```text
Render the gliosis disease chapter preview and show me remaining evidence gaps.
```

## Help And Getting Started

Start with a disease or research question. If you have imaging modality,
anatomic location, stage, treatment history, or report text, include it.

Good starting prompts:

- "What should I look for on MRI for gliosis?"
- "How is chronic gliosis different from a low-grade glioma mimic?"
- "What does this report phrase imply for cohort definition?"
- "What sources and figures support this disease chapter?"

## How To Call From An LLM

```text
Use the clinical-statistical-expert skill. Load the disease index, then the gliosis chapter. Help me understand MRI appearance, mimic-aware differential considerations, report-language patterns, and statistical implications for a research cohort.
```

## How To Call From The CLI

```text
python -m skillforge disease-preview gliosis --json
python -m skillforge evaluate clinical-statistical-expert --json
```

## Trust And Safety

Risk level:
medium

Permissions:
The skill may read local disease chapters, local evidence manifests, and
user-provided research context. It may write draft disease chapters, manifests,
review artifacts, and local HTML previews when the user asks for development
work.

Data handling:
Do not process private clinical data unless the user confirms it is approved
for local use. Do not commit source pages or image assets unless reuse terms
explicitly allow it.

Writes vs read-only:
Normal question answering is read-only. Disease chapter development can write
local Markdown, JSON, image assets, and HTML previews.

## Limitations

- The current packaged disease reference covers gliosis first; other disease
  chapters are planned but should not be treated as implemented.
- The gliosis chapter is evidence-backed but still developing. It has met the
  50 image-candidate target, but the link-only figures still need qualitative
  review before figure evidence should be called mature.
- The skill supports clinical research reasoning and claims review. It does not
  provide final clinical diagnosis, treatment guidance, triage, or emergency
  decision support.
- Narrow sources should only support narrow claims.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

## Contributing

Contributions should be made through pull requests to the SkillForge repo. For
disease chapters, include the updated disease Markdown, source manifest, figure
manifest, review artifact, and generated preview when relevant.

Before opening a pull request, run:

```text
python -m skillforge disease-preview <disease> --json
python -m skillforge disease-template-check <disease> --json
python -m skillforge build-catalog --json
python -m skillforge evaluate clinical-statistical-expert --json
```

## Author

medatasci

## Citations

Disease-specific citations live in `references/diseases/<disease>.md` and the
corresponding source manifest. The gliosis chapter currently uses NCBI
Bookshelf/Springer, ACR, Radiology Assistant, and broad PMC review sources.

## Related Skills

- `codebase-to-agentic-skills`
- `skill-discovery-evaluation`
- `radiological-report-to-roi`
- `nv-segment-ctmr`

## Additional Information

The disease chapter workflow is intentionally evidence-heavy. Mature imaging
chapters should document approximately 100 pages or equivalent domain-specific
source material, review at least 50 image candidates when images are central,
and preserve uncertainty when the source base is narrow.
