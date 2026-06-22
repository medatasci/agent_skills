# Codex Failure Analyst

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/codex-failure-analyst

Parent package:
Agent Skills Marketplace

Parent package repo URL:
https://github.com/medatasci/agent_skills

Distribution or marketplace:
SkillForge local catalog and Codex skill install workflow

## Parent Collection

Parent collection:
Agent Skills Marketplace

Collection URL:
https://github.com/medatasci/agent_skills

Categories:
Developer Tools, Agent Workflows, Evaluation

## What This Skill Does

Codex Failure Analyst audits local Codex Desktop history for repeated tool,
shell, runtime, sandbox, network, local app, and environment failures. It turns
rollout evidence into CSV, JSON, Markdown, and SQLite reports with root causes,
solution patterns, priority targets, efficiency estimates, repair-turn
estimates, unmapped repeated failures, and prevention guidance.

## Why You Would Call It

Call this skill when:

- You need evidence about recurring Codex tool or environment failures.
- A prevention skill update should be grounded in local failure history.
- You want to know which failure families cost the most rework.
- You need to review unmapped repeated failures before adding caller rules.

## Keywords

Codex failure analysis, Codex Desktop history, rollout diagnostics, shell
failure audit, sandbox failure, missing runtime, PowerShell diagnostics,
solution patterns, prevention rules, SQLite report.

## Search Terms

analyze Codex failures, audit shell_command failures, Codex repair turns,
Codex sandbox error report, missing Python failures, tool failure root cause,
Codex Desktop rollout history, update caller skill evidence.

## How It Works

The skill uses `scripts/analyze_codex_failures.py` to inspect local Codex
state and rollout JSONL files. It detects known PowerShell and environment
diagnostics, groups repeated failures, estimates repair burden, and writes
structured reports for follow-up analysis.

## API And Options

Common commands:

```powershell
& $py '<skill-dir>\scripts\analyze_codex_failures.py' --days 30 --mode all --output-dir 'reports'
& $py '<skill-dir>\scripts\analyze_codex_failures.py' --days 30 --mode quoting --output-dir 'reports'
& $py '<skill-dir>\scripts\analyze_codex_failures.py' --since 2026-05-17 --until 2026-06-17 --mode all
```

Resolve `$py` with `codex_app.load_workspace_dependencies` when available.

## Inputs And Outputs

Inputs:

- local Codex `state_5.sqlite` rollout index
- session JSONL rollout files with tool call and shell output records
- optional date window, mode, and output directory

Outputs:

- CSV event evidence
- JSON summary with solution patterns, priority targets, efficiency, and
  carry-forward guidance
- Markdown report
- SQLite database for follow-up queries
- prevention recommendations for caller skills

## Limitations

- It only analyzes available local Codex history.
- Detector coverage is strongest for PowerShell `shell_command` diagnostics.
- It should summarize aggregate diagnostics rather than expose sensitive raw
  transcript content.

## Examples

```text
Use codex-failure-analyst to analyze the last 30 days of Codex shell and tool failures.
```

```text
Audit Codex failures since June 1 and summarize which prevention rules should be promoted.
```

```text
Generate a focused report for repeated PowerShell quoting, missing runtime, and sandbox errors.
```

## Help And Getting Started

Install the skill with SkillForge, then ask Codex to run an analysis window.

```text
python -m skillforge install codex-failure-analyst --scope global
```

## How To Call From An LLM

Use plain language:

```text
Use codex-failure-analyst to analyze recent Codex tool and environment failures and summarize priority prevention targets.
```

## How To Call From The CLI

Run the bundled script through a resolved Python interpreter:

```powershell
& $py '<skill-dir>\scripts\analyze_codex_failures.py' --days 30 --mode all --output-dir 'reports'
```

## Trust And Safety

Risk level:
medium

Permissions:

- read local Codex state and rollout history files
- run the bundled Python analysis script
- write reports to the requested local output directory
- do not send rollout content, secrets, or private transcript text to external
  services without explicit approval

Data handling:
Prefer aggregate diagnostics and local report files. Treat raw rollout content
as private unless the user explicitly authorizes sharing.

Writes vs read-only:
The analysis reads local Codex history and writes local reports. It does not
modify Codex history.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

## Contributing

Contributions should add detectors only when the root cause is stable and the
prevention guidance is reusable. Use pull requests against the Agent Skills
Marketplace.

## Author

Marc Edgar / medatasci

## Citations

Not applicable. This skill analyzes local Codex workflow evidence.

## Related Skills

- `codex-efficient-caller`: compact prevention guidance for future calls.
- `powershell-caller`: Windows PowerShell command-shaping guidance.
- `powershell-failure-analyst`: focused PowerShell failure reporting.
