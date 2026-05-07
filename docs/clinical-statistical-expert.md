# Clinical Statistical Expert Requirements

Status: Draft

## Purpose

`clinical-statistical-expert` is a proposed SkillForge skill for clinical
research reasoning at the intersection of disease-specific clinical knowledge
and statistical design. The skill should help users translate a clinical
question into a statistically coherent research plan, review cohort and endpoint
definitions, identify bias and misclassification risks, and explain statistical
choices in clinically meaningful language.

The skill is for research, study design, cohort definition, claims review, and
analysis planning. It must not diagnose patients, recommend treatment, triage
clinical urgency, replace board-certified clinical review, or replace a
qualified biostatistician for regulated or patient-impacting work.

## Brain Disease Profile

The first specialization should be a brain-disease profile. The parent skill is
`clinical-statistical-expert`; the brain-disease profile is implemented as
progressively loaded disease and method references rather than as one giant
context file.

The main skill should include only routing, safety boundaries, and the clinical
statistical reasoning workflow. Disease-specific knowledge should live in
separate Markdown files under a disease reference directory.

Recommended structure:

```text
skills/clinical-statistical-expert/
  SKILL.md
  README.md
  references/
    disease-index.md
    statistical-method-index.md
    clinical-statistical-workflow.md
    diseases/
      gliosis.md
      glioma.md
      ischemic-stroke.md
      multiple-sclerosis.md
      epilepsy.md
      brain-metastases.md
    statistical-methods/
      survival-analysis.md
      longitudinal-models.md
      diagnostic-performance.md
      prediction-models.md
      imaging-biomarkers.md
      missing-data.md
      multiplicity.md
      causal-inference.md
```

## Disease Chapter Requirements

Each disease chapter must support known-diagnosis clinical characterization.
At the top of the chapter, include a goals section that states the disease
chapter is designed to help a clinical-statistical reviewer:

1. Given a known diagnosis or suspected disease context, describe how the
   disease commonly presents on diagnostic imaging, especially MRI when MRI is
   the primary modality, using clinically realistic radiology-report language.
2. When reviewing diagnostic images or radiology reports, identify the imaging
   features, locations, structural patterns, report phrases, and clinical
   context that support or argue against this disease relative to
   similar-appearing conditions.
3. Translate disease appearance, report language, disease course, and
   diagnostic uncertainty into research-design and statistical implications,
   including cohort definition, endpoint selection, covariates, adjudication,
   misclassification risk, and claims language.

When the diagnosis is provided, the disease chapter should help the agent answer:

- What should a clinically trained reviewer look for on diagnostic images?
- What is the typical and atypical appearance?
- How does the appearance vary by modality, disease stage, location, treatment
  history, and structural pattern?
- How does the practical "what to look for" checklist change across acute,
  subacute, chronic/stable, progressive/recurrent/worsening, and
  improving/resolving presentations?
- What do key sequence findings look like visually and structurally, rather
  than only as shorthand labels such as T2/FLAIR hyperintensity or T1
  hypointensity?
- How would those findings usually be described in the Findings section of a
  radiology report?
- How would they usually be synthesized in the Impression?
- Which similar-presentation diseases or mimics should remain in mind?
- What features help distinguish this diagnosis from mimics?
- What missing information would change interpretation?
- How do these findings affect cohort definition, endpoint selection,
  covariate selection, subgrouping, sensitivity analysis, and claims?

Each disease chapter should include:

- goals
- figure evidence and image reuse status
- disease name, aliases, and scope
- clinical context
- known-diagnosis review framing
- what to look for, grouped by longitudinal presentation when clinically
  relevant
- modality-specific appearance, with MRI prioritized when relevant
- locations and structural appearance
- typical versus atypical findings
- differential diagnosis and mimics, including a quick guide, imaging
  discriminators, matrix, report-language cues, and context prompts
- disease-stage, treatment, or timing considerations
- natural history and clinical course
- treatment, response, and outcome context
- evidence of active disease, progression, or recurrence
- stable or chronic residual findings
- improvement, treatment response, or resolution
- serial imaging assessment and interval change
- clinical and imaging endpoints
- common covariates and confounders, separated into clinical, imaging,
  treatment/temporal, acquisition/protocol, and research-design implications
- statistical implications
- missing information to ask for
- safety boundaries and claim limits
- authoritative sources and citations
- related disease and statistical method files

