---
name: codex-failure-analyst
owner: medatasci
description: >-
  Use when Codex needs to audit local Codex Desktop history for tool, shell,
  runtime, sandbox, network, local app, or environment failures and turn them
  into root-cause analysis, reusable solution patterns, priority targets, and
  prevention-skill updates. Produces CSV, JSON, Markdown, and SQLite reports
  from state_5.sqlite rollout paths and session JSONL tool outputs. Current
  detector coverage includes Windows PowerShell shell_command diagnostics,
  quoting/parser mistakes, missing python, profile noise, path assumptions,
  sandbox boundaries, optional CLI availability, and rework-turn estimates.
title: Codex Failure Analyst
short_description: Analyze Codex Desktop tool and environment failures into root causes, patterns, priority targets, and prevention updates.
expanded_description: Audits local Codex Desktop state and rollout history to find repeated tool, shell, runtime, sandbox, network, local app, and environment failures. It produces CSV, JSON, Markdown, and SQLite reports with root-cause classes, solution patterns, priority targets, efficiency estimates, repair-turn estimates, unmapped repeated failures, and guidance for updating prevention skills.
aliases:
  - Codex failure audit
  - Codex shell failure analysis
  - tool failure root cause
  - Codex history diagnostics
  - environment failure analyst
  - prevention skill evidence
categories:
  - Developer Tools
  - Agent Workflows
  - Evaluation
tags:
  - codex
  - diagnostics
  - failure-analysis
  - powershell
  - sandbox
  - sqlite
  - shell
tasks:
  - audit Codex Desktop tool and shell failures
  - classify runtime, sandbox, network, filesystem, and local app failures
  - estimate repair turns and lost time from repeated failures
  - generate CSV, JSON, Markdown, and SQLite failure reports
  - identify solution patterns and priority targets
  - provide evidence for codex-efficient-caller updates
use_when:
  - Codex needs evidence about recurring tool, shell, runtime, sandbox, network, local app, or environment failures.
  - A prevention skill update should be grounded in local failure history instead of anecdote.
  - The user asks why Codex keeps failing in a local environment or wants a failure-pattern report.
  - Codex needs to review unmapped repeated failures before adding a new caller rule.
do_not_use_when:
  - The user has not allowed inspection of local Codex history or rollout files.
  - The task only needs one immediate command fix and no history analysis.
  - The user asks for general application log analysis outside Codex Desktop history.
  - The answer would expose secrets, private data, or sensitive transcript content instead of aggregated diagnostics.
inputs:
  - local Codex state_5.sqlite rollout index
  - session JSONL rollout files with tool call and shell output records
  - optional date window, mode, and output directory
outputs:
  - CSV event evidence
  - JSON summary with solution patterns, priority targets, efficiency, and carry-forward guidance
  - Markdown report
  - SQLite database for follow-up queries
  - prevention recommendations for caller skills
examples:
  - Use codex-failure-analyst to analyze the last 30 days of Codex shell and tool failures.
  - Audit Codex failures since June 1 and summarize which prevention rules should be promoted.
  - Generate a focused report for repeated PowerShell quoting, missing runtime, and sandbox errors.
related_skills:
  - codex-efficient-caller
  - powershell-caller
  - powershell-failure-analyst
risk_level: medium
permissions:
  - read local Codex state and rollout history files
  - run the bundled Python analysis script
  - write reports to the requested local output directory
  - do not send rollout content, secrets, or private transcript text to external services without explicit approval
page_title: Codex Failure Analyst Skill - Analyze Codex Tool And Environment Failures
meta_description: Use the Codex Failure Analyst skill to audit local Codex Desktop failures and produce root-cause reports, solution patterns, priority targets, and prevention guidance.
---

# Codex Failure Analyst

## What This Skill Does

Analyze local Codex Desktop history for repeated tool, shell, runtime,
sandbox, network, local app, and environment failures. The skill turns rollout
records into structured root-cause evidence, solution patterns, priority
targets, efficiency estimates, and prevention recommendations.

It is designed for improving caller skills and local automation reliability,
not for reading rollouts manually or exposing raw conversation content.

