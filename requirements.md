# SkillForge Requirements

Status: Draft
Date: 2026-05-02

## Goal

Build SkillForge: a GitHub-backed, static-generated skill catalog and Codex installer for personal skills and future NVIDIA-internal use. SkillForge helps humans and agents find and install public-safe skills for research and task execution.

## Scope

MVP supports both personal use and company-shaped workflows, but only public-safe content. No NVIDIA-internal data, secrets, private process knowledge, or privileged automation in v1.

The MVP public surface is the repository `README.md`. A static HTML catalog draft may be generated for evaluation, but the README remains the authoritative human-facing page until the site design is validated.

SkillForge must support Windows, macOS, and Linux for the Python CLI, local
catalog generation, skill install/remove, peer cache operations, and static site
generation.

## Primary Users

- Engineers
- General business professionals
- Agents acting on behalf of those users

## Clinical Statistical Expert

SkillForge should support a future `clinical-statistical-expert` skill for
clinical research reasoning at the intersection of disease-specific clinical
knowledge and statistical design. The skill should help with study design,
cohort definition, endpoint selection, statistical analysis plan review,
clinical claims review, missing-data and bias review, and disease-specific
interpretation of analysis choices.

The skill must use progressive disclosure for efficient memory and reasoning.
The main `SKILL.md` should contain routing logic, safety boundaries, and the
clinical-statistical workflow. Disease-specific knowledge should live in
separate Markdown files referenced from a disease index. Statistical method
knowledge should live in separate method files referenced from a method index.

For brain diseases, each disease page should support known-diagnosis disease
characterization. Given that a patient, subject, cohort, or report already has a
particular diagnosis or finding, the disease page should help a clinical
statistical reviewer understand what to look for, how the appearance differs
from diseases with similar presentation, and how those distinctions affect
cohort definition, endpoints, covariates, adjudication, sensitivity analysis,
and claims.

At the top of each disease page, include a goals section that states the chapter
is designed to help a clinical-statistical reviewer:

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

The canonical draft template for disease pages is:

```text
skillforge/templates/clinical-statistical-expert/disease.md.tmpl
```

The packaged `clinical-statistical-expert` skill must also carry a copy of the
clinical disease templates under:

```text
skills/clinical-statistical-expert/references/templates/
```

That folder must include a `README.md` template index that maps each template
or schema to the artifact it creates. This keeps the process discoverable to
human reviewers and calling agents after the skill is installed.

Prototype chapters may live under:

```text
docs/clinical-statistical-expert/diseases/
```

Each disease page should include goals, figure evidence and image reuse status,
common names and aliases, clinical context, known-diagnosis review framing, what
to look for on diagnostic imaging grouped by longitudinal presentation when
clinically relevant, primary imaging modality, other modalities and when they
matter, locations and structural appearance, typical and atypical
appearance, differential diagnosis and mimics, disease stage and treatment
effects, natural history and clinical course, treatment,
response, and outcome context, evidence of active disease, progression, or
recurrence, stable or chronic residual findings, improvement, treatment
response, or resolution, serial imaging assessment and interval change,
clinical endpoints, imaging and biomarker endpoints, common covariates and
confounders, statistical implications, missing information to ask for, safety
and claim boundaries, related disease files, related statistical method files,
and authoritative sources.

Disease pages should include an easy-to-find `## Differential Diagnosis And
Mimics` section. This should be the primary place for humans and agents to learn
what else could explain the imaging appearance, what features support the target
diagnosis or finding, what features argue against it, and what additional
clinical or imaging context would help. The section should include:

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

The What To Look For section must be practical for image review. It should not
only say that a finding is T2/FLAIR hyperintense, T1 hypointense, enhancing, or
diffusion restricting. It should describe what the finding looks like visually
and structurally, such as a rim, patch, band, tract, mass-like region, cavitary
margin, diffuse signal abnormality, volume-loss pattern, enhancement pattern,
diffusion abnormality, susceptibility pattern, edema, mass effect, atrophy, or
ex vacuo change. When time course changes interpretation, this section should
be organized by longitudinal presentation, such as acute or early,
subacute/evolving, chronic/stable residual, progressive/recurrent/worsening,
and improving/resolving/treatment-response presentation.

Disease pages should include report-language patterns for major appearances.
These examples must distinguish Findings-style descriptive language from
Impression-style synthesis. Findings-style examples should describe anatomy,
laterality, distribution, sequence-specific appearance, morphology, associated
features, relevant negatives, and interval change. Impression-style examples
should synthesize diagnosis or favored interpretation, acuity/chronicity,
stability/progression, uncertainty, mimic concern, and source-supported
follow-up, comparison, or adjudication language. Report uncertainty phrases,
such as "nonspecific", "favored", "compatible with", "may represent", "cannot
exclude", "stable", "new", and "progressive", should be mapped to cohort-label
confidence, adjudication, exclusion, sensitivity analysis, or endpoint
implications when relevant.

Disease pages should include a structured Treatment, Response, And Outcome
Context section when treatment history, guideline-supported management,
response criteria, progression criteria, or expected outcomes affect imaging
interpretation, disease-course framing, endpoint selection, covariate design,
or statistical claims. This section should stay at research-context level and
must not be written as patient-specific treatment instructions.

The section should use:

- `### Guideline-Based Management Context`
- `### Common Treatment Pathways`
- `### Imaging Appearance After Treatment`
- `### Evidence Of Treatment Response`
- `### Evidence Of Progression, Recurrence, Or Treatment Failure`
- `### Expected Outcomes And Prognostic Factors`
- `### Statistical Implications Of Treatment And Progression`

The section should capture guideline sources with society or organization,
guideline title, year or version, jurisdiction or population, evidence level or
recommendation strength when available, and disease subgroup covered. It should
capture common treatment categories, disease-specific progression or response
systems such as RANO, RECIST-like criteria, relapse criteria, seizure-freedom
outcomes, disability scales, or functional outcome measures when relevant,
posttreatment imaging effects and mimics, expected outcomes and prognostic
factors, and statistical issues such as confounding by indication, treatment
switching, immortal time bias, lead-time bias, informative censoring, competing
risks, treatment-era effects, endpoint ambiguity, progression-free survival
definitions, adjudication, and sensitivity analyses by treatment or response
status.

For findings or sequelae that are not usually treated directly, such as
gliosis, this section should describe treatment, response, and outcomes by
underlying cause rather than implying a standalone treatment guideline for the
finding itself.

The `## Common Covariates And Confounders` section should be easy to find and
should separate variables into:

- `### Clinical Covariates`
- `### Imaging Covariates`
- `### Treatment And Temporal Confounders`
- `### Acquisition And Protocol Confounders`
- `### Research Design Implications`

The section should connect variables to research actions: adjustment,
stratification, eligibility or exclusion, adjudication, sensitivity analysis,
or claim limitation.

Disease pages should include representative figure evidence when imaging
figures materially improve clinical interpretation. Images may be stored locally
only when reuse is explicitly allowed. If reuse is not allowed, uncertain, or
limited to source-site viewing, the disease page should link to the external
figure instead of downloading or committing the image. Each figure should have a
metadata record that captures figure ID, disease, source title and URL, figure
label, figure URL, license, reuse status, local path when stored, supported
sections, clinical point, attribution, date accessed, and notes. The canonical
figure evidence template and schema are:

```text
skillforge/templates/clinical-statistical-expert/disease-figure-evidence.md.tmpl
skillforge/templates/clinical-statistical-expert/disease.figures.schema.json
```

The `figure-evidence` helper should record figure metadata and copy local image
files only when `--reuse-status ok-to-embed` is provided. Other reuse statuses
must result in link-only or review-needed metadata without copying the image:

```text
python -m skillforge figure-evidence <disease> --figure-id <id> --source-title "<title>" --source-url <url> --figure-label "Figure 31" --license "<license>" --reuse-status ok-to-embed --image-path <file> --clinical-point "<clinical point>" --section "<Disease.md section>" --json
```

For multi-disease projects, SkillForge should provide a deterministic
`download-reusable-assets` helper that reviews figure manifests and downloads
only direct image references whose metadata already records explicit reusable
license text and a local-embedding reuse status such as `ok-to-embed`,
`local-embeddable-cc-by`, or `downloaded-explicit-license`:

```text
python -m skillforge download-reusable-assets --project-root docs/clinical-statistical-expert/mr-rate-disease-research --json
```

The helper must not scrape source pages, infer rights from vague license notes,
or download `link-only`, `needs-review`, or `private-review` evidence. It
should write a review report at `reports/download-reusable-assets.json`, update
eligible figure manifests with local path and checksum metadata, and refresh
the project asset gallery so reviewers can inspect actual downloaded files.

Disease-page sources should be authoritative, relevant, and matched to the
scope of the claim. Broad clinical claims, such as disease appearance, clinical
course, location patterns, and mimic-aware comparison, should be grounded in
broad clinical sources such as medical imaging textbooks, textbook-style
clinical references, clinical guidelines, professional criteria, radiology
training material, broad review articles, or broad consensus papers. Narrow
primary sources should be used only for narrow technical claims, such as a
specific imaging biomarker, radiomics method, pathology correlation, unusual
subtype, small cohort, segmentation method, or statistical-performance result.

Useful places to look for broad clinical and imaging sources include:

1. Medical imaging textbooks or textbook-style chapters available on the web,
   such as NCBI Bookshelf chapters or open educational radiology texts.
2. Professional society guidance and appropriateness criteria, such as ACR,
   RSNA, ASNR, AAN, ILAE, NICE, or disease-specific society guidance.
3. Authoritative radiology training resources written for clinicians,
   radiologists, or trainees, such as Radiology Assistant, MRI Online/Medality,
   Radiopaedia reference articles with citations and revision history, or
   accredited professional education material.

Disease pages must not infer general disease behavior from a scattered set of
narrow papers. When the available evidence is narrow, the chapter should label
the claim as narrow. Patient-facing health pages, SEO summaries, unsourced blog
posts, and general consumer explanations may help with vocabulary discovery,
but they must not ground clinical disease characterization, imaging appearance,
mimic comparison, or statistical guidance.

Disease-page source handling must distinguish a reproducibility cache from
public repo artifacts. SkillForge may keep a local source cache under an
ignored path such as:

```text
.skillforge/source-cache/clinical-statistical-expert/<disease>/<date>/
```

The local cache is for updating disease pages on the current machine. It is not
automatically publishable source content. Full source pages, PDFs, article
HTML, or training pages must not be committed unless redistribution is
explicitly permitted and recorded. Public repo artifacts should instead commit a
source manifest that records:

- source ID
- title
- URL
- source type
- claim breadth supported
- license or reuse status
- local cache path when cached
- cache status
- date accessed
- checksum when cached
- supported disease-page sections
- notes about access failures, client challenges, or link-only sources

Each disease page should link to its source manifest when one exists. The
manifest should make it easy for a future human or agent to refresh sources,
identify which cached files were actually useful, and avoid confusing
downloaded-but-unusable challenge pages with full source material.

The source manifest schema and deterministic helper are:

```text
skillforge/templates/clinical-statistical-expert/disease.sources.schema.json
python -m skillforge source-archive <disease> --source-id <id> --title "<title>" --url <url> --source-type "<type>" --claim-breadth "<broad/narrow/scope>" --section "<Disease.md section>" --download --json
```

The helper should write or update `docs/clinical-statistical-expert/diseases/<disease>.sources.json`,
download source material only into the ignored local cache when `--download` is
provided, compute checksums for cached files, and mark access-denial, login,
captcha, JavaScript challenge, or incomplete landing pages as not suitable for
evidence extraction.

