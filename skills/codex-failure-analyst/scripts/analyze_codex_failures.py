#!/usr/bin/env python
"""Audit Codex Desktop rollout history for tool and environment failures."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


PS_DIAG_RE = re.compile(
    r"(At line:\d+\s+char:\d+|CategoryInfo\s*:|FullyQualifiedErrorId\s*:)",
    re.I,
)
EXIT_RE = re.compile(r"Exit code:\s*(-?\d+)")
ERR_ID_RE = re.compile(r"FullyQualifiedErrorId\s*:\s*([^\r\n]+)", re.I)

DEFAULT_DETECTOR_ID = "powershell-shell-command"
DEFAULT_TOOL_NAME = "functions.shell_command"
DEFAULT_TOOL_FAMILY = "shell"
DEFAULT_RUNTIME_ENVIRONMENT = "windows-powershell"
DEFAULT_DIAGNOSTIC_LANGUAGE = "powershell"

CONFIDENCE_BY_RULE = {
    "ps-unmapped-001": ("low", 3.0),
    "native-wrapper-001": ("medium", 6.0),
    "local-app-001": ("medium", 6.5),
    "process-lifecycle-001": ("medium", 6.5),
    "win-api-001": ("medium", 6.5),
}

SEVERITY_BASE_BY_PATTERN = {
    "codex-runtime-environment": 2.0,
    "filesystem-state-assumption": 3.0,
    "codex-boundary-management": 4.0,
    "powershell-grammar-object-model": 3.0,
    "shell-dialect-mismatch": 3.5,
    "shell-complexity-overflow": 3.5,
    "process-lifecycle-management": 4.0,
    "local-tool-availability": 2.5,
    "unmapped-diagnostic-discovery": 2.0,
}

QUOTE_RULES = [
    ("unclosed string quote", [r"The string is missing the terminator", r"TerminatorExpectedAtEndOfString"]),
    ("bash heredoc/redirection in PowerShell", [r"Missing file specification after redirection operator", r"MissingFileSpecification"]),
    ("pipeline after statement/block parsed incorrectly", [r"EmptyPipeElement"]),
    ("variable interpolation before colon", [r"InvalidVariableReferenceWithDrive"]),
    ("bracket/array parsing from unescaped text", [r"MissingArrayIndexExpression"]),
    ("unexpected token from quote/brace nesting", [r"Unexpected token", r"UnexpectedToken"]),
    ("here-string formatting error", [r"No characters are allowed after a here-string header", r"White space is not allowed before the string terminator"]),
    ("ampersand not invoked as call operator", [r"The ampersand.*character is not allowed"]),
    ("generic PowerShell parser failure", [r"ParserError", r"Missing expression after"]),
]
QUOTE_PATTERNS = [(name, [re.compile(p, re.I) for p in pats]) for name, pats in QUOTE_RULES]

ROOT_CAUSE_RULES = {
    "unclosed string quote": {
        "rule_id": "ps-quote-001",
        "root_cause": "Fragile nested quoting in a one-line PowerShell command.",
        "prevention": "Prefer single-quoted literal paths; move complex inline code into a here-string piped to the target executable or a temporary .ps1 file.",
    },
    "bash heredoc/redirection in PowerShell": {
        "rule_id": "ps-bash-001",
        "root_cause": "Bash heredoc or redirection syntax was used in PowerShell.",
        "prevention": "Use a PowerShell here-string, for example @' ... '@ | & $py -, instead of python - <<'PY'.",
    },
    "pipeline after statement/block parsed incorrectly": {
        "rule_id": "ps-pipe-001",
        "root_cause": "PowerShell statement/block output was piped as if the statement itself were an expression.",
        "prevention": "Assign foreach/if/block output to a variable first, then pipe the variable, or wrap expression output explicitly.",
    },
    "variable interpolation before colon": {
        "rule_id": "ps-var-001",
        "root_cause": "PowerShell parsed $name: as a scoped variable reference instead of variable text followed by a colon.",
        "prevention": "Use braces when variables touch punctuation, for example ${name}: complete.",
    },
    "bracket/array parsing from unescaped text": {
        "rule_id": "ps-bracket-001",
        "root_cause": "Literal bracket or array-like text was interpreted by PowerShell syntax.",
        "prevention": "Quote literal text, use -LiteralPath for filesystem paths, and avoid unquoted globs or regex fragments in shell text.",
    },
    "unexpected token from quote/brace nesting": {
        "rule_id": "ps-nesting-001",
        "root_cause": "Nested quoting, braces, or inline JSON exceeded safe one-liner complexity.",
        "prevention": "Use a here-string or temporary script file and let the target runtime parse structured data.",
    },
    "here-string formatting error": {
        "rule_id": "ps-herestr-001",
        "root_cause": "PowerShell here-string delimiters were formatted incorrectly.",
        "prevention": "Put @' or @\" at the end of its own opening line and the closing delimiter at the start of its own line.",
    },
    "ampersand not invoked as call operator": {
        "rule_id": "ps-call-001",
        "root_cause": "An executable path was quoted but not invoked with PowerShell's call operator.",
        "prevention": "Invoke quoted executable paths with &, for example & $py --version.",
    },
    "generic PowerShell parser failure": {
        "rule_id": "ps-parser-001",
        "root_cause": "Command text relied on shell syntax that PowerShell did not parse.",
        "prevention": "Reduce shell syntax, split complex commands, or move logic into a script with explicit error handling.",
    },
}

CATEGORY_ROOT_CAUSES = {
    "python not on PATH": {
        "rule_id": "codex-python-001",
        "root_cause": "Codex assumed python resolved on PATH in a desktop sandbox where it often does not.",
        "prevention": "Call codex_app.load_workspace_dependencies and invoke the returned Python executable with & $py.",
    },
    "profile/execution-policy security": {
        "rule_id": "ps-profile-001",
        "root_cause": "A login PowerShell session loaded profile code blocked by execution policy.",
        "prevention": "Use login:false for shell_command; for nested PowerShell use -NoProfile -ExecutionPolicy Bypass.",
    },
    "missing path/file assumption": {
        "rule_id": "fs-path-001",
        "root_cause": "The command assumed a file, directory, drive, or relative path existed.",
        "prevention": "Use Test-Path/Resolve-Path before acting, pass absolute paths for cross-context files, and use -LiteralPath.",
    },
    "permission/sandbox access": {
        "rule_id": "codex-sandbox-001",
        "root_cause": "The command crossed the Codex filesystem sandbox or OS permission boundary.",
        "prevention": "Keep writes inside the workspace or request require_escalated approval for necessary external writes.",
    },
    "web request surfaced by PowerShell": {
        "rule_id": "codex-network-001",
        "root_cause": "The command depended on network access that may be restricted in the Codex sandbox.",
        "prevention": "On sandbox/network failure, rerun the same necessary command with require_escalated and a narrow justification.",
    },
    "Windows API permission/availability": {
        "rule_id": "win-api-001",
        "root_cause": "The command assumed a Windows API, WMI/CIM provider, or privilege was available.",
        "prevention": "Probe capability first and provide a fallback path when local Windows APIs are unavailable or blocked.",
    },
    "PowerShell cmdlet/variable semantics": {
        "rule_id": "ps-semantics-001",
        "root_cause": "The command used Bash/general-language assumptions against PowerShell cmdlets or objects.",
        "prevention": "Check cmdlet parameters, object properties, and mutability; use Add-Member before setting missing JSON properties.",
    },
    "other PowerShell diagnostic": {
        "rule_id": "ps-unmapped-001",
        "root_cause": "PowerShell reported a diagnostic that is not yet mapped to a specific recurring pattern.",
        "prevention": "Review the event excerpt and add a rule if the same signature appears more than once.",
    },
    "local CLI/tool availability": {
        "rule_id": "tool-cli-001",
        "root_cause": "The command assumed an optional local CLI or executable was installed and on PATH.",
        "prevention": "Check Get-Command or Test-Path before invoking optional tools; use available Codex connectors/tools when a CLI is absent.",
    },
    "missing Codex environment variable": {
        "rule_id": "codex-envvar-001",
        "root_cause": "The command assumed a Codex environment variable such as CODEX_HOME was populated.",
        "prevention": "Resolve required paths with explicit fallbacks, for example use $env:CODEX_HOME when set and otherwise Join-Path $env:USERPROFILE '.codex'.",
    },
    "local app/COM availability": {
        "rule_id": "local-app-001",
        "root_cause": "The command assumed a local interactive application, profile, or COM automation target was available.",
        "prevention": "Probe local app/profile availability first and fall back to Codex connectors or user approval when local desktop integration is unavailable.",
    },
    "process lifecycle assumption": {
        "rule_id": "process-lifecycle-001",
        "root_cause": "The command assumed a background process or PID file still represented a live process.",
        "prevention": "Check Test-Path and Get-Process with error handling before waiting on, killing, or reading process state.",
    },
    "PowerShell language mode restriction": {
        "rule_id": "ps-language-mode-001",
        "root_cause": "The command assumed full PowerShell language features were available in a constrained runtime.",
        "prevention": "Avoid unnecessary .NET static mutation and prefer plain cmdlets or target runtime configuration when language mode is constrained.",
    },
    "native command wrapper failure": {
        "rule_id": "native-wrapper-001",
        "root_cause": "A native command or wrapper script failed and surfaced through PowerShell without a more specific mapped cause.",
        "prevention": "Preserve the native exit code, capture stderr/stdout, and inspect the tool-specific error before changing PowerShell syntax.",
    },
}

SOLUTION_PATTERN_DEFS = {
    "shell-dialect-mismatch": {
        "rule_ids": ["ps-bash-001", "ps-parser-001"],
        "problem_class": "Shell dialect mismatch",
        "abstraction": "Command text uses Bash or generic shell habits in Windows PowerShell.",
        "safe_pattern": "Translate shell-specific syntax to PowerShell, or move the logic into Python/a script and call it with literal arguments.",
        "anti_pattern": "Using Bash heredocs, source, Bash redirection assumptions, or Bash-style control flow in shell_command on Windows.",
        "when_to_use": "Use when an error says ParserError, MissingFileSpecification, or the command contains Bash-only syntax.",
        "when_not_to_use": "Do not over-apply to simple native commands whose arguments are already literal and PowerShell-safe.",
        "canonical_example": "@'\nfrom pathlib import Path\nprint(Path.cwd())\n'@ | & $py -",
        "target_skill": "codex-efficient-caller",
    },
    "shell-complexity-overflow": {
        "rule_ids": ["ps-quote-001", "ps-nesting-001", "ps-herestr-001"],
        "problem_class": "Shell complexity overflow",
        "abstraction": "Too much quoting, JSON, brace nesting, or multi-line logic is packed into one shell command.",
        "safe_pattern": "Use single-quoted literal paths, here-strings, temporary .ps1 files, or a Python script for structured logic.",
        "anti_pattern": "A long one-liner with nested JSON, escaped quotes, script blocks, and native command arguments mixed together.",
        "when_to_use": "Use whenever command text needs more than one quoting layer or embeds structured data.",
        "when_not_to_use": "Do not create a temp script for a short literal command that is easier to audit inline.",
        "canonical_example": "$script = Join-Path $env:TEMP 'codex-task.ps1'\n@'\n$ErrorActionPreference = 'Stop'\nGet-ChildItem -LiteralPath 'reports' -File\n'@ | Set-Content -LiteralPath $script -Encoding UTF8\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File $script",
        "target_skill": "codex-efficient-caller",
    },
    "powershell-grammar-object-model": {
        "rule_ids": ["ps-pipe-001", "ps-var-001", "ps-bracket-001", "ps-call-001", "ps-semantics-001"],
        "problem_class": "PowerShell grammar and object model mismatch",
        "abstraction": "The command treats PowerShell statements, variables, cmdlets, or objects like Bash text streams.",
        "safe_pattern": "Respect PowerShell grammar: assign block output before piping, use ${name} near punctuation, use -LiteralPath, invoke quoted executables with &, and mutate objects deliberately.",
        "anti_pattern": "Piping directly after foreach blocks, using $name: text, unquoted bracket text, quoted executable paths without &, or blind JSON property assignment.",
        "when_to_use": "Use when errors mention EmptyPipeElement, InvalidVariableReferenceWithDrive, MissingArrayIndexExpression, parameter binding, or object mutation.",
        "when_not_to_use": "Do not replace useful PowerShell object pipelines; only reshape grammar that PowerShell rejected.",
        "canonical_example": "$rows = foreach ($p in Get-ChildItem -LiteralPath 'reports' -File) {\n  [pscustomobject]@{ name = $p.Name; bytes = $p.Length }\n}\n$rows | ConvertTo-Json -Depth 5",
        "target_skill": "codex-efficient-caller",
    },
    "codex-runtime-environment": {
        "rule_ids": ["codex-python-001", "ps-profile-001", "codex-envvar-001", "ps-language-mode-001"],
        "problem_class": "Codex runtime environment assumption",
        "abstraction": "The command assumes a normal interactive Windows shell instead of Codex Desktop's bundled runtime and shell profile behavior.",
        "safe_pattern": "Resolve bundled dependencies through Codex tools, invoke returned executable paths with &, use login:false or -NoProfile when profile noise appears, and provide fallbacks for Codex env vars.",
        "anti_pattern": "Calling bare python, treating codex_app.load_workspace_dependencies as a file path, assuming CODEX_HOME exists, or letting profile execution-policy errors pollute commands.",
        "when_to_use": "Use before Python/scripts, Codex-home path access, and after profile/security noise appears.",
        "when_not_to_use": "Do not hard-code runtime paths when codex_app.load_workspace_dependencies is available.",
        "canonical_example": "& $py --version\nif ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }",
        "target_skill": "codex-efficient-caller",
    },
    "codex-boundary-management": {
        "rule_ids": ["codex-sandbox-001", "codex-network-001", "win-api-001", "local-app-001"],
        "problem_class": "Codex sandbox, network, or Windows API boundary",
        "abstraction": "The command crosses a permission, network, local app, profile, COM, or Windows API boundary that may be blocked in Codex.",
        "safe_pattern": "Probe locally first, keep writes inside the workspace, and request narrow escalation only when the operation is necessary.",
        "anti_pattern": "Retrying blocked writes/downloads/API calls/local app automation with different syntax instead of recognizing the boundary.",
        "when_to_use": "Use when errors mention unauthorized access, sandbox write failures, network failures, WMI/CIM restrictions, Outlook/COM profile failures, or unavailable Windows APIs.",
        "when_not_to_use": "Do not escalate if a workspace-local or read-only fallback gives the same answer.",
        "canonical_example": "if (-not (Test-Path -LiteralPath $target)) { throw \"Missing target: $target\" }",
        "target_skill": "codex-efficient-caller",
    },
    "filesystem-state-assumption": {
        "rule_ids": ["fs-path-001"],
        "problem_class": "Filesystem state assumption",
        "abstraction": "The command assumes paths, directories, or files exist without verifying them in the current Codex cwd/sandbox.",
        "safe_pattern": "Use absolute paths for cross-context files, Test-Path before actions, Resolve-Path for existing targets, and -LiteralPath for user/workspace paths.",
        "anti_pattern": "Using fragile relative paths or unquoted paths with spaces in generated commands.",
        "when_to_use": "Use before reading/writing files outside the immediate cwd or when paths contain spaces, brackets, or user profile segments.",
        "when_not_to_use": "Do not add extra probing for static repo files already confirmed by rg/Get-ChildItem in the same turn.",
        "canonical_example": "$path = 'C:\\path with spaces\\input.txt'\nif (-not (Test-Path -LiteralPath $path)) { throw \"Missing file: $path\" }\nGet-Content -LiteralPath $path -Raw",
        "target_skill": "codex-efficient-caller",
    },
    "unmapped-diagnostic-discovery": {
        "rule_ids": ["ps-unmapped-001"],
        "problem_class": "Unmapped repeated diagnostic",
        "abstraction": "PowerShell emitted a recurring diagnostic that is not yet explained by the current rule catalog.",
        "safe_pattern": "Cluster by error type and excerpt, inspect examples, then promote repeated signatures to a named root-cause rule only when prevention is stable.",
        "anti_pattern": "Leaving repeated unknown diagnostics as isolated one-off failures.",
        "when_to_use": "Use when unmapped_repeated_failures is non-empty.",
        "when_not_to_use": "Do not create a new pattern for a single noisy false positive.",
        "canonical_example": "Review summary.unmapped_repeated_failures before editing prevention skills.",
        "target_skill": "codex-failure-analyst",
    },
    "local-tool-availability": {
        "rule_ids": ["tool-cli-001"],
        "problem_class": "Optional local tool availability",
        "abstraction": "The command assumes local developer CLIs or executable paths exist in the Codex desktop environment.",
        "safe_pattern": "Probe optional CLIs with Get-Command or Test-Path, then choose an installed connector/tool, an approved install, or a direct API fallback.",
        "anti_pattern": "Calling gh, uv, py, codex.exe, or other optional executables before verifying they exist.",
        "when_to_use": "Use before invoking non-bundled CLIs and hard-coded executable paths.",
        "when_not_to_use": "Do not replace a known repo-local executable that was already resolved with Test-Path.",
        "canonical_example": "$gh = Get-Command gh -ErrorAction SilentlyContinue\nif (-not $gh) { throw 'gh is not installed; use the GitHub connector or another approved path.' }",
        "target_skill": "codex-efficient-caller",
    },
    "process-lifecycle-management": {
        "rule_ids": ["process-lifecycle-001", "native-wrapper-001"],
        "problem_class": "Process and native command lifecycle",
        "abstraction": "The command assumes a process, server, PID file, or native wrapper state is still valid.",
        "safe_pattern": "Check process existence and native exit codes explicitly; preserve logs before retrying.",
        "anti_pattern": "Waiting on stale PIDs or changing PowerShell syntax when the native process actually failed.",
        "when_to_use": "Use around background servers, PID files, Start-Process, Wait-Process, and native command wrappers.",
        "when_not_to_use": "Do not add process management for simple foreground commands that return complete output.",
        "canonical_example": "if (Test-Path -LiteralPath $pidFile) {\n  $pidValue = Get-Content -LiteralPath $pidFile -Raw\n  $proc = Get-Process -Id $pidValue -ErrorAction SilentlyContinue\n}",
        "target_skill": "codex-efficient-caller",
    },
}

RULE_TO_PATTERN = {
    rule_id: pattern_id
    for pattern_id, pattern in SOLUTION_PATTERN_DEFS.items()
    for rule_id in pattern["rule_ids"]
}

GENERAL_PATTERNS = [
    re.compile(r"FullyQualifiedErrorId\s*:", re.I),
    re.compile(r"CategoryInfo\s*:", re.I),
    re.compile(r"At line:\d+\s+char:\d+", re.I),
    re.compile(
        r"\b(ParserError|CommandNotFoundException|ParameterBindingException|ItemNotFoundException|PathNotFound|UnauthorizedAccessException|RuntimeException|DriveNotFoundException|ParentContainsErrorRecordException|NativeCommandError)\b",
        re.I,
    ),
    re.compile(r"The term '.+?' is not recognized as the name of a cmdlet", re.I),
    re.compile(r"A parameter cannot be found that matches parameter name", re.I),
    re.compile(r"Cannot bind parameter", re.I),
    re.compile(r"Cannot find path", re.I),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", default=str(Path.home() / ".codex"))
    parser.add_argument("--tz", default="America/New_York")
    parser.add_argument("--since", help="Start date YYYY-MM-DD, local time")
    parser.add_argument("--until", help="Inclusive end date YYYY-MM-DD, local time")
    parser.add_argument("--days", type=int, default=30, help="Look back this many days when --since is absent")
    parser.add_argument("--mode", choices=["all", "quoting"], default="all")
    parser.add_argument("--output-dir", default="reports")
    parser.add_argument("--prefix", default="")
    parser.add_argument("--sqlite-path", help="Optional SQLite output path; defaults next to CSV/JSON/Markdown")
    return parser.parse_args()


def clean(text: str | None, limit: int = 260) -> str:
    value = re.sub(r"\s+", " ", text or "").strip()
    return value if len(value) <= limit else value[: limit - 3] + "..."


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def percent(numerator: float, denominator: float) -> float:
    return round((numerator / denominator) * 100.0, 2) if denominator else 0.0


def severity_label(score: float) -> str:
    if score >= 7.0:
        return "critical"
    if score >= 5.0:
        return "high"
    if score >= 3.0:
        return "medium"
    return "low"


def confidence_for_rule(rule_id: str) -> tuple[str, float]:
    return CONFIDENCE_BY_RULE.get(rule_id, ("high", 8.5))


def token_cost_estimate(*parts: str) -> int:
    text = " ".join(part or "" for part in parts)
    words = len(re.findall(r"\S+", text))
    return max(1, int(words * 1.35))


def token_efficiency_score(token_cost: int) -> float:
    return max(0.0, min(10.0, 10.0 - (token_cost / 45.0)))


def command_terms(command: str | None) -> set[str]:
    terms = {
        term.lower()
        for term in re.findall(r"[A-Za-z0-9_.:-]{2,}", command or "")
        if term.lower() not in {"the", "and", "for", "with", "true", "false", "null"}
    }
    return terms


def command_similarity(left: str | None, right: str | None) -> float:
    left_terms = command_terms(left)
    right_terms = command_terms(right)
    if not left_terms or not right_terms:
        return 0.0
    score = len(left_terms & right_terms) / len(left_terms | right_terms)
    left_head = next(iter(re.findall(r"\S+", left or "")), "").lower()
    right_head = next(iter(re.findall(r"\S+", right or "")), "").lower()
    if left_head and left_head == right_head:
        score += 0.15
    return round(min(score, 1.0), 3)


def group_priority(
    count: int,
    thread_count: int,
    avg_severity: float,
    avg_rework: float,
    unresolved_rate: float,
    confidence_score: float,
    token_cost: int,
) -> dict[str, float]:
    evidence_score = min(10.0, math.log2(count + 1) * 1.55)
    generality_score = min(10.0, math.log2(thread_count + 1) * 2.2)
    rework_score = min(10.0, avg_rework * 1.25 + unresolved_rate * 4.0)
    token_score = token_efficiency_score(token_cost)
    priority_score = (
        evidence_score * 0.25
        + avg_severity * 0.24
        + generality_score * 0.18
        + rework_score * 0.15
        + confidence_score * 0.13
        + token_score * 0.05
    )
    return {
        "priority_score": round(priority_score, 2),
        "evidence_score": round(evidence_score, 2),
        "severity_score": round(avg_severity, 2),
        "generality_score": round(generality_score, 2),
        "rework_score": round(rework_score, 2),
        "confidence_score": round(confidence_score, 2),
        "token_efficiency_score": round(token_score, 2),
    }


def parse_local_ts(value: str | None, tz: ZoneInfo) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(tz)
    except ValueError:
        return None


def date_window(args: argparse.Namespace, tz: ZoneInfo) -> tuple[datetime, datetime]:
    if args.since:
        start = datetime.fromisoformat(args.since).replace(tzinfo=tz)
    else:
        today = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        start = today - timedelta(days=args.days)
    if args.until:
        until_day = datetime.fromisoformat(args.until).replace(tzinfo=tz)
        end = until_day + timedelta(days=1)
    else:
        end = datetime.now(tz)
    return start, end


def body_from_tool_output(output: str) -> str:
    marker = "\nOutput:\n"
    return output.split(marker, 1)[1] if marker in output else output


def quoted_old_transcript(body: str) -> bool:
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    return bool(lines) and all(re.match(r"^\d+[:-]\{", line) or line.startswith("{") for line in lines[: min(5, len(lines))])


def quote_subtype(body: str) -> str:
    for name, patterns in QUOTE_PATTERNS:
        if any(pattern.search(body) for pattern in patterns):
            return name
    return ""


def error_type(body: str) -> str:
    match = ERR_ID_RE.search(body)
    if match:
        return clean(match.group(1), 160)
    subtype = quote_subtype(body)
    if subtype:
        return subtype
    match = re.search(
        r"\b(ParserError|CommandNotFoundException|ParameterBindingException|ItemNotFoundException|PathNotFound|UnauthorizedAccessException|RuntimeException|DriveNotFoundException|NativeCommandError)\b",
        body,
        re.I,
    )
    return match.group(1) if match else "PowerShellDiagnostic"


def category(body: str, command: str) -> str:
    subtype = quote_subtype(body)
    hay = f"{body}\n{command}".lower()
    if "commandnotfoundexception" in hay and (
        re.match(r"\s*(python|python3|py)\b", command, re.I)
        or re.search(r"ObjectNotFound:\s*\((python|python3|py):String\)", body, re.I)
    ):
        return "python not on PATH"
    if "join-path" in hay and "$env:codex_home" in hay and "cannot bind argument to parameter" in hay:
        return "missing Codex environment variable"
    if "pssecurityexception" in hay and ("windowspowershell" in hay or "documents\\windowspow" in hay):
        return "profile/execution-policy security"
    if subtype:
        return "quoting/parser"
    if "commandnotfoundexception" in hay and (
        re.search(r"ObjectNotFound:\s*\((gh|uv|codex\.exe|codex|node|npm):String\)", body, re.I)
        or re.match(r"\s*(gh|uv|codex|node|npm)\b", command, re.I)
        or "appdata\\local\\openai\\codex\\bin\\codex.exe" in hay
    ):
        return "local CLI/tool availability"
    if "outlook profile" in hay or "outlook com" in hay or "nocomclassidentified" in hay:
        return "local app/COM availability"
    if "noprocessfoundforgivenid" in hay or "processnotterminated" in hay:
        return "process lifecycle assumption"
    if "propertysetternotsupportedinconstrainedlanguage" in hay:
        return "PowerShell language mode restriction"
    if any(term in hay for term in ["pathnotfound", "itemnotfound", "cannot find path", "directorynotfound", "processingfile"]):
        return "missing path/file assumption"
    if any(term in hay for term in ["unauthorizedaccess", "permissiondenied", "fileopenfailure"]):
        return "permission/sandbox access"
    if any(term in hay for term in ["invokewebrequest", "webcmdletwebresponseexception"]):
        return "web request surfaced by PowerShell"
    if any(term in hay for term in ["get-ciminstance", "get-nettcpconnection", "0x80041003"]):
        return "Windows API permission/availability"
    if any(term in hay for term in ["namedparameternotfound", "invalidcast", "invokemethodonnull", "exceptionwhensetting", "variablenotwritable", "incorrectvalueforcommandparameter", "startprocesscommand"]):
        return "PowerShell cmdlet/variable semantics"
    if any(term in hay for term in ["nativecommanderror", "nativecommandfailed", "writeerrorexception", "search runner failed"]):
        return "native command wrapper failure"
    return "other PowerShell diagnostic"


def root_cause_for(cat: str, subtype: str) -> dict[str, str]:
    if cat == "quoting/parser" and subtype and subtype in ROOT_CAUSE_RULES:
        return ROOT_CAUSE_RULES[subtype]
    return CATEGORY_ROOT_CAUSES.get(cat, CATEGORY_ROOT_CAUSES["other PowerShell diagnostic"])


def solution_pattern_for(rule_id: str) -> tuple[str, dict]:
    pattern_id = RULE_TO_PATTERN.get(rule_id, "unmapped-diagnostic-discovery")
    return pattern_id, SOLUTION_PATTERN_DEFS[pattern_id]


def include_event(mode: str, body: str, command: str, exit_code: int | None) -> bool:
    if quoted_old_transcript(body):
        return False
    if mode == "quoting":
        return exit_code not in (None, 0) and bool(quote_subtype(body)) and bool(PS_DIAG_RE.search(body))
    if not any(pattern.search(body) for pattern in GENERAL_PATTERNS):
        return False
    if exit_code in (None, 0) and not PS_DIAG_RE.search(body):
        return False
    return True


def excerpt(body: str, limit: int = 650) -> str:
    interesting: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or re.match(r"^\d+[:-]\{", stripped) or stripped.startswith("{"):
            continue
        if PS_DIAG_RE.search(stripped) or any(any(pattern.search(stripped) for pattern in patterns) for _, patterns in QUOTE_PATTERNS) or stripped.startswith("+ "):
            interesting.append(stripped)
    if not interesting:
        interesting = [line.strip() for line in body.splitlines() if line.strip()][:5]
    return clean(" | ".join(interesting), limit)


def load_threads(codex_home: Path, start: datetime, end: datetime) -> list[dict]:
    db = codex_home / "state_5.sqlite"
    with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            select id, title, cwd, rollout_path, created_at, updated_at, source, thread_source
            from threads
            where rollout_path is not null
              and coalesce(updated_at, created_at, 0) >= ?
              and coalesce(created_at, updated_at, 0) < ?
            order by updated_at desc
            """,
            (int(start.timestamp()), int(end.timestamp())),
        ).fetchall()
    return [dict(row) for row in rows]


