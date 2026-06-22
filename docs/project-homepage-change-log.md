# Project Homepage Change Log

## 2026-06-22 - Add Manuscript Builder Skill

What changed:
Added `manuscript-builder` as a publishable SkillForge workflow skill and added
a homepage pointer under Featured Workflow Skills.

Why:
The skill helps collaborators keep research projects publication-ready with a
living manuscript page, structured evidence files, citation discipline, and
reproducibility notes.

Validation performed:
Passed `python -m skillforge build-catalog --json`; passed
`python -m skillforge validate skills\manuscript-builder --json`; passed
`python -m skillforge evaluate manuscript-builder --json` with score `100/100`.

Follow-up:
Review collaborator feedback after the first paper-authoring use and consider
adding venue-specific manuscript templates if repeated demand appears.