Disease pages should have a deterministic static HTML preview for expert
review. The preview helper should read the disease Markdown chapter, source
manifest, and figure manifest, then write a local HTML report that summarizes
source counts, figure counts, local embeddable figures, and the rendered
chapter:

```text
python -m skillforge disease-preview <disease> --json
```

The default output should be:

```text
docs/clinical-statistical-expert/reports/<disease>.html
```

The helper must not download sources, process private clinical data, run
clinical models, or change source or figure manifests.

Disease-page creation should follow a search and review plan that defines the
scope, source selection strategy, source review log, evidence extraction matrix,
disease-course extraction questions, and statistical translation questions. The
canonical draft template is:

```text
skillforge/templates/clinical-statistical-expert/disease-research-plan.md.tmpl
```

The research plan template should include Expert-Framed Source Discovery
Questions so humans and agents can turn plain clinical questions into
role-and-task search prompts. SkillForge should expose the same pattern through
a deterministic, read-only CLI command:

```text
python -m skillforge evidence-query-pack <target-concept> --modality MRI --json
```

The command should emit basic and advanced prompts, search variants,
source-type suggestions, and capture notes without searching the web,
downloading sources, or writing files.

Disease-page review should use criteria that identify weak source quality,
clinical characterization, imaging coverage, location/structure description,
disease-course reasoning, mimic-aware comparison, statistical translation,
safety boundaries, and missing-information handling. The canonical draft
criteria template is:

```text
skillforge/templates/clinical-statistical-expert/disease-review-criteria.md.tmpl
```

A disease page should not be considered mature until it has a documented source
review of roughly 100 pages or equivalent domain-specific material from
authoritative, relevant sources, with broad clinical claims supported by broad
clinical sources and narrow technical claims clearly labeled as narrow.

A disease page with imaging content should also review at least 50 image
candidates before its figure evidence is considered mature. Image candidates
may be saved locally only when reuse terms clearly permit it; otherwise they
should be recorded as link-only evidence with source URL, figure label, reuse
status, and the chapter sections they support.

The packaged `clinical-statistical-expert` skill should include a concise
agent-facing `SKILL.md`, a human-facing `README.md`, progressive disease and
method indexes, a disease-chapter workflow reference, disease chapters under
`references/diseases/`, packaged disease-chapter templates under
`references/templates/`, source and figure manifests, and reusable figure
assets only when reuse terms explicitly allow embedding.

SkillForge should provide a deterministic disease template checker:

```text
python -m skillforge disease-template-check <disease> --json
python -m skillforge disease-template-check --json
```

The default checker should verify conceptual conformance to the disease chapter
template, source manifests, figure manifests, local figure paths, and supporting
artifacts without requiring exact heading names. A `--strict` mode may require
exact heading matches for template debugging.

## Format Decision

MVP supports Agent Skills / `SKILL.md` as the primary artifact.

Rationale: it is portable, Git-friendly, supported by Codex and Cursor-like ecosystems, and light enough for humans to review.

Design for later attachment of:

- Codex plugins
- MCP server configs
- NeMoClaw-specific packaging
- AGENTS.md or prompt packs

Do not make these first-class MVP artifacts unless needed by a real pilot skill.

## Repository Workflow

- GitHub is the source of truth.
- Anyone may propose a skill by PR.
- PRs should use the Python catalog tool to validate and upload skills.
- Approved catalog is generated from the default branch.
- Every skill must have an owner, description, source path, and last-updated date.
- The repository includes `peer-catalogs.json` with known peer skill libraries.

## Codebase-To-Agentic-Skills

SkillForge should support a project and SkillForge skill called
`codebase-to-agentic-skills`. It turns useful algorithm repositories into
reviewable Codex skill packages. It should be automated where possible and
directed by the workflow the user wants to support.

Codebase-to-agentic-skills should not blindly wrap repositories. It should
first create a **Skill Design Card** for human review. Existing internal paths
may continue to use `docs/readiness-cards/` for compatibility, but user-facing
documentation should prefer "Skill Design Card" over "Readiness Card". The card
should describe:

- workflow goal
- source repo or local path
- primary users
- input artifacts
- output artifacts
- execution surface
- dependencies
- GPU, Docker, Conda, network, and credential requirements
- license, model weight, and dataset terms
- risk level and safety boundaries
- deterministic adapter opportunities
- LLM decisions needed
- minimal smoke test
- blockers and recommendation

Canonical repo-to-skills workflow requirements:

1. Define the workflow goal and target users before inspecting the repo.
2. Build a source-context map, not just a file inventory. For every important
   source artifact, record what it provides and how it should influence skill
   design:
   - README and quick starts: intended use, setup path, example commands,
     supported workflows, advertised limits, and user-facing language.
   - Docs and tutorials: workflow variants, parameter meanings, edge cases,
     troubleshooting guidance, and domain vocabulary.
   - Scripts, CLIs, Python APIs, notebooks, and MONAI bundles: executable
     entrypoints, arguments, side effects, return artifacts, and adapter
     opportunities.
   - Configs, manifests, metadata, and label maps: modes, labels, defaults,
     schemas, supported modalities, model paths, and validation rules.
   - Examples, tests, sample data, and expected outputs: realistic input/output
     contracts and smoke-test fixtures.
   - Dependency files, Dockerfiles, Conda files, install scripts, and CI:
     runtime, OS, GPU, CUDA, Docker, package, and environment requirements.
   - Model cards, dataset cards, papers, standards, and benchmarks: intended
     use, model/data terms, method context, citations, limitations, and claims
     that may or may not be safe to repeat.
   - Licenses, release notes, issues, and security notes: permitted use,
     restricted use, version pinning, known bugs, and maintenance status.
3. Pin or record the source version: repo URL, source subdirectory, commit,
   tag, release, model card URL, license URL, and date inspected. If the source
   is not pinned, mark it as unpinned and explain the risk.
4. Create a candidate skill table informed by the source-context map. Each row
   must include the candidate skill name, what it does, why it is useful,
   source evidence links or paths, sample prompt call, proposed CLI contract,
   inputs, outputs, deterministic entrypoints, LLM context needed, safety and
   license notes, smoke-test source, and recommendation. The generated table
   should include compact per-candidate review summaries before the detailed
   comparison table so humans can triage candidates quickly while agents still
   have structured evidence fields.
5. For each candidate, create a Skill Design Card before generating skill files.
6. Decide whether the result should be one algorithm skill, several
   functional-block skills, a workflow skill, or a mixed package.
7. Separate LLM responsibilities from deterministic Python responsibilities:
   what the LLM may infer, what Python must verify, and what must never be
   guessed.
8. Define a runtime/deployment plan when source code must actually run.
9. Create `SKILL.md`, `README.md`, `references/`, and `scripts/` as needed.
10. Run publication quality gates that are informed by the source-context map.
    Gates must verify that skill behavior, examples, CLI commands, safety
    claims, citations, metadata, README copy, and catalog fields are supported
    by the mapped source context. Unsupported claims must be removed, marked as
    assumptions, or turned into open questions before publication.
11. Add smoke tests or explicit smoke-test skip reasons.
12. Run `python -m skillforge build-catalog --json`.
13. Run `python -m skillforge evaluate <skill-id> --json`.
14. Review gaps, generated files, sample search results, source provenance,
    safety notes, and unresolved questions.
15. Publish by PR with generated catalog/site/plugin files included.

Human-facing document naming should follow these conventions:

- **Skill Design Card:** Preferred public name for the evidence, design,
  safety, adapter, smoke-test, and gap review artifact.
- **Readiness Card:** Legacy/internal name for the same class of artifact; keep
  existing file paths stable until a deliberate migration is approved.
- **Requirements:** Binding product or implementation requirements, not the
  evidence-and-review card.
- **POR / Plan of Record:** Avoid in public SkillForge docs unless a team has
  formally committed to a plan.
- **Skill Family Roadmap:** Preferred name for future child-skill planning.
  Avoid "split roadmap" in user-facing copy because the user goal is managing a
  family of related skills, not splitting for its own sake.

`evaluate` should include warning-level repo-derived advisory checks before
they become hard publication gates. Advisory checks must not change the
publication `ok` result during early iteration, but they must be visible in JSON
and human output so contributors can see missing source evidence. The advisory
checks should cover Skill Design Card, source-context map, candidate skill table,
source version pin or explicit unpinned risk, runtime/deployment plan, smoke
test or skip reason, and authoritative-source/citation evidence.

Skill Design Cards should use `docs/templates/codebase-readiness-card.md` and
live under `docs/readiness-cards/` until paths are migrated. Current exemplar
cards include
`docs/readiness-cards/nv-segment-ctmr.md` and
`docs/readiness-cards/radiological-report-to-roi.md`.

Codebase-to-agentic-skills should produce, when appropriate:

- `skills/<skill-id>/SKILL.md`
- `skills/<skill-id>/README.md`
- references for source summary, data contract, safety/license, and execution
- deterministic adapter scripts
- an agent-facing Python CLI in `scripts/` for deterministic commands
- smoke test scaffolding
- search/discovery metadata
- generated catalog metadata after review

The common source-context scan workflow must also be reachable from the
top-level SkillForge CLI so users and agents do not need to know the skill
script path:

```text
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --json
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
python -m skillforge codebase-scaffold-adapter setup-plan --adapter-name <adapter-name> --output-dir skills/<skill-id> --json
python -m skillforge codebase-scaffold-adapter --from-scan-json docs/reports/<repo>-repo-to-skills/scan.json --candidate-id <candidate-id> --stub-type guarded-run --output-dir skills/<skill-id> --json
```

When a generated skill reads data, writes outputs, runs a model, extracts
measurements, validates artifacts, downloads resources, or performs any other
stateful operation, it should expose a Python CLI for agents. The preferred
shape is:

- `python scripts/<adapter>.py check --json`
- `python scripts/<adapter>.py schema --json`
- `python scripts/<adapter>.py <action> ... --json`
- `python scripts/<adapter>.py report-html ... --json` when the skill produces
  outputs that benefit from a human-readable audit report

The CLI must return stable JSON, document side effects, require explicit output
paths for writes, and include warnings, errors, suggested fixes, and provenance
where applicable.

HTML report commands must consume existing deterministic outputs rather than
changing analysis results. For 3D medical image data, the MVP should embed
representative 2D slice previews and document existing viewer options instead
of implementing a custom viewer.

For radiological report-to-ROI workflows, HTML reports should audit anatomy
mentioned in the impression and distinguish regions with available segmentation
masks from regions mentioned in the radiology report where no corresponding mask
exists in the selected segmentation.

HTML reports for deterministic workflows should include the Python commands
needed to reproduce the processing pipeline and regenerate the report.

The first exemplar is the Radiological Report to ROI. It uses an
MRI image volume and corresponding radiology report to select anatomy, call or
reuse NV-Segment-CTMR segmentation, extract an ROI, and return
evidence-grounded outputs. The design lives in
`docs/radiological-report-to-roi.md`.

The first reusable medical AI algorithm skill is `nv-segment-ctmr`. It provides
a planning-first agentic interface to NVIDIA-Medtech NV-Segment-CTMR for CT/MRI
segmentation workflows, including mode selection, label lookup, MONAI bundle
command planning, brain MRI preprocessing guidance, batch planning, output
verification, research-only safety boundaries, and guarded Python
execution. Its current Python adapter supports read-only `schema`, `check`,
`setup-plan`, `labels`, `plan`, `brain-plan`, `batch-plan`, and
`verify-output` commands, an agent-friendly `segment-test-mri` workflow command,
plus a guarded `run`, `brain-run`, and `batch-run` command set that requires
`--confirm-execution` and local prerequisites before writing outputs.
`segment-test-mri` must default to read-only verification of the accepted local
`22B7CXEZ6T` output and return a deterministic `segmentation_path`; model
execution may occur only with `--run-if-missing --confirm-execution`.
`setup-plan` must remain read-only and return planned
WSL2/Linux setup commands, side effects, and required approvals before any
source clone, environment creation, dependency install, or model download.
Automated tests should use small synthetic NIfTI fixtures; local realistic
smoke tests may use the previously provided `22B7CXEZ6T` MR-RATE image and
NV-Segment-CTMR segmentation files when available. The detailed requirements
and development plan live in `docs/nv-segment-ctmr-skill-requirements-and-plan.md`.
Lightweight CI may skip synthetic NIfTI output verification when optional
medical-imaging dependencies such as `nibabel` and `numpy` are not installed;
that skipped test must be reported explicitly rather than treated as a hidden
failure. Environments that claim full medical-imaging adapter readiness should
install those optional dependencies and run the skipped test.

