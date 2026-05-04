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

## Codebase-To-Agentic-Skill Generator

SkillForge should support a project called the codebase-to-agentic-skill
generator. The generator turns useful algorithm repositories into reviewable
Codex skill packages. It should be automated where possible and directed by the
workflow the user wants to support.

The generator should not blindly wrap repositories. It should first create a
skill readiness card that describes:

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

Readiness cards should use `docs/templates/codebase-readiness-card.md` and live
under `docs/readiness-cards/`. The first readiness card is
`docs/readiness-cards/nv-segment-ctmr.md`.

The generator should produce, when appropriate:

- `skills/<skill-id>/SKILL.md`
- `skills/<skill-id>/README.md`
- references for source summary, data contract, safety/license, and execution
- deterministic adapter scripts
- an agent-facing Python CLI in `scripts/` for deterministic commands
- smoke test scaffolding
- search/discovery metadata
- generated catalog metadata after review

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
`verify-output` commands, plus a guarded `run`, `brain-run`, and `batch-run`
command set that requires `--confirm-execution` and local prerequisites before
writing outputs. `setup-plan` must remain read-only and return planned
WSL2/Linux setup commands, side effects, and required approvals before any
source clone, environment creation, dependency install, or model download.
Automated tests should use small synthetic NIfTI fixtures; local realistic
smoke tests may use the previously provided `22B7CXEZ6T` MR-RATE image and
NV-Segment-CTMR segmentation files when available. The detailed requirements
and development plan live in `docs/nv-segment-ctmr-skill-requirements-and-plan.md`.

The general project design lives in
`docs/codebase-to-agentic-skill-generator.md`.

The generator should be applied first to NVIDIA-Medtech and MONAI codebases
because those repositories contain medical-imaging algorithms, models, MONAI
bundle workflows, examples, and reusable inference patterns that can become
agentic skills.

Medical-imaging generated skills must default to conservative safety language:
research use only unless the source explicitly says otherwise; not for
diagnosis, treatment, triage, or clinical decision-making; respect dataset and
model terms; do not redistribute restricted data; report source provenance,
model, command, label mapping, and output files.

## User Workflow

The public README must be grouped by the user workflow, not by internal project
structure:

1. Installing SkillForge, including a Codex prompt and direct `git clone` path.
2. Searching for a skill in SkillForge and known peer catalogs.
3. Installing a selected skill into Codex.
4. Browsing the SkillForge Skill List.
5. Sending feedback on a skill, Python helper, CLI command, documentation, or missing workflow.
6. Submitting improvements with Git.
7. Uninstalling a skill.
8. Getting help when the user is unsure what to do next.
9. Checking whether SkillForge itself has upstream updates.
10. Seeing what changed after an update.
11. Controlling how much coaching or extra guidance SkillForge emits.

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
- Recommended SkillForge discovery fields should be written in a readable
  Markdown section named `## SkillForge Discovery Metadata` unless a peer or
  source format requires frontmatter. This keeps the human-readable `#` heading
  near the top while preserving catalog/search metadata.
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
4. If a future skill format uses `AGENTS.md`, keep the same rule: every
   `AGENTS.md` skill folder should have a sibling `README.md` home page.
5. Skill generation must produce both files before the catalog is rebuilt; a
   generated `SKILL.md` without a README home page is not publishable.
6. Ask Codex to use `skill-discovery-evaluation` before publishing.
7. Let the LLM improve only source content in `SKILL.md` and human-authored
   docs; let Python regenerate catalog JSON, search indexes, static pages, and
   checksums, the Codex plugin skill bundle, and `skill_list.md`.
8. Run `python -m skillforge build-catalog --json`.
9. Run `python -m skillforge evaluate <skill-id> --json`.
10. Review the evaluation report, sample search results, and generated file
   changes.
11. Submit the PR with generated files included and with any evaluation gaps
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

Validation and search-audit requirements:

- `validate` should continue to pass portable skills with only `name` and
  `description`.
- `validate` should warn when recommended discovery fields are missing from
  SkillForge-owned skills.
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
