# GitHub Skill Repository Best Practices Research

Updated: 2026-05-02 12:31 America/New_York

## Purpose

This note identifies GitHub repositories worth studying before designing a personal or company skill-sharing platform. The goal is not to list every public skill repository. The useful signal is which repositories demonstrate repeatable practices for authoring, versioning, validating, evaluating, distributing, and governing agent skills.

## Executive Takeaways

1. Use the Agent Skills `SKILL.md` format as the core unit of portability: one skill folder, required YAML frontmatter, Markdown instructions, optional `scripts/`, `references/`, and `assets/`.
2. Treat the `description` field as routing infrastructure, not prose. It is the pre-activation trigger surface for agents and should include what the skill does, when to use it, and near-miss exclusions when useful.
3. Design every skill around progressive disclosure: small `SKILL.md`, larger reference files loaded only when relevant, deterministic scripts for fragile/repeated work, and assets for output templates.
4. The best repos add evaluation and validation, not just Markdown. Strong patterns include linting, acceptance criteria, trigger evals, task evals, baselines, CI gates, and human review loops.
5. Public marketplaces are optimized for discovery and installs; company platforms need stronger trust: ownership, CODEOWNERS, review states, security scanning, provenance, lockfiles, compatibility, and deprecation.
6. For your platform, the differentiator should be "trusted skill supply chain for humans and agents," not another broad public index.

## Highest-Value Repositories To Study