def annotate_rework(thread_events: list[dict], thread_outputs: list[dict], max_repair_window: int = 12) -> None:
    for event in thread_events:
        current_index = event["thread_output_index"]
        next_output = thread_outputs[current_index + 1] if current_index + 1 < len(thread_outputs) else None
        candidates = thread_outputs[current_index + 1 : current_index + 1 + max_repair_window]
        repeated_same_failure = 0
        scored_successes: list[tuple[dict, float]] = []
        for later in candidates:
            similarity = command_similarity(event.get("command"), later.get("command"))
            if later["exit_code"] == 0:
                scored_successes.append((later, similarity))
                continue
            if later["exit_code"] not in (None, 0):
                if similarity >= 0.35:
                    repeated_same_failure += 1

        chosen_success: dict | None = None
        chosen_similarity = 0.0
        if next_output and next_output["exit_code"] == 0 and command_similarity(event.get("command"), next_output.get("command")) >= 0.18:
            chosen_success = next_output
            chosen_similarity = command_similarity(event.get("command"), next_output.get("command"))
            mode = "direct_next_shell_success_similar_command"
            confidence = "high"
        else:
            for later, similarity in scored_successes:
                if similarity >= 0.45:
                    chosen_success = later
                    chosen_similarity = similarity
                    mode = "later_similar_command_success_within_window"
                    confidence = "high"
                    break
            if chosen_success is None:
                for later, similarity in scored_successes:
                    if similarity >= 0.18:
                        chosen_success = later
                        chosen_similarity = similarity
                        mode = "later_related_command_success_within_window"
                        confidence = "medium"
                        break
            if chosen_success is None and scored_successes:
                chosen_success, chosen_similarity = scored_successes[0]
                mode = "later_generic_shell_success_within_window"
                confidence = "low"

        if chosen_success is None:
            rework_turns: int | None = None
            failed_before_success = sum(1 for later in candidates if later["exit_code"] not in (None, 0))
            mode = "no_repair_success_within_window" if candidates else "unresolved_no_later_shell_success"
            confidence = "low"
        else:
            rework_turns = chosen_success["thread_output_index"] - current_index
            failed_before_success = sum(
                1
                for later in candidates
                if later["thread_output_index"] < chosen_success["thread_output_index"] and later["exit_code"] not in (None, 0)
            )
        if repeated_same_failure:
            mode = f"repeated_failure_then_{mode}"
            if confidence == "low":
                confidence = "medium"
        event["rework_turns_to_resolve"] = rework_turns
        event["rework_failed_turns_before_resolve"] = failed_before_success
        event["rework_repeated_failure_count"] = repeated_same_failure
        event["repair_detection_mode"] = mode
        event["repair_confidence_label"] = confidence
        event["repair_success_similarity"] = chosen_similarity
        event["repair_success_command"] = clean(chosen_success.get("command"), 260) if chosen_success else ""
        event["resolved_status"] = "resolved_by_later_shell_success" if rework_turns is not None else "no_later_shell_success_observed"


