#!/usr/bin/env python3
"""Orchestrate MR-RATE source download and SQLite import from a workspace."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path


DEFAULT_CDP_URL = "http://127.0.0.1:9222"
DEFAULT_GROUPS = "reports,labels,metadata"
DEFAULT_DB = Path("research-data") / "mr-rate.sqlite"
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


def default_query_sql() -> str:
    return """
    SELECT path, kind, row_count, size_bytes
    FROM source_files
    ORDER BY id
    """


def descriptor_sql(kind: str) -> str:
    if kind == "views":
        return """
        SELECT view_name, grain, best_for, default_count_unit, privacy_note, example_question
        FROM llm_query_view_catalog
        ORDER BY view_name
        """
    if kind == "columns":
        return """
        SELECT view_name, column_name, meaning, counting_role, natural_language_aliases
        FROM llm_query_column_catalog
        ORDER BY view_name, column_name
        """
    if kind == "intents":
        return """
        SELECT intent_name, natural_language_triggers, preferred_views, counting_rule, caveats
        FROM llm_query_intent_catalog
        ORDER BY intent_name
        """
    if kind == "rules":
        return """
        SELECT rule_name, guidance, example
        FROM llm_query_rules
        ORDER BY rule_name
        """
    if kind == "examples":
        return """
        SELECT view_name, example_type, natural_language, query_sql, notes
        FROM llm_query_examples
        ORDER BY view_name,
                 CASE example_type
                     WHEN 'direct' THEN 1
                     WHEN 'filter_summary' THEN 2
                     WHEN 'join' THEN 3
                     ELSE 4
                 END,
                 natural_language
        """
    raise SystemExit(f"Unknown descriptor: {kind}")


def read_query_sql(args: argparse.Namespace) -> str:
    if args.describe:
        return descriptor_sql(args.describe)
    if args.sql_file:
        return args.sql_file.read_text(encoding="utf-8")
    return args.sql or default_query_sql()


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_rows(conn: sqlite3.Connection, sql: str) -> tuple[list[str], list[sqlite3.Row]]:
    cursor = conn.execute(sql)
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description or []]
    return columns, rows


def print_json(columns: list[str], rows: list[sqlite3.Row]) -> None:
    print(json.dumps([{column: row[column] for column in columns} for row in rows], indent=2))


def print_csv(columns: list[str], rows: list[sqlite3.Row]) -> None:
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([row[column] for column in columns])


def print_table(columns: list[str], rows: list[sqlite3.Row], limit: int) -> None:
    display_rows = rows[:limit]
    values = [[str(row[column] if row[column] is not None else "") for column in columns] for row in display_rows]
    widths = [
        max([len(column), *(len(value[index]) for value in values)] or [len(column)])
        for index, column in enumerate(columns)
    ]
    print(" | ".join(column.ljust(widths[index]) for index, column in enumerate(columns)))
    print("-+-".join("-" * width for width in widths))
    for value in values:
        print(" | ".join(value[index].ljust(widths[index]) for index in range(len(columns))))
    if len(rows) > limit:
        print(f"... {len(rows) - limit} more row(s). Re-run with --format json/csv or a larger --limit.")


def query_database(args: argparse.Namespace) -> None:
    db_path = args.db
    if not db_path.is_absolute():
        db_path = args.workspace / db_path
    sql = read_query_sql(args)
    try:
        with connect_readonly(db_path) as conn:
            columns, rows = fetch_rows(conn, sql)
    except sqlite3.OperationalError as error:
        if args.describe and "no such table" in str(error).lower():
            raise SystemExit(
                "The selected database does not contain the LLM query descriptor tables. "
                "Refresh the schema with the project MR-RATE DB builder, then retry."
            ) from error
        raise
    if args.format == "json":
        print_json(columns, rows)
    elif args.format == "csv":
        print_csv(columns, rows)
    else:
        print_table(columns, rows, args.limit)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["download", "import", "run", "status", "query"])
    parser.add_argument("sql", nargs="?", help="SQL query to run for the query command.")
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
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help=f"SQLite database path for query. Default: {DEFAULT_DB}")
    parser.add_argument("--sql-file", type=Path, help="Read query SQL from a file.")
    parser.add_argument(
        "--describe",
        choices=["views", "columns", "intents", "rules", "examples"],
        help="Show the LLM-oriented query dictionary instead of running custom SQL.",
    )
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table", help="Query output format.")
    parser.add_argument("--limit", type=int, default=100, help="Display limit for table query output.")
    args = parser.parse_args()
    args.workspace = args.workspace.resolve()
    return args


def main() -> None:
    args = parse_args()
    batches = parse_batches(args.batches)
    if args.command == "status":
        status(args)
        return
    if args.command == "query":
        query_database(args)
        return
    if args.command in {"download", "run"}:
        download_batches(args, batches)
    if args.command in {"import", "run"}:
        import_batches(args, batches)


if __name__ == "__main__":
    main()