The next reusable medical AI algorithm skill is `nv-generate-ctmr`. It provides
a planning-first agentic interface to NVIDIA-Medtech NV-Generate-CTMR for
research synthetic CT and MRI generation workflows, including model variant
selection, CT image/mask pair planning, MR and MR brain image-only planning,
setup guidance, configuration previews, source-compatible config writing,
output verification, and guarded execution. Its Python adapter supports
read-only `schema`, `check`,
`setup-plan`, `models`, `modalities`, `config-template`, `plan`, and
`verify-output` commands; `config-template --output-file` writes a preview
JSON; `config-template --config-dir` writes upstream-compatible config files;
and a guarded `run` command that requires
`--confirm-execution`, `--confirm-downloads`, a valid source checkout, model
license review, and local prerequisites before writing generated outputs.

`nv-generate-ctmr` should remain one umbrella algorithm-interface skill for the
MVP because the model variants share source, setup, dependencies, model
download behavior, safety boundaries, and provenance needs. Split it later only
when a candidate has a distinct user workflow, distinct deterministic adapter
surface, separate smoke-test evidence, and enough search demand to justify
another installable catalog skill. Future split candidates include CT paired
image/mask generation, MR brain generation, image-only generation,
synthetic-output evaluation, and training/fine-tuning.

Local WSL2 smoke-test work for `nv-generate-ctmr` should distinguish completed
preflight checks from runtime acceptance for each workflow. Completed preflight
may include WSL2 availability, CUDA visibility through `nvidia-smi`, pinned
source checkout, read-only adapter planning, generated config writing, and
guarded execution refusal. Runtime acceptance requires a working WSL Python
package environment, installed upstream dependencies, reviewed model terms,
approved model downloads, and a validated config suitable for the available
GPU. The first accepted runtime path is `rflow-ct` `ct-paired` with output size
`256,256,128`, spacing `1.5,1.5,2.0`, and verified generated image/label
NIfTI outputs on local WSL2. Other workflows such as MR brain, image-only,
evaluation, and training still require their own acceptance evidence. If a
workflow is missing evidence, record explicit skip reasons rather than implying
the model has been run.

When a local runtime smoke test changes what is known about a skill, SkillForge
should update the public requirements, Skill Design Card, source-context
reference, skill README, and tests as appropriate. The update should record the
runtime target, source commit, dependency state, selected model/workflow, exact
adapter command shape, generated config files, output file types, verification
result, observed GPU memory, remaining unaccepted workflows, and any adapter
bugs found during the test. Runtime setup artifacts are not publication
artifacts: virtual environments, model weights, downloaded datasets, Hugging
Face caches, generated NIfTI volumes, and local smoke-test outputs must not be
committed to the SkillForge repo. If a smoke test exposes an adapter bug, the
fix should include a deterministic regression test before publishing.

The general project design lives in
`docs/codebase-to-agentic-skills.md`.

Codebase-to-agentic-skills should be applied first to NVIDIA-Medtech and MONAI
codebases because those repositories contain medical-imaging algorithms,
models, MONAI bundle workflows, examples, and reusable inference patterns that
can become agentic skills.

For healthcare and medical-imaging repositories, the deterministic scanner
should produce both raw evidence and a usable review path:

- `healthcare_signals`: raw deterministic evidence candidates.
- `healthcare_signal_summary`: grouped counts, representative terms, and files
  to review.
- `healthcare_reading_plan`: prioritized review areas, source files, bounded
  evidence hints, review questions, related source-context artifacts, and claim
  boundaries that tell the LLM and human reviewer what to verify before
  proposing candidate skills.
- `candidate_skill_hypotheses`: provisional, scanner-generated candidate rows
  based on task/output signals, source-context artifacts, and healthcare reading
  plan evidence.
- `command_evidence`: source-grounded command candidates extracted from
  documented quick-start snippets, notebook code cells, and common Python CLI
  framework clues. Each item must include command text, source path, line
  number or notebook cell index, snippet, source type, nearest Markdown or
  notebook markdown heading when available, platform assumption, side-effect
  risk, side-effect notes, and whether source review is required.
- `command_evidence_summary`: grouped command side-effect triage. It must
  include total command count, review-required count, read-only inspection
  count, highest risk category, category counts, representative commands, and a
  caveat that categories are heuristic. It must also include adapter-policy
  counts, the highest adapter policy needed across detected commands, a
  candidate-level recommended adapter policy, the recommendation basis, and any
  repo-maintenance commands ignored for the candidate-level recommendation.
- command `execution_gate`: conservative execution recommendation derived from
  side-effect categories and healthcare context. Allowed values are
  `safe-to-inspect`, `needs-user-approval`, `needs-runtime-plan`,
  `needs-data-safety-review`, and `do-not-run-from-scanner`. Each gate must
  include reasons, required reviews, and a caveat that the gate is not approval
  to run the command.
- command and hypothesis `adapter_policy`: conservative adapter-design guidance
  derived from execution gates. Allowed adapter policies are `read-only-check`,
  `setup-plan`, `runtime-plan`, `guarded-run`, and
  `no-adapter-until-review`. Each policy must include allowed actions, blocked
  actions, required before-run reviews, source gate, and a caveat that the
  policy is not permission to execute source commands.
- hypothesis `source_coverage`: detected evidence breadth across README/docs,
  executable entrypoints, configs, examples, runtime, model/data, and
  license/safety artifacts.
- hypothesis `provisional_cli_draft`: review-only adapter-design hints derived
  from detected entrypoints, configs, runtime files, and command evidence. It
  should include status, entrypoint references, config references, runtime
  references, source command references, suggested review commands, side-effect
  notes, adapter policy summary, adapter-plan stubs, and a caveat that the
  commands are not validated run commands.
- hypothesis `adapter_plan_stubs`: scaffolded adapter design plans derived from
  adapter policies. Each stub must include adapter type, status, purpose,
  suggested commands, required inputs, expected outputs, guardrails, required
  reviews, confirmation requirement, source references, smoke-test stub, and a
  caveat that the stub is not implemented behavior.

These scanner outputs are triage aids. They must guide source review and
candidate-skill design, but they must not be treated as proof of modality
support, runtime readiness, license status, medical safety, or clinical use.
Healthcare signal extraction should retain multiple matching terms from the
same file. A README that mentions both segmentation and generation must not
collapse to only the first task term found.
The reading plan should connect each healthcare signal to nearby source-context
evidence, including README, docs, configs, runtime files, model/data references,
and license or security artifacts when those artifacts are detected.
Evidence hints should be short and line-aware when available. They are
navigation aids only and must not replace full source review.
Candidate skill hypotheses must be explicitly marked provisional and must not be
treated as publication recommendations until a human or LLM confirms source
evidence, runtime feasibility, safety boundaries, license constraints, examples,
and smoke-test paths.
Source coverage is an artifact-presence score. It must not be treated as
confidence, source truth, safety validation, or runtime acceptance.
Command evidence extraction is heuristic. It must not be treated as proof that
a command is current, complete, safe, portable, or source-supported beyond the
captured line/snippet.
Command side-effect categories must help reviewers separate read-only
inspection from installs, downloads, file writes, GPU/model execution, network
access, container runtime, environment management, shell scripts, and unknown
review-required commands.
Execution gates must turn those categories into a conservative next-review
recommendation. Healthcare-context commands that write files or run model/GPU
work should default to `needs-data-safety-review`. Install, download, or
network commands should require user approval. Unknown or shell-delegated
commands should default to `do-not-run-from-scanner`.
Adapter policies must turn execution gates into a conservative wrapper design
path. `safe-to-inspect` maps to `read-only-check`; install, download, or
network gates map to `setup-plan`; runtime gates map to `runtime-plan`;
healthcare data-safety gates map to `guarded-run`; unknown or shell-delegated
commands map to `no-adapter-until-review`. These policies help decide what
kind of SkillForge adapter to design, not whether a source command may run.
For candidate-level adapter recommendations, SkillForge must preserve the
conservative highest policy across all detected commands separately from the
workflow-command recommendation. Repo-maintenance-only evidence such as
pre-commit, lint, or formatting configuration may still be recorded as command
evidence and counted in the conservative policy, but it should not dominate the
candidate-level recommended adapter policy when workflow-specific command
evidence exists.
When a scan produces multiple candidate skill hypotheses, each hypothesis must
receive its own provisional CLI draft and candidate-level adapter
recommendation. The scanner should score command evidence against the
candidate's task terms, the matched workflow-goal terms, and source-section
context such as nearby Markdown headings or the most recent notebook markdown
heading before a code cell, then surface the most relevant commands first. For
example, a generation-oriented candidate should prefer commands from a
generation section over segmentation commands when both appear in the same
repository, while still preserving the other commands as review context.
Provisional CLI drafts are not proof that a command exists, is safe, is
cross-platform, or can be run in the user's environment. They must drive source
review and adapter planning, not autonomous execution. Suggested command lists
in provisional CLI drafts should prioritize workflow-scoped command evidence
over repo-maintenance command evidence, while still preserving ignored
maintenance evidence for reviewer context.
Candidate skill hypotheses must be ordered with the user workflow goal in mind
when task/output signals produce several plausible candidates. For example, if
a repository contains both segmentation-mask and synthetic-image generation
terms, and the workflow goal asks for generation, generation-oriented
hypotheses should appear before generic segmentation or mask hypotheses while
remaining marked provisional.
Candidate names should include the source project name when available so real
repo scans produce reviewable names such as `NV-Generate-CTMR synthetic medical
image workflow` instead of only generic names such as `Research synthetic
medical image workflow`. The generic task name should still be retained as
metadata for traceability.
Adapter-plan stubs must be treated as scaffolding for design and implementation
review. `read-only-check` and `setup-plan` stubs may be implemented before
runtime acceptance. `guarded-run` stubs must require an explicit confirmation
flag, an explicit output directory, provenance output, data-safety review when
healthcare context is present, and smoke tests that prove refusal behavior
before any source runtime is invoked.
The `codebase-scaffold-adapter` command must generate review-only Python
adapter skeletons from selected adapter-plan stubs. It must support both a
generic adapter-policy mode and a source-grounded mode that reads
`scan.json`, selects a `candidate_skill_hypotheses` entry by candidate id or
index, selects an `adapter_plan_stub` by stub type or index, and preserves the
selected source refs, required reviews, guardrails, and suggested commands in
the generated skeleton. Generated skeletons must support `schema`, `check`, and
`setup-plan`, must not include a runnable `run` command, must not install
dependencies, must not download assets, must not call the network, and must not
execute upstream code. The skeleton's setup plan must emit planned commands and
approvals as data only.
Selection failures must return structured JSON with `ok: false` and actionable
messages, including available candidate names when candidate selection fails and
available adapter-plan stub types when stub selection fails. Conflicting
adapter type inputs, such as a positional adapter type that disagrees with
`--stub-type`, must fail before writing files.
Source-version provenance should be captured for Git repositories. If Git
refuses a read-only provenance command because of safe-directory or dubious
ownership checks, the scanner may retry the single command with a per-command
`safe.directory=<repo>` override. It must not write global Git config, change
the source checkout, or treat the override as trust in the source code.
`source_version` must include commit, branch, origin remote URL,
dirty-worktree status, lookup status, and whether the safe-directory override
was used. Generated review artifacts and adapter scaffolds should preserve that
metadata so reviewers can tell which source state produced a candidate. At a
minimum, the source-context map, candidate skill table, Skill Design Card draft,
scan JSON, and scan-backed adapter scaffold metadata must show or preserve this
provenance.

