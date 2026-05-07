#!/usr/bin/env python3
"""Orchestrate MR-RATE source download and SQLite import from a workspace."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_CDP_URL = "http://127.0.0.1:9222"
DEFAULT_GROUPS = "reports,labels,metadata"
ALL_BATCHES = [f"{index:02d}" for index in range(28)]
GROUP_ORDER = ["reports", "labels", "metadata", "mri"]


def normalize_batch(value: str) -> str:
    text = value.strip().lower().removeprefix("batch")
    if text == "all":
        return text
    return f"{int(text):02d}"


def parse_batches(value: str) -> list[str]:
    batches: list[str] = []
    for part in value.split(","):
        normalized = normalize_batch(part)
        if normalized == "all":
            batches.extend(ALL_BATCHES)
        else:
            batches.append(normalized)
    return list(dict.fromkeys(batches))


def parse_groups(value: str) -> set[str]:
    groups = {part.strip().lower() for part in value.split(",") if part.strip()}
    unknown = groups - set(GROUP_ORDER)
    if unknown:
        raise SystemExit(f"Unknown source group(s): {', '.join(sorted(unknown))}")
    return groups


def format_groups(groups: set[str]) -> str:
    return ",".join(group for group in GROUP_ORDER if group in groups)


def bundled_python() -> str:
    candidate = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "python" / "python.exe"
    if candidate.exists():
        return str(candidate)
    return sys.executable


def bundled_node() -> str:
    candidate = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "node" / "bin" / "node.exe"
    if candidate.exists():
        return str(candidate)
    return "node"


def run_command(command: list[str], cwd: Path, dry_run: bool = False) -> None:
    print(" ".join(quote_arg(part) for part in command))
    if dry_run:
        return
    subprocess.run(command, cwd=str(cwd), check=True)


def quote_arg(value: str) -> str:
    if not value or any(ch.isspace() for ch in value):
        return f'"{value}"'
    return value


def ensure_workspace_tools(workspace: Path) -> None:
    required = [
        workspace / "tools" / "browser_download_mr_rate_batch.js",
        workspace / "tools" / "build_mr_rate_db.py",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing required MR-RATE project tool(s):\n" + "\n".join(missing))


def download_batches(args: argparse.Namespace, batches: list[str]) -> None:
    ensure_workspace_tools(args.workspace)
    node = args.node or bundled_node()
    script = args.workspace / "tools" / "browser_download_mr_rate_batch.js"
    requested_groups = parse_groups(args.groups)
    for index, batch in enumerate(batches):
        batch_groups = set(requested_groups)
        if "labels" in requested_groups and index > 0:
            batch_groups.discard("labels")
        if not batch_groups:
            continue
        command = [
            node,
            str(script),
            "--cdp-url",
            args.cdp_url,
            "--batch",
            batch,
            "--include",
            format_groups(batch_groups),
            "--wait-seconds",
            str(args.wait_seconds),
        ]
        if args.download_dry_run:
            command.append("--dry-run")
        run_command(command, args.workspace, dry_run=args.command_dry_run)


def import_batches(args: argparse.Namespace, batches: list[str]) -> None:
    ensure_workspace_tools(args.workspace)
    python = args.python or bundled_python()
    builder = args.workspace / "tools" / "build_mr_rate_db.py"
    requested_groups = parse_groups(args.groups)
    for index, batch in enumerate(batches):
        command = [python, str(builder), "--batch", batch]
        if args.skip_derived or index > 0:
            command.append("--skip-derived")
        if "reports" not in requested_groups:
            command.append("--skip-source-reports")
        if args.defer_labels or "labels" not in requested_groups:
            command.append("--skip-labels")
        if "metadata" not in requested_groups:
            command.append("--skip-metadata")
        if "mri" not in requested_groups:
            command.append("--skip-mri")
        run_command(command, args.workspace, dry_run=args.command_dry_run)

    if args.defer_labels and "labels" in requested_groups:
        labels_csv = args.workspace / "research-data" / "sources" / "mr-rate" / "pathology_labels" / "mrrate_labels.csv"
        command = [
            python,
            str(builder),
            "--skip-derived",
            "--skip-source-reports",
            "--labels-csv",
            str(labels_csv),
            "--labels-existing-studies-only",
            "--skip-metadata",
            "--skip-mri",
        ]
        run_command(command, args.workspace, dry_run=args.command_dry_run)


def status(args: argparse.Namespace) -> None:
    db_path = args.workspace / "research-data" / "mr-rate.sqlite"
    source_root = args.workspace / "research-data" / "sources" / "mr-rate"
    payload = {
        "workspace": str(args.workspace),
        "database_exists": db_path.exists(),
        "database": str(db_path),
        "source_root": str(source_root),
        "source_files": [],
    }
    if source_root.exists():
        for path in sorted(source_root.rglob("*")):
            if path.is_file():
                payload["source_files"].append(
                    {
                        "path": str(path.relative_to(args.workspace)),
                        "bytes": path.stat().st_size,
                    }
                )
    print(json.dumps(payload, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["download", "import", "run", "status"])
    parser.add_argument("--workspace", type=Path, default=Path.cwd(), help="MR-RATE project workspace root.")
    parser.add_argument("--batches", default="01", help="Comma-separated batches or all. Example: 00,01 or all.")
    parser.add_argument("--groups", default=DEFAULT_GROUPS, help="Comma-separated download groups: reports,labels,metadata. Add mri only explicitly.")
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL, help="Persistent NVIDIA Chrome DevTools endpoint.")
    parser.add_argument("--wait-seconds", type=int, default=60)
    parser.add_argument("--python", default=os.environ.get("PYTHON", ""))
    parser.add_argument("--node", default=os.environ.get("NODE", ""))
    parser.add_argument("--skip-derived", action="store_true", help="Skip derived local analysis CSV import.")
    parser.add_argument("--defer-labels", action="store_true", help="Import labels once after all selected batches are loaded.")
    parser.add_argument("--download-dry-run", action="store_true", help="Pass --dry-run to the browser downloader.")
    parser.add_argument("--command-dry-run", action="store_true", help="Print commands without running them.")
    args = parser.parse_args()
    args.workspace = args.workspace.resolve()
    return args


def main() -> None:
    args = parse_args()
    batches = parse_batches(args.batches)
    if args.command == "status":
        status(args)
        return
    if args.command in {"download", "run"}:
        download_batches(args, batches)
    if args.command in {"import", "run"}:
        import_batches(args, batches)


if __name__ == "__main__":
    main()
