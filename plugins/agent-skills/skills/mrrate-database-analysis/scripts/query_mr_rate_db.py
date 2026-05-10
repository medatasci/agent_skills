#!/usr/bin/env python3
"""Run read-only queries against the local MR-RATE SQLite database."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path


DEFAULT_DB = Path("research-data") / "mr-rate.sqlite"

DESCRIPTOR_SQL = {
    "views": """
        SELECT view_name, grain, best_for, default_count_unit, privacy_note, example_question
        FROM llm_query_view_catalog
        ORDER BY view_name
    """,
    "columns": """
        SELECT view_name, column_name, meaning, counting_role, natural_language_aliases
        FROM llm_query_column_catalog
        ORDER BY view_name, column_name
    """,
    "intents": """
        SELECT intent_name, natural_language_triggers, preferred_views, counting_rule, caveats
        FROM llm_query_intent_catalog
        ORDER BY intent_name
    """,
    "rules": """
        SELECT rule_name, guidance, example
        FROM llm_query_rules
        ORDER BY rule_name
    """,
    "examples": """
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
    """,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sql", nargs="?", help="SQL query to run. Defaults to a source/status summary.")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(), help="Workspace root for relative database paths.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help=f"SQLite database path. Default: {DEFAULT_DB}")
    parser.add_argument("--sql-file", type=Path, help="Read SQL from a file instead of the positional argument.")
    parser.add_argument(
        "--describe",
        choices=sorted(DESCRIPTOR_SQL),
        help="Show the LLM-oriented query dictionary instead of running custom SQL.",
    )
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table", help="Output format.")
    parser.add_argument("--limit", type=int, default=100, help="Display limit for table output.")
    return parser.parse_args()


def default_sql() -> str:
    return """
    SELECT path, kind, row_count, size_bytes
    FROM source_files
    ORDER BY id
    """


def resolve_path(workspace: Path, path: Path) -> Path:
    if path.is_absolute():
        return path
    return workspace / path


def read_sql(args: argparse.Namespace) -> str:
    if args.describe:
        return DESCRIPTOR_SQL[args.describe]
    if args.sql_file:
        sql_file = resolve_path(args.workspace, args.sql_file)
        return sql_file.read_text(encoding="utf-8")
    return args.sql or default_sql()


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


def descriptor_error(kind: str | None, exc: sqlite3.OperationalError) -> SystemExit:
    message = str(exc)
    if kind and "no such table" in message.lower():
        return SystemExit(
            "Descriptor tables are missing from this database. "
            "Rebuild or refresh the MR-RATE SQLite schema with the project DB builder, "
            "then retry the --describe request."
        )
    return SystemExit(f"SQLite error: {message}")


def main() -> None:
    args = parse_args()
    args.workspace = args.workspace.resolve()
    db_path = resolve_path(args.workspace, args.db)
    sql = read_sql(args)
    try:
        with connect_readonly(db_path) as conn:
            columns, rows = fetch_rows(conn, sql)
    except sqlite3.OperationalError as exc:
        raise descriptor_error(args.describe, exc) from exc
    if args.format == "json":
        print_json(columns, rows)
    elif args.format == "csv":
        print_csv(columns, rows)
    else:
        print_table(columns, rows, args.limit)


if __name__ == "__main__":
    main()
