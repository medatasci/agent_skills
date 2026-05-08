# `skillforge/clinical_statistical_expert.py`

## Purpose

`clinical_statistical_expert.py` supports clinical-statistical disease chapter
workflows. It renders a disease Markdown chapter, source manifest, and figure
manifest into a single HTML preview that is easier for a human clinical reviewer
to inspect. It can also render a disease-research project homepage from a
`manifest.json`, create a downloaded-assets gallery, link existing disease HTML
pages back to those project pages, conservatively download explicitly reusable
figure assets, and check disease chapters against the packaged templates before
publication.

The preview is intentionally local and static. It does not run clinical models,
download source pages, or make patient-specific decisions.

## Public Interface

Top-level CLI:

```text
python -m skillforge disease-preview <disease> --json
python -m skillforge disease-homepage --project-root docs/clinical-statistical-expert/mr-rate-disease-research --json
python -m skillforge download-reusable-assets --project-root docs/clinical-statistical-expert/mr-rate-disease-research --json
python -m skillforge disease-template-check <disease> --json
python -m skillforge disease-template-check --json
python -m skillforge evidence-query-pack <target-concept> --modality MRI --json
```

Optional paths:

```text
python -m skillforge disease-preview gliosis --disease-dir docs/clinical-statistical-expert/diseases --output docs/clinical-statistical-expert/reports/gliosis.html --json
python -m skillforge disease-homepage --project-root docs/clinical-statistical-expert/mr-rate-disease-research --no-link-disease-pages --json
python -m skillforge download-reusable-assets --project-root docs/clinical-statistical-expert/mr-rate-disease-research --dry-run
python -m skillforge download-reusable-assets --project-root docs/clinical-statistical-expert/mr-rate-disease-research --disease cerebral-infarction --json
```

Python API:

```python
from skillforge.clinical_statistical_expert import disease_homepage, disease_preview, disease_template_check
from skillforge.clinical_statistical_expert import download_reusable_assets
from skillforge.clinical_statistical_expert import evidence_query_pack
```

## Inputs

- disease name or slug
- disease chapter Markdown file named `<disease>.md`
- optional `<disease>.sources.json` source manifest
- optional `<disease>.figures.json` figure manifest
- optional output HTML path
- disease research project root containing `manifest.json`, `diseases/`, and
  `reports/` when generating a project homepage
- optional homepage and downloaded-asset-gallery output paths
- optional disease slug when downloading reusable assets
- optional template directory when checking conformance
- target concept, expert lens, expert role, modality, or evidence type when
  generating source-discovery query packs

## Outputs

- static HTML preview under `docs/clinical-statistical-expert/reports/` by
  default
- project homepage, usually `reports/all-diseases.html`
- downloaded local asset gallery, usually `reports/assets.html`
- JSON summary with chapter path, output path, source count, image-candidate
  count, and local figure count
- JSON project-homepage summary with disease counts, downloaded asset counts,
  linked disease page count, and completed-disease asset gaps
- downloaded local image assets when figure manifests already record direct
  image references, explicit reusable license text, and a local-embedding reuse
  status
- `download-reusable-assets.json` review report summarizing downloaded,
  already-local, skipped, and failed figure records
- JSON template-check summary with per-chapter required checks, advisory
  checks, missing conceptual sections, and strict heading differences when
  requested
- JSON evidence-query pack with basic and advanced expert-framed prompts,
  search variants, source-type suggestions, and capture notes

## Side Effects

- Writes the requested HTML preview file.
- Writes `all-diseases.html` and `assets.html` for a disease research project.
- `download-reusable-assets` writes only image assets whose figure records
  already have explicit reusable licensing and local reuse permission. Link-only
  and needs-review records are preserved as metadata, not downloaded.
- `download-reusable-assets` may access the network only for direct image URLs
  recorded in eligible figure manifests. Use `--dry-run` for a read-only review.
- Updates existing disease HTML pages with links to the project homepage and
  downloaded-assets gallery unless `--no-link-disease-pages` is supplied.
- Reads local Markdown and JSON artifacts.
- Reads packaged clinical-statistical templates.
- Evidence query packs are read-only deterministic prompt/query generation.
- Does not modify source manifests, source caches, or skill packages.

## Cross-Platform Notes

The module uses `pathlib` and does not invoke shell commands. Markdown image and
link paths are resolved relative to the source chapter and emitted as portable
relative paths when possible.

## Tests

Relevant tests live in:

```text
tests/test_skillforge.py
```
