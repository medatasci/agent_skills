# Clinical Statistical Expert Skill Design Card

## Purpose

`clinical-statistical-expert` is a SkillForge-authored clinical research skill,
not a wrapper around a single upstream code repository. It uses authoritative
medical imaging and clinical-statistical sources to support progressive disease
chapters, starting with gliosis in the brain.

## Source Context Map

| Source context | How it informs the skill | Public artifact |
| --- | --- | --- |
| SkillForge requirements | Defines disease chapter structure, figure evidence, source archive, preview, and publication workflow | `requirements.md` |
| Clinical-statistical requirements doc | Defines progressive disease and method references plus disease chapter maturity expectations | `docs/clinical-statistical-expert.md` |
| Disease chapter templates | Provide reusable structure for disease chapters, research plans, reviews, figure evidence, and source manifests | `skillforge/templates/clinical-statistical-expert/` |
| Gliosis source and figure manifests | Preserve evidence provenance, local-cache status, figure reuse status, and remaining gaps | `skills/clinical-statistical-expert/references/diseases/` |
| Gliosis disease chapter | Provides the first disease-specific reference for brain MRI gliosis appearance, mimics, report language, and statistical implications | `skills/clinical-statistical-expert/references/diseases/gliosis.md` |

## Candidate Skill Table

| Candidate skill | Decision | Rationale |
| --- | --- | --- |
| Clinical Statistical Expert | Implemented | Parent routing skill for clinical-statistical reasoning, disease references, method references, and disease chapter workflow. |
| Gliosis disease sub-expert | Implemented as progressive reference | Best packaged as `references/diseases/gliosis.md` rather than a standalone skill so it can share the parent clinical-statistical workflow. |
| Statistical method sub-experts | Planned references | Better as progressively loaded method files until there is enough executable or reusable behavior for standalone skills. |
| Disease chapter generator | Implemented as workflow plus helpers | Packaged through templates and deterministic CLI helpers rather than a separate skill for now. |

## Source Version Status

Status: unpinned by design.

This is not a repo-derived executable skill with one source commit. Source
provenance is tracked through committed requirements, templates, disease
chapters, `*.sources.json`, and `*.figures.json` manifests. Web sources should
be refreshed and re-reviewed when disease chapters are updated.

## Execution Surface

The skill is guidance plus local SkillForge helper commands. It does not run
clinical models or medical image inference.

Implemented commands used by the workflow:

```text
python -m skillforge source-archive <disease> ...
python -m skillforge figure-evidence <disease> ...
python -m skillforge disease-preview <disease> --json
python -m skillforge evaluate clinical-statistical-expert --json
```

## Dependencies

- Python standard library for the current preview, source-manifest, and
  figure-manifest helpers.
- No model weights, GPU runtime, credentials, or private data access are
  required.
- Network access is needed only when the user approves source retrieval or web
  research.

## Smoke Test Plan

Expected command:

```text
python -m skillforge disease-preview gliosis --json
python -m skillforge evaluate clinical-statistical-expert --json
```

Skip condition:
Skip source download or image download smoke tests when network access,
permissions, or reuse rights are not available. The local preview and
evaluation should still run from committed artifacts.

## Current Readiness

Ready for review as a developing clinical-statistical skill. The packaged
gliosis chapter has 34 source records, 54 image candidates, 3 reusable local
figures, source and figure manifests, review artifacts, and an HTML preview.

Remaining maturity work:

- Extract more source-derived Findings and Impression language from the
  expanded source set.
- Qualitatively review the 51 link-only image candidates.
- Add more disease chapters and statistical method references.
- Add expert clinical review before calling any disease chapter mature.
