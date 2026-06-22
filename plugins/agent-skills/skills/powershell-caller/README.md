# PowerShell Caller

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/powershell-caller

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
Developer Tools, Agent Workflows, Safety And Review

## What This Skill Does

PowerShell Caller helps Codex shape Windows PowerShell commands that work in
Codex Desktop and CLI environments. It covers literal paths, quoted
executables, bundled runtime resolution, here-strings instead of Bash heredocs,
optional CLI probes, profile and execution-policy noise, native exit-code
handling, JSON object mutation, cmdlet semantics, and sandbox-aware file
operations.

## Why You Would Call It

Call this skill when:

- Codex needs to run a command through Windows PowerShell.
- A command includes paths with spaces, quoted executables, here-strings, JSON
  mutation, native tools, or optional CLIs.
- A previous command failed with parser, quoting, profile, execution-policy,
  missing runtime, or path diagnostics.
- Codex needs to use bundled Python or workspace dependencies from PowerShell.

## Keywords

PowerShell caller, Windows shell_command, Codex Desktop, PowerShell quoting,
literal path, bundled Python, here-string, native exit code, JSON mutation,
sandbox command.

## Search Terms

run PowerShell safely in Codex, fix shell_command parser error, PowerShell
quoted path with spaces, resolve bundled Python in PowerShell, avoid Bash
heredoc in PowerShell, PowerShell JSON mutation, check LASTEXITCODE.

## How It Works

The skill converts command intent into PowerShell-native patterns. It prefers
`-LiteralPath`, quotes executable paths, invokes resolved executables with `&`,
probes optional CLIs, uses here-strings for inline scripts, handles JSON object
properties safely, and checks native command exit codes.

## API And Options

This is an LLM-facing Codex skill. It has no standalone CLI command. It often
uses paths returned by `codex_app.load_workspace_dependencies`, especially the
bundled Python executable.

## Inputs And Outputs

Inputs:

- intended Windows PowerShell command or shell workflow
- current cwd, sandbox, and writable roots
- bundled runtime paths from `codex_app.load_workspace_dependencies`
- PowerShell error text, exit code, or stderr from failed attempts

Outputs:

- PowerShell-native command shape
- runtime and optional CLI probe pattern
- safe literal-path and quoting pattern
- native exit-code handling
- escalation or connector fallback recommendation when needed

## Limitations

- It is for Windows PowerShell, not Bash, zsh, or cmd.exe.
- It does not grant network access, credentials, or filesystem permissions.
- It does not replace broader tool-choice guidance from `codex-efficient-caller`.

## Examples

```text
Use powershell-caller to run this Python script from Codex Desktop on Windows.
```

```text
Fix this shell_command failure caused by Bash heredoc syntax in PowerShell.
```

```text
Shape a PowerShell command that reads JSON, adds a missing property, and preserves native exit codes.
```

## Help And Getting Started

Install the skill with SkillForge, then ask Codex to use `powershell-caller`
for Windows shell commands.

```text
python -m skillforge install powershell-caller --scope global
```

## How To Call From An LLM

Use plain language:

```text
Use powershell-caller to shape this shell_command for Windows PowerShell.
```

## How To Call From The CLI

This skill is called by Codex during a chat turn. Use SkillForge only to
install, inspect, evaluate, or update it:

```text
python -m skillforge info powershell-caller --json
python -m skillforge evaluate powershell-caller --json
```

## Trust And Safety

Risk level:
low

Permissions:

- read command text, local path availability, and shell error output
- run PowerShell commands only when the active task already requires shell
  execution
- request approval for writes outside allowed roots, network access, installs,
  credentials, GUI automation, or destructive operations

Data handling:
Do not expose secrets, private logs, or sensitive command output in public
reports or PRs.

Writes vs read-only:
The skill itself is guidance. The commands it shapes may read or write
depending on the user's active task and approvals.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

## Contributing

Contributions should use PowerShell-native examples and keep broad
environment-boundary guidance in `codex-efficient-caller`.

## Author

Marc Edgar / medatasci

## Citations

Not applicable. This skill describes Codex PowerShell command patterns.

## Related Skills

- `codex-efficient-caller`: broader tool-choice and boundary guidance.
- `powershell-failure-analyst`: evidence from local PowerShell failures.
- `codex-failure-analyst`: broader Codex failure history analysis.