def annotate_event_scores(events: list[dict]) -> None:
    for event in events:
        confidence_label, confidence_score = confidence_for_rule(event["rule_id"])
        rework_turns = event.get("rework_turns_to_resolve")
        rework_component = min(float(rework_turns or 0), 8.0) * 0.35
        unresolved_component = 0.7 if event.get("resolved_status") == "no_later_shell_success_observed" else 0.0
        nonzero_component = 0.4 if event.get("exit_code") not in (None, 0) else 0.0
        base = SEVERITY_BASE_BY_PATTERN.get(event["solution_pattern_id"], 2.0)
        score = min(10.0, base + rework_component + unresolved_component + nonzero_component)
        event["confidence_label"] = confidence_label
        event["confidence_score"] = confidence_score
        event["severity_score"] = round(score, 2)
        event["severity_label"] = severity_label(score)
        event["error_class"] = event["rule_id"]
        event["error_family"] = event["solution_pattern_id"]


def repair_turn_keys_for_event(event: dict) -> set[tuple[str, int]]:
    rework_turns = event.get("rework_turns_to_resolve")
    if rework_turns is None:
        return set()
    start_index = int(event["thread_output_index"]) + 1
    end_index = int(event["thread_output_index"]) + int(rework_turns)
    return {(event["thread_id"], output_index) for output_index in range(start_index, end_index + 1)}


