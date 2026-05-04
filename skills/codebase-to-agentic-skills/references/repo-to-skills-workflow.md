# Repo-To-Skills Workflow

Use this reference when converting a repository into candidate agentic skills.
The purpose is to make the work evidence-driven and hard to skip.

## Ordered Workflow

1. Define the user workflow goal, target users, expected inputs, expected
   outputs, and constraints.
2. Build a source-context map. Record what each important source artifact
   contributes to skill design, adapter design, LLM prompting, safety, tests,
   and publication claims.
3. Pin or record the source version. Include repo URL, source subdirectory,
   commit/tag/release, model card URL, license URL, and date inspected. If the
   source is unpinned, say so.
4. Create a candidate skill table from the source-context map. Every candidate
   should cite source evidence.
5. Create a readiness card before generating skill files.
6. Decide whether the repo should become one algorithm skill, several
   functional-block skills, a workflow skill, or a mixed package.
7. Split LLM and deterministic responsibilities.
8. Define runtime/deployment requirements if source code must actually run.
9. Create `SKILL.md`, `README.md`, `references/`, and `scripts/` as needed.
10. Run publication gates using source context as evidence.
11. Add smoke tests or documented smoke-test skip reasons.
12. Run `python -m skillforge build-catalog --json`.
13. Run `python -m skillforge evaluate <skill-id> --json`.
14. Review gaps, generated outputs, search results, source provenance, safety
    notes, and open questions.
15. Publish by pull request.

## What Must Not Be Skipped

- Source version pin or explicit unpinned-risk note.
- Source-context map.
- Candidate skill table.
- Readiness card.
- LLM vs deterministic responsibility split.
- Runtime/deployment plan for executable skills.
- Smoke test or documented skip reason.
- Publication evaluation.

## Evidence Rule

Do not create skill behavior, safety claims, citations, examples, CLI commands,
or catalog metadata that cannot be traced back to source context, user-provided
workflow requirements, or implemented adapter behavior.
