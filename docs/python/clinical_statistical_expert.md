# `skillforge/clinical_statistical_expert.py`

## Purpose

`clinical_statistical_expert.py` supports clinical-statistical disease chapter
workflows. It renders a disease Markdown chapter, source manifest, and figure
manifest into a single HTML preview that is easier for a human clinical reviewer
to inspect, and it checks disease chapters against the packaged templates before
publication.

The preview is intentionally local and static. It does not run clinical models,
download sources, or make patient-specific decisions.

## Public Interface

Top-level CLI:

```text
python -m skillforge disease-preview <disease> --json
python -m skillforge disease-template-check <disease> --json
python -m skillforge disease-template-check --json
```

Optional paths:

```text
python -m skillforge disease-preview gliosis --disease-dir docs/clinical-statistical-expert/diseases --output docs/clinical-statistical-expert/reports/gliosis.html --json
```

Python API:

```python
from skillforge.clinical_statistical_expert import disease_preview, disease_template_check
```

## Inputs

- disease name or slug
- disease chapter Markdown file named `<disease>.md`
- optional `<disease>.sources.json` source manifest
- optional `<disease>.figures.json` figure manifest
- optional output HTML path
- optional template directory when checking conformance

## Outputs

- static HTML preview under `docs/clinical-statistical-expert/reports/` by
  default
- JSON summary with chapter path, output path, source count, image-candidate
  count, and local figure count
- JSON template-check summary with per-chapter required checks, advisory
  checks, missing conceptual sections, and strict heading differences when
  requested

## Side Effects

- Writes the requested HTML preview file.
- Reads local Markdown and JSON artifacts.
- Reads packaged clinical-statistical templates.
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
