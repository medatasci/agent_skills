# PowerShell Failure Analyst

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/powershell-failure-analyst

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

PowerShell Failure Analyst audits local Codex Desktop rollout history for
Windows PowerShell `shell_command` failures. It turns parser errors, quoting
mistakes, missing runtime assumptions, path failures, profile noise, sandbox
boundaries, and repeated repair loops into structured CSV, JSON, Markdown, and
SQLite reports.

## Why You Would Call It

Call this skill when:

- You need evidence about recurring Windows PowerShell failures in Codex.
- A `powershell-caller` rule should be updated from local failure history.
- You want a focused report on quoting, parser, missing Python, path, profile,
  or sandbox issues.
- You need to review unmapped PowerShell failures before adding a new rule.

## Keywords

PowerShell failure analysis, Codex shell_command failures, parser errors,
quoting mistakes, missing Python, sandbox noise, profile noise, repair turns,
PowerShell diagnostics, prevention rules.

## Search Terms

analyze Codex PowerShell failures, audit shell_command parser errors, PowerShell
quoting failure report, missing Python in PowerShell, Codex sandbox PowerShell
errors, update powershell-caller evidence, PowerShell repair turns.

## How It Works

The skill uses `scripts/analyze_powershell_failures.py` to inspect local Codex
state and rollout JSONL files. It detects PowerShell-specific diagnostics,
groups repeated failure classes, estimates repair burden, and writes reports
that can guide updates to `powershell-caller`.

## API And Options

Common commands:

```powershell
& $py '<skill-dir>\scripts\analyze_powershell_failures.py' --days 30 --mode all --output-dir 'reports'
& $py '<skill-dir>\scripts\analyze_powershell_failures.py' --days 30 --mode quoting --output-dir 'reports'
& $py '<skill-dir>\scripts\analyze_powershell_failures.py' --since 2026-05-17 --until 2026-06-17 --mode all
```

Resolve `$py` with `codex_app.load_workspace_dependencies` when available.

## Inputs And Outputs

Inputs:

- local Codex `state_5.sqlite` rollout index
- session JSONL rollout files with `shell_command` call and output records
- optional date window, mode, and output directory

Outputs:

- CSV PowerShell failure evidence
- JSON summary with solution patterns, priority targets, and carry-forward
  guidance
- Markdown report
- SQLite database for follow-up queries
- prevention recommendations for `powershell-caller`

## Limitations

- It only analyzes available local Codex history.
- It is focused on Windows PowerShell shell_command diagnostics.
- It should summarize aggregate diagnostics rather than expose sensitive raw
  transcript content.

## Examples

```text
Use powershell-failure-analyst to analyze the last 30 days of Codex PowerShell command failures.
```

```text
Generate a focused quoting and parser failure report for recent shell_command attempts.
```

```text
Audit PowerShell failures and recommend which powershell-caller rules should be promoted.
```

## Help And Getting Started

Install the skill with SkillForge, then ask Codex to run a PowerShell failure
analysis window.

```text
python -m skillforge install powershell-failure-analyst --scope global
```

## How To Call From An LLM

Use plain language:

```text
Use powershell-failure-analyst to analyze recent Codex PowerShell failures and summarize prevention targets.
```

## How To Call From The CLI

Run the bundled script through a resolved Python interpreter:

```powershell
& $py '<skill-dir>\scripts\analyze_powershell_failures.py' --days 30 --mode all --output-dir 'reports'
```

## Trust And Safety

Risk level:
medium

Permissions:

- read local Codex state and rollout history files
- run the bundled Python PowerShell failure-analysis script
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

Contributions should preserve focused PowerShell diagnostics and promote only
stable, reusable prevention guidance to `powershell-caller`.

## Author

Marc Edgar / medatasci

## Citations

Not applicable. This skill analyzes local Codex PowerShell workflow evidence.

## Related Skills

- `powershell-caller`: command-shaping guidance that uses the evidence.
- `codex-efficient-caller`: broader caller preflight and boundary guidance.
- `codex-failure-analyst`: broader Codex failure history analysis.
