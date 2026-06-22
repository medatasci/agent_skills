---
name: powershell-failure-analyst
owner: medatasci
description: >-
  Use when Codex needs to audit local Codex Desktop history for Windows
  PowerShell failures, quoting/parser mistakes, sandbox/profile noise, missing
  python, or recurring shell_command problems. Produces compact CSV, JSON,
  Markdown, and SQLite reports with root-cause analysis, solution patterns,
  rework-turn estimates, priority scoring, unmapped repeated failures, and
  prevention recommendations from state_5.sqlite rollout paths and session JSONL
  tool outputs. Supports periodic self-improvement cycles for updating compact
  prevention skills from observed failures.
title: PowerShell Failure Analyst
short_description: Analyze recurring Codex Windows PowerShell failures into root causes, solution patterns, and prevention guidance.
expanded_description: Audits local Codex Desktop rollout history for Windows PowerShell shell_command failures, parser and quoting mistakes, sandbox or profile noise, missing Python, path assumptions, and recurring repair loops. It produces CSV, JSON, Markdown, and SQLite reports with root-cause classes, solution patterns, priority targets, rework-turn estimates, unmapped repeated failures, and guidance for improving PowerShell caller behavior.
aliases:
  - PowerShell failure audit
  - PowerShell shell_command analysis
  - Codex PowerShell diagnostics
  - PowerShell quoting failures
  - PowerShell parser error analysis
  - PowerShell prevention report
categories:
  - Developer Tools
  - Agent Workflows
  - Evaluation
tags:
  - powershell
  - windows
  - codex
  - diagnostics
  - failure-analysis
  - shell
  - sqlite
tasks:
  - audit Codex PowerShell shell_command failures
  - classify parser, quoting, missing runtime, path, profile, and sandbox failures
  - estimate repair turns from repeated PowerShell failures
  - generate CSV, JSON, Markdown, and SQLite PowerShell diagnostics
  - identify PowerShell solution patterns and priority targets
  - provide evidence for powershell-caller updates
use_when:
  - Codex needs evidence about recurring Windows PowerShell shell_command failures.
  - A PowerShell caller rule should be updated from local failure history.
  - The user asks why Codex keeps failing on PowerShell commands or wants a focused PowerShell failure report.
  - Codex needs to review unmapped PowerShell failures before adding a new command-shaping rule.
do_not_use_when:
  - The user has not allowed inspection of local Codex history or rollout files.
  - The task only needs one immediate PowerShell command correction.
  - The shell failures are not PowerShell-related.
  - The answer would expose secrets, private data, or sensitive transcript content instead of aggregated diagnostics.
inputs:
  - local Codex state_5.sqlite rollout index
  - session JSONL rollout files with shell_command call and output records
  - optional date window, mode, and output directory
outputs:
  - CSV PowerShell failure evidence
  - JSON summary with solution patterns, priority targets, and carry-forward guidance
  - Markdown report
  - SQLite database for follow-up queries
  - prevention recommendations for powershell-caller
examples:
  - Use powershell-failure-analyst to analyze the last 30 days of Codex PowerShell command failures.
  - Generate a focused quoting and parser failure report for recent shell_command attempts.
  - Audit PowerShell failures and recommend which powershell-caller rules should be promoted.
related_skills:
  - powershell-caller
  - codex-efficient-caller
  - codex-failure-analyst
risk_level: medium
permissions:
  - read local Codex state and rollout history files
  - run the bundled Python PowerShell failure-analysis script
  - write reports to the requested local output directory
  - do not send rollout content, secrets, or private transcript text to external services without explicit approval
page_title: PowerShell Failure Analyst Skill - Analyze Codex PowerShell Failures
meta_description: Use the PowerShell Failure Analyst skill to audit local Codex Desktop PowerShell failures and produce root-cause reports, solution patterns, and prevention guidance.
---

# PowerShell Failure Analyst

## What This Skill Does

Analyze local Codex Desktop history for recurring Windows PowerShell
`shell_command` failures. The skill turns parser errors, quoting mistakes,
missing runtime assumptions, path failures, profile noise, sandbox boundaries,
and repeated repair loops into structured root-cause reports and prevention
guidance.

It is designed to improve `powershell-caller` and related command-shaping
guidance, not to expose raw conversation content.

## Safe Default Behavior

Default to local, evidence-preserving analysis. Read only the Codex state and
rollout files needed for the requested window, write reports under a local
output directory, and summarize aggregate diagnostics instead of quoting
sensitive transcript content.

Do not inspect local Codex history when the user has not authorized it. Do not
send rollout data, secrets, private content, or environment details to external
services without explicit approval.

Analyze PowerShell failures in Codex history without manually reading rollouts.

## Workflow

1. Resolve Python with `codex_app.load_workspace_dependencies` when available.
2. Run `scripts/analyze_powershell_failures.py`.
3. Read `summary.solution_patterns` first for class-level fixes.
4. Read `summary.priority_targets` for evidence/severity/generality/confidence/token/rework ranking.
5. Read `summary.carry_forward` for rule-level root causes.
6. Review `summary.unmapped_repeated_failures` for new pattern candidates.
7. Query the SQLite output for group-by analysis across runs or labels.
8. Use CSV for event-level evidence and thread clustering.

## Commands

Last 30 days, all PowerShell diagnostics:

```powershell
& $py '<skill-dir>\scripts\analyze_powershell_failures.py' --days 30 --mode all --output-dir 'reports'
```

Focused quoting/parser scan:

```powershell
& $py '<skill-dir>\scripts\analyze_powershell_failures.py' --days 30 --mode quoting --output-dir 'reports'
```

Specific inclusive date window:

```powershell
& $py '<skill-dir>\scripts\analyze_powershell_failures.py' --since 2026-05-17 --until 2026-06-17 --mode all
```

## Notes

- Uses `~/.codex/state_5.sqlite` to find rollout paths, then parses rollout JSONL `shell_command` call/output pairs.
- `mode=all` includes PowerShell diagnostics such as `FullyQualifiedErrorId`, `CategoryInfo`, `At line`, profile/security noise, missing `python`, path errors, and parser errors.
- `mode=quoting` is stricter: nonzero shell outputs with live PowerShell parser/quoting diagnostics.
- Root-cause fields are `rule_id`, `root_cause`, `prevention`, `rework_turns_to_resolve`, `repair_detection_mode`, `repair_confidence_label`, `severity_label`, `confidence_label`, `summary.carry_forward`, `summary.solution_patterns`, `summary.priority_targets`, and `summary.unmapped_repeated_failures`.
- SQLite tables include `runs`, `events`, `rule_summary`, `pattern_summary`, and `priority_targets`; views include `v_rule_priority`, `v_pattern_priority`, `v_event_classes`, and `v_repair_modes`.
- For durable pattern guidance and skill-length tradeoffs, read `references/solution-patterns.md` only when updating prevention skills or explaining the method.
- For periodic self-improvement, run a fresh 30-60 day scan, promote repeated unmapped failures, distill prevention skill updates, rerun the same window, then compare rates per 100 shell calls.
- For command-shaping prevention, use the companion `$powershell-caller` skill.
