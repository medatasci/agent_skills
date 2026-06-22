# AGENTS.md Manuscript Hook

Use this text when adding manuscript maintenance behavior to a project-level
`AGENTS.md` file.

```md
## Manuscript Documentation Maintenance

If this project contains `project_publication.html`, publication files, or the
`manuscript-builder` skill is relevant, keep manuscript documentation current
after substantive project work.

Use the `manuscript-builder` skill's
`assets/project_publication_template.html` file when creating
`project_publication.html`. Maintain the related publication files when they
exist:

- `publication_claims.json`
- `publication_experiments.json`
- `publication_figures.json`
- `publication_tables.json`
- `publication_references.bib`
- `publication_updates.jsonl`

Update manuscript documentation when work changes project goals, motivation,
methods, experiments, results, figures, tables, claims, limitations, citations,
data availability, code availability, reproducibility, ethics, privacy, safety,
or publication readiness.

Infer the user's intended project meaning before updating publication files.
Confirm meaningful interpretation choices in the response. Do not capture noise:
brief conversational replies, status-only messages, ordinary command attempts,
minor typo fixes, or corrections that only resolve a miscommunication. When the
user is trying to fix something, decide whether it represents a real project
change or just a clarification.

At wrap-up for substantive project work:

1. State whether manuscript files were updated.
2. Identify weak manuscript areas, missing evidence, or unclear claims.
3. Suggest next steps most likely to improve publication readiness.
```
