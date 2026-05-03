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
- `search-audit`: deterministic search/SEO sub-check used by evaluation
- `create`: generate a new skill folder from templates and promptable metadata
- `info`: show metadata, files, source URL, and Codex install path
- `install`: install a pinned local SkillForge skill or explicitly confirmed peer skill for Codex
- `import-peer`: import a peer skill into the local GitHub-backed SkillForge catalog
- `remove`: remove an installed Codex skill
- `list`: show locally installed Codex skills
- `feedback`: draft a GitHub issue for a skill, Python helper, CLI command, documentation area, or missing workflow
- `cache list|refresh|clear`: inspect, refresh, and clear peer caches
- `peer-diagnostics`: inspect peer catalog metadata, adapters, duplicate IDs, cache freshness, and missing provenance
- `doctor`: check local Codex paths and installation health

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
- Generated `SKILL.md` must include valid frontmatter with `name` and
  `description`, plus recommended discovery fields when provided.
- Generated `README.md` must include the full skill home page structure:
  repo/package, parent collection, purpose, call reasons, keywords, search
  terms, method, API/options, inputs/outputs, examples, help, LLM/CLI calls,
  trust and safety, feedback, author, citations, and related skills.
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
   checksums.
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
- Update checks
- Enterprise allowlist
- Multi-agent install targets

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
- Peer search must rank local SkillForge results and peer results separately
  enough that users can tell what is local vs external.
- Peer search must never imply trust by default. Source catalogs are discovery
  sources, not endorsements.
- Peer install must continue to require explicit confirmation with `--yes` and
  must show peer source metadata before installation.
- Peer import must remain the only operation that vendors peer skill content
  into this repository.
- Cached peer content should be inspectable through CLI commands:
  - `python -m skillforge cache list --json`
  - `python -m skillforge cache refresh --peer <peer-id> --json`
  - `python -m skillforge cache clear --peer <peer-id> --yes`
- Add a peer diagnostic command or mode that reports broken peer URLs,
  stale caches, adapter failures, duplicate IDs, and missing provenance.
- The static catalog UI should be able to display peer catalogs and peer search
  results without making them look local.

## Git Submission Workflow

SkillForge must document a low-friction Git submission path for skills, Python
helpers, CLI changes, documentation, catalog updates, and feedback fixes.

Required command pattern:

- `git checkout -b <branch-name>`
- `git add <changed-files>`
- `git commit -m "<clear change summary>"`
- `git push -u origin <branch-name>`

Skill submissions must update:

- `plugins/agent-skills/skills/<skill-name>/SKILL.md`
- `plugins/agent-skills/skills/skill_list.md`
- `plugins/agent-skills/.codex-plugin/plugin.json` when installed skill content changes

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

## Open Decisions

- Whether NeMoClaw needs first-class package metadata post-MVP
- Whether to keep personal and company-ready skills in one repo with labels, or separate repos later
- Whether to package the Python installer for `uvx` or `pipx`, or keep it repo-local first
- Which external catalogs should be included in the default federation allowlist

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