Medical-imaging generated skills must default to conservative safety language:
research use only unless the source explicitly says otherwise; not for
diagnosis, treatment, triage, or clinical decision-making; respect dataset and
model terms; do not redistribute restricted data; report source provenance,
model, command, label mapping, and output files.

## Strategic Improvement Loop

SkillForge should support a recurring strategic improvement loop for improving
SkillForge itself, especially `skills/codebase-to-agentic-skills` and
healthcare-domain repo-derived skills from NVIDIA-Medtech and MONAI sources.

The loop should run through Codex automation, not through a self-waking skill.
The current target cadence is every 20 minutes. Because a run may still be
active when the next one starts, the loop must be concurrency-aware:

- Use unique run logs under `docs/improvement-loop/runs/`.
- Use an advisory active-run lock under `.skillforge/improvement-loop/`.
- Treat the lock as collision avoidance, not a permission or trust model.
- If another run is active, avoid editing shared files; prefer read-only
  research, a separate worktree, or stopping cleanly with a log.
- Use stale-lock handling so interrupted runs do not block future work forever.

The loop should choose or continue one focus per run. It should not thrash
across unrelated ideas. Strategic lanes are:

- researcher: source/web research, papers, examples, prior art, and evidence.
- planner: requirements, plans, backlog items, issue drafts, and review paths.
- builder: small reviewable code, docs, tests, adapters, or skill changes.
- hardener: tests, cross-platform behavior, failure modes, and maintainability.
- safety: healthcare, privacy, license, permissions, data handling, and side
  effects.
- brainstormer: new skill opportunities and triage, especially healthcare
  skills.

Every run must log:

- run ID, timestamp, branch, commit, dirty state, and selected focus
- sources reviewed, including healthcare repo URLs or local files
- commands run
- files changed
- tests and checks
- what went well
- what could be improved
- one next action

Default source priorities for healthcare-domain work:

- https://github.com/NVIDIA-Medtech
- https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR
- https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/tree/main
- https://github.com/project-monai/monai
- `docs/codebase-to-agentic-skills.md`
- `skills/codebase-to-agentic-skills/`

The deterministic CLI surface is:

```text
python -m skillforge improve-cycle --json
python -m skillforge improve-cycle --write-log --claim-run --json
python -m skillforge improve-cycle --lane researcher --write-log --claim-run --json
python -m skillforge improve-cycle --focus "<focus>" --write-log --claim-run --json
python -m skillforge improve-cycle --release-run <run-id> --json
```

Autonomous runs must not merge, push, publish, install large dependencies,
download model weights, use credentials, or run expensive GPU jobs without
explicit human approval. New skill development is allowed when it is the best
way to improve SkillForge or healthcare repo-to-skills workflows, but
repo-derived skills must still follow the source-context map and Skill Design
Card process.

## User Workflow

The public README must be grouped by the user workflow, not by internal project
structure:

1. Installing SkillForge, including a Codex prompt and direct `git clone` path.
2. Searching for a skill in SkillForge and known peer catalogs.
3. Installing a selected skill into Codex.
4. Browsing the SkillForge Skill List.
5. Sending feedback on a skill, Python helper, CLI command, documentation, or missing workflow.
6. Submitting improvements with Git.
7. Turning repositories, algorithms, or codebases into candidate agentic skills.
8. Uninstalling a skill.
9. Getting help when the user is unsure what to do next.
10. Checking whether SkillForge itself has upstream updates.
11. Seeing what changed after an update.
12. Controlling how much coaching or extra guidance SkillForge emits.
13. Running a recurring strategic improvement loop for SkillForge and
    healthcare repo-to-skills work.

Each major workflow should include a promptable Codex version. When a Python CLI
or Git command exists, the README should include the deterministic command too.

## Python Catalog Tool

MVP includes a fast Python package in the repo for catalog upload, download, evaluation support, search, and Codex install.

Supported operating systems:

- Windows
- macOS
- Linux

Cross-platform command requirements:

- Prefer `python -m skillforge ...` in documentation because it works with the
  active Python environment on Windows, macOS, and Linux.
- When install documentation needs shell setup, provide Windows PowerShell and
  macOS/Linux shell examples separately.
- Do not require Bash, PowerShell, or CMD-specific syntax for core CLI
  behavior. Shell-specific commands may appear only as documentation examples.
- Invoke subprocesses with argument lists and `shell=False`.
- Treat Git and optional tools such as `ffmpeg` as external dependencies that
  may be missing from PATH; report actionable errors instead of assuming a
  platform package manager.

Cross-platform filesystem requirements:

- Use `pathlib.Path` for local paths and avoid hard-coded path separators.
- Store catalog-relative paths with POSIX separators in JSON and generated
  HTML, even when running on Windows.
- Expand `~` for user-provided paths where users may reasonably provide home
  directory shorthand.
- Honor `CODEX_HOME` for the default global Codex install root when set.
- Honor `SKILLFORGE_CODEX_SKILLS_DIR` as the explicit test/user override for
  global skill installs.
- Use `.codex/skills` for project installs on all operating systems.
- Remove and replace directories with logic that handles Windows read-only file
  attributes and Python-version differences in `shutil.rmtree`.
- Avoid symlink-dependent install behavior in the MVP because symlink
  privileges differ on Windows and can surprise users on managed machines.
- Read and write text as UTF-8 with stable newlines for generated files.
- Use platform-aware parsing for `file://` URIs, including Windows drive-letter
  URIs and POSIX paths.
- Exclude transient platform and runtime artifacts, such as `__pycache__`,
  `*.pyc`, `.DS_Store`, and `Thumbs.db`, from skill checksums, catalog file
  lists, installs, downloads, imports, and peer-cache materialization.

Things that can be operating-system or platform specific:

- Path separators and drive letters, such as `C:\...` vs `/home/...`.
- Home directory discovery and environment variable syntax, such as
  `%USERPROFILE%`, `$HOME`, `CODEX_HOME`, and PowerShell `$env:...`.
- Shell quoting and line continuation rules across PowerShell, CMD, Bash, and
  Zsh.
- Executable file extensions and scripts, such as `.exe`, `.bat`, `.cmd`,
  `.ps1`, and `.sh`.
- File permissions, read-only attributes, executable bits, symlink privileges,
  and directory deletion behavior.
- Filesystem case sensitivity, reserved filenames, maximum path length, Unicode
  normalization, and newline conventions.
- Availability and location of external binaries such as `git`, `ffmpeg`, and
  platform package managers.
- Network, proxy, TLS certificate, and corporate endpoint policy differences.
- Browser behavior when opening static files directly from `file://` versus a
  hosted static site.
- PowerShell execution policy or enterprise endpoint controls that can affect
  shell startup scripts without changing Python behavior.

CLI style:

- `python -m skillforge validate <path>`
- `python -m skillforge evaluate <skill-id-or-path>`
- `python -m skillforge search "<task>"`
- `python -m skillforge peer-search "<task>"`
- `python -m skillforge corpus-search "<task>"`
- `python -m skillforge search-audit <skill-id>`
- `python -m skillforge create <skill-id>`
- `python -m skillforge install <skill-id>`
- `python -m skillforge install <skill-id> --peer <peer-id> --yes`
- `python -m skillforge peer-diagnostics --json`

Required commands:

- `validate`: run deterministic structural checks on a local skill before catalog upload
- `evaluate`: run deterministic publication-readiness checks; may wrap structural validation, catalog checks, search audit, and generated-file checks
- `upload`: add or update a skill in the GitHub-backed catalog structure
- `download`: fetch a skill from the catalog to a local cache or folder
- `search`: find skills by exact ID, keyword, task, domain, or peer catalog
- `peer-search`: search configured peer catalogs and cache source-attributed results
- `corpus-search`: search cached full provider catalog snapshots and show
  source-attributed results with installation or review next steps
- `search-audit`: deterministic search/SEO sub-check used by evaluation
- `create`: generate a new skill folder from templates and promptable metadata
- `info`: show metadata, files, source URL, and Codex install path
- `install-skillforge`: verify or repair the SkillForge Codex marketplace installation
- `install`: install a pinned local SkillForge skill or explicitly confirmed peer skill for Codex
- `import-peer`: import a peer skill into the local GitHub-backed SkillForge catalog
- `remove`: remove an installed Codex skill
- `list`: show locally installed Codex skills
- `feedback`: draft a GitHub issue for a skill, Python helper, CLI command, documentation area, or missing workflow
- `contribute`: draft a pull request package for a bug fix, feature, docs change, catalog update, or new skill contribution
- `cache list|refresh|clear`: inspect, refresh, and clear peer caches
- `peer-diagnostics`: inspect peer catalog metadata, adapters, duplicate IDs, cache freshness, and missing provenance
- `doctor`: check local Codex paths and installation health
- `welcome`: show a stable, novice-friendly introduction to SkillForge
- `help`: show human-readable and agent-readable help for workflows, commands, and uncertain user intents
- `getting-started`: show first-run next steps after SkillForge is installed
- `update-check`: compare the local SkillForge checkout to the configured upstream repo without changing files
- `update`: apply an explicitly confirmed fast-forward-only update for a clean local SkillForge checkout
- `whats-new`: summarize user-facing changes since the last installed or recorded SkillForge revision

Upload-time automated review:

- Validate `SKILL.md` frontmatter and folder naming
- Confirm required metadata exists
- Detect scripts, binaries, archives, large files, and unusual file types
- Scan for secrets and credentials
- Extract external URLs and network domains
- Flag write/delete/credential/network/tool-use instructions
- Verify referenced files exist
- Generate catalog metadata

Download/install-time automated review:

- Verify source URL and checksum
- Re-run structural validation before install
- Refuse malformed skills
- Warn on scripts, external URLs, suspicious instructions, or unsupported file types
- Avoid executing skill scripts during install
- Install by copying or symlinking into global or project-local Codex skill paths
- Produce JSON output for agents and readable output for humans

Peer cache and install behavior:

- Cache peer repositories and search results under `.skillforge/cache`.
- Cache search results with source catalog, repo URL, skill path, commit SHA, timestamp, and match score.
- Default peer search cache TTL is 24 hours.
- Peer selection must ignore generic prompt words such as "find", "skill", "task", and "install" so broad prompts do not scan every configured peer catalog.
- Cache fetched peer skill folders under `.skillforge/cache/peers/<peer-id>/<commit>/skills/<skill-id>/`.
- `install --peer` installs from the peer cache and must not modify `skills/`, `catalog/`, or other repo files.
- `install --peer` requires `--yes` after source catalog review.
- `import-peer` is the explicit command that vendors a peer skill into this repository and updates catalog files.
- Peer source metadata must include peer ID, source repo, source URL, source commit SHA, source skill path, fetched timestamp, checksum, and validation warnings.
- If the network is unavailable and a cache exists, SkillForge may use stale cache and must label the result as stale.
- Adding/importing one skill must not rewrite unrelated per-skill metadata.

Feedback behavior:

