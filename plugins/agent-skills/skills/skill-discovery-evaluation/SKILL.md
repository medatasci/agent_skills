---
name: skill-discovery-evaluation
owner: medatasci
description: Use this skill to evaluate and improve SkillForge skill discoverability before publication. Use when the user asks to make a SkillForge skill findable by humans or agents, improve skill search or SEO metadata, prepare a skill for publication, evaluate a SKILL.md file, improve trigger descriptions, add aliases and task phrases, write should-trigger and should-not-trigger queries, compare nearby skills, or run the SkillForge publication evaluation workflow.
title: Skill Discovery Evaluation
short_description: Improve SkillForge skill discoverability for humans, agents, local search, generated catalog pages, and publication review.
expanded_description: Use this skill to evaluate SkillForge skills before publishing them to a GitHub-backed catalog. It combines LLM judgment with deterministic SkillForge CLI evidence so skills become easier to find, evaluate, trust, install, and use. It improves SKILL.md metadata, trigger language, examples, search phrases, generated-page copy, and publication-readiness reports while leaving generated JSON, checksums, and static pages to the Python pipeline.
aliases:
  - skill SEO
  - skill discovery evaluation
  - make skill findable
  - improve skill search
  - evaluate skill for publication
  - skill trigger evaluation
  - SkillForge publication review
categories:
  - Developer Tools
  - Documentation
  - Safety And Review
tags:
  - skillforge
  - discovery
  - seo
  - evaluation
  - metadata
  - publishing
tasks:
  - evaluate SkillForge skill discoverability
  - improve SKILL.md search metadata
  - write aliases and trigger phrases
  - draft should-trigger and should-not-trigger queries
  - compare nearby skills for overlap
  - prepare a skill for publication
  - run deterministic SkillForge evaluation commands
use_when:
  - The user asks to make a SkillForge skill easier to find by humans or agents.
  - The user asks to improve skill search, SEO, trigger descriptions, aliases, examples, or generated catalog copy.
  - The user is preparing a new, imported, or edited SkillForge skill for publication.
  - The user wants an evaluation workflow that combines LLM judgment with deterministic Python checks.
do_not_use_when:
  - The user wants generic website SEO for a normal website that is not a SkillForge skill catalog or skill page.
  - The user wants to change the behavior, permissions, risk posture, owner, or provenance of a skill without explicit approval.
  - The user wants ranking manipulation such as artificial installs, meaningless version bumps, keyword stuffing, or unsupported trust claims.
inputs:
  - SkillForge skill ID
  - path to a SkillForge skill folder or SKILL.md
  - optional target users or publication context
  - optional peer-catalog or competitor skill results
outputs:
  - improved SKILL.md discovery metadata and examples
  - improved README.md skill home page
  - should-trigger and should-not-trigger query suggestions
  - deterministic SkillForge evaluation summary
  - sample search queries that should find the skill
  - publication-readiness notes and open questions
examples:
  - Evaluate skill huggingface-datasets for publication and improve its search metadata.
  - Help make project-retrospective findable by humans and agents.
  - Improve the SkillForge SEO for skills/my-skill/SKILL.md, then rebuild and evaluate the catalog.
  - Draft should-trigger and should-not-trigger queries for get-youtube-media.
  - Compare this skill against nearby SkillForge skills before I open a PR.
related_skills:
  - project-retrospective
risk_level: low
permissions:
  - read and edit SkillForge SKILL.md files when the user asks for implementation
  - run local SkillForge Python CLI commands
  - no credential access required
page_title: Skill Discovery Evaluation Skill - Improve SkillForge Search, SEO, and Publication Readiness
meta_description: Use the Skill Discovery Evaluation Skill to make SkillForge skills easier for humans and agents to find, evaluate, trust, install, and use before publication.
---

# Skill Discovery Evaluation

Evaluate and improve a SkillForge skill so humans, agents, GitHub search, local
SkillForge search, peer catalogs, and generated catalog pages can find it.

This skill is for SkillForge skills. It is not a generic website SEO tool. The
goal is helpful discovery, not ranking manipulation.

## Core Principles

- Treat `SKILL.md` as the source of truth.
- Keep `description` compact and trigger-oriented.
- Put broader search coverage in structured fields such as `aliases`, `tasks`,
  `use_when`, `do_not_use_when`, `examples`, and `meta_description`.
- Improve language for real user intent, not keyword stuffing.
- Preserve truth: do not invent capabilities, trust status, owners,
  permissions, or provenance.
- Let Python regenerate generated artifacts: catalog JSON, search index JSON,
  static HTML, checksums, and well-known files.
