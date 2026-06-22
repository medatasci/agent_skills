# Publication File Schemas

All structured files are placeholders at creation time. Replace placeholder text
with project-specific content as evidence becomes available.

## publication_claims.json

Tracks claims that may appear in the manuscript.

Important fields:

- `id`: stable claim identifier, such as `claim-001`.
- `claim`: specific scientific or technical assertion.
- `status`: `placeholder`, `draft`, `supported`, `needs-evidence`,
  `rejected`, or `retired`.
- `evidence`: artifacts, experiments, figures, tables, citations, or analyses
  supporting the claim.
- `missing_evidence`: what still needs to be shown.
- `risks`: what could weaken or invalidate the claim.
- `linked_experiments`, `linked_figures`, `linked_tables`: identifiers in other
  publication files.

## publication_experiments.json

Tracks every planned, running, completed, or abandoned experiment.

Important fields:

- `id`: stable experiment identifier, such as `exp-001`.
- `research_question`: question the experiment answers.
- `hypothesis`: expected outcome and rationale.
- `status`: `planned`, `running`, `completed`, `blocked`, or `abandoned`.
- `datasets`: datasets, cohorts, source repositories, or input files.
- `methods`: algorithms, workflows, commands, models, or analysis procedures.
- `baselines`: comparator methods or reference conditions.
- `metrics`: primary and secondary metrics.
- `statistical_plan`: uncertainty, tests, confidence intervals, or comparison
  plan.
- `results_summary`: evidence-backed result summary.
- `artifacts`: output files, logs, notebooks, plots, tables, or reports.
- `reproducibility_notes`: environment, commands, seeds, versions, and expected
  outputs.
- `limitations`: experiment-specific weaknesses.

## publication_figures.json

Tracks figures and their evidence.

Important fields:

- `id`: stable figure identifier, such as `fig-001`.
- `title`: working figure title.
- `intended_message`: what the figure should communicate.
- `file_path`: figure image or source file.
- `source_data`: data or artifact used to create the figure.
- `caption`: manuscript-ready caption draft.
- `alt_text`: accessibility text.
- `quality_checks`: resolution, readability, permissions, and source-data checks.

## publication_tables.json

Tracks tables and their source data.

Important fields:

- `id`: stable table identifier, such as `table-001`.
- `title`: working table title.
- `purpose`: why the table belongs in the manuscript.
- `columns`: planned or actual columns.
- `source_data`: data or artifact used to populate the table.
- `statistical_notes`: tests, uncertainty, denominators, or aggregation rules.

## publication_references.bib

Stores BibTeX references. Do not invent citations. Add placeholders only when a
specific missing citation is known.

## publication_updates.jsonl

Stores one JSON object per update. Keep entries short and factual. Include:

- `timestamp`
- `summary`
- `changed_files`
- `weak_areas`
- `next_steps`