- Accept a generic feedback subject, not only a skill ID.
- Support subjects such as `project-retrospective`, `python:skillforge.search`, `cli:install`, and `docs:README install flow`.
- Produce a GitHub issue title, issue-template URL, feedback-screen fields, Markdown body, and JSON output.
- Keep feedback low-risk: drafting an issue is in scope; authenticated issue creation is optional/future work.
- Feedback is for reports, confusion, feature requests, missing workflows, or ideas when the user does not already have a local change to submit.

Pull request contribution behavior:

- Users who have a bug fix, feature, documentation change, catalog update, or
  new skill contribution should submit a pull request instead of pushing
  directly to `main`.
- `python -m skillforge contribute "<summary>"` must produce a read-only PR
  draft with title, branch name, base branch, PR body, manual compare URL,
  suggested commands, safety/privacy notes, checks, and a review checklist.
- Contribution drafting should track a contributor profile:
  `unknown`, `non-developer`, or `developer`.
- Contributor profile is a guidance and user-experience signal, not a
  permission model or trust claim.
- When the profile is `unknown`, SkillForge should ask or infer from context
  whether the user wants Codex to handle Git/PR mechanics step by step.
- `non-developer` guidance should emphasize promptable help, review before
  submitting, and avoiding direct Git commands unless the user understands the
  side effects.
- `developer` guidance may show normal Git commands but should still default to
  PR review instead of direct pushes to `main`.
- `contribute` must not run Git commands, push branches, create commits, or
  create authenticated GitHub pull requests.
- `contribute --json` must expose stable fields for calling agents:
  `intent`, `title`, `branch`, `base`, `contributor_profile`,
  `manual_pr_url`, `body`, `promptable_request`, `commands`,
  `direct_push_to_main`, `side_effects`, `next_steps`, `fields`, and
  `review_checklist`.
- `direct_push_to_main` must be false for normal contribution drafts.
- The PR body should distinguish the user problem, changed files, checks,
  generated catalog/static-site impact, and safety/privacy notes.
- If the user only has a report or idea, SkillForge should recommend
  `feedback` instead of `contribute`.

Skill creation command requirements:

- Add `python -m skillforge create <skill-id>` as the preferred authoring
  entrypoint for new local skills.
- `create` must generate both source files required for publication:
  - `skills/<skill-id>/SKILL.md`
  - `skills/<skill-id>/README.md`
- `create` must use repository templates, starting with:
  - `skillforge/templates/skill/README.md.tmpl`
  - `skillforge/templates/skill/SKILL.md.tmpl`
- `create` should accept low-friction flags for common metadata:
  - `--title`
  - `--description`
  - `--owner`
  - `--category`
  - `--tag`
  - `--risk-level`
  - `--force`
  - `--json`
- `create` should support non-interactive use first. Interactive prompting is
  optional and should not be required for agents or CI.
- Generated `SKILL.md` must include minimal valid frontmatter with `name` and
  `description` at the top so it remains portable as a Codex skill.
- `SKILL.md` is intentionally human-readable, but it is the agent-facing skill
  contract, not the public marketing home page. The file should read like a
  concise playbook a human reviewer can audit and an agent can follow.
- After frontmatter, generated `SKILL.md` must put a readable `#` H1 near the
  top, followed by early sections named `## What This Skill Does` and
  `## Safe Default Behavior`.
- The top of `SKILL.md` should explain purpose, default side-effect posture,
  permission expectations, and a small decision guide before broader metadata
  or implementation detail.
- Recommended SkillForge discovery fields should be written in a readable
  Markdown section named `## SkillForge Discovery Metadata` unless a peer or
  source format requires frontmatter. This keeps the human-readable agent
  instructions near the top while preserving catalog/search metadata.
- `SKILL.md` should stay concise. Prefer progressive disclosure: keep the core
  behavior contract in `SKILL.md`, put long background in `references/`, put
  deterministic code in `scripts/`, put reusable assets in `assets/`, and put
  public/SEO-oriented explanation in the skill `README.md`.
- Generated `README.md` must include the full skill home page structure:
  repo/package, parent collection, purpose, call reasons, keywords, search
  terms, method, API/options, inputs/outputs, examples, help, LLM/CLI calls,
  trust and safety, feedback, author, citations, and related skills.
- For research, medical, scientific, security, legal, financial, or other
  high-trust skills, generated `SKILL.md` and `README.md` must include
  authoritative upstream sources such as source repositories, official model or
  dataset cards, documentation, papers, standards, and license terms. Private
  user data and local task artifacts must not be used as public SEO copy.
- Generated files must contain obvious placeholders where information is
  unknown, and `evaluate` must fail or warn until unresolved placeholders are
  removed.
- `create` must not run generated skill code, install the skill, or modify peer
  catalogs.
- After `create`, the recommended next commands are:
  - `python -m skillforge build-catalog`
  - `python -m skillforge evaluate <skill-id> --json`
- Promptable flow: users should be able to ask Codex to create a SkillForge
  skill for a workflow, and Codex should use `create`, then fill in the source
  files based on the user's intent and existing templates.

Later checks:

- Trigger evals
- Task evals
- Dependency scanning
- Prompt-injection scan
- License/provenance checks
- Risk scoring and trust labels
- Agent compatibility smoke tests beyond Codex

## Skill Evaluation Workflow

Product language should use **evaluation** as the umbrella term. Structural
validation is only one deterministic part of evaluation.

SkillForge has two evaluation layers:

- Python-driven evaluation: deterministic, fast, repeatable, and suitable for
  CLI, CI, and PR checks.
- LLM-driven evaluation: semantic, editorial, user-centered, and suitable for
  improving discoverability, examples, trigger language, and human-facing copy.

Python-driven evaluation requirements:

- Parse `SKILL.md` frontmatter and body without executing skill code.
- Check required portable fields: `name` and `description`.
- Check SkillForge recommended discovery fields: `title`,
  `short_description`, `aliases`, `categories`, `tags`, `tasks`, `use_when`,
  `do_not_use_when`, `inputs`, `outputs`, and `examples`.
- Accept recommended discovery fields from either frontmatter or the
  `## SkillForge Discovery Metadata` Markdown section, with frontmatter taking
  precedence when both are present.
- Check folder naming, file inventory, referenced files, checksums, source
  provenance, and generated catalog metadata.
- Check template conformance for SkillForge-owned skills:
  - `SKILL.md` must follow the agent-facing contract shape from
    `skillforge/templates/skill/SKILL.md.tmpl`, including portable
    frontmatter, a Markdown H1, `## What This Skill Does`,
    `## Safe Default Behavior`, and a workflow or equivalent method section.
  - `README.md` must follow the human-facing home page shape from
    `skillforge/templates/skill/README.md.tmpl`, including repo/package,
    parent collection, purpose, call reasons, keywords, search terms, method,
    API/options, inputs/outputs, limitations, examples, help, LLM/CLI calls,
    trust and safety, feedback, contributing, author, citations, and related
    skills.
  - `evaluate` must report exact missing sections and suggested fixes in JSON
    and human-readable output.
- Scan for suspicious files, archives, binaries, secrets, destructive language,
  external URLs, credential references, and unusual network/tool needs.
- Generate or verify `catalog/skills/<skill-id>.json`,
  `catalog/skills.json`, `catalog/search-index.json`, and static `site/`
  pages.
- Run deterministic search checks using aliases, tags, tasks, examples, and
  `use_when` phrases.
- Produce human-readable output and stable `--json` output for agents and CI.
- Avoid rewriting skill content unless an explicit future `--fix` mode is
  requested.

LLM-driven evaluation requirements:

- Read the skill as a user and an agent would, then judge whether the skill is
  easy to find, evaluate, trust, install, and use.
- Infer likely human search queries, GitHub search terms, and agent task
  prompts that should find the skill.
- Suggest better `title`, `short_description`, `expanded_description`,
  aliases, categories, tags, tasks, `use_when`, `do_not_use_when`, inputs,
  outputs, examples, related skills, page title, and meta description.
- Detect vague, overbroad, misleading, duplicated, or keyword-stuffed language.
- Compare the skill against nearby catalog skills and flag possible overlap or
  confusion.
- Keep public-safe language and avoid adding NVIDIA-internal details to public
  skills.
- Update `SKILL.md` when the improvement is clear and low-risk, then invoke the
  Python catalog workflow to regenerate indexes and pages.
- Update the per-skill `README.md` when human-facing positioning, examples,
  related-skill context, or discovery copy should improve.
- Ask before changing the skill's actual behavior, permissions, risk posture,
  or source/provenance claims.

SkillForge SEO/discovery skill requirements:

- The repository must include a first-class SkillForge skill named
  `skill-discovery-evaluation`.
- The skill must be the LLM-driven side of publication evaluation for skills.
- The skill must focus on skill discoverability, not generic website SEO.
- The skill must improve `SKILL.md` as the source of truth for:
  - compact agent trigger description
  - human-readable title and short description
  - expanded explanation
  - aliases and natural-language search phrases
  - categories and tags
  - supported tasks
  - `use_when` and `do_not_use_when` trigger boundaries
  - inputs, outputs, examples, related skills, risk level, permissions,
    page title, and meta description
- The skill must improve `README.md` as the human-facing home page for:
  - what the skill is for
  - who should use it
  - common use cases
  - example prompts and CLI commands
  - collection or marketplace context
  - related skills
  - inputs, outputs, risk, permissions, and limits
  - feedback and contribution paths
  - natural-language search terms that help humans and agents understand the
    skill without keyword stuffing
- The skill must call deterministic SkillForge commands for evidence:
  - `python -m skillforge validate <skill-path> --json`
  - `python -m skillforge search-audit <skill-id> --json`
  - `python -m skillforge search "<query>" --json`
  - `python -m skillforge build-catalog --json`
  - `python -m skillforge evaluate <skill-id> --json`
- The skill must produce or update realistic should-trigger and
  should-not-trigger query sets for human review, even before automated trigger
  evals exist.
- The skill must ask before changing behavior, adding risky permissions, making
  unsupported trust claims, or importing/installing peer skills.

Promptable evaluation requirements:

- Users should be able to ask: "Evaluate this SkillForge skill for publication."
- Users should be able to ask: "Help make skill `<skill-id>` discoverable by
  humans and agents."
- Users should be able to ask: "Improve the search and SEO metadata for this
  skill."
- Codex should map those prompts to the LLM-driven evaluation workflow and call
  the deterministic Python commands as evidence.

Recommended publish-time sequence:

1. Author or import the skill.
2. Run deterministic structural validation.
3. Run LLM-driven discovery evaluation.
4. Update `SKILL.md` metadata and examples when needed.
5. Update `README.md` as the skill's human-facing home page.
6. Run `python -m skillforge build-catalog`.
7. Run `python -m skillforge evaluate <skill-id> --json`.
8. Submit a PR containing the skill, catalog metadata, search index, static
   pages, and evaluation summary.

Skill generation, creation, and publishing workflow:

1. Create or import `skills/<skill-id>/SKILL.md`.
2. Create or update `skills/<skill-id>/README.md` as the skill home page.
3. Keep skill behavior and reusable agent instructions in `SKILL.md`; keep
   public explanation, examples, collection context, related skills, and
   discovery copy in `README.md`.
4. Confirm `SKILL.md` starts with a readable agent contract: frontmatter, H1,
   what the skill does, safe default behavior, and enough workflow detail for a
   human reviewer to understand the skill before reading generated metadata.
5. If a future skill format uses `AGENTS.md`, keep the same rule: every
   `AGENTS.md` skill folder should have a sibling `README.md` home page.
6. Skill generation must produce both files before the catalog is rebuilt; a
   generated `SKILL.md` without a README home page is not publishable.
