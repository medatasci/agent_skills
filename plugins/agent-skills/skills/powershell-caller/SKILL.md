---
name: powershell-caller
owner: medatasci
description: >-
  Use when Codex needs to run commands through Windows PowerShell, especially in
  Codex Desktop on Windows. Helps avoid common shell_command failures including
  missing python on PATH, resolving bundled runtime paths through
  codex_app.load_workspace_dependencies, Bash heredocs/redirection, quoting
  paths with spaces, PowerShell parser errors, profile/execution-policy noise,
  native command exit handling, JSON object mutation, and cmdlet parameter
  semantics, and Codex sandbox constraints.
title: PowerShell Caller
short_description: Shape reliable Windows PowerShell commands for Codex Desktop and CLI environments.
expanded_description: Provides PowerShell-native command patterns for Codex shell_command calls on Windows. It covers literal paths, quoted executables, bundled Python resolution, here-strings instead of Bash heredocs, optional CLI probes, profile and execution-policy noise, native exit-code handling, JSON object mutation, cmdlet semantics, and sandbox-aware file operations.
aliases:
  - Windows PowerShell caller
  - PowerShell command preflight
  - shell_command PowerShell
  - Codex PowerShell quoting
  - bundled Python PowerShell
  - PowerShell sandbox commands
categories:
  - Developer Tools
  - Agent Workflows
  - Safety And Review
tags:
  - powershell
  - windows
  - codex
  - shell
  - quoting
  - runtime
  - sandbox
tasks:
  - shape Windows PowerShell commands for Codex shell_command
  - resolve bundled Python before running scripts
  - quote literal paths and executable paths correctly
  - avoid Bash-only heredocs, redirects, and shell assumptions
  - handle native command exit codes in PowerShell
  - mutate JSON objects safely in PowerShell
  - probe optional local CLIs before invoking them
use_when:
  - Codex needs to run shell commands through Windows PowerShell.
  - A command involves paths with spaces, quoted executables, here-strings, JSON mutation, native tools, or optional CLIs.
  - A prior PowerShell command failed with parser, quoting, profile, execution-policy, missing runtime, or path diagnostics.
  - Codex is using bundled Python or other Codex workspace dependencies from PowerShell.
do_not_use_when:
  - The active shell is Bash, zsh, cmd.exe, or another non-PowerShell shell.
  - The task is a direct connector call and no local PowerShell command is needed.
  - The command would require credentials, network, global installs, destructive file operations, or writes outside allowed roots without approval.
inputs:
  - intended Windows PowerShell command or shell workflow
  - current cwd, sandbox, and writable roots
  - available bundled runtime paths from codex_app.load_workspace_dependencies
  - any PowerShell error text, exit code, or stderr from failed attempts
outputs:
  - PowerShell-native command shape
  - runtime and optional CLI probe pattern
  - safe literal-path and quoting pattern
  - native exit-code handling
  - escalation or connector fallback recommendation when needed
examples:
  - Use powershell-caller to run this Python script from Codex Desktop on Windows.
  - Fix this shell_command failure caused by Bash heredoc syntax in PowerShell.
  - Shape a PowerShell command that reads JSON, adds a missing property, and preserves native exit codes.
related_skills:
  - codex-efficient-caller
  - powershell-failure-analyst
  - codex-failure-analyst
risk_level: low
permissions:
  - read command text, local path availability, and shell error output
  - run PowerShell commands only when the active task already requires shell execution
  - request approval for writes outside allowed roots, network access, installs, credentials, GUI automation, or destructive operations
page_title: PowerShell Caller Skill - Reliable Windows PowerShell Commands For Codex
meta_description: Use the PowerShell Caller skill to shape reliable Windows PowerShell shell_command calls with runtime resolution, literal paths, quoting, JSON mutation, and sandbox-aware behavior.
---

# PowerShell Caller

## What This Skill Does

Shape Windows PowerShell commands that work in Codex Desktop and CLI
environments. Use it for quoting, literal paths, bundled runtime resolution,
PowerShell here-strings, JSON mutation, optional CLI probes, native exit-code
handling, profile noise, and sandbox-aware command design.

This skill is a command-shaping companion to `codex-efficient-caller`; use the
broader caller skill first when the main question is which tool or connector to
use.

## Safe Default Behavior

Use PowerShell-native syntax and verify local assumptions before invoking a
command. Prefer `-LiteralPath`, quote executable paths, invoke resolved
executables with `&`, probe optional CLIs, check native exit codes, and keep
writes within allowed workspace roots unless the user approves escalation.

Do not translate real permission, network, credential, install, GUI, or
destructive-operation boundaries into repeated quoting retries.

## Workflow

1. Confirm the active shell is Windows PowerShell.
2. Resolve runtimes and optional CLIs before invoking them.
3. Use PowerShell-native syntax for paths, here-strings, JSON, and pipelines.
4. Execute one failure-sensitive command at a time when diagnosis matters.
5. Check native exit codes and classify failures before retrying.