- Treat `README.md` as the human-facing home page for GitHub, web search, peer
  catalogs, and agents browsing before install.

## Discovery Surfaces

Review each surface through the lens of how a human or agent would find and
trust the skill:

- `SKILL.md`: frontmatter, H1, opening summary, workflow, examples, inputs,
  outputs, limits, and safety boundaries.
- `skills/<skill-id>/README.md`: public home page with purpose, examples,
  collection context, related skills, risk, limits, feedback, and search terms.
- `catalog/skills/<skill-id>.json`: generated full metadata and provenance.
- `catalog/skills.json`: generated catalog summary for browsing.
- `catalog/search-index.json`: generated search index for local and agent
  search.
- `plugins/agent-skills/skills/skill_list.md`: human browsing copy.
- `README.md`: marketplace-level positioning and workflow links.
- `site/skills/<skill-id>/index.html`: generated SEO page with visible copy and
  JSON-LD.
- Peer catalogs: source attribution, overlap, and trust caveats.

## Workflow

1. Resolve the skill.
   - Accept either a skill ID such as `project-retrospective` or a path such as
     `skills/project-retrospective/SKILL.md`.
   - Confirm the source file is `skills/<skill-id>/SKILL.md` when working
     inside the SkillForge repo.
2. Run deterministic evidence commands.
   - `python -m skillforge validate skills/<skill-id> --json`
   - `python -m skillforge search-audit <skill-id> --json`
   - `python -m skillforge search "<query>" --json`
3. Read the current skill.
   - Identify the core job, supported tasks, inputs, outputs, limits, and
     permission needs.
   - Separate what the skill truly does from what adjacent tools do.
4. Generate search intent coverage.
   - Human searches: short phrases a user would type.
   - Agent prompts: full natural-language requests that should trigger the
     skill.
   - Near misses: prompts that share terms but should not trigger the skill.
5. Improve `SKILL.md` when the edit is clear.
   - Strengthen `description` as the compact trigger contract.
   - Add or refine `title`, `short_description`, `expanded_description`,
     `aliases`, `categories`, `tags`, `tasks`, `use_when`,
     `do_not_use_when`, `inputs`, `outputs`, `examples`, `related_skills`,
     `risk_level`, `permissions`, `page_title`, and `meta_description`.
   - Keep the body readable and useful for a human reviewer.
6. Improve `README.md` as the skill home page.
   - Explain what the skill is for, who should use it, when to use it, when not
     to use it, repo URL, parent package, keywords, search terms, method,
     parent collection, API/options, inputs and outputs, examples, help, LLM
     and CLI calls, trust and safety, feedback URL, author, citations, related
     skills, collection context, risk, permissions, data handling, writes vs
     read-only behavior, limits, feedback, and contribution.
   - Include natural-language search terms and synonyms without keyword
     stuffing or unsupported capability claims.
7. Rebuild generated files.
   - `python -m skillforge build-catalog --json`
8. Run publication evaluation.
   - `python -m skillforge evaluate <skill-id> --json`
   - If `evaluate` is unavailable, run `validate`, `search-audit`, and sample
     `search` commands separately.
9. Report the result.
   - Summarize source edits.
   - List sample queries that should now find the skill.
   - List near-miss queries that should not trigger it.
   - Note remaining gaps, risks, or questions.

## Query Design

Create both positive and negative examples.

Should-trigger queries:

- include direct skill names and common synonyms
- include casual phrasing and incomplete requests
- include realistic task context
- include prompts where the user does not know the exact skill name

Should-not-trigger queries:

- include adjacent tasks that share vocabulary
- include unsafe or unsupported requests
- include tasks that belong to another skill
- include requests that require behavior the skill does not provide

Avoid overfitting to one exact query. Prefer reusable concepts and natural
phrases.

## Publication Checklist

Before the skill is ready to publish, confirm:

- A human can understand the skill from the title and first two sentences.
- An agent can decide when to use the skill from `name` and `description`.
- The skill has at least three aliases or search phrases.
- The skill has task phrases and clear `use_when` guidance.
- The skill has `do_not_use_when` guidance for near misses.
- The skill lists expected inputs and outputs.
- The skill has realistic example prompts.
- The skill has a README home page with purpose, examples, related skills,
  collection context, risk, permissions, and natural search terms.
- The skill states risk level and permissions honestly.
- Sample `skillforge search` queries find the skill.
- Generated catalog and site files are rebuilt by Python.

## Approval Gates

Ask the user before:

- changing what the skill does
- adding write, delete, credential, network, or external tool permissions
- adding trust, review, certification, company, or source claims
- importing or installing anything from a peer catalog
- applying changes that would make a public-safe skill mention internal or
  private information
