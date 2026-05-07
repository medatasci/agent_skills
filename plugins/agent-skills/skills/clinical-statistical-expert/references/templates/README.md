# Clinical Disease Chapter Templates

These templates define the repeatable workflow for building disease chapters in
the `clinical-statistical-expert` skill. They are packaged with the skill so a
human reviewer, Codex agent, or future publishing pipeline can inspect the same
standards that were used to create the chapter.

Use this folder when you need to understand which template creates which
artifact, rebuild a disease chapter process, or check whether a new chapter is
still aligned with the expected structure.

## Template Map

| Layer | Template Or Standard | Output Artifact | Purpose |
| --- | --- | --- | --- |
| Disease Chapter | [`disease.md.tmpl`](disease.md.tmpl) | `references/diseases/<disease>.md` | Defines the human-readable and agent-usable disease chapter structure. |
| Research Plan | [`disease-research-plan.md.tmpl`](disease-research-plan.md.tmpl) | `references/diseases/<disease>.research-plan.md` | Guides source discovery, evidence collection, search iteration, and periodic status review. |
| Content Review | [`disease-review-criteria.md.tmpl`](disease-review-criteria.md.tmpl) | `references/diseases/<disease>.review.md` | Checks whether the chapter is weak, undersourced, too narrow, or missing key clinical-statistical content. |
| Figure Evidence | [`disease-figure-evidence.md.tmpl`](disease-figure-evidence.md.tmpl) | `references/diseases/<disease>.figures.json` and chapter figure notes | Records image evidence, reuse status, attribution, and supported chapter sections. |
| Source Manifest | [`disease.sources.schema.json`](disease.sources.schema.json) | `references/diseases/<disease>.sources.json` | Keeps source provenance, source type, reuse status, local cache status, and supported sections machine-readable. |
| Figure Manifest | [`disease.figures.schema.json`](disease.figures.schema.json) | `references/diseases/<disease>.figures.json` | Keeps figure provenance, reuse decisions, local file paths, and clinical points machine-readable. |

## Recommended Workflow

1. Start with `disease-research-plan.md.tmpl` and create a disease-specific
   research plan before drafting the chapter.
2. Record sources with `python -m skillforge source-archive`.
3. Record image evidence with `python -m skillforge figure-evidence`.
4. Draft or update `references/diseases/<disease>.md` using
   `disease.md.tmpl` as the structure.
5. Review the draft with `disease-review-criteria.md.tmpl`.
6. Render a preview with `python -m skillforge disease-preview <disease>`.
7. Check template conformance before publishing.

```text
python -m skillforge disease-template-check <disease> --json
python -m skillforge disease-template-check --json
python -m skillforge disease-template-check <disease> --strict --json
```

The default checker uses conceptual section conformance so mature chapters can
use clearer clinical headings without failing the workflow. Use `--strict` when
you need an exact heading-by-heading comparison with `disease.md.tmpl`.