7. Ask Codex to use `skill-discovery-evaluation` before publishing.
8. Let the LLM improve only source content in `SKILL.md` and human-authored
   docs; let Python regenerate catalog JSON, search indexes, static pages, and
   checksums, the Codex plugin skill bundle, and `skill_list.md`.
9. Run `python -m skillforge build-catalog --json`.
10. Run `python -m skillforge evaluate <skill-id> --json`.
11. Review the evaluation report, sample search results, and generated file
   changes.
12. Submit the PR with generated files included and with any evaluation gaps
   either fixed or explained.

Per-skill README home page requirements:

- Each canonical skill folder under `skills/<skill-id>/` must include
  `README.md` beside `SKILL.md`.
- The README is a public, human-facing home page, not a developer scratchpad.
- The README should be useful when reached from GitHub search, web search,
  SkillForge generated pages, peer catalogs, or an agent browsing files.
- The README must explain what the skill is for, who it helps, when to use it,
  when not to use it, example prompts, CLI examples if available, inputs,
  outputs, limitations, risk and permissions, related skills, collection
  membership, feedback, and contribution paths.
- The README should use a consistent home-page structure:
  - skill name
  - skill repo URL
  - parent package name and URL, when relevant
  - parent collection name and URL, when relevant
  - what the skill does
  - why a human or agent would call it
  - keywords
  - search terms
  - how it works or method, when relevant
  - API and options
  - inputs and outputs
  - examples
  - help and getting started
  - how to call it from an LLM
  - how to call it from the CLI
  - trust and safety: risk level, permissions, data handling, and writes vs
    read-only behavior
  - feedback URL
  - author
  - citations for the method, when relevant
  - related skills
- The README should include natural language discovery terms, synonyms, and
  task phrases, but must avoid keyword stuffing or unsupported capability
  claims.
- The SkillForge pipeline should record `homepage_path`, include README text in
  the search index, include the README in checksums, and fail publication
  evaluation when the README is missing or too thin.
- `python -m skillforge build-catalog` must mirror each canonical
  `skills/<skill-id>/` folder into
  `plugins/agent-skills/skills/<skill-id>/` so the public Codex plugin tree
  contains the same skills listed in `plugins/agent-skills/skills/skill_list.md`.
- `plugins/agent-skills/skills/skill_list.md` should be generated from the
  catalog so it cannot list skills that are missing from the plugin bundle.
- The canonical README home page template should live at
  `skillforge/templates/skill/README.md.tmpl`.

## Discovery

Human discovery:

- Static website generated from GitHub
- Search by task, domain, owner, recency, and source catalog
- Skill pages show summary, install options, files, source link, and examples
- SEO-friendly public pages for skill categories, task pages, and individual skills
- Public README links to the SkillForge Skill List at `plugins/agent-skills/skills/skill_list.md`

Agent discovery:

- Generate `skills.json`
- Generate per-skill JSON metadata
- Generate `llms.txt`
- Consider `/.well-known/agent-skills/index.json`
- Keep descriptions short and trigger-oriented
- Expose exact skill IDs, task keywords, install commands, and federation links

Unknown-marketplace discovery:

- Use GitHub topics such as `agent-skills`, `skill-marketplace`, `codex-skills`, `cursor-skills`, and `nemoclaw-skills`
- Publish clear README metadata so GitHub search and agent web search can find the repository
- Submit or cross-link the catalog from existing skill directories and awesome lists
- Publish `llms.txt` and `.well-known/agent-skills/index.json` from the hosted site
- Publish the installer name and usage examples in repo docs, PyPI metadata if packaged later, and generated catalog pages
- Make "SkillForge" and "Agent Skills Marketplace" both searchable phrases in README metadata

## Skill Search And SEO Requirements

The SEO plan for SkillForge is called the **Skill Search And SEO Plan**.
Implementation should improve skill discoverability for humans, GitHub search,
generated web catalogs, local CLI search, peer-catalog search, and agents
reading structured metadata.

Primary discovery requirement:

- A skill must be easy to find, evaluate, trust, install, and use from metadata
  alone.

Discovery metadata model:

- MVP required fields remain `name` and `description` for portability.
- SkillForge must support these optional discovery fields in `SKILL.md`
  frontmatter, generated per-skill JSON, aggregate indexes, and static catalog
  pages:
  - `title`: human-readable display name
  - `short_description`: one-sentence catalog/card description
  - `expanded_description`: 3-6 sentence explanation of tasks, inputs, outputs, and constraints
  - `aliases`: common names, synonyms, and user search phrases
  - `categories`: controlled top-level groupings
  - `tags`: task, domain, object, and intent keywords
  - `tasks`: task phrases the skill supports
  - `use_when`: agent trigger guidance
  - `do_not_use_when`: exclusion and safety guidance
  - `inputs`: expected inputs
  - `outputs`: expected outputs
  - `examples`: prompt examples
  - `related_skills`: adjacent or complementary skills
  - `risk_level`: human-readable preliminary risk label
  - `permissions`: network, file, credential, write, delete, or external tool needs
  - `page_title`: generated website title override
  - `meta_description`: generated website/search snippet override

Search index requirements:

- Generate `catalog/search-index.json` for agent and human search.
- Index `name`, `title`, `description`, `short_description`,
  `expanded_description`, `aliases`, `categories`, `tags`, `tasks`,
  `use_when`, `do_not_use_when`, `inputs`, `outputs`, and `examples`.
- Preserve source catalog, owner, updated date, install commands, and checksum in
  search results.
- Boost exact skill ID, aliases, task phrases, and `use_when` matches above
  incidental body text matches.
- Ignore generic prompt terms such as "find", "install", "skill", "task", and
  "help" when selecting peer catalogs or ranking skills.
- Track zero-result searches and low-confidence searches as feedback candidates.

SEO/search file requirements:

- Update `skills/<skill-id>/SKILL.md` when the source skill needs better
  frontmatter, visible examples, aliases, trigger guidance, exclusions, inputs,
  outputs, or related-skill links.
- Update `schemas/skill.schema.json` to allow optional discovery fields for one
  skill.
- Update `schemas/skills.schema.json` to allow the aggregate catalog to expose
  discovery fields safely.
- Create or update `schemas/search-index.schema.json` when the search index
  structure changes.
- Update `catalog/skills/<skill-id>.json` when a skill's generated metadata
  changes.
- Update `catalog/skills.json` when aggregate skill summaries, tags,
  categories, descriptions, or install metadata change.
- Create and update `catalog/search-index.json` as the machine-readable
  search/SEO index for humans and agents.
- Update `plugins/agent-skills/skills/skill_list.md` when human-facing skill
  descriptions, categories, or prompt examples change.
- Update `README.md` when repository-level discovery, category links, install
  examples, or public positioning change.
- Update `docs/skill-search-seo-plan.md` when the SEO/search
  strategy changes.
- When static catalog generation is implemented, create or update
  `site/skills/<skill-id>/index.html`, `site/categories/<category>/index.html`,
  `site/search-index.json`, `site/llms.txt`, and
  `site/.well-known/agent-skills/index.json`.
- Generated files must be deterministic. A generated-files check should fail CI
  if `catalog/search-index.json`, per-skill metadata, or static pages are stale.
- CI should run unit tests, rebuild generated catalog/site/plugin surfaces,
  fail if generated files are not committed, and run publication evaluation for
  exemplar skills such as `nv-segment-ctmr`.

Validation and search-audit requirements:

- `validate` should continue to pass portable skills with only `name` and
  `description`.
- `validate` should warn when recommended discovery fields are missing from
  SkillForge-owned skills.
- `validate` should warn when a SkillForge-owned `SKILL.md` does not begin
  with a readable agent contract: a Markdown H1 after frontmatter, a
  `## What This Skill Does` section, and a `## Safe Default Behavior` section.
- `validate` should warn when `## SkillForge Discovery Metadata` appears before
  the first human-readable overview sections.
- `validate` should warn when a SkillForge-owned `SKILL.md` grows too long for
  progressive disclosure. The recommended soft limit is roughly 500 body lines;
  longer background should move into `references/`.
- `validate` should warn when a SkillForge-owned code-backed skill exposes
  guarded execution commands such as `--confirm-execution` but does not include
  runtime/deployment planning documentation.
- Runtime/deployment planning documentation for guarded code-backed skills
  should cover install location, OS/runtime target, dependency setup,
  model/data download policy, license review, environment checks, smoke-test
  data, and rollback/cleanup notes.
- `search-audit <skill-id>` should produce a human-readable report and `--json`
  output.
- `search-audit` should score:
  - human clarity
  - agent triggerability
  - alias and synonym coverage
  - task coverage
  - example prompt quality
  - inputs and outputs clarity
  - `do_not_use_when` and safety/permission clarity
  - source/provenance completeness
  - catalog/web metadata readiness
- `search-audit` should list the exact files that should be created or updated
  for each finding.
- `search-audit` should suggest concrete metadata additions without
  automatically changing skill files unless a future `--fix` flag is added.
- `evaluate <skill-id>` should include a `skill_md_agent_contract` check that
  reports whether the current `SKILL.md` follows the readable agent-contract
  shape used by the SkillForge template.

Generated page requirements:

- Generate one stable URL/page per skill using `skills/<skill-id>/`.
- Generate category pages for top-level categories.
- Each skill page must include:
  - skill name and short description
  - "Use this when"
  - "Do not use this when"
  - example Codex prompts
  - CLI install command
  - inputs and outputs
  - risk level and permissions
  - source/provenance
  - related skills
  - feedback link
- Each generated skill page should include JSON-LD using Schema.org
  `CreativeWork` for the skill and `SoftwareApplication` for SkillForge.
- Visible page content and JSON-LD must describe the same skill; do not add
  hidden structured data that is not represented in visible content.

Controlled vocabulary requirements:

- Initial categories:
  - Research
  - Media
  - Data
  - Documentation
  - Project Memory
  - Developer Tools
  - Business Workflows
  - AI/ML
  - Safety And Review
- Tags should be lower-case, stable, and hyphenated when multi-word.
- Aliases may preserve natural language spacing because they mirror search
  phrases.

GitHub discovery requirements:

- README must link to skill categories and individual skills once generated
  pages exist.
- Repository description and topics should include discoverable terms such as
  `SkillForge`, `agent-skills`, `codex-skills`, `skill-marketplace`, and
  `workflow-automation`.
- Per-skill `SKILL.md` files should include common synonyms and realistic
  prompt examples in visible text.
- Issue labels should distinguish `skill-feedback`, `skill-request`, `docs`,
  `catalog`, and `risk-review`.

## Supported Agent

MVP supports Codex only.

Later priority:

1. NeMoClaw
2. Cursor
3. Other Agent Skills-compatible clients

MVP should still use portable `SKILL.md` so later agents can be added without changing the skill format.

## Install Experience

Install must be low-burden and promptable:

- "Install skill abc from Agent Skills Marketplace"
- "Find and install a skill that will help with task X"
- Copyable install commands for humans
- Clear Codex support indicator
- Direct GitHub/source links
- "Use with Codex" path first
- Search and install are separate capabilities, even when exposed as one prompt
- Exact-name Codex install should be fast and non-interactive after validation passes
- Task-based install should search first, rank candidates, and install the best match only when confidence is high
- Ambiguous matches should ask before installing
- Install scope supports both global Codex skills and project-local skills

The install path must be usable by agents, not only humans. Agents should be able to call a deterministic installer instead of improvising copy/symlink logic.

Installer behavior:

- Installing SkillForge itself must be idempotent: if the marketplace is already
  installed, the tool should verify health instead of recloning or overwriting.
- `python -m skillforge install-skillforge --json` should inspect the resolved
  Codex home, marketplace checkout path, config path, repo identity, branch,
  commit, dirty state when Git metadata is available, plugin registration, and
  required marketplace files. The plugin manifest, skill list, and README are
  required for marketplace verification; the Python CLI file may be absent in
  plugin-only cache layouts and should be reported rather than treated as an
  overwrite-worthy conflict.