## Safe Default Behavior

Default to local, evidence-preserving analysis. Read only the Codex state and
rollout files needed for the requested window, write reports under a local
output directory, and summarize aggregate diagnostics instead of quoting
sensitive transcript content.

Do not inspect local Codex history when the user has not authorized it. Do not
send rollout data, secrets, private content, or environment details to external
services without explicit approval.

Analyze Codex tool and environment failures without manually reading rollouts.

## Workflow

1. Resolve Python with `codex_app.load_workspace_dependencies` when available.
2. Run `scripts/analyze_codex_failures.py`.
3. Read `summary.solution_patterns` first for class-level fixes.
4. Read `summary.priority_targets` for evidence/severity/generality/confidence/token/rework ranking.
5. Read `summary.efficiency` for shell-call efficiency, detected-event efficiency, lost-time estimate, and formula notes.
6. Read `summary.efficiency_by_error_family` to see which error families consume the most repair turns.
7. Read `summary.carry_forward` for rule-level root causes.
8. Review `summary.unmapped_repeated_failures` for new pattern candidates.
9. Query the SQLite output for group-by analysis across runs or labels.
10. Use CSV for event-level evidence and thread clustering.

## Commands

Last 30 days, all PowerShell diagnostics:

```powershell
& $py '<skill-dir>\scripts\analyze_codex_failures.py' --days 30 --mode all --output-dir 'reports'
```

Focused quoting/parser scan:

```powershell
& $py '<skill-dir>\scripts\analyze_codex_failures.py' --days 30 --mode quoting --output-dir 'reports'
```

Specific inclusive date window:

```powershell
& $py '<skill-dir>\scripts\analyze_codex_failures.py' --since 2026-05-17 --until 2026-06-17 --mode all
```

## Notes

- Uses `~/.codex/state_5.sqlite` to find rollout paths, then parses rollout JSONL tool call/output pairs.
- Current detector is `powershell-shell-command`, which analyzes `functions.shell_command` output from Windows PowerShell.
- `mode=all` includes PowerShell diagnostics such as `FullyQualifiedErrorId`, `CategoryInfo`, `At line`, profile/security noise, missing `python`, path errors, and parser errors.
- `mode=quoting` is stricter: nonzero shell outputs with live PowerShell parser/quoting diagnostics.
- Root-cause fields are `detector_id`, `tool_name`, `tool_family`, `runtime_environment`, `diagnostic_language`, `error_family`, `error_class`, `rule_id`, `root_cause`, `prevention`, `rework_turns_to_resolve`, `repair_detection_mode`, `repair_confidence_label`, `severity_label`, `confidence_label`, `summary.carry_forward`, `summary.solution_patterns`, `summary.priority_targets`, and `summary.unmapped_repeated_failures`.
- Efficiency fields are in `summary.efficiency`: `shell_call_efficiency_percent`, `detected_event_efficiency_percent`, `lost_time_percent`, `efficiency_percent`, `unique_repair_turns_estimate`, `repair_turn_burden_percent`, and formula notes.
- Family-level efficiency fields are in `summary.efficiency_by_error_family` and SQLite `efficiency_by_error_family`.
- `lost_time_percent` is `(unique shell output indexes inside detected-event repair windows / shell_calls_seen) * 100`; `efficiency_percent` is `100 - lost_time_percent`.
- SQLite tables include `runs`, `events`, `rule_summary`, `pattern_summary`, `priority_targets`, and `efficiency_by_error_family`; views include `v_efficiency_summary`, `v_lost_time_by_error_family`, `v_rule_priority`, `v_pattern_priority`, `v_event_classes`, and `v_repair_modes`.
- For durable pattern guidance and skill-length tradeoffs, read `references/solution-patterns.md` only when updating prevention skills or explaining the method.
- For periodic self-improvement, run a fresh 30-60 day scan, promote repeated unmapped failures, distill prevention skill updates, rerun the same window, then compare rates per 100 shell calls.
- For compact prevention guidance, update `$codex-efficient-caller`; for Windows PowerShell command details, use `$powershell-caller`.