| Repository | Why it matters | Best practices to borrow |
| --- | --- | --- |
| [agentskills/agentskills](https://github.com/agentskills/agentskills) | Canonical specification and reference SDK for Agent Skills. | Minimal portable format, validation library, spec-first design, open contribution model. |
| [anthropics/skills](https://github.com/anthropics/skills) | Reference implementation and production-grade examples for Claude. | Self-contained folders, complex document skills, `skill-creator`, eval-driven skill iteration, human review loop. |
| [openai/skills](https://github.com/openai/skills) | Codex skill catalog and OpenAI-specific authoring patterns. | Curated/system/experimental separation, installer flow, `agents/openai.yaml` UI metadata, init and validation scripts. |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) | Large community catalog for Copilot instructions, prompts, chat modes, and agent skills. | Human-friendly cataloging, contribution paths, GitHub-native distribution, examples at broad scale. |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | CLI/package manager for installing skills across many agents. | `npx skills add`, install/update/list/init commands, lockfile thinking, multi-agent path support, source parsing, update detection. |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | Official Vercel skill pack with domain best practices and deploy workflows. | Rule categorization by impact, script packaging, installable repo model, practical trigger examples. |
| [microsoft/skills](https://github.com/microsoft/skills) | Enterprise-scale skill library for Azure SDKs and Foundry. | Skill Explorer, language/product categorization, symlink organization, acceptance criteria, scenarios, test harnesses, current-doc verification. |
| [getsentry/skills](https://github.com/getsentry/skills) | Strong model for company-internal skills shared publicly. | Scope placement rules, `SPEC.md` maintenance contract, vendoring policy, attribution, concise AGENTS.md skill, security-review skill, internal conventions. |
| [trailofbits/skills](https://github.com/trailofbits/skills) | Security-focused skill marketplace with high standards. | Plugin marketplace structure, Codex compatibility mapping, mandatory validation, quality standards, "when not to use" sections, security-specific rationalization rejection. |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Opinionated lifecycle skills for production engineering. | Workflow stages from spec to ship, agent personas, anti-rationalization tables, evidence requirements, reference checklists. |
| [antfu/skills](https://github.com/antfu/skills) | Proof-of-concept for generating/syncing skills from source docs. | Git submodules for upstream docs, generated skills from official docs, vendored skills, skill collection as reusable template. |
| [huggingface/skills](https://github.com/huggingface/skills) | AI/ML domain skill pack with cross-agent claims. | AGENTS.md fallback, compatibility across Codex/Claude/Gemini/Cursor, domain tasks such as datasets, Gradio, evaluation, Hub operations. |
| [supabase/agent-skills](https://github.com/supabase/agent-skills) | Focused developer-platform skill pack. | Narrow domain scope, small number of high-value skills, references for detailed docs, compatibility with many agents. |
| [WordPress/agent-skills](https://github.com/WordPress/agent-skills) | Community/project ecosystem skills for a mature OSS platform. | Generated from official docs, human-reviewed by contributors, eval folder, shared reusable content, transparent AI-authorship disclosure. |
| [cloudflare/skills](https://github.com/cloudflare/skills) | Skills plus MCP servers and slash commands for a developer platform. | Combined skill/command/MCP distribution, platform-specific skill table, multi-agent install paths, docs and API MCP augmentation. |
| [tech-leads-club/agent-skills](https://github.com/tech-leads-club/agent-skills) | Security-hardened registry positioning. | Static analysis, content hashing, lockfiles, no-binaries policy, path isolation, audit trail, curated trust layer. |
| [LambdaTest/agent-skills](https://github.com/LambdaTest/agent-skills) | Test automation skill library. | `skills_index.json`, `evals/`, validation script, framework-specific skill variants, contribution checklist. |
| [himself65/skill-lint](https://github.com/himself65/skill-lint) | Dedicated linter/GitHub Action for Agent Skills. | CI validation for frontmatter, naming, field constraints, unknown fields, name/directory mismatch, JSON output. |
| [cloudflare/agent-skills-discovery-rfc](https://github.com/cloudflare/agent-skills-discovery-rfc) | Proposal for web-native skill discovery. | `/.well-known/agent-skills/index.json`, artifact URLs, archive vs single-file skills, progressive disclosure over HTTP. |
| [mgechev/skills-best-practices](https://github.com/mgechev/skills-best-practices) | Concise third-party best-practices guide. | LLM-assisted discovery validation, logic validation, edge-case testing, architecture refinement, trigger/negative-trigger checks. |

## Patterns That Recur In Good Repositories

### 1. Skill Package Shape

The common package shape is:

```text
skill-name/
  SKILL.md
  scripts/
  references/
  assets/
```

Strong repos keep this boring on purpose. `SKILL.md` is the activation document; `scripts/` gives deterministic execution; `references/` stores detailed docs; `assets/` stores output templates or static resources. Public catalogs that diverge too much from this become harder for agents and humans to audit.

### 2. Discovery Metadata

The highest-quality repositories treat metadata as an index:

- Required fields: `name`, `description`.
- Common optional fields: `license`, `compatibility`, `metadata`, `allowed-tools`.
- Name constraints: lowercase, hyphenated, short, folder matches frontmatter.
- Description constraints: specific trigger language, third-person voice, includes when to use the skill.

For your platform, add a generated registry layer rather than extending the core spec too aggressively. Keep `SKILL.md` portable, then add company metadata in sidecar JSON.

### 3. Progressive Disclosure

The strongest repos converge on the same instruction economy:

- Keep `SKILL.md` under roughly 500 lines.
- Move detailed docs into directly linked reference files.
- Avoid reference chains where `SKILL.md` points to a file that points to another file.
- Include a table of contents in long reference files.
- Use scripts when repeated code generation would be fragile or wasteful.

This matters for a company platform because a registry could eventually expose hundreds of skills; only metadata should be loaded up front.

### 4. Evals And Quality Gates

The best practices are moving beyond "write a Markdown file":

- Anthropic emphasizes baseline vs with-skill runs, human review, quantitative assertions, and repeated iteration.
- Microsoft adds acceptance criteria and scenario files for SDK skills.
- WordPress and LambdaTest include eval-oriented folders.
- `skill-lint` and `skills-ref` cover structural validation.
- Mgechev's repo recommends discovery validation, logic validation, edge-case testing, and architecture refinement with LLMs.

For your platform, skills should have at least two eval types:

- Trigger evals: should the agent load this skill for this prompt?
- Task evals: does using the skill improve the result against a baseline?

### 5. Security And Trust

The public ecosystem already has signs of marketplace risk. The repos worth copying add controls:

- Trail of Bits: validation scripts, explicit "when not to use", quality standards, Codex compatibility, security review culture.
- Sentry: vendoring policy, attribution, skill scanning, repo/domain/global placement rules.
- Tech Leads Club: lockfiles, content hashing, path isolation, no-binaries policy, audit trail, security scan claims.
- Cloudflare discovery RFC: explicit artifact location and index structure.

Internal platform requirements should include owner, reviewer, risk class, allowed tools, network domains, script dependencies, provenance, and install pinning.

### 6. Distribution And Install

Current distribution patterns:

- Git repo as source of truth.
- `npx skills add owner/repo --skill name` for broad cross-agent installation.
- Claude plugin marketplace model for skill bundles.
- GitHub/Copilot project and personal skill directories.
- Codex/Claude/Cursor/Gemini/OpenCode path conventions.
- Static catalog sites such as skills.sh and Awesome Copilot.
- Emerging `/.well-known/agent-skills/index.json` discovery.

For your platform, preserve Git-first publishing but generate:

- Static human catalog.
- Machine-readable registry JSON.
- Per-skill detail JSON.
- `llms.txt` or docs index.
- Optional MCP endpoint for query/install metadata.
- Optional `.well-known/agent-skills/index.json`.

## What Each Repo Suggests For Your Platform

### Minimum Viable Skill Registry

Borrow from `agentskills/agentskills`, `openai/skills`, and `vercel-labs/skills`:

- Skills live in Git.
- Each skill has `SKILL.md`.
- The catalog is generated from repo metadata.
- Installation can work from Git URL, repo path, or package manager.
- Validation runs in CI.
- Version pinning records commit SHA or release tag.

### Company-Grade Registry

Borrow from Microsoft, Sentry, Trail of Bits, and Tech Leads Club:

- Skill owners and CODEOWNERS.
- Review states: draft, reviewed, approved, deprecated, blocked.
- Security scan and license scan before publishing.
- Evals and acceptance criteria before promotion.
- Domain/team/global placement rules.
- Vendoring and attribution policy.
- Compatibility and allowed-tools metadata.
- Audit log for install/update/publish events.

### Human And Agent Discovery

Borrow from Awesome Copilot, skills.sh, Cloudflare, and Cloudflare's discovery RFC:

- Human catalog with categories, tags, install commands, owners, stars/usage, compatibility, last verified date.
- Agent-readable index with name, description, URL, version, checksum, compatibility, and risk metadata.
- Full-text search and faceted filtering.
- "Open in GitHub" and "install this skill" affordances.
- Machine-readable docs index for white-paper/agent consumption.

## Recommended Internal Metadata Sidecar

Keep core `SKILL.md` standard-compatible, then add a generated or curated sidecar such as `skill.json`:

```json
{
  "name": "example-skill",
  "version": "1.0.0",
  "owner": "team-or-person",
  "status": "approved",
  "risk_class": "medium",
  "source_url": "https://github.com/company/skills/tree/main/skills/example-skill",
  "commit_sha": "abc123",
  "license": "MIT",
  "compatible_agents": ["codex", "claude-code", "copilot", "cursor"],
  "allowed_tools": ["read", "grep", "bash"],
  "network_domains": [],
  "has_scripts": true,
  "has_evals": true,
  "last_reviewed": "2026-05-02",
  "checks": {
    "lint": "pass",
    "security_scan": "pass",
    "trigger_evals": "pass",
    "task_evals": "pass"
  }
}
```

## Requirements Implied By The Research

1. Authoring: scaffold new skills with a template, examples, optional scripts/references/assets, and trigger guidance.
2. Validation: lint `SKILL.md`, verify file references, enforce naming and metadata constraints, and block malformed skills in CI.
3. Evaluation: support trigger evals, task evals, baselines, human review, and regression reports.
4. Versioning: pin installs by commit SHA or release tag; maintain lockfiles for reproducible onboarding.
5. Discovery: provide both human UI and agent-readable JSON indexes.
6. Governance: require owner, reviewer, lifecycle status, risk class, last reviewed date, and deprecation path.
7. Security: scan scripts and dependencies, flag network access, enforce path safety, check licenses, and record provenance.
8. Compatibility: track supported agents and install paths; generate fallbacks such as `AGENTS.md` where useful.
9. Distribution: install from GitHub repo, specific skill folder, release archive, or internal catalog.
10. Observability: capture install counts, usage feedback, eval history, quality score, and open issues.

## Shortlist To Clone Or Read First

1. `agentskills/agentskills` for the spec.
2. `anthropics/skills` for reference implementations and eval loops.
3. `openai/skills` for Codex-oriented packaging and UI metadata.
4. `vercel-labs/skills` for package-manager and lockfile mechanics.
5. `microsoft/skills` for enterprise-scale categorization and testing.
6. `getsentry/skills` for company-internal governance and maintenance contracts.
7. `trailofbits/skills` for security-grade authoring and review standards.
8. `addyosmani/agent-skills` for process-heavy workflow skills.
9. `antfu/skills` for generated/synced skills from source docs.
10. `cloudflare/agent-skills-discovery-rfc` for web discovery.

## Open Questions For The Platform

1. Should personal skills and company-approved skills share one catalog with different trust badges, or be separate registries?
2. Should your MVP support install/update flows, or only catalog/discovery first?
3. Should company skills be vendored into one repo for consistency, or federated from many team repos with a central index?
4. How strict should review be for skills without scripts versus skills that execute code or call external services?
5. Should eval scores be mandatory before publishing, or only before promoting to "approved"?

## Sources

- Agent Skills specification: https://agentskills.io/specification
- Agent Skills overview: https://agentskills.io/
- Agent Skills best practices: https://agentskills.io/skill-creation/best-practices
- Claude skill authoring best practices: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- GitHub Copilot agent skills docs: https://docs.github.com/copilot/concepts/agents/about-agent-skills
- `agentskills/agentskills`: https://github.com/agentskills/agentskills
- `anthropics/skills`: https://github.com/anthropics/skills
- `openai/skills`: https://github.com/openai/skills
- `github/awesome-copilot`: https://github.com/github/awesome-copilot
- `vercel-labs/skills`: https://github.com/vercel-labs/skills
- `vercel-labs/agent-skills`: https://github.com/vercel-labs/agent-skills
- `microsoft/skills`: https://github.com/microsoft/skills
- `getsentry/skills`: https://github.com/getsentry/skills
- `trailofbits/skills`: https://github.com/trailofbits/skills
- `addyosmani/agent-skills`: https://github.com/addyosmani/agent-skills
- `antfu/skills`: https://github.com/antfu/skills
- `huggingface/skills`: https://github.com/huggingface/skills
- `supabase/agent-skills`: https://github.com/supabase/agent-skills
- `WordPress/agent-skills`: https://github.com/WordPress/agent-skills
- `cloudflare/skills`: https://github.com/cloudflare/skills
- `tech-leads-club/agent-skills`: https://github.com/tech-leads-club/agent-skills
- `LambdaTest/agent-skills`: https://github.com/LambdaTest/agent-skills
- `himself65/skill-lint`: https://github.com/himself65/skill-lint
- `cloudflare/agent-skills-discovery-rfc`: https://github.com/cloudflare/agent-skills-discovery-rfc
- `mgechev/skills-best-practices`: https://github.com/mgechev/skills-best-practices
