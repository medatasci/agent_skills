# `skillforge/clinical_statistical_expert.py`

## Purpose

`clinical_statistical_expert.py` supports clinical-statistical disease chapter
workflows. The first helper renders a disease Markdown chapter, source manifest,
and figure manifest into a single HTML preview that is easier for a human
clinical reviewer to inspect.

The preview is intentionally local and static. It does not run clinical models,
download sources, or make patient-specific decisions.

## Public Interface

Top-level CLI:

```text
python -m skillforge disease-preview <disease> --json
```

Optional paths:

```text
python -m skillforge disease-preview gliosis --disease-dir docs/clinical-statistical-expert/diseases --output docs/clinical-statistical-expert/reports/gliosis.html --json
```

Python API:

```python
from skillforge.clinical_statistical_expert import disease_preview
```

## Inputs

- disease name or slug
- disease chapter Markdown file named `<disease>.md`
- optional `<disease>.sources.json` source manifest
- optional `<disease>.figures.json` figure manifest
- optional output HTML path

## Outputs

- static HTML preview under `docs/clinical-statistical-expert/reports/` by
  default
- JSON summary with chapter path, output path, source count, image-candidate
  count, and local figure count

## Side Effects

- Writes the requested HTML preview file.
- Reads local Markdown and JSON artifacts.
- Does not modify source manifests, figure manifests, source caches, or skill
  packages.
- Does not access the network.

## Cross-Platform Notes

The module uses `pathlib` and does not invoke shell commands. Markdown image and
link paths are resolved relative to the source chapter and emitted as portable
relative paths when possible.

## Tests

Relevant tests live in:

```text
tests/test_skillforge.py
```
