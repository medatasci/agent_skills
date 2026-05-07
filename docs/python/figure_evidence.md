# `skillforge/figure_evidence.py`

## Purpose

`figure_evidence.py` records clinical image evidence for disease chapters. It
lets a human or agent capture a source figure, citation, reuse status, supported
disease-section links, and an optional local image copy when reuse is explicitly
allowed.

The helper is intentionally conservative: it copies local image files only when
`reuse_status` is `ok-to-embed`. Otherwise it records a link-only or
review-needed entry and leaves the image outside the repository.

## Public Interface

Top-level CLI:

```text
python -m skillforge figure-evidence <disease> --figure-id <id> --source-title "<title>" --source-url <url> --figure-label "Figure 31" --license "CC BY 4.0" --reuse-status ok-to-embed --image-path <file> --clinical-point "<point>" --section "Primary Imaging Modality" --json
```

Python API:

```python
from skillforge.figure_evidence import record_figure_evidence
```

## Inputs

- disease name
- figure ID
- source title and URL
- figure label or figure number
- license text
- reuse status
- clinical point supported by the image
- optional supported disease sections
- optional local image path
- optional manifest path and assets directory

## Outputs

- JSON manifest entry
- optional copied image under the configured assets directory
- Markdown snippet for the disease chapter
- warnings when an image was not copied or reuse metadata is incomplete

## Side Effects

- Writes or updates a JSON figure manifest.
- Copies an image file only when reuse is explicitly allowed.
- Does not download images.
- Does not verify copyright or license correctness.

## Cross-Platform Notes

All paths use `pathlib` and should work on Windows, macOS, and Linux. The helper
does not invoke shell commands.

## Tests

Relevant tests live in:

```text
tests/test_skillforge.py
```
