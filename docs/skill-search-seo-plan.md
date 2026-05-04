# Skill Search And SEO Plan

## What This Document Is Called

For normal websites, this is usually called an **SEO strategy**, **SEO plan**, or
**content strategy plan**.

For SkillForge, use **Skill Search And SEO Plan**. It is more accurate because
SkillForge skills need to be discoverable by humans, GitHub, static web
catalogs, CLI search, and agents reading structured metadata.

## Goal

Make each SkillForge skill easy to find, evaluate, trust, install, and use.

Discovery should work for:

- Humans browsing GitHub, a README, or a generated catalog page.
- Humans searching Google or another web search engine.
- Agents searching `catalog/skills.json`, `SKILL.md`, peer catalogs, local skill
  folders, README text, or CLI JSON output.
- Contributors trying to decide whether a new skill duplicates an existing one.

## Working Definition

Skill search and SEO readiness means every skill has:

- A clear canonical name.
- Natural-language descriptions that match how users ask for help.
- Structured metadata for machines.
- Prompt examples for agents and humans.
- Trust and source information.
- Authoritative upstream source links, especially for research, medical,
  scientific, security, and regulated-domain skills.
- Good internal links from the README, catalog, peer catalogs, and skill list.
- Enough context to know when to use the skill and when not to use it.

## Discovery Surfaces

Prepare each skill for discovery in these places:

| Surface | What It Needs |
| --- | --- |
| `SKILL.md` | Frontmatter, clear H1, use cases, workflow, examples, limits. |
| `skills/<skill>/README.md` | Public skill home page with purpose, examples, collection context, related skills, risk, limits, feedback path, authoritative source links, citations, and natural search terms. |
| `catalog/skills.json` | Stable ID, concise description, tags, source, checksum, install commands, authoritative sources, and citations when available. |
| `catalog/skills/<skill>.json` | Full metadata, provenance, warnings, files, optional search terms, authoritative sources, and citations. |
| `plugins/agent-skills/skills/skill_list.md` | Human-friendly browsing copy and example prompts. |
| `README.md` | Category links, install/search examples, public positioning. |
| Static catalog page | One page per skill, category pages, search index, JSON-LD. |
| GitHub | Descriptive paths, headings, repo topics, README anchors, linked examples. |
| Peer catalogs | Source catalog ID, repo URL, commit, path, freshness, trust notes. |
| `skillforge/README.md` | Package-level Python architecture overview for humans and agents modifying SkillForge itself. |
| `docs/python/<module>.md` | Human and agent-facing module docs for ownership, side effects, commands, tests, and safe edit boundaries. |
| `skillforge/modules.toml` | Machine-readable map of module ownership, commands, reads, writes, network use, risk, tests, and docs. |

## Metadata Requirements

Each skill should have two descriptions:

- **Short description:** one sentence, useful in search results and catalog cards.
- **Expanded description:** 3-6 sentences covering tasks, inputs, outputs,
  constraints, and common user phrasing.

Recommended metadata fields:

```yaml
name: get-youtube-media
title: Get YouTube Media
description: Search YouTube, retrieve transcripts, inspect captions, and download authorized media for research workflows.
aliases:
  - youtube transcripts
  - youtube captions
  - youtube research
  - video transcript extraction
tags:
  - youtube
  - transcripts
  - captions
  - media
  - research
tasks:
  - search YouTube for research sources
  - get a transcript from a YouTube URL
  - inspect caption languages
  - download authorized video or audio
use_when:
  - The user needs YouTube transcripts, captions, or authorized media downloads.
  - The user is building a research or evidence workflow from YouTube sources.
do_not_use_when:
  - The user wants to bypass access controls or download media they are not allowed to save.
inputs:
  - YouTube URL
  - YouTube search query
  - optional language code
outputs:
  - transcript text
  - captions
  - search results
  - optional media files
risk_level: medium
trust:
  source: SkillForge
  owner: medatasci
```

Not every field needs to be required in the MVP, but this is the shape to grow
toward.

## Writing Rules For Skill Descriptions

Good skill descriptions should:

- Start with the job the user wants done.
- Include common synonyms users might search for.
- Include agent trigger phrases such as "Use when the user asks..."
- Name important inputs and outputs.
- Name major constraints or safety limits.
- Avoid keyword stuffing.
- Stay readable as normal prose.

Bad:

```text
YouTube skill for media.
```

Better:

```text
Search YouTube for research videos, retrieve transcripts and captions, inspect
available caption languages, and download authorized video or audio files.
Use when the user asks for YouTube transcripts, video evidence collection,
caption extraction, or repeatable research-source workflows.
```