def efficiency_metrics(stats: Counter[str], events: list[dict]) -> dict:
    shell_calls = stats["shell_calls_seen"]
    failed_shell_calls = stats["failed_shell_calls_seen"]
    event_count = len(events)
    resolved_events = 0
    total_rework_turns = 0
    repair_turn_keys: set[tuple[str, int]] = set()
    detected_nonzero = 0
    detected_zero_exit = 0

    for event in events:
        exit_code = event.get("exit_code")
        if exit_code not in (None, 0):
            detected_nonzero += 1
        elif exit_code == 0:
            detected_zero_exit += 1

        rework_turns = event.get("rework_turns_to_resolve")
        if rework_turns is None:
            continue
        resolved_events += 1
        total_rework_turns += int(rework_turns)
        repair_turn_keys.update(repair_turn_keys_for_event(event))

    unique_repair_turns = len(repair_turn_keys)
    lost_time_percent = percent(unique_repair_turns, shell_calls)
    return {
        "successful_shell_calls_seen": shell_calls - failed_shell_calls,
        "failed_shell_call_rate_percent": percent(failed_shell_calls, shell_calls),
        "shell_call_efficiency_percent": percent(shell_calls - failed_shell_calls, shell_calls),
        "detected_event_rate_percent": percent(event_count, shell_calls),
        "detected_event_efficiency_percent": percent(shell_calls - event_count, shell_calls),
        "detected_nonzero_events": detected_nonzero,
        "detected_zero_exit_events": detected_zero_exit,
        "resolved_detected_events": resolved_events,
        "unique_repair_turns_estimate": unique_repair_turns,
        "total_rework_turns_to_resolve": total_rework_turns,
        "repair_turn_burden_percent": percent(total_rework_turns, shell_calls),
        "lost_time_percent": lost_time_percent,
        "efficiency_percent": round(100.0 - lost_time_percent, 2),
        "lost_time_formula": "(unique shell output indexes inside detected-event repair windows / shell_calls_seen) * 100",
        "efficiency_formula": "100 - lost_time_percent",
        "notes": "lost_time_percent is a repair-turn estimate, not wall-clock time; low-confidence repair matches can overstate or understate true rework.",
    }