- Install status output must include source/version facts when available:
  source repository, configured ref, source type, Git branch, Git commit, dirty
  state, plugin name, plugin version, code version, last updated timestamp, and
  which source supplied the timestamp.
- `python -m skillforge install-skillforge --yes` may create or append missing
  non-conflicting Codex config entries only when the target path is already
  verified as a SkillForge checkout.
- Existing non-SkillForge folders at the marketplace path must be treated as
  conflicts and must not be overwritten.
- Existing Codex config entries with different source URLs, refs, disabled
  plugins, malformed TOML, or partial tables require manual review rather than
  blind rewriting.
- If the marketplace checkout is missing, SkillForge should return a clear clone
  command and next steps rather than silently failing.
- If SkillForge is already healthy, output should say so and suggest useful next
  commands such as `welcome`, `update-check`, or `update`.
- Reads generated marketplace indexes, not the website HTML
- Supports exact skill IDs and natural-language task search
- Supports `--scope global`, `--scope project`, `--project <path>`, `--yes`, `--pin`, `--json`, and `--catalog` options
- Verifies checksum and source URL before install
- Installs by copying or symlinking skill folders into the Codex skill path
- Avoids executing skill scripts during install
- Produces JSON output for agents and readable output for humans
- Is dependency-light and fast enough to run frequently

Later:

- Lockfile/pinning
- Enterprise allowlist
- Multi-agent install targets

## User Affordances

SkillForge should actively help users and calling agents understand what to do
next without turning the CLI into noisy marketing copy. The affordance model has
six parts:

1. Human and agent-friendly documentation.
2. A discoverable help system for uncertain users and calling LLMs.
3. First-run guidance after SkillForge is installed.
4. Periodic upstream update checks.
5. A "what changed" summary after update.
6. Configurable chattiness from coaching to silent.

Voice and behavior requirements:

- SkillForge should have an explicit, normal Codex-skill-compliant voice and
  behavior contract in `skills/skillforge/SKILL.md`.
- `skills/skillforge/SKILL.md` is the canonical agent-facing source for
  SkillForge's own behavior. Supporting docs may summarize it, but should not
  create a competing persona file.
- The short personality statement is: helpful, practical, novice-friendly,
  safety-aware, transparent about side effects, next-step aware, adjustable in
  chattiness, and deterministic enough for agents.
- "Novice-friendly" means low-assumption and recoverable, not always verbose.
  Experienced users and automation must be able to choose lower-noise output.
- Default human output should answer the immediate request, show the minimum
  context needed to trust the answer, surface important side effects, and offer
  one or two likely next steps when useful.
- `coach` mode may provide deeper teaching and more next-step guidance.
  `normal` should stay concise. `terse` and `silent` should reduce prose while
  preserving warnings, errors, and required confirmations.
- Next-step suggestions should be context-specific, such as inspecting a search
  result before install, opening a source URL for peer results, listing skills
  after install, checking updates after setup, or sending feedback when search
  results are weak.
- SkillForge must not invent trust claims, owners, citations, permissions, or
  behavior to sound helpful.

Documentation requirements:

- `README.md` remains the public human entry point and should explain workflows
  in the order users experience them.
- SkillForge must keep hardcoded onboarding affordances for first-time users in
  `skillforge/help.py`, starting with `welcome`. Hardcoded welcome/help text is
  intentional because novice users need a stable, low-assumption entrypoint
  before any LLM improvises.
- Hardcoded responses should be documented in `README.md`, `docs/python/help.md`,
  tests, and requirements whenever their purpose or behavior changes.
- `docs/` should contain deeper technical and architecture docs for Python
  modules, catalog schemas, install paths, peer federation, update behavior,
  and contribution workflows.
- Python module docs should use
  `skillforge/templates/python/module.md.tmpl` and live under `docs/python/`
  instead of creating one README beside every `.py` file.
- `skillforge/modules.toml` should provide a machine-readable map of Python
  module ownership, commands, reads, writes, network use, risk, tests, and docs.
- `site/llms.txt`, generated catalog JSON, and CLI `--json` output are
  agent-facing documentation surfaces, not afterthoughts.
- Each command that can be invoked by an agent should have stable JSON output,
  examples, exit-code behavior, and documented side effects.
- Documentation should distinguish what exists now from future/backlog features
  so agents do not hallucinate unsupported commands.

Help system requirements:

- `python -m skillforge welcome` should greet first-time users, explain
  SkillForge in plain language, show examples of natural prompts, and avoid
  installing or modifying anything.
- `python -m skillforge welcome --json` should expose the same welcome hints in
  a stable machine-readable shape.
- `python -m skillforge help` should show the core workflows: install, search,
  inspect, install a skill, list installed skills, send feedback, create/share a
  skill, prepare a pull request contribution, diagnose problems, update
  SkillForge, and tune output style.
- `python -m skillforge help <topic>` should support topics such as `search`,
  `install`, `peer-search`, `feedback`, `contribute`, `create`, `update`,
  `doctor`, and `chattiness`.
- `python -m skillforge help "natural language question"` may map common user
  intents to suggested commands without executing anything.
- `--json` help output must be easy for a calling LLM to parse and include
  command names, descriptions, example prompts, CLI examples, risk/side-effect
  notes, and related commands.
- Help should recommend `doctor` for environment/path confusion and `feedback`
  when the user cannot find an appropriate skill.

First-run guidance requirements:

- After a successful SkillForge installation or update, users should see a short
  getting-started message unless chattiness is `silent`.
- The message should include:
  - how to search for a skill by task
  - how to list installed skills
  - how to inspect a skill before install
  - how to ask for help
  - how to check for updates
- The guidance should be available on demand through
  `python -m skillforge getting-started`.
- The guidance must not imply that peer catalog results are trusted or installed
  without review.

Update-check requirements:

- SkillForge should check upstream Git status at a configurable cadence, with a
  default of no more than once every 6 hours per local checkout.
- Update checks should be opportunistic and low-risk: no background daemon, no
  surprise file changes, and no auto-update without explicit user confirmation.
- `python -m skillforge update-check --json` should report local commit,
  upstream commit, branch/ref, whether updates are available, last checked time,
  network or Git errors, and the suggested next command.
- `python -m skillforge update` without `--yes` should report status and the
  next safe command, but must not change files.
- `python -m skillforge update --yes` should run a fast-forward update only when
  the checkout is clean, the upstream branch is configured, and the local branch
  has not diverged. It must refuse before overwriting local changes.
- After a successful `update --yes`, SkillForge should summarize what changed
  since the previous local revision.
- Update behavior must respect restricted networks, corporate proxies, and
  offline operation by returning actionable errors and using cached last-known
  status when available.

What-changed requirements:

- After an update, SkillForge should summarize user-facing changes since the
  user's previous local revision.
- `python -m skillforge whats-new` should use Git history and release notes when
  available, then group changes into practical categories such as new skills,
  improved search, install/update behavior, documentation, peer catalogs, and
  breaking or risky changes.
- Default human output from `whats-new` should be feature-centric, not a commit
  dump. It should focus on what users can now do, what workflows changed, and
  major new capabilities such as search/SEO, install/update, onboarding/help,
  skill creation/publishing, peer catalogs, and new skills.
- Default human output should end by asking whether the user wants more detail.
- `whats-new --details` or `--technical` should include the technical category
  summary and commits. `whats-new --commits` should show commits without making
  commit lists the default experience.
- `whats-new --json` should include the previous commit, current commit,
  commits inspected, changed files, inferred categories, user-facing summary,
  technical summary, and detail prompt.
- The summary should be factual and derived from Git history; it should not
  invent feature claims from vague commit messages.

Chattiness requirements:

- SkillForge should support at least four output modes:
  - `coach`: extra context, next-step suggestions, and friendly explanations
  - `normal`: concise human-readable output with useful next steps
  - `terse`: minimal human output
  - `silent`: no extra prose beyond requested command output, warnings, errors,
    and machine-readable JSON
- Configuration sources should be deterministic and documented:
  - CLI flag such as `--chattiness coach|normal|terse|silent`
  - environment variable such as `SKILLFORGE_CHATTINESS`
  - future user config through `python -m skillforge config set chattiness <mode>`
- `--json` output must remain stable and machine-readable regardless of
  chattiness mode.
- Dangerous or ambiguous operations must still warn or require confirmation even
  in `silent` mode.

## Promptable Search And Install

Promptable install has two phases:

1. Resolve intent: translate "task X" into candidate skills using local index search plus optional federated search.
2. Execute install: install one selected skill with deterministic path, checksum, and validation checks.

The marketplace should support these agent-facing intents:

- Find skills for a task
- Explain why a skill matches a task
- Compare candidate skills
- Install an exact skill
- Install the best matching skill for a task
- Refuse malformed skills
- Search SkillForge and peer catalogs while preserving source catalog attribution

Implication: discovery metadata is product-critical. A skill with a vague description is effectively undiscoverable.

## Loose Federation

The marketplace should not assume one central catalog owns all skills.

MVP federation model:

- Each skill library publishes a static `skills.json`
- Each library may publish `.well-known/agent-skills/index.json`
- This repo keeps a simple `peer-catalogs.json` list of known peer catalogs
- The Python catalog tool can search the local catalog plus listed peer catalogs
- Search results preserve source, skill ID, version, and checksum
- A peer catalog entry is a discovery source, not a trust endorsement
- Peer entries may point to a static index or to a high-quality GitHub skill repository that needs an adapter

Federation requirements:

- Catalogs must be static, cacheable, and Git-backed
- Federation must be opt-in by source
- The peer catalog list controls which external catalogs are searched
- Duplicate skills are resolved by source, ID, version, and checksum
- The UI should show "source marketplace"
- MVP peer list should include known reliable sources from OpenAI, Anthropic, GitHub, Vercel, Microsoft, Sentry, Trail of Bits, Addy Osmani, Supabase, Cloudflare, WordPress, and the Agent Skills spec project
- Until federated CLI adapters are implemented, the README must clearly distinguish local CLI search from peer-aware Codex discovery.

Expanded peer catalog requirements:

- Peer catalog support should graduate from "source list plus cache" to a
  reliable federation layer for discovery.
- `peer-catalogs.json` entries should support:
  - peer ID
  - display name
  - publisher
  - kind or adapter type
  - source URL
  - repository URL when applicable
  - catalog URL when applicable
  - default enabled flag
  - reliability or maturity label
  - trust notes
  - freshness/TTL hint
  - supported skill formats
  - optional categories or domains
- SkillForge should support at least two peer adapter types:
  - static catalog adapter for `skills.json` or `.well-known/agent-skills/index.json`
  - GitHub skill repository adapter for repos with `skills/<skill-id>/SKILL.md`
- Peer search results must show source catalog, source repo, source commit or
  catalog timestamp, source path, checksum when available, cache status, and
  stale/fresh label.
- Local and peer search result JSON must include enough text to choose between
  skills: `summary`, `description`, `short_description`, and
  `expanded_description` when available. Human CLI output should label Source,
  Repo or Path, Score, Summary, and Description.
- Default human search output should be a Markdown table that is readable by a
  person and easy for an agent to parse. Table columns should include rank,
  skill name, what the skill helps with, comments extracted from `SKILL.md`, the
  CLI install command when one is available, and the source URL for manual
  review or install. Do not mix descriptive "helps with" content with install
  or review actions.
- Search-table comments must come from the skill body itself, not from peer
  catalog trust notes or runtime cache state. Prefer explicit `SKILL.md`
  comment/notes fields, then useful sections such as important rules,
  requirements, limitations, trust and safety, or do-not-use guidance.