Use PowerShell-native command shapes. Do not assume Bash syntax works.

## Codex Environment

- `functions.shell_command` runs in the current thread `cwd` under the current sandbox policy.
- Writes are usually limited to the workspace/writable roots; writing elsewhere needs approval with `sandbox_permissions:"require_escalated"`.
- Network is often restricted; installs, downloads, and remote API calls may need escalation after a sandbox/network failure.
- `codex_app.load_workspace_dependencies` is a tool call that returns bundled runtime paths; it is not a filesystem path.

## Defaults

- Use `-LiteralPath` for filesystem paths, especially user/workspace paths with spaces.
- Quote executable paths and invoke them with `&`.
- Treat `codex_app.load_workspace_dependencies` as a Codex tool call, not a filesystem path. Use the returned `Python executable` string; do not memorize it.
- Do not assume `python` is on `PATH`. Resolve `$py` once in the current turn/command and invoke `& $py`.
- If a command shows profile/execution-policy noise, rerun `functions.shell_command` with `login:false`. For nested PowerShell, use `powershell.exe -NoProfile -ExecutionPolicy Bypass`.
- Do not assume `$env:CODEX_HOME` is set; fall back to `$env:USERPROFILE\.codex` when resolving Codex-local paths.
- Before using optional CLIs such as `gh`, `uv`, `py`, `node`, or hard-coded executables, probe with `Get-Command` or `Test-Path`; use available Codex connectors/tools when a CLI is absent.
- Treat local apps, COM automation, WMI/CIM, and background processes as availability boundaries; probe first and keep a fallback path.
- For persistent repo edits, use `apply_patch`. Use PowerShell writes only for transient files or generated outputs.
- Prefer one command per tool call when failure handling matters. If chaining native tools, check `$LASTEXITCODE`.
- If failures repeat, use `$codex-failure-analyst` to extract root causes and carry-forward prevention rules from Codex history.

## Resolve Python

In Codex Desktop, first call `codex_app.load_workspace_dependencies` when the tool is available. Copy its `Python executable` value into `$py` in the PowerShell command.

When the tool is unavailable, verify locally instead of relying on memory:

```powershell
$py = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (-not (Test-Path -LiteralPath $py)) {
  $cmd = Get-Command python -ErrorAction SilentlyContinue
  if ($cmd) { $py = $cmd.Source } else { throw 'No Python executable found' }
}
& $py --version
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

## One-Shot Patterns

Run resolved Python:

```powershell
& $py 'scripts\tool.py' --input 'data\file.json'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

Inline Python. Do not use Bash heredocs such as `<<'PY'`.

```powershell
@'
from pathlib import Path
print(Path.cwd())
'@ | & $py -
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

Read files safely:

```powershell
$path = 'C:\Users\medgar\OneDrive - NVIDIA Corporation\Documents\Codex General\input.txt'
Get-Content -LiteralPath $path -Raw
```

Resolve Codex home without assuming `$env:CODEX_HOME` exists:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
```

Probe optional local tools before invoking them:

```powershell
$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) { throw 'gh is not installed; use a connector or another approved path' }
```

Create objects and pipe them. Do not pipe directly after a `foreach (...) { ... }` statement.

```powershell
$rows = foreach ($p in Get-ChildItem -LiteralPath 'reports' -Filter '*.csv' -File) {
  [pscustomobject]@{ name = $p.Name; bytes = $p.Length }
}
$rows | ConvertTo-Json -Depth 5
```

Mutate JSON robustly. Add missing properties before assigning them.

```powershell
$obj = Get-Content -LiteralPath 'state.json' -Raw | ConvertFrom-Json
if (-not $obj.PSObject.Properties.Match('status')) {
  $obj | Add-Member -NotePropertyName status -NotePropertyValue $null
}
$obj.status = 'complete'
$obj | ConvertTo-Json -Depth 20
```

Use variables next to colons safely:

```powershell
$name = 'step'
Write-Output "${name}: complete"
```

Call native tools with literal arguments:

```powershell
git -C 'C:\path with spaces\repo' status --short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

Use a temporary `.ps1` only when the command is too complex to quote reliably:

```powershell
$script = Join-Path $env:TEMP 'codex-task.ps1'
@'
$ErrorActionPreference = 'Stop'
Get-ChildItem -LiteralPath 'reports' -File | Select-Object Name, Length
'@ | Set-Content -LiteralPath $script -Encoding UTF8
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

## Avoid

- Bare `python ...`; resolve `$py` first using the pattern above.
- `cmd /c` for file deletion/move operations built from PowerShell output.
- Bash heredocs: `python - <<'PY'`.
- Bash-only assumptions: `source`, `$?` as an exit code object, `/tmp` paths without checking, unquoted paths with spaces.
- `foreach (...) { ... } | ConvertTo-Json`; assign to `$rows` first.
- Blind property assignment on `ConvertFrom-Json` objects when the property may not exist.