def efficiency_by_error_family(stats: Counter[str], events: list[dict]) -> list[dict]:
    shell_calls = stats["shell_calls_seen"]
    global_repair_turn_keys: set[tuple[str, int]] = set()
    for event in events:
        global_repair_turn_keys.update(repair_turn_keys_for_event(event))
    global_unique_repair_turns = len(global_repair_turn_keys)

    grouped: defaultdict[str, list[dict]] = defaultdict(list)
    for event in events:
        grouped[event["error_family"]].append(event)

    rows: list[dict] = []
    for error_family, group in grouped.items():
        family_repair_turn_keys: set[tuple[str, int]] = set()
        total_rework_turns = 0
        rework_values: list[float] = []
        resolved_events = 0
        detected_nonzero = 0
        detected_zero_exit = 0
        for event in group:
            exit_code = event.get("exit_code")
            if exit_code not in (None, 0):
                detected_nonzero += 1
            elif exit_code == 0:
                detected_zero_exit += 1

            rework_turns = event.get("rework_turns_to_resolve")
            if rework_turns is None:
                continue
            resolved_events += 1
            total_rework_turns += int(rework_turns)
            rework_values.append(float(rework_turns))
            family_repair_turn_keys.update(repair_turn_keys_for_event(event))

        unique_repair_turns = len(family_repair_turn_keys)
        lost_time_percent = percent(unique_repair_turns, shell_calls)
        rows.append(
            {
                "error_family": error_family,
                "event_count": len(group),
                "thread_count": len({event["thread_id"] for event in group}),
                "detected_nonzero_events": detected_nonzero,
                "detected_zero_exit_events": detected_zero_exit,
                "resolved_detected_events": resolved_events,
                "unique_repair_turns_estimate": unique_repair_turns,
                "total_rework_turns_to_resolve": total_rework_turns,
                "avg_rework_turns_to_resolve": round(mean(rework_values), 2),
                "repair_turn_burden_percent": percent(total_rework_turns, shell_calls),
                "lost_time_percent": lost_time_percent,
                "lost_time_share_percent": percent(unique_repair_turns, global_unique_repair_turns),
                "efficiency_percent": round(100.0 - lost_time_percent, 2),
                "formula_note": "Family lost_time_percent uses unique repair turns for that error_family divided by shell_calls_seen; family windows can overlap, so shares may sum above 100%.",
            }
        )
    rows.sort(key=lambda item: (-item["lost_time_percent"], -item["event_count"], item["error_family"]))
    return rows


def scan(args: argparse.Namespace) -> tuple[dict, list[dict]]:
    tz = ZoneInfo(args.tz)
    start, end = date_window(args, tz)
    codex_home = Path(args.codex_home)
    threads = load_threads(codex_home, start, end)
    stats: Counter[str] = Counter()
    events: list[dict] = []

    for thread in threads:
        path = thread.get("rollout_path")
        if not path or not Path(path).exists():
            stats["missing_rollout"] += 1
            continue
        stats["rollout_files_read"] += 1
        calls: dict[str, dict] = {}
        thread_outputs: list[dict] = []
        thread_events: list[dict] = []
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            for line_no, line in enumerate(handle, 1):
                stats["json_lines_read"] += 1
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    stats["json_parse_errors"] += 1
                    continue
                payload = entry.get("payload") or {}
                ts_local = parse_local_ts(entry.get("timestamp"), tz)
                if entry.get("type") == "response_item" and payload.get("type") == "function_call" and payload.get("name") == "shell_command":
                    call_id = payload.get("call_id")
                    if not call_id:
                        continue
                    try:
                        args_payload = json.loads(payload.get("arguments") or "{}")
                    except json.JSONDecodeError:
                        args_payload = {"_raw_arguments": payload.get("arguments") or ""}
                    calls[call_id] = {"args": args_payload}
                    stats["shell_calls_seen"] += 1
                    continue
                if entry.get("type") != "response_item" or payload.get("type") != "function_call_output":
                    continue
                call = calls.get(payload.get("call_id"))
                if not call:
                    continue
                if ts_local and not (start <= ts_local < end):
                    continue
                output = payload.get("output") or ""
                body = body_from_tool_output(output)
                match = EXIT_RE.search(output)
                exit_code = int(match.group(1)) if match else None
                if exit_code not in (None, 0):
                    stats["failed_shell_calls_seen"] += 1
                command = (call["args"].get("command") or call["args"].get("_raw_arguments") or "")
                output_index = len(thread_outputs)
                thread_outputs.append(
                    {
                        "thread_output_index": output_index,
                        "local_time": ts_local.isoformat() if ts_local else "",
                        "exit_code": exit_code,
                        "command": clean(command, 220),
                        "rollout_line": line_no,
                    }
                )
                if not include_event(args.mode, body, command, exit_code):
                    continue
                cat = category(body, command)
                subtype = quote_subtype(body) if cat == "quoting/parser" else ""
                cause = root_cause_for(cat, subtype)
                pattern_id, pattern = solution_pattern_for(cause["rule_id"])
                thread_events.append(
                    {
                        "local_time": ts_local.isoformat() if ts_local else "",
                        "thread_id": thread["id"],
                        "thread_source": thread.get("thread_source") or "",
                        "title": clean(thread.get("title") or "", 180),
                        "detector_id": DEFAULT_DETECTOR_ID,
                        "tool_name": DEFAULT_TOOL_NAME,
                        "tool_family": DEFAULT_TOOL_FAMILY,
                        "runtime_environment": DEFAULT_RUNTIME_ENVIRONMENT,
                        "diagnostic_language": DEFAULT_DIAGNOSTIC_LANGUAGE,
                        "category": cat,
                        "quoting_subtype": subtype,
                        "error_type": error_type(body),
                        "rule_id": cause["rule_id"],
                        "root_cause": cause["root_cause"],
                        "prevention": cause["prevention"],
                        "solution_pattern_id": pattern_id,
                        "solution_pattern": pattern["problem_class"],
                        "exit_code": exit_code,
                        "thread_output_index": output_index,
                        "command": clean(command, 700),
                        "excerpt": excerpt(body),
                        "workdir": call["args"].get("workdir") or "",
                        "rollout_path": path,
                        "rollout_line": line_no,
                        "cwd": thread.get("cwd") or "",
                    }
                )
        annotate_rework(thread_events, thread_outputs)
        events.extend(thread_events)

    events.sort(key=lambda event: (event["local_time"], event["thread_id"], event["rollout_line"]))
    annotate_event_scores(events)
    by_thread: defaultdict[str, list[dict]] = defaultdict(list)
    for event in events:
        by_thread[event["thread_id"]].append(event)
    thread_summary = [
        {
            "thread_id": thread_id,
            "count": len(thread_events),
            "first": min(event["local_time"] for event in thread_events),
            "last": max(event["local_time"] for event in thread_events),
            "title": thread_events[0]["title"],
            "top_categories": dict(Counter(event["category"] for event in thread_events).most_common(5)),
            "rollout_path": thread_events[0]["rollout_path"],
        }
        for thread_id, thread_events in sorted(by_thread.items(), key=lambda item: (-len(item[1]), item[1][0]["local_time"]))
    ]
    summary = {
        "window_local": {"start": start.isoformat(), "end_exclusive": end.isoformat()},
        "mode": args.mode,
        "threads_selected": len(threads),
        "rollout_files_read": stats["rollout_files_read"],
        "json_lines_read": stats["json_lines_read"],
        "shell_calls_seen": stats["shell_calls_seen"],
        "failed_shell_calls_seen": stats["failed_shell_calls_seen"],
        "event_count": len(events),
        "efficiency": efficiency_metrics(stats, events),
        "efficiency_by_error_family": efficiency_by_error_family(stats, events),
        "detector_counts": dict(Counter(event["detector_id"] for event in events).most_common()),
        "tool_family_counts": dict(Counter(event["tool_family"] for event in events).most_common()),
        "runtime_environment_counts": dict(Counter(event["runtime_environment"] for event in events).most_common()),
        "category_counts": dict(Counter(event["category"] for event in events).most_common()),
        "quoting_subtype_counts": dict(Counter(event["quoting_subtype"] for event in events if event["quoting_subtype"]).most_common()),
        "error_type_counts": dict(Counter(event["error_type"] for event in events).most_common()),
        "root_cause_counts": dict(Counter(event["root_cause"] for event in events).most_common()),
        "carry_forward": carry_forward(events),
        "solution_patterns": solution_patterns(events),
        "priority_targets": priority_targets(events),
        "unmapped_repeated_failures": unmapped_repeated_failures(events),
        "threads_with_events": thread_summary,
    }
    return summary, events