The What To Look For section should be clinically usable, not merely a list of
sequence labels. For MRI-first diseases, it should explain what T1, T2, FLAIR,
DWI/ADC, SWI/GRE, contrast, perfusion, spectroscopy, or other findings look like
on the image, including visible morphology such as rim, patch, band, tract,
mass-like region, cavitary margin, diffuse abnormality, volume loss,
enhancement pattern, diffusion abnormality, susceptibility, edema, mass effect,
or atrophy. When longitudinal presentation matters, group the practical review
features by acute or early presentation, subacute or evolving presentation,
chronic or stable residual presentation, progressive/recurrent/worsening
presentation, and improving/resolving/treatment-response presentation.

For source discovery, use the Expert-Framed Source Discovery Questions section
in `skillforge/templates/clinical-statistical-expert/disease-research-plan.md.tmpl`
so disease-specific plans inherit the same source-search pattern.

Agents can generate the same prompt and query pack deterministically:

```text
python -m skillforge evidence-query-pack gliosis --modality MRI --json
```

Disease chapters should also include report-language patterns for major
appearances. These examples should distinguish Findings-style descriptive
language from Impression-style synthesis. Findings-style examples should
capture what is seen: anatomy, laterality, distribution, sequence appearance,
morphology, associated positive and negative findings, and interval change.
Impression-style examples should capture what the finding likely means:
diagnosis or favored interpretation, acuity/chronicity, stability/progression,
uncertainty, mimic concern, and source-supported follow-up, comparison, or
adjudication language. Report uncertainty phrases such as "nonspecific",
"favored", "compatible with", "may represent", "cannot exclude", "stable",
"new", and "progressive" should be mapped to cohort-label confidence,
adjudication, exclusion, sensitivity analysis, or endpoint implications when
relevant.

## Differential Diagnosis And Mimic Requirements

Disease chapters should include an easy-to-find `## Differential Diagnosis And
Mimics` section. This section is the main place for questions such as "what
else could this be?", "what features support the target diagnosis or finding?",
and "what additional context would make a mimic more likely?"

Use the following structure:

- `### Quick Differential Diagnosis Guide`
- `### Key Imaging Discriminators`
- `### Differential Diagnosis Matrix`
- `### Similar-Presentation Diseases And Mimic-Aware Comparison`
- `### Report Language That Supports Or Argues Against Each Diagnosis`
- `### When Additional Imaging Or Clinical Context Helps`

The differential matrix should include comparator, why it can look similar,
features supporting the target diagnosis or finding, features arguing against
it, helpful sequences or context, example report language, and statistical or
cohort implication.

## Treatment, Response, And Outcome Requirements

Disease chapters should include `## Treatment, Response, And Outcome Context`
when treatment history, guideline-supported management, response criteria,
progression criteria, or expected outcomes affect imaging interpretation,
disease-course framing, endpoint selection, covariate design, or statistical
claims. This section should stay at research-context level and should not be
written as patient-specific treatment instructions.

Use the following structure:

- `### Guideline-Based Management Context`
- `### Common Treatment Pathways`
- `### Imaging Appearance After Treatment`
- `### Evidence Of Treatment Response`
- `### Evidence Of Progression, Recurrence, Or Treatment Failure`
- `### Expected Outcomes And Prognostic Factors`
- `### Statistical Implications Of Treatment And Progression`

The section should capture:

- Guideline sources: society or organization, guideline title, publication year
  or version, jurisdiction or population, evidence level or recommendation
  strength when available, and disease stage or subgroup covered.
- Treatment categories: surveillance, surgery, biopsy, procedures, radiation,
  systemic therapy, chemotherapy, targeted therapy, immunotherapy,
  disease-modifying therapy, rehabilitation, supportive care, recurrence,
  relapse, rescue, or salvage treatment.
- Progression criteria: disease-specific response or progression systems such
  as RANO, RECIST-like oncology criteria, relapse criteria, seizure-freedom
  outcomes, disability scales, functional outcome measures, biomarker response,
  or pathology-based response when relevant.
- Treatment effects on imaging: postsurgical change, radiation effect,
  pseudoprogression, radiation necrosis, edema, enhancement, scarring, gliosis,
  atrophy, volume loss, lesion resolution, new lesions, and treatment-related
  mimics.
- Outcome measures: survival, progression-free survival, recurrence risk,
  relapse rate, seizure freedom, disability progression, functional status,
  lesion burden, treatment response durability, and disease-specific endpoints.
- Statistical implications: confounding by indication, treatment switching,
  immortal time bias, lead-time bias, informative censoring, competing risks,
  treatment-era effects, endpoint ambiguity, progression-free survival
  definitions, adjudication requirements, and sensitivity analyses by treatment
  status, disease stage, or response status.