## Per-Skill README Template

Every source skill folder should include a `README.md` beside `SKILL.md`.
`SKILL.md` is the agent instruction and behavior contract. `README.md` is the
human-facing home page for GitHub, web search, peer catalogs, and agents that
are browsing before deciding what to install.

The README should include:

- Skill name and repository URL.
- Parent package name and repository URL when relevant.
- Parent collection name and URL when relevant.
- What the skill does.
- Why a human or agent would call it.
- Keywords and natural search terms.
- How it works or method notes when relevant.
- API and options.
- Inputs and outputs.
- Examples.
- Help and getting started guidance.
- How to call it from an LLM and from the CLI.
- Trust and safety: risk level, permissions, data handling, and writes vs
  read-only behavior.
- Feedback URL.
- Author.
- Citations for the method when relevant.
- Related skills and adjacent workflows.

The canonical template lives at
`skillforge/templates/skill/README.md.tmpl`.

## Python Module Documentation As Agent SEO

SkillForge itself also needs discovery surfaces. Humans and agents should be
able to find the right Python module for a change without scanning every source
file or guessing ownership from filenames.

This is agent SEO: it makes implementation knowledge findable by the agents that
will maintain the project.

Use these surfaces:

- `skillforge/README.md`: package-level overview and editing map.
- `docs/python/README.md`: guide to the Python internals docs.
- `docs/python/<module>.md`: one module doc per important Python module.
- `skillforge/modules.toml`: machine-readable module manifest.
- `skillforge/templates/python/module.md.tmpl`: reusable template for module docs.

Each Python module doc should include:

- Module path and one-sentence purpose.
- Responsibilities and non-responsibilities.
- When to edit the module and when to choose another module.
- Commands or workflows backed by the module.
- Inputs, reads, outputs, writes, and generated files.
- Side effects and safety notes.
- Network access, filesystem writes, external commands, and confirmation gates.
- Public functions and stable data contracts.
- Cross-platform notes for Windows, macOS, and Linux.
- Tests and acceptance checks.
- Agent editing checklist and related docs.

`skillforge/modules.toml` should mirror the docs in a form agents can parse:

```toml
[[module]]
path = "skillforge/peer.py"
purpose = "Peer catalog federation, peer caches, corpus search, peer install, peer import, and diagnostics."
commands = ["peer-search", "corpus-search", "cache", "peer-diagnostics", "install --peer", "import-peer"]
reads = ["peer-catalogs.json", "SkillForge cache", "peer repositories", "peer static catalogs"]
writes = ["SkillForge cache", "Codex skills directory", "skills/", "catalog/"]
network = true
risk = "high"
tests = ["tests/test_skillforge.py"]
docs = ["docs/python/peer.md"]
```

Do not create one `README.md` beside every `.py` file. Prefer the package
overview, `docs/python/`, and `modules.toml` pattern so the docs stay navigable
and lower-maintenance.

The deterministic quality gate should check that every module and doc path in
`skillforge/modules.toml` exists.

## Generated Skill Page Template

Every generated skill page should include:

1. Skill name.
2. One-sentence value proposition.
3. "Use this when" list.
4. "Do not use this when" list.
5. Example Codex prompts.
6. CLI install command.
7. Inputs and outputs.
8. Risk level and permissions.
9. Source and provenance.
10. Related skills.
11. Feedback link.

Example page title:

```text
Get YouTube Media Skill - YouTube Transcript, Caption, and Research Workflow for Codex
```

Example meta description:

```text
Install the Get YouTube Media Skill for Codex to search YouTube, retrieve
transcripts and captions, inspect caption languages, and support repeatable
research workflows.
```

## Prompt Examples As Search Content

Prompt examples are discovery content. Include examples that match how humans
actually ask for help:

```text
Find transcripts for YouTube videos about agent skill marketplaces.
```

```text
Get captions from this YouTube URL and save them as text and SRT.
```

```text
Search YouTube for videos about MR datasets and summarize the best sources.
```

For every skill, include:

- 3 beginner prompts.
- 3 task-specific prompts.
- 1 troubleshooting prompt.
- 1 feedback prompt.

## Categories And Tags

Use a small controlled vocabulary first, then allow aliases.

Initial categories:

- Research
- Media
- Data
- Documentation
- Project Memory
- Developer Tools
- Business Workflows
- AI/ML
- Safety And Review

Tags should include:

- Domain terms: `youtube`, `hugging-face`, `datasets`.
- Task terms: `transcripts`, `pagination`, `retrospective`.
- Object terms: `video`, `captions`, `parquet`, `interaction-log`.
- User intent terms: `research`, `evidence`, `summarize`, `inspect`.

## Agent Discovery Rules

Agents need low-ambiguity metadata. Add explicit trigger and exclusion language:

```text
Use when the user asks to inspect Hugging Face dataset metadata, list splits,
preview rows, paginate rows, search dataset text, filter rows, or retrieve
parquet URLs.

Do not use when the user wants to train a model, upload a dataset, manage Hub
repositories, or run non-read-only Hugging Face operations.
```

For agent search, every skill should expose:

- `name`
- `description`
- `aliases`
- `tags`
- `tasks`
- `use_when`
- `do_not_use_when`
- `inputs`
- `outputs`
- `risk_level`
- `source`
- `updated_at`
- `examples`
- `authoritative_sources`
- `citations`

For research, scientific, medical-imaging, security, legal, financial, or other
high-trust domains, every skill should connect itself to authoritative upstream
sources. Prefer primary sources: source repositories, official model cards,
dataset cards, official documentation, papers, standards, and license terms.
Do not turn private task data, logs, reports, or local files into SEO copy.

## Human SEO Rules

Use classic SEO where SkillForge has web pages:

- One stable URL per skill.
- Clear page titles that include the skill name and primary task.
- Unique meta descriptions per skill.
- Descriptive URLs such as `/skills/get-youtube-media/`.
- Internal links from the README, catalog, category pages, and related skills.
- Helpful visible content that matches the structured metadata.
- JSON-LD structured data on generated pages.

Use `SoftwareApplication` for SkillForge as a tool and `CreativeWork` or
`SoftwareSourceCode`-style metadata for individual skills. At minimum, emit:

```json
{
  "@context": "https://schema.org",
  "@type": "CreativeWork",
  "name": "Get YouTube Media",
  "description": "Search YouTube, retrieve transcripts and captions, inspect caption languages, and download authorized media for research workflows.",
  "keywords": ["youtube", "transcripts", "captions", "research", "codex skill"],
  "citation": ["https://github.com/yt-dlp/yt-dlp"],
  "isBasedOn": ["https://developers.google.com/youtube"],
  "isPartOf": {
    "@type": "SoftwareApplication",
    "name": "SkillForge"
  }
}
```

## GitHub Discovery Rules

GitHub is a search engine for developers. Improve discovery through:

- Repo description: include "Codex skills", "agent skills", and "SkillForge".
- Repo topics: `codex`, `agent-skills`, `skills`, `ai-agents`,
  `workflow-automation`, `skillforge`.
- Directory names: keep skill IDs descriptive and stable.
- README anchors: link to each skill and category.
- Per-skill README and `SKILL.md`: include synonyms and examples, with README
  serving as the human home page and `SKILL.md` serving as the agent contract.
- Issues: use labels such as `skill-feedback`, `skill-request`, `docs`,
  `catalog`, `risk-review`.

## Current Skill Audit

### `get-youtube-media`

Strengths:

- Strong long description.
- Good task terms: YouTube, transcripts, captions, download, research.
- Good safety language around authorization and copyright.
- Stronger authority links are needed for the upstream tool, API docs,
  licenses, and relevant standards.

Improve:

- Add aliases: `youtube-transcripts`, `video-captions`, `caption-extraction`,
  `yt-dlp-workflow`.
- Add `do_not_use_when` metadata for bypassing access controls.
- Add a generated web page title and meta description.

### `huggingface-datasets`

Strengths:

- Clear source provenance.
- Strong endpoint-specific details.
- Good read-only positioning.

Improve:

- Add tags: `hugging-face`, `datasets`, `dataset-viewer`, `parquet`,
  `metadata`, `rows`.
- Add aliases: `hf datasets`, `hugging face dataset viewer`,
  `dataset rows`, `parquet URLs`.
- Add explicit "Do not use for training, uploading, or repo management."

### `project-retrospective`

Strengths:

- Clear purpose and workflow.
- Good use cases: retrospectives, interaction logs, after-action reviews.

Improve:

- Add aliases: `project memory`, `interaction log`, `after action review`,
  `collaboration memory`, `project journal`.
- Add examples for business users, engineering teams, and research projects.
- Add outputs: `retrospectives/interaction_log.md`,
  `interaction_template.md`.

## Implementation Status

Implemented:

1. Extend the skill metadata schema with optional discovery fields.
2. Update `skillforge validate` to warn when discovery fields are missing from
   repo-owned skills.
3. Update catalog generation to preserve aliases, tasks, inputs, outputs, and
   risk metadata.
4. Generate `catalog/search-index.json` for human and agent search.
5. Generate one static HTML page per skill.
6. Add JSON-LD to generated skill pages.
7. Add category pages for Research, Data, Documentation, AI/ML, and Media.
8. Add `skillforge search-audit <skill-id>` to audit search and SEO discoverability.

Backlog:

1. Add a deterministic `skillforge evaluate <skill-id-or-path>` command that
   wraps structural validation, search audit, catalog freshness, and generated
   page checks.
2. Add a SkillForge skill for LLM-driven search and SEO evaluation.
3. Add peer-catalog search terms to cache results.
4. Track feedback queries that failed to find a good skill.

## Evaluation Workflow

Use **evaluation** as the product term. Validation is the deterministic
structural sub-check. Evaluation includes both machine checks and LLM judgment.

Python should own:

- Required field checks.
- Folder naming and file inventory.
- Checksum and source/provenance metadata.
- Secret, suspicious-file, external URL, and destructive-language scans.
- Search index generation.
- Static catalog generation.
- Generated-file freshness checks.
- Machine-readable JSON output.
- Module-manifest path checks for `skillforge/modules.toml`.

The LLM should own:

- Search intent expansion.
- Human-facing title and description quality.
- Agent trigger and exclusion language.
- Alias, synonym, category, tag, task, input, output, and example suggestions.
- Duplicate or confusing overlap with adjacent skills.
- Public-safe wording.
- Python module doc clarity when SkillForge internals change.
- Pull-request summary and evaluation narrative.

Recommended publish sequence:

1. Run structural validation.
2. Run LLM-driven discovery evaluation with `skill-discovery-evaluation`.
3. Update `SKILL.md` metadata, examples, and trigger language.
4. Update `README.md` as the human-facing skill home page.
5. Rebuild catalog, search index, and static pages.
6. Run deterministic publication evaluation.
7. Submit the PR with generated files and an evaluation summary.

## Skill Discovery Evaluation Skill

SkillForge should include a first-class skill named
`skill-discovery-evaluation`. This skill is the LLM side of the publication
pipeline.

Use it when a user asks to:

- evaluate a SkillForge skill for publication
- improve search and SEO metadata for a skill
- make a skill findable by humans and agents
- prepare a new or imported skill for the SkillForge catalog
- compare a skill against nearby catalog or peer-catalog skills

The skill should:

1. Read `skills/<skill-id>/SKILL.md` as the source of truth.
2. Run deterministic SkillForge commands for evidence.
3. Infer likely human searches, GitHub searches, and agent prompts.
4. Draft should-trigger and should-not-trigger queries.
5. Improve source metadata and examples in `SKILL.md` only when the meaning is
   clear.
6. Improve `README.md` as the public skill home page.
7. Rebuild generated files.
8. Run deterministic evaluation.
8. Report what changed, what queries should find the skill, and what risks or
   open questions remain.

The skill must not:

- hand-edit generated catalog JSON, search index JSON, static HTML, checksums,
  or provenance fields
- add unsupported trust claims
- change what a skill does without asking
- recommend ranking manipulation such as artificial installs or meaningless
  version bumps

## Quality Checklist

Before publishing a skill, answer:

- Can a human understand the skill from the first two sentences?
- Can an agent determine when to use it from metadata alone?
- Does the skill include common synonyms and task phrases?
- Does it say when not to use the skill?
- Does it list inputs and outputs?
- Does it include 5-8 realistic prompt examples?
- Does it link to related skills?
- Does it include source, owner, version, and updated date?
- Does it avoid private/company-internal claims unless the repo is private?
- Does it avoid over-promising capability?

## Sources

- Google Search Central: SEO is about helping search engines understand content
  and helping users decide whether to visit; useful, well-organized,
  people-first content matters most.
- Google Search Central: good titles should be unique, clear, concise, and
  accurate; snippets can use visible page content or meta descriptions.
- Google Search Central: structured data gives explicit clues about page meaning;
  JSON-LD is the recommended format when practical.
- Schema.org: `CreativeWork` supports fields such as `name`, `description`,
  `keywords`, `author`, `publisher`, `license`, `version`, and `isPartOf`.
- Schema.org: `SoftwareApplication` supports software-specific fields such as
  `applicationCategory`, `softwareVersion`, `softwareRequirements`, and
  `softwareHelp`.