def group_metrics(group: list[dict], confidence_score: float, token_cost: int) -> dict:
    rework_values = [float(event["rework_turns_to_resolve"]) for event in group if event.get("rework_turns_to_resolve") is not None]
    unresolved_count = sum(1 for event in group if event.get("resolved_status") == "no_later_shell_success_observed")
    thread_count = len({event["thread_id"] for event in group})
    avg_severity = mean([float(event.get("severity_score") or 0.0) for event in group])
    avg_rework = mean(rework_values)
    unresolved_rate = unresolved_count / len(group) if group else 0.0
    scores = group_priority(
        count=len(group),
        thread_count=thread_count,
        avg_severity=avg_severity,
        avg_rework=avg_rework,
        unresolved_rate=unresolved_rate,
        confidence_score=confidence_score,
        token_cost=token_cost,
    )
    return {
        **scores,
        "thread_count": thread_count,
        "avg_rework_turns_to_resolve": round(avg_rework, 2),
        "max_rework_turns_to_resolve": int(max(rework_values)) if rework_values else 0,
        "unresolved_count": unresolved_count,
        "unresolved_rate": round(unresolved_rate, 3),
        "token_cost_estimate": token_cost,
    }


def carry_forward(events: list[dict]) -> list[dict]:
    grouped: defaultdict[str, list[dict]] = defaultdict(list)
    for event in events:
        grouped[event["rule_id"]].append(event)
    lessons: list[dict] = []
    for rule_id, group in grouped.items():
        first = group[0]
        confidence_label, confidence_score = confidence_for_rule(rule_id)
        token_cost = token_cost_estimate(first["root_cause"], first["prevention"])
        metrics = group_metrics(group, confidence_score, token_cost)
        lessons.append(
            {
                "rule_id": rule_id,
                "count": len(group),
                "root_cause": first["root_cause"],
                "prevention": first["prevention"],
                "confidence_label": confidence_label,
                "severity_label": severity_label(metrics["severity_score"]),
                "example_error_type": first["error_type"],
                "example_thread": first["thread_id"],
                **metrics,
            }
        )
    lessons.sort(key=lambda item: (-item["priority_score"], -item["count"], item["rule_id"]))
    return lessons


def solution_patterns(events: list[dict]) -> list[dict]:
    grouped: defaultdict[str, list[dict]] = defaultdict(list)
    for event in events:
        grouped[event["solution_pattern_id"]].append(event)
    patterns: list[dict] = []
    for pattern_id, group in grouped.items():
        definition = SOLUTION_PATTERN_DEFS[pattern_id]
        rules = Counter(event["rule_id"] for event in group)
        token_cost = token_cost_estimate(
            definition["abstraction"],
            definition["safe_pattern"],
            definition["anti_pattern"],
            definition["canonical_example"],
        )
        confidence_score = mean([float(event.get("confidence_score") or 0.0) for event in group])
        metrics = group_metrics(group, confidence_score, token_cost)
        patterns.append(
            {
                "pattern_id": pattern_id,
                "count": len(group),
                "problem_class": definition["problem_class"],
                "abstraction": definition["abstraction"],
                "safe_pattern": definition["safe_pattern"],
                "anti_pattern": definition["anti_pattern"],
                "when_to_use": definition["when_to_use"],
                "when_not_to_use": definition["when_not_to_use"],
                "canonical_example": definition["canonical_example"],
                "target_skill": definition["target_skill"],
                "evidence_rule_counts": dict(rules.most_common()),
                "evidence_error_types": dict(Counter(event["error_type"] for event in group).most_common(5)),
                "severity_label": severity_label(metrics["severity_score"]),
                "example_thread": group[0]["thread_id"],
                **metrics,
            }
        )
    patterns.sort(key=lambda item: (-item["priority_score"], -item["count"], item["pattern_id"]))
    return patterns


def priority_targets(events: list[dict]) -> list[dict]:
    targets: list[dict] = []
    for item in carry_forward(events):
        targets.append(
            {
                "target_type": "rule",
                "target_id": item["rule_id"],
                "count": item["count"],
                "priority_score": item["priority_score"],
                "severity_label": item["severity_label"],
                "thread_count": item["thread_count"],
                "avg_rework_turns_to_resolve": item["avg_rework_turns_to_resolve"],
                "unresolved_count": item["unresolved_count"],
                "confidence_label": item["confidence_label"],
                "token_cost_estimate": item["token_cost_estimate"],
                "recommended_action": item["prevention"],
            }
        )
    for item in solution_patterns(events):
        targets.append(
            {
                "target_type": "pattern",
                "target_id": item["pattern_id"],
                "count": item["count"],
                "priority_score": item["priority_score"],
                "severity_label": item["severity_label"],
                "thread_count": item["thread_count"],
                "avg_rework_turns_to_resolve": item["avg_rework_turns_to_resolve"],
                "unresolved_count": item["unresolved_count"],
                "confidence_label": "mixed",
                "token_cost_estimate": item["token_cost_estimate"],
                "recommended_action": item["safe_pattern"],
            }
        )
    targets.sort(key=lambda item: (-item["priority_score"], -item["count"], item["target_type"], item["target_id"]))
    return targets[:30]


def unmapped_repeated_failures(events: list[dict], min_count: int = 2) -> list[dict]:
    grouped: defaultdict[str, list[dict]] = defaultdict(list)
    for event in events:
        if event["rule_id"] != "ps-unmapped-001":
            continue
        signature = clean(f"{event['category']} | {event['error_type']} | {event['excerpt']}", 260)
        grouped[signature].append(event)
    repeated: list[dict] = []
    for signature, group in grouped.items():
        if len(group) < min_count:
            continue
        repeated.append(
            {
                "count": len(group),
                "signature": signature,
                "category": group[0]["category"],
                "error_type": group[0]["error_type"],
                "candidate_abstraction": "Repeated unmapped diagnostic; inspect examples and promote to a root-cause rule if prevention is stable.",
                "example_thread": group[0]["thread_id"],
                "example_excerpt": group[0]["excerpt"],
            }
        )
    repeated.sort(key=lambda item: (-item["count"], item["signature"]))
    return repeated


