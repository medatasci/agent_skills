---
name: manuscript-builder
description: Create and maintain a shareable project_publication.html manuscript page plus structured publication files for research projects. Use when the user asks to prepare, update, review, or keep current a manuscript, project publication page, Nature-style or NeurIPS-style paper record, publication claims, experiments, figures, tables, references, reproducibility notes, limitations, or publication readiness. Also use at the end of substantive project work when AGENTS.md asks for manuscript documentation to stay current.
title: Manuscript Builder
short_description: Keep research projects publication-ready with a living manuscript page and structured evidence files.
expanded_description: Use this skill to create and maintain project_publication.html plus structured claim, experiment, figure, table, reference, and update files so research work can become a collaborator-friendly manuscript record. It emphasizes citation discipline, reproducibility notes, limitations, and Nature-style or NeurIPS-style publication readiness.
aliases:
  - paper authoring
  - manuscript writing
  - publication page
  - research paper builder
  - project publication
categories:
  - Documentation
  - Research
  - Scientific Writing
  - Collaboration
tags:
  - manuscript
  - publication
  - research
  - citations
  - reproducibility
tasks:
  - create a living manuscript page
  - update publication claims and evidence
  - maintain figure and table registries
  - audit inline citations
  - document reproducibility and limitations
use_when:
  - The user asks to prepare, update, review, or keep current a manuscript or project publication page.
  - A research project needs structured publication claims, experiments, figures, tables, references, reproducibility notes, limitations, or readiness tracking.
  - Collaborators need a shareable HTML manuscript page and evidence files that can evolve with the project.
do_not_use_when:
  - The user only wants a short status summary with no persistent manuscript artifact.
  - The task is only copyediting text and does not change project substance or publication readiness.
  - The user needs journal submission-system actions, authorship decisions, or legal publication advice.
inputs:
  - project goals, methods, experiments, results, claims, limitations, and collaboration context
  - existing publication files or a project root where they should be created
  - references, figure evidence, table provenance, and citation requirements when literature claims are present
outputs:
  - project_publication.html
  - publication_claims.json
  - publication_experiments.json
  - publication_figures.json
  - publication_tables.json
  - publication_references.bib
  - publication_updates.jsonl
examples:
  - Use manuscript-builder to create a project_publication.html page for this research project.
  - Update the manuscript claims, experiment log, and limitations after these benchmark results.
  - Audit inline citations in project_publication.html before I share it with collaborators.
related_skills:
  - project-retrospective
  - clinical-statistical-expert
risk_level: low
permissions:
  - read local project manuscript and evidence files
  - write local publication files when the user requests manuscript maintenance
  - run bundled local helper scripts for file initialization and citation audits
page_title: Manuscript Builder Skill - Living Research Manuscripts and Publication Evidence for Codex
meta_description: Install the Manuscript Builder Skill for Codex to maintain project_publication.html, structured publication evidence files, citation audits, reproducibility notes, and collaborator-ready research manuscripts.
---

# Manuscript Builder

## What This Skill Does

Use this skill to keep a project publication-ready as work happens. The primary
artifact is `project_publication.html`, a polished living manuscript page that
can be shared at any time. Structured files preserve the evidence needed to
support claims, experiments, figures, tables, references, and update history.

## Safe Default Behavior

Default to local, evidence-preserving manuscript maintenance. Update manuscript
files only when project substance changed, keep claims tied to evidence, and
mark missing citations visibly instead of inventing references. Do not submit,
upload, email, or otherwise publish a manuscript externally unless the user
explicitly asks for that separate action and the destination is clear.

## Core Rule

Update manuscript files only when project substance changed. Capture goals,
motivation, methods, experiments, results, claims, limitations, citations,
figures, tables, reproducibility, data availability, code availability, and
publication readiness. Do not capture noise: status-only replies, ordinary
debugging chatter, typo fixes, command attempts with no lasting relevance, or
clarifications that only resolve a miscommunication.

