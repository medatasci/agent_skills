# Manuscript Section Guide

Use this guide when filling or reviewing `project_publication.html`.

## Public-Facing Sections

### Title And Project Summary

State the project title, short summary, current status, target venues, and last
updated date. This section should be safe to share with a reviewer, collaborator,
or program committee member.

### Research Goal

State the central research or engineering goal in one to three sentences. Explain
what success makes possible.

### Motivation And Need

Explain why the problem matters, who is affected, what current work fails to
solve, and why now is the right time to address it.

### Main Contributions

List specific contributions. Each contribution should eventually map to a claim
in `publication_claims.json`.

### Abstract

Maintain a concise working abstract. Prefer a broad significance opening,
specific method or system description, key results when available, and a careful
conclusion.

### Background And Related Work

Summarize the prior work needed to understand the contribution. Use inline
numeric bracket citations near every prior-work claim, especially specific
statistics, study outcomes, and comparisons. Keep visible placeholders such as
`[citation needed: source]` for missing citations rather than inventing
references. Do not rely on an end-of-section bibliography alone.

### Methods

Describe study design, algorithms, workflows, implementation, analysis plan,
human review, and any AI-agent use that affects the research process.

### Evaluation And Experiments

Describe research questions, hypotheses, baselines, datasets, metrics,
statistical plan, ablations, robustness checks, and reproducibility steps.

### Results

Report results only when evidence exists. Link each major result to an
experiment, figure, table, claim, or artifact.

### Limitations And Risks

State what is unknown, fragile, unvalidated, biased, underpowered,
non-generalizable, or dependent on assumptions.

### Ethics, Privacy, And Safety

Document privacy constraints, human-subject concerns, dataset permissions,
license constraints, model risks, clinical risks, misuse risks, and mitigation.

### Reproducibility

Record code, environment, commands, seeds, data versions, model versions,
hardware, and expected outputs when available.

### Data And Code Availability

State what is available, where it is available, under what restrictions, and what
cannot be shared.

## Evidence Sections

### Claim And Evidence Record

Summarize the strongest claims, current evidence, missing evidence, and risk.

### Experiment Record

Summarize planned, running, and completed experiments. Keep full detail in
`publication_experiments.json`.

### Figure And Table Records

List figures and tables, their intended message, source data, status, and quality
checks.

### Publication Readiness And Next Steps

Identify weak areas and concrete next actions. Favor evidence-generating next
steps over generic writing tasks.

## Venue Notes

Nature-family submissions usually require careful availability statements,
author contributions, competing interests, methods, figure legends, and reporting
transparency.

NeurIPS submissions usually require strong reproducibility, experimental detail,
dataset/model transparency, limitations, ethics, and checklist readiness.