def write_sqlite(sqlite_path: Path, summary: dict, events: list[dict]) -> None:
    if sqlite_path.exists():
        sqlite_path.unlink()
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    run_id = f"{summary['mode']}-{summary['window_local']['start'][:10]}-to-{summary['window_local']['end_exclusive'][:10]}"
    with sqlite3.connect(sqlite_path) as conn:
        conn.execute("pragma journal_mode=wal")
        conn.executescript(
            """
            create table runs (
              run_id text primary key,
              mode text not null,
              window_start text not null,
              window_end_exclusive text not null,
              threads_selected integer not null,
              shell_calls_seen integer not null,
              failed_shell_calls_seen integer not null,
              event_count integer not null,
              successful_shell_calls_seen integer not null,
              failed_shell_call_rate_percent real not null,
              shell_call_efficiency_percent real not null,
              detected_event_rate_percent real not null,
              detected_event_efficiency_percent real not null,
              detected_nonzero_events integer not null,
              detected_zero_exit_events integer not null,
              resolved_detected_events integer not null,
              unique_repair_turns_estimate integer not null,
              total_rework_turns_to_resolve integer not null,
              repair_turn_burden_percent real not null,
              lost_time_percent real not null,
              efficiency_percent real not null,
              lost_time_formula text not null,
              efficiency_formula text not null
            );

            create table events (
              run_id text not null,
              event_id text not null,
              local_time text,
              thread_id text,
              thread_source text,
              title text,
              detector_id text,
              tool_name text,
              tool_family text,
              runtime_environment text,
              diagnostic_language text,
              error_family text,
              error_class text,
              category text,
              severity_label text,
              severity_score real,
              confidence_label text,
              confidence_score real,
              rule_id text,
              solution_pattern_id text,
              solution_pattern text,
              error_type text,
              exit_code integer,
              resolved_status text,
              rework_turns_to_resolve integer,
              rework_failed_turns_before_resolve integer,
              rework_repeated_failure_count integer,
              repair_detection_mode text,
              repair_confidence_label text,
              repair_success_similarity real,
              repair_success_command text,
              command text,
              excerpt text,
              workdir text,
              cwd text,
              rollout_path text,
              rollout_line integer,
              primary key (run_id, event_id)
            );

            create table rule_summary (
              run_id text not null,
              rule_id text not null,
              root_cause text,
              prevention text,
              count integer,
              thread_count integer,
              severity_label text,
              priority_score real,
              evidence_score real,
              severity_score real,
              generality_score real,
              rework_score real,
              confidence_label text,
              confidence_score real,
              token_efficiency_score real,
              token_cost_estimate integer,
              avg_rework_turns_to_resolve real,
              max_rework_turns_to_resolve integer,
              unresolved_count integer,
              unresolved_rate real,
              primary key (run_id, rule_id)
            );

            create table pattern_summary (
              run_id text not null,
              pattern_id text not null,
              problem_class text,
              abstraction text,
              safe_pattern text,
              anti_pattern text,
              target_skill text,
              count integer,
              thread_count integer,
              severity_label text,
              priority_score real,
              evidence_score real,
              severity_score real,
              generality_score real,
              rework_score real,
              confidence_score real,
              token_efficiency_score real,
              token_cost_estimate integer,
              avg_rework_turns_to_resolve real,
              max_rework_turns_to_resolve integer,
              unresolved_count integer,
              unresolved_rate real,
              evidence_rule_counts_json text,
              evidence_error_types_json text,
              primary key (run_id, pattern_id)
            );

            create table priority_targets (
              run_id text not null,
              rank integer not null,
              target_type text not null,
              target_id text not null,
              count integer,
              priority_score real,
              severity_label text,
              thread_count integer,
              avg_rework_turns_to_resolve real,
              unresolved_count integer,
              confidence_label text,
              token_cost_estimate integer,
              recommended_action text,
              primary key (run_id, rank)
            );

            create table efficiency_by_error_family (
              run_id text not null,
              error_family text not null,
              event_count integer not null,
              thread_count integer not null,
              detected_nonzero_events integer not null,
              detected_zero_exit_events integer not null,
              resolved_detected_events integer not null,
              unique_repair_turns_estimate integer not null,
              total_rework_turns_to_resolve integer not null,
              avg_rework_turns_to_resolve real not null,
              repair_turn_burden_percent real not null,
              lost_time_percent real not null,
              lost_time_share_percent real not null,
              efficiency_percent real not null,
              formula_note text not null,
              primary key (run_id, error_family)
            );

            create index events_family_idx on events (run_id, error_family);
            create index events_class_idx on events (run_id, error_class);
            create index events_detector_idx on events (run_id, detector_id, tool_family);
            create index events_severity_idx on events (run_id, severity_label, severity_score);
            create index events_rework_idx on events (run_id, rework_turns_to_resolve);

            create view v_rule_priority as
              select * from rule_summary order by priority_score desc, count desc;
            create view v_pattern_priority as
              select * from pattern_summary order by priority_score desc, count desc;
            create view v_efficiency_summary as
              select run_id, mode, window_start, window_end_exclusive,
                     shell_calls_seen, failed_shell_calls_seen,
                     successful_shell_calls_seen, event_count,
                     failed_shell_call_rate_percent,
                     shell_call_efficiency_percent,
                     detected_event_rate_percent,
                     detected_event_efficiency_percent,
                     unique_repair_turns_estimate,
                     total_rework_turns_to_resolve,
                     repair_turn_burden_percent,
                     lost_time_percent,
                     efficiency_percent,
                     lost_time_formula,
                     efficiency_formula
              from runs;
            create view v_lost_time_by_error_family as
              select * from efficiency_by_error_family
              order by lost_time_percent desc, event_count desc;
            create view v_event_classes as
              select run_id, detector_id, tool_name, tool_family, runtime_environment,
                     error_family, error_class, severity_label,
                     count(*) as event_count,
                     count(distinct thread_id) as thread_count,
                     avg(severity_score) as avg_severity,
                     avg(coalesce(rework_turns_to_resolve, 0)) as avg_rework_turns,
                     sum(case when resolved_status = 'no_later_shell_success_observed' then 1 else 0 end) as unresolved_count
              from events
              group by run_id, detector_id, tool_name, tool_family, runtime_environment,
                       error_family, error_class, severity_label;
            create view v_repair_modes as
              select run_id, repair_detection_mode, repair_confidence_label,
                     count(*) as event_count,
                     count(distinct thread_id) as thread_count,
                     avg(coalesce(rework_turns_to_resolve, 0)) as avg_rework_turns,
                     avg(coalesce(repair_success_similarity, 0)) as avg_success_similarity
              from events
              group by run_id, repair_detection_mode, repair_confidence_label;
            """
        )
        conn.execute(
            """
            insert into runs values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                summary["mode"],
                summary["window_local"]["start"],
                summary["window_local"]["end_exclusive"],
                summary["threads_selected"],
                summary["shell_calls_seen"],
                summary["failed_shell_calls_seen"],
                summary["event_count"],
                summary["efficiency"]["successful_shell_calls_seen"],
                summary["efficiency"]["failed_shell_call_rate_percent"],
                summary["efficiency"]["shell_call_efficiency_percent"],
                summary["efficiency"]["detected_event_rate_percent"],
                summary["efficiency"]["detected_event_efficiency_percent"],
                summary["efficiency"]["detected_nonzero_events"],
                summary["efficiency"]["detected_zero_exit_events"],
                summary["efficiency"]["resolved_detected_events"],
                summary["efficiency"]["unique_repair_turns_estimate"],
                summary["efficiency"]["total_rework_turns_to_resolve"],
                summary["efficiency"]["repair_turn_burden_percent"],
                summary["efficiency"]["lost_time_percent"],
                summary["efficiency"]["efficiency_percent"],
                summary["efficiency"]["lost_time_formula"],
                summary["efficiency"]["efficiency_formula"],
            ),
        )
        event_rows = []
        for event in events:
            event_id = f"{event['thread_id']}:{event['rollout_line']}:{event.get('thread_output_index', '')}"
            event_rows.append(
                (
                    run_id,
                    event_id,
                    event.get("local_time"),
                    event.get("thread_id"),
                    event.get("thread_source"),
                    event.get("title"),
                    event.get("detector_id"),
                    event.get("tool_name"),
                    event.get("tool_family"),
                    event.get("runtime_environment"),
                    event.get("diagnostic_language"),
                    event.get("error_family"),
                    event.get("error_class"),
                    event.get("category"),
                    event.get("severity_label"),
                    event.get("severity_score"),
                    event.get("confidence_label"),
                    event.get("confidence_score"),
                    event.get("rule_id"),
                    event.get("solution_pattern_id"),
                    event.get("solution_pattern"),
                    event.get("error_type"),
                    event.get("exit_code"),
                    event.get("resolved_status"),
                    event.get("rework_turns_to_resolve"),
                    event.get("rework_failed_turns_before_resolve"),
                    event.get("rework_repeated_failure_count"),
                    event.get("repair_detection_mode"),
                    event.get("repair_confidence_label"),
                    event.get("repair_success_similarity"),
                    event.get("repair_success_command"),
                    event.get("command"),
                    event.get("excerpt"),
                    event.get("workdir"),
                    event.get("cwd"),
                    event.get("rollout_path"),
                    event.get("rollout_line"),
                )
            )
        conn.executemany(
            """
            insert into events values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            event_rows,
        )
        conn.executemany(
            """
            insert into rule_summary values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    item["rule_id"],
                    item["root_cause"],
                    item["prevention"],
                    item["count"],
                    item["thread_count"],
                    item["severity_label"],
                    item["priority_score"],
                    item["evidence_score"],
                    item["severity_score"],
                    item["generality_score"],
                    item["rework_score"],
                    item["confidence_label"],
                    item["confidence_score"],
                    item["token_efficiency_score"],
                    item["token_cost_estimate"],
                    item["avg_rework_turns_to_resolve"],
                    item["max_rework_turns_to_resolve"],
                    item["unresolved_count"],
                    item["unresolved_rate"],
                )
                for item in summary["carry_forward"]
            ],
        )
        conn.executemany(
            """
            insert into pattern_summary values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    item["pattern_id"],
                    item["problem_class"],
                    item["abstraction"],
                    item["safe_pattern"],
                    item["anti_pattern"],
                    item["target_skill"],
                    item["count"],
                    item["thread_count"],
                    item["severity_label"],
                    item["priority_score"],
                    item["evidence_score"],
                    item["severity_score"],
                    item["generality_score"],
                    item["rework_score"],
                    item["confidence_score"],
                    item["token_efficiency_score"],
                    item["token_cost_estimate"],
                    item["avg_rework_turns_to_resolve"],
                    item["max_rework_turns_to_resolve"],
                    item["unresolved_count"],
                    item["unresolved_rate"],
                    json.dumps(item["evidence_rule_counts"], sort_keys=True),
                    json.dumps(item["evidence_error_types"], sort_keys=True),
                )
                for item in summary["solution_patterns"]
            ],
        )
        conn.executemany(
            """
            insert into priority_targets values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    rank,
                    item["target_type"],
                    item["target_id"],
                    item["count"],
                    item["priority_score"],
                    item["severity_label"],
                    item["thread_count"],
                    item["avg_rework_turns_to_resolve"],
                    item["unresolved_count"],
                    item["confidence_label"],
                    item["token_cost_estimate"],
                    item["recommended_action"],
                )
                for rank, item in enumerate(summary["priority_targets"], 1)
            ],
        )
        conn.executemany(
            """
            insert into efficiency_by_error_family values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    item["error_family"],
                    item["event_count"],
                    item["thread_count"],
                    item["detected_nonzero_events"],
                    item["detected_zero_exit_events"],
                    item["resolved_detected_events"],
                    item["unique_repair_turns_estimate"],
                    item["total_rework_turns_to_resolve"],
                    item["avg_rework_turns_to_resolve"],
                    item["repair_turn_burden_percent"],
                    item["lost_time_percent"],
                    item["lost_time_share_percent"],
                    item["efficiency_percent"],
                    item["formula_note"],
                )
                for item in summary["efficiency_by_error_family"]
            ],
        )