When the user's wording is ambiguous, infer the intended project meaning and
confirm it in the response. A user trying to fix something may be correcting a
miscommunication rather than making a major project change.

## Citation Discipline

Use refereed-journal citation practices for scholarly prose. A bibliography or
reference list alone is not enough. Any sentence or clause that summarizes prior
work, reports a published result, gives a literature-derived statistic, names a
paper's finding, or compares the project with prior methods must include an
inline citation near the claim.

For HTML manuscripts, default to numeric bracket citations such as `[1]` or
hyperlinked bracket citations such as `<a href="#ref-key">[1]</a>`. Author-year
phrasing is fine in the prose, but it should still carry an inline bracket
citation unless the user explicitly asks for another venue style. If the source
is known but the exact reference has not been added yet, write a visible marker
such as `[citation needed: Han et al. ISBI 2018]` rather than leaving the claim
uncited. Do not invent citations.

Before handing off a manuscript with literature, background, related-work,
discussion, or comparative claims, run a citation audit or explicitly report why
it could not be run. The audit should check for uncited literature paragraphs,
orphan inline citations, and references listed without corresponding in-text
callouts.

## Files

Maintain these files at the project root unless the user gives another location:

- `project_publication.html`: shareable living manuscript page.
- `publication_claims.json`: scientific and technical claims with evidence.
- `publication_experiments.json`: planned, running, and completed experiment
  records.
- `publication_figures.json`: figure registry and caption evidence.
- `publication_tables.json`: table registry and data provenance.
- `publication_references.bib`: BibTeX references.
- `publication_updates.jsonl`: dated update log, one JSON object per line.

Use `assets/project_publication_template.html` when creating the HTML file.
Use `scripts/update_project_publication.py` to create missing files and append
update-log entries.

## Workflow

1. Inspect the project and existing publication files.
2. Decide whether the current task changed publication-relevant substance.
3. If files are missing, run:

```powershell
python <path-to-this-skill>\scripts\update_project_publication.py --project .
```

If the skill is installed globally, the script is usually under
`%USERPROFILE%\.codex\skills\manuscript-builder\scripts\update_project_publication.py`.
If the skill is stored in a project, the script may be under
`skills\manuscript-builder\scripts\update_project_publication.py`. Use the
available Python executable if `python` is not on PATH.

4. Edit `project_publication.html` directly when the readable manuscript should
   change.
5. Update the relevant structured files:
   - claims for new or changed assertions,
   - experiments for evaluation plans or results,
   - figures for visual evidence and captions,
   - tables for tabular evidence and source data,
   - references for citations,
   - updates for a short dated log entry.
6. For literature-bearing edits, audit inline citations before wrap-up. Prefer:

```powershell
python <path-to-this-skill>\scripts\audit_inline_citations.py --html project_publication.html
```

If `python` is unavailable, use the available bundled Python executable. Treat
uncited prior-work claims as manuscript defects to fix or mark with
`[citation needed: source]`.
7. At wrap-up, state whether manuscript files were updated, list weak areas, and
   suggest the next steps most likely to improve publication readiness.

## Venue Style

Keep `project_publication.html` as a venue-aware manuscript, not a rigid
submission clone. It should be readable and serious now, while retaining enough
structure to adapt later.

Emphasize Nature-style strengths:

- broad motivation and significance,
- concise contribution narrative,
- clear methods and reporting standards,
- data and code availability,
- figure-first communication,
- careful limitations and competing-interest statements.

Emphasize NeurIPS-style strengths:

- explicit problem formulation,
- reproducible methods and experiments,
- baselines, ablations, metrics, and uncertainty,
- limitations, ethics, and societal impact,
- transparent dataset, code, and model documentation.

## References

Read `references/section_guide.md` when deciding how to fill manuscript
sections. Read `references/file_schemas.md` when editing the structured files.
Read `references/citation_practices.md` before adding or revising Background,
Related Work, Discussion, or any literature-derived claim.

Read `references/agents_hook.md` when a project needs an `AGENTS.md` rule to
keep manuscript documentation current.
