# SkillForge Requirements

Status: Draft
Date: 2026-05-02

## Goal

Build SkillForge: a GitHub-backed, static-generated skill catalog and Codex installer for personal skills and future NVIDIA-internal use. SkillForge helps humans and agents find and install public-safe skills for research and task execution.

## Scope

MVP supports both personal use and company-shaped workflows, but only public-safe content. No NVIDIA-internal data, secrets, private process knowledge, or privileged automation in v1.

The MVP public surface is the repository `README.md`. A static HTML catalog draft may be generated for evaluation, but the README remains the authoritative human-facing page until the site design is validated.

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

## Python Catalog Tool

MVP includes a fast Python package in the repo for catalog upload, download, validation, search, and Codex install.

CLI style:

- `python -m skillforge validate <path>`
- `python -m skillforge search "<task>"`
- `python -m skillforge install <skill-id>`

Required commands:

- `validate`: validate a local skill before catalog upload
- `upload`: add or update a skill in the GitHub-backed catalog structure
- `download`: fetch a skill from the catalog to a local cache or folder
- `search`: find skills by exact ID, keyword, task, domain, or peer catalog
- `info`: show metadata, files, source URL, and Codex install path
- `install`: install a pinned skill for Codex
- `remove`: remove an installed Codex skill
- `list`: show locally installed Codex skills
- `feedback`: draft a GitHub issue for skill feedback
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

Later checks:

- Trigger evals
- Task evals
- Dependency scanning
- Prompt-injection scan
- License/provenance checks
- Risk scoring and trust labels
- Agent compatibility smoke tests beyond Codex

## Discovery

Human discovery:

- Static website generated from GitHub
- Search by task, domain, owner, recency, and source catalog
- Skill pages show summary, install options, files, source link, and examples
- SEO-friendly public pages for skill categories, task pages, and individual skills

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