def write_outputs(args: argparse.Namespace, summary: dict, events: list[dict]) -> dict:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    start = summary["window_local"]["start"][:10]
    end = (datetime.fromisoformat(summary["window_local"]["end_exclusive"]) - timedelta(days=1)).date().isoformat()
    prefix = args.prefix or f"codex-failures-{args.mode}-{start}_to_{end}"
    csv_path = output_dir / f"{prefix}.csv"
    json_path = output_dir / f"{prefix}.json"
    md_path = output_dir / f"{prefix}.md"
    sqlite_path = Path(args.sqlite_path) if args.sqlite_path else output_dir / f"{prefix}.sqlite"

    fields = [
        "local_time",
        "thread_id",
        "thread_source",
        "title",
        "detector_id",
        "tool_name",
        "tool_family",
        "runtime_environment",
        "diagnostic_language",
        "error_family",
        "error_class",
        "category",
        "quoting_subtype",
        "error_type",
        "rule_id",
        "root_cause",
        "prevention",
        "solution_pattern_id",
        "solution_pattern",
        "severity_label",
        "severity_score",
        "confidence_label",
        "confidence_score",
        "resolved_status",
        "rework_turns_to_resolve",
        "rework_failed_turns_before_resolve",
        "rework_repeated_failure_count",
        "repair_detection_mode",
        "repair_confidence_label",
        "repair_success_similarity",
        "repair_success_command",
        "exit_code",
        "thread_output_index",
        "command",
        "excerpt",
        "workdir",
        "rollout_path",
        "rollout_line",
        "cwd",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(events)
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump({"summary": summary, "events": events}, handle, indent=2)
    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write("# Codex Failure Analysis\n\n")
        handle.write(f"Mode: `{summary['mode']}`\n\n")
        handle.write(f"Window: {summary['window_local']['start']} to {summary['window_local']['end_exclusive']} exclusive\n\n")
        handle.write(f"Events: {summary['event_count']}\n\n")
        efficiency = summary["efficiency"]
        handle.write("## Efficiency\n\n")
        handle.write(f"- shell-call efficiency: {efficiency['shell_call_efficiency_percent']}%\n")
        handle.write(f"- failed shell-call rate: {efficiency['failed_shell_call_rate_percent']}%\n")
        handle.write(f"- detected-event efficiency: {efficiency['detected_event_efficiency_percent']}%\n")
        handle.write(f"- detected-event rate: {efficiency['detected_event_rate_percent']}%\n")
        handle.write(f"- lost-time estimate: {efficiency['lost_time_percent']}%\n")
        handle.write(f"- efficiency percent: {efficiency['efficiency_percent']}%\n")
        handle.write(f"- repair turns: {efficiency['unique_repair_turns_estimate']} unique, {efficiency['total_rework_turns_to_resolve']} summed\n")
        handle.write(f"- formula: `{efficiency['lost_time_formula']}`\n")
        handle.write(f"- note: {efficiency['notes']}\n\n")
        if summary["efficiency_by_error_family"]:
            handle.write("### Lost Time By Error Family\n\n")
            for item in summary["efficiency_by_error_family"][:12]:
                handle.write(
                    f"- {item['error_family']}: lost {item['lost_time_percent']}%, "
                    f"share {item['lost_time_share_percent']}%, "
                    f"{item['unique_repair_turns_estimate']} repair turns, "
                    f"{item['event_count']} events\n"
                )
            handle.write("\n")
        if summary["detector_counts"]:
            handle.write("## Detectors\n\n")
            for key, value in summary["detector_counts"].items():
                handle.write(f"- {key}: {value}\n")
            handle.write("\n")
        handle.write("## Categories\n\n")
        for key, value in summary["category_counts"].items():
            handle.write(f"- {key}: {value}\n")
        if summary["quoting_subtype_counts"]:
            handle.write("\n## Quoting Subtypes\n\n")
            for key, value in summary["quoting_subtype_counts"].items():
                handle.write(f"- {key}: {value}\n")
        if summary["carry_forward"]:
            handle.write("\n## Root Cause Analysis\n\n")
            for lesson in summary["carry_forward"]:
                handle.write(f"- {lesson['count']} - {lesson['rule_id']}: {lesson['root_cause']}\n")
                handle.write(f"  - prevention: {lesson['prevention']}\n")
                handle.write(f"  - example: {lesson['example_error_type']} in `{lesson['example_thread']}`\n")
        if summary["solution_patterns"]:
            handle.write("\n## Solution Patterns\n\n")
            for pattern in summary["solution_patterns"]:
                handle.write(f"### {pattern['pattern_id']} ({pattern['count']}, priority {pattern['priority_score']})\n\n")
                handle.write(f"- class: {pattern['problem_class']}\n")
                handle.write(f"- severity: {pattern['severity_label']} score {pattern['severity_score']}\n")
                handle.write(f"- rework: avg {pattern['avg_rework_turns_to_resolve']} turns, unresolved {pattern['unresolved_count']}\n")
                handle.write(f"- token cost estimate: {pattern['token_cost_estimate']}\n")
                handle.write(f"- abstraction: {pattern['abstraction']}\n")
                handle.write(f"- safe pattern: {pattern['safe_pattern']}\n")
                handle.write(f"- anti-pattern: {pattern['anti_pattern']}\n")
                handle.write(f"- when to use: {pattern['when_to_use']}\n")
                handle.write(f"- when not to use: {pattern['when_not_to_use']}\n")
                handle.write(f"- target skill: {pattern['target_skill']}\n")
                handle.write(f"- evidence rules: {pattern['evidence_rule_counts']}\n\n")
                handle.write("```powershell\n")
                handle.write(pattern["canonical_example"].rstrip() + "\n")
                handle.write("```\n\n")
        if summary["priority_targets"]:
            handle.write("\n## Priority Targets\n\n")
            for item in summary["priority_targets"][:20]:
                handle.write(
                    f"- {item['priority_score']} - {item['target_type']} `{item['target_id']}`: "
                    f"{item['count']} events, {item['thread_count']} threads, "
                    f"{item['severity_label']} severity, avg rework {item['avg_rework_turns_to_resolve']}, "
                    f"token cost {item['token_cost_estimate']}\n"
                )
        if summary["unmapped_repeated_failures"]:
            handle.write("\n## Unmapped Repeated Failures\n\n")
            for item in summary["unmapped_repeated_failures"]:
                handle.write(f"- {item['count']} - {item['signature']}\n")
                handle.write(f"  - candidate abstraction: {item['candidate_abstraction']}\n")
                handle.write(f"  - example: `{item['example_thread']}` - {item['example_excerpt']}\n")
        handle.write("\n## Top Threads\n\n")
        for thread in summary["threads_with_events"][:20]:
            handle.write(f"- {thread['count']} - {thread['title']} - `{thread['thread_id']}`\n")
            handle.write(f"  - first: {thread['first']} last: {thread['last']}\n")
            handle.write(f"  - rollout: {thread['rollout_path']}\n")
            handle.write(f"  - categories: {thread['top_categories']}\n")
    write_sqlite(sqlite_path, summary, events)
    return {"csv_path": str(csv_path), "json_path": str(json_path), "md_path": str(md_path), "sqlite_path": str(sqlite_path)}


def main() -> None:
    args = parse_args()
    summary, events = scan(args)
    paths = write_outputs(args, summary, events)
    print(json.dumps({"paths": paths, "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