For findings or sequelae that are not usually treated directly, such as
gliosis, the section should describe treatment, response, and outcomes by
underlying cause rather than implying a standalone treatment guideline for the
finding itself.

## Covariates And Confounders Requirements

Disease chapters should include an easy-to-find `## Common Covariates And
Confounders` section because these variables often determine whether a cohort,
endpoint, subgroup, or model adjustment is credible.

Use the following structure:

- `### Clinical Covariates`
- `### Imaging Covariates`
- `### Treatment And Temporal Confounders`
- `### Acquisition And Protocol Confounders`
- `### Research Design Implications`

The section should connect variables to practical analytic decisions: adjust
for them, stratify by them, use them as eligibility or exclusion criteria,
route them to adjudication, include them in sensitivity analysis, or limit
claims language when they are missing.

## Figure Evidence Requirements

Disease chapters should use image evidence when representative imaging figures
would make the clinical characterization more useful. Figure evidence should be
captured as a source-grounded artifact, not as a loose screenshot.

Store images locally only when reuse is explicitly allowed. If reuse is not
allowed, uncertain, or limited to source-site viewing, link to the external
source instead of downloading or committing the image.

Use this reuse model:

- `ok-to-embed`: store the image locally and embed it with attribution.
- `link-only`: do not store the image locally; cite and link to the source
  figure.
- `needs-review`: do not store the image locally until reuse terms are reviewed.
- `private-review`: keep any local copy out of the public repository.

Each figure should record:

- figure ID
- disease
- source title and URL
- figure number, label, or source-local reference
- figure URL when different from source URL
- license and reuse status
- local path when stored
- clinical point supported by the figure
- disease chapter sections supported by the figure
- attribution text
- date accessed
- notes or reuse limitations

The figure-evidence template and schema live at:

```text
skillforge/templates/clinical-statistical-expert/disease-figure-evidence.md.tmpl
skillforge/templates/clinical-statistical-expert/disease.figures.schema.json
```

The deterministic helper is:

```text
python -m skillforge figure-evidence <disease> --figure-id <id> --source-title "<title>" --source-url <url> --figure-label "Figure 31" --license "<license>" --reuse-status ok-to-embed --image-path <file> --clinical-point "<clinical point>" --section "<Disease.md section>" --json
```

## Source Requirements

Disease chapters should be grounded in authoritative, relevant sources that fit
the scope of the claim. Use broad clinical sources for broad disease claims, and
use narrow primary studies only for narrow technical claims.

Broad disease claims include general clinical context, expected imaging
appearance, disease course, typical locations, structural patterns, and
mimic-aware comparison. Ground these in medical imaging textbooks,
textbook-style clinical references, clinical guidelines, professional criteria,
radiology training material, broad review articles, or broad consensus papers.
Useful places to look include:

1. Medical imaging textbooks or textbook-style chapters available on the web,
   such as NCBI Bookshelf chapters or open educational radiology texts.
2. Professional society guidance and appropriateness criteria, such as ACR,
   RSNA, ASNR, AAN, ILAE, NICE, or disease-specific society guidance.
3. Authoritative radiology training resources written for clinicians,
   radiologists, or trainees, such as Radiology Assistant, MRI Online/Medality,
   Radiopaedia reference articles with citations and revision history, or
   accredited professional education material.

Narrow claims include specific imaging biomarkers, radiomics results, pathology
correlations, segmentation methods, unusual subtypes, small cohorts, or
statistical-performance results. Ground these in the narrow source and label
the claim as narrow.

Do not infer general disease behavior from a scattered set of narrow papers.
When the available evidence is narrow, preserve that limitation in the chapter.
Patient-facing pages, SEO summaries, unsourced blog posts, and general consumer
explanations may help with vocabulary discovery, but they should not ground
clinical disease characterization, imaging appearance, mimic comparison, or
statistical guidance.

Each disease chapter should make it clear which sources support broad clinical
claims and which sources support narrow technical points. When sources disagree
or are incomplete, preserve the uncertainty instead of smoothing it away.

## Source Archive Requirements

Disease-page source handling must separate local reproducibility from public
repo artifacts. Full source pages, PDFs, article HTML, or training pages should
be cached locally only under an ignored path such as:

```text
.skillforge/source-cache/clinical-statistical-expert/<disease>/<date>/
```

Public artifacts should commit a source manifest instead of the full source
pages:

```text
docs/clinical-statistical-expert/diseases/<disease>.sources.json
skillforge/templates/clinical-statistical-expert/disease.sources.schema.json
```

Use the helper to record metadata and optionally download a local cache copy:

```text
python -m skillforge source-archive <disease> --source-id <id> --title "<title>" --url <url> --source-type "<type>" --claim-breadth "<broad/narrow/scope>" --section "<Disease.md section>" --download --json
```

Downloaded access-denial pages, client challenges, login pages, or incomplete
landing pages must not be treated as source evidence.

## Disease Preview Requirements

Disease chapters should have a human-reviewable HTML preview so clinical domain
experts can inspect the chapter, embedded figures, source counts, and evidence
gaps without reading raw Markdown and JSON manifests.

The deterministic helper is:

```text
python -m skillforge disease-preview <disease> --json
```

By default, the helper reads:

```text
docs/clinical-statistical-expert/diseases/<disease>.md
docs/clinical-statistical-expert/diseases/<disease>.sources.json
docs/clinical-statistical-expert/diseases/<disease>.figures.json
```

and writes:

```text
docs/clinical-statistical-expert/reports/<disease>.html
```

The preview should be static, local, and deterministic. It must not download
sources, process private clinical data, run clinical models, or change source
or figure manifests.

## Disease Template

The canonical draft template lives at:

```text
skillforge/templates/clinical-statistical-expert/disease.md.tmpl
```

Published clinical-statistical skills should also package the templates under:

```text
skills/clinical-statistical-expert/references/templates/
```

The packaged `references/templates/README.md` should explain which template or
schema creates each disease artifact, so the installed skill remains
self-describing for humans and agents.

Prototype disease chapters may live under:

```text
docs/clinical-statistical-expert/diseases/
```

until the skill package itself is created.

Disease chapter creation should use the search and review plan template:

```text
skillforge/templates/clinical-statistical-expert/disease-research-plan.md.tmpl
```

Disease chapter review should use the weakness checklist:

```text
skillforge/templates/clinical-statistical-expert/disease-review-criteria.md.tmpl
```

A disease chapter should not be considered mature until it has a documented
source review of roughly 100 pages or equivalent domain-specific material from
authoritative imaging textbooks, professional criteria, radiology training
resources, review articles, consensus papers, and narrow primary literature
where appropriate.

For imaging-heavy chapters, figure evidence should not be considered mature
until at least 50 image candidates have been reviewed. Locally store images only
when reuse terms clearly allow it; otherwise record link-only figure evidence
with source URL, figure label, reuse status, clinical point, and supported
chapter sections.

## Skill Package Requirements

The packaged skill should live at:

```text
skills/clinical-statistical-expert/
```

and include:

- `SKILL.md` as the concise agent behavior contract
- `README.md` as the human-facing home page
- `references/disease-index.md` for progressive disease routing
- `references/statistical-method-index.md` for progressive method routing
- `references/disease-chapter-workflow.md` for repeatable disease chapter
  creation and review
- `references/diseases/<disease>.md` for source-grounded disease chapters
- `references/templates/` for packaged disease templates and the template index
- source and figure manifests for published disease chapters
- local figure assets only when reuse terms explicitly allow embedding

Before publishing a disease chapter, run:

```text
python -m skillforge disease-template-check <disease> --json
python -m skillforge disease-preview <disease> --json
python -m skillforge evaluate clinical-statistical-expert --json
```

## Clinical Safety Requirements

The skill must:

- make patient-specific diagnostic or treatment decisions out of scope
- flag emergency, acute, or unstable clinical scenarios as requiring qualified
  clinical care rather than skill reasoning
- distinguish educational/research reasoning from clinical adjudication
- preserve uncertainty when imaging findings are nonspecific
- require source-grounded claims for disease appearance, modality support,
  endpoints, biomarkers, and safety boundaries
- identify when pathology, expert neuroradiology review, neurologic evaluation,
  EEG, PET/SPECT, laboratory testing, genomic testing, or longitudinal imaging
  may be the appropriate clinical reference standard for a specific question

## Statistical Requirements

The skill should connect disease characterization to statistical consequences:

- label uncertainty and misclassification
- adjudication requirements
- inter-reader variability
- imaging protocol heterogeneity
- missing clinical or imaging data
- confounding by age, vascular risk, treatment history, disease stage, scanner,
  site, and indication
- endpoint ambiguity
- multiplicity and subgroup analyses
- sensitivity analyses for uncertain or mimic-prone cases
- appropriate claim language for exploratory versus confirmatory analyses
