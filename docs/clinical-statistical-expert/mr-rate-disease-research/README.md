# MR-RATE Disease Research Workspace

This workspace tracks disease-related research for the MR-RATE pathology
categories used by the `clinical-statistical-expert` skill.

## Source Of Truth

The source category list comes from:

https://github.com/forithmus/MR-RATE/blob/main/data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing/06_pathology_classification/data/pathologies_snomed_map.json

The user prompt referred to 32 categories. The current source file contains 37
mapped categories, so this workspace includes all 37 until an explicit exclusion
decision is recorded.

## How To Resume

1. Open `manifest.json`.
2. Find the first disease whose `status` is not complete.
3. Work one disease and one phase at a time.
4. Update the disease folder, `manifest.json`, `TODO.md`, and a run log under
   `runs/` before stopping.

## Core Files

- `TODO.md`: human-readable work queue and definition of done.
- `manifest.json`: machine-readable restart state.
- `query-packs.json`: generated expert-framed source discovery prompts for each
  category.
- `cross-disease-differential-framework.md`: reusable MR-RATE comparator frame.
- `diseases/<slug>/research-plan.md`: disease-specific scope and checkpoint.
- `diseases/<slug>/sources.json`: source evidence manifest.
- `diseases/<slug>/differential-matrix.md`: MR-RATE-aware differential matrix.
- `runs/*.md`: execution logs.

## Status Meaning

- `not_started`: only the generated scaffold exists.
- `existing_chapter_needs_cross_disease_update`: a chapter exists, but it still
  needs this batch workflow's cross-category review.
- `authoritative_source_discovery_started`: URL-only source evidence and/or a
  first-pass differential matrix has been recorded.
- `source_review_started`: sources are being read and claim notes are being
  extracted.
- `chapter_draft_started`: a disease chapter is being drafted or updated.
- `ready_for_expert_review`: the disease chapter, sources, figures, differential
  matrix, and template review are complete enough for human expert review.

## Current Execution Notes

The initial run created scaffolds for all 37 categories. Source discovery has
started for the ischemic-vascular, hemorrhagic-vascular, and neoplasm/mass
clusters. Remaining clusters still need source discovery and differential
matrix work.