- `corpus-search` should use cached provider catalog snapshots first, refresh
  only when the provider cache is expired or `--refresh` is supplied, and return
  source-attributed results with `installable`, `install_command`, and
  `next_step` fields in JSON.
- Peer search must rank local SkillForge results and peer results separately
  enough that users can tell what is local vs external.
- Peer search must never imply trust by default. Source catalogs are discovery
  sources, not endorsements.
- Peer install must continue to require explicit confirmation with `--yes` and
  must show peer source metadata before installation.
- Peer import must remain the only operation that vendors peer skill content
  into this repository.
- Cached peer content should be inspectable through CLI commands:
  - `python -m skillforge cache catalogs --json`
  - `python -m skillforge cache list --json`
  - `python -m skillforge cache refresh --peer <peer-id> --json`
  - `python -m skillforge cache clear --peer <peer-id> --yes`
- `cache catalogs` must fetch or build one full provider catalog snapshot per
  configured peer and write it as JSON under the SkillForge user cache:
  `catalogs/<peer-id>/catalog.json`.
- Static providers must preserve the raw provider JSON response as
  `catalogs/<peer-id>/raw.json`; GitHub skill repos must produce an equivalent
  normalized JSON snapshot from the cached repo contents.
- Provider catalog cache expiration defaults to 24 hours. A fresh provider
  catalog cache should be reused without network access; expired caches should
  be refreshed, and stale cached JSON may be used with explicit stale/error
  metadata if refresh fails.
- Provider catalog snapshots should include enough text for later semantic or
  LLM-assisted retrieval, including source catalog metadata, skill metadata,
  descriptions, available README text, available SKILL.md text, provenance,
  checksums, skipped parser records, and errors.
- Add a peer diagnostic command or mode that reports broken peer URLs,
  stale caches, adapter failures, duplicate IDs, and missing provenance.
- Peer search errors must be classified with stable machine-readable kinds,
  including `network_blocked`, `path_too_long`, `checkout_failed`,
  `parser_skipped`, `peer_error`, and `no_match` status for searched peers with
  no relevant skills.
- Peer search must search every default-enabled peer catalog unless the user
  passes `--peer <peer-id>`. It must not silently drop peers because the peer's
  catalog metadata does not match the query. Disabled peers should still appear
  in diagnostics/search status as `disabled` so users can understand why a peer
  catalog was not queried.
- Peer search must run peer catalog queries in parallel with bounded
  concurrency. The default and maximum concurrency is 15 peer workers. The CLI
  must expose `--jobs <n>` for lower limits, and `SKILLFORGE_PEER_JOBS` may set
  the default for scripted use. Result sorting and `peer_statuses` ordering must
  remain deterministic regardless of completion order.
- Peer Git fetches should minimize platform-specific path failures by using an
  OS-appropriate user cache by default, sparse checkout for GitHub peer repos,
  and platform-specific Git options only where needed, such as Windows
  `core.longpaths`.
- Peer parsing must tolerate common real-world `SKILL.md` frontmatter,
  including nested metadata mappings such as `metadata.author` and
  `metadata.version`, and folded or literal block scalars such as
  `description: >-`, without rejecting otherwise valid skills.
- Peer search should include small intent expansions for common discovery
  terms, such as mapping database-access language to SQL, Postgres, Supabase,
  schema, migration, CLI, and MCP terms.
- Static peer catalog adapters must support both object payloads such as
  `{ "skills": [...] }` and aggregator list payloads such as OpenSkills
  Agency's `skills-data.json`. Normalization must preserve useful provenance
  fields including `repo`, `url`, `tags`, `category`, `desc`, and `summary`.
- HTML-only marketplace home pages must not be configured as queryable static
  catalogs unless a matching adapter exists. Prefer documented JSON APIs such
  as SkillsMD's `/api/skills` endpoint or curated JSON indexes such as
  OpenSkills Agency's `skills-data.json`.
- The static catalog UI should be able to display peer catalogs and peer search
  results without making them look local.

## Pull Request Contribution Workflow

SkillForge must document a low-friction pull request path for skills, Python
helpers, CLI changes, documentation, catalog updates, and feedback fixes.
Direct pushes to `main` are a maintainer path, not the default user or
developer contribution path.

User intent routing:

- If a user finds a bug, confusion, missing workflow, or feature idea and does
  not have a fix, draft a GitHub issue with `feedback`.
- If a user has a bug fix, feature, documentation update, catalog update, or
  new skill package, draft a pull request with `contribute`.
- If the user is not a developer or is uncomfortable with Git, provide a
  promptable PR-prep path and explain each side effect before running branch,
  commit, push, or PR commands.
- If the user's comfort level is unknown, ask one short question before
  choosing between a Git-command-oriented path and a Codex-guided path.

Required PR preparation command pattern:

- `python -m skillforge contribute "<summary>" --type <bugfix|feature|docs|skill|catalog|improvement> --user-type <unknown|non-developer|developer> --json`
- `git checkout -b <branch-name>`
- `git add <changed-files>`
- `git commit -m "<clear change summary>"`
- `git push -u origin <branch-name>`
- Open a GitHub pull request from the branch to `main`.

The SkillForge CLI may display these Git commands but must not execute them in
`contribute`.

Skill PRs must update:

- `skills/<skill-name>/SKILL.md`
- `skills/<skill-name>/README.md`
- generated catalog, static site, and plugin mirror files produced by
  `python -m skillforge build-catalog`
- `plugins/agent-skills/.codex-plugin/plugin.json` when installed skill content changes

Skill PR review checklist items must include:

- Confirm `SKILL.md` follows `skillforge/templates/skill/SKILL.md.tmpl` for
  the agent-facing contract.
- Confirm `README.md` follows `skillforge/templates/skill/README.md.tmpl` for
  the human-facing skill home page.
- Confirm no `{{placeholder}}` values remain.
- Confirm `python -m skillforge build-catalog` was run after skill changes.
- Confirm `python -m skillforge evaluate <skill-id> --json` passes or clearly
  documents remaining advisory gaps.

PR descriptions should include:

- summary and why it helps users or agents
- changed files
- checks run and any remaining gaps
- safety/privacy notes, especially secrets, private data, writes, network use,
  and generated-file churn

Future enterprise mode:

- NVIDIA can run an internal federation node that indexes approved public-safe sources plus private internal catalogs
- Internal policy can override or hide public risk ratings
- Enterprise catalogs can require SSO, audit logs, and allowlisted sources

## Website Requirements

MVP is a static generated catalog.

Must have:

- Home/search page
- Skill detail page
- Codex compatibility indicator
- Install instructions
- Source links
- Generated machine-readable indexes
- Federation metadata page

No login, database, workflow engine, or runtime execution in MVP.

Static catalog search UI requirements:

- The generated `site/index.html` should be a usable catalog search interface,
  not only a static list.
- The UI must run as static files with no backend, login, database, or runtime
  skill execution.
- The UI should load `site/search-index.json` client-side and support:
  - keyword search
  - task search
  - category filtering
  - tag filtering
  - risk-level filtering
  - local vs peer source filtering when peer indexes are exposed
  - empty-state messaging with feedback prompt
- Search results should show:
  - skill title
  - short description
  - categories and tags
  - source catalog
  - risk level
  - install command
  - link to skill detail page
  - link to source `SKILL.md`
  - link to source `README.md`
- Skill detail pages should link back to search results/category pages and show
  human-facing README home page links.
- The UI should be readable on desktop and mobile, with no build step beyond
  `python -m skillforge build-catalog`.
- The UI should avoid heavy frontend frameworks for MVP unless plain static
  HTML/CSS/JS becomes difficult to maintain.
- `site/llms.txt`, `site/search-index.json`, and
  `site/.well-known/agent-skills/index.json` remain machine-readable surfaces
  and must stay consistent with the visible UI.
- Static generated files must be deterministic so CI can detect stale site
  output.

## Non-Goals

- No arbitrary public skill marketplace in v1
- No user-selected execution of untrusted skills
- No NVIDIA-internal knowledge in public-safe catalog
- No dynamic runtime sandbox in MVP
- No custom app backend unless static generation fails
- No central federation authority in MVP
- No formal trust/risk scoring in MVP
- No non-Codex installers in MVP

## White Paper Impact

If framed as an MVP, emphasize practical build sequence: GitHub repo, static catalog, checks, indexes, install flow.

If framed as NVIDIA reference architecture, add: governance, RBAC, enterprise GitHub, SSO, policy approvals, audit logs, private/internal catalogs, and controlled integration with NVIDIA agent platforms.

Design implication: build the MVP as a small public-safe reference implementation, but use metadata and lifecycle fields that can scale into the enterprise architecture.

The white paper should treat user affordances as architecture, not polish:
documentation, help, onboarding, update awareness, "what changed" summaries,
and configurable chattiness are the mechanisms that let humans and agents use a
federated skill catalog safely when they are uncertain.

The current white paper draft is `docs/skillforge-whitepaper.md`.

## Open Decisions

- Whether NeMoClaw needs first-class package metadata post-MVP
- Whether to keep personal and company-ready skills in one repo with labels, or separate repos later
- Whether to package the Python installer for `uvx` or `pipx`, or keep it repo-local first
- Which external catalogs should be included in the default federation allowlist
- Whether `help "natural language question"` should remain deterministic
  keyword routing or invoke an LLM when one is available.
- Whether update checks should stay explicitly requested or become
  opportunistic in selected low-risk commands when the cached update status is
  older than 6 hours.
- Whether chattiness should be stored in SkillForge user config, inherited from
  Codex preferences, or both.

## Backlog

- Formal trust model
- Formal risk definitions
- Dynamic/on-the-fly risk evaluation at install or use time
- Risk labels such as `low-risk`, `reviewed`, `deprecated`, and `blocked`
- Human review workflows
- NeMoClaw installer support
- Cursor installer support
- Multi-agent compatibility badges
- Enterprise allowlists, audit logs, SSO, and private catalogs
- Signed release metadata and enterprise-approved update channels
- LLM capability evaluation: test whether the calling LLM can run SkillForge
  well without over-assuming user knowledge, skipping source review, confusing
  local and peer installs, or hallucinating unsupported commands.

### Codebase-Derived Skills Backlog

- Ancestor README discovery: `codebase-scan` should automatically walk from
  the nearest source root to the scanned subdirectory and include every
  `README.md` found along that path in the source-context map. This lets agents
  understand scoped code with the same root-to-leaf context a human maintainer
  would read.
- Git provenance from the parent repository: when scanning any path inside a
  git checkout, `codebase-scan` should find the nearest git root and record the
  remote URL, branch, commit SHA, source root, scanned relative path, and date
  inspected. If the path is not in a git repository or cannot be pinned, the
  scan should explicitly mark the source as unpinned and explain the risk.
- Skill family metadata: SkillForge should support first-class umbrella and
  child-skill relationships in skill metadata, catalog generation, search
  results, static pages, and install UX. A workflow skill should be able to
  declare child skills, and child skills should be able to declare their parent
  family.
- Medical and safety labels: SkillForge should add structured labels for
  domain and operation risk, including `PHI-sensitive`, `research-only`,
  `model-job`, `GPU-required`, and `writes-derived-data`. These labels should
  be machine-readable in catalog metadata and visible in human-facing pages.
- Changed/new skill evaluation: the CLI should provide an easy command to
  evaluate every changed or newly added skill in the working tree, including
  generated catalog/search/static-site checks. The command should return stable
  JSON and a concise human summary.
- Template/evaluator alignment: `python -m skillforge create` should scaffold
  all README and `SKILL.md` sections that `evaluate` requires. A newly created
  skill should make required publication sections obvious before authors add
  domain-specific content.
