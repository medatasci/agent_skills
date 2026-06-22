#!/usr/bin/env python3
"""Create or update manuscript-builder publication files for a project."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


FILES = {
    "project_publication.html": "project_publication_template.html",
    "publication_claims.json": "publication_claims.template.json",
    "publication_experiments.json": "publication_experiments.template.json",
    "publication_figures.json": "publication_figures.template.json",
    "publication_tables.json": "publication_tables.template.json",
    "publication_references.bib": "publication_references.template.bib",
}


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def render_template(text: str, project_title: str, date: str) -> str:
    return (
        text.replace("{{PROJECT_TITLE}}", project_title)
        .replace("{{DATE}}", date)
    )


def create_missing_files(project: Path, project_title: str, dry_run: bool) -> list[str]:
    assets = skill_dir() / "assets"
    created: list[str] = []
    date = today()

    for output_name, template_name in FILES.items():
        output_path = project / output_name
        if output_path.exists():
            continue
        template_path = assets / template_name
        text = template_path.read_text(encoding="utf-8")
        rendered = render_template(text, project_title, date)
        created.append(output_name)
        if not dry_run:
            output_path.write_text(rendered, encoding="utf-8", newline="\n")

    updates_path = project / "publication_updates.jsonl"
    if not updates_path.exists():
        created.append("publication_updates.jsonl")
        if not dry_run:
            entry = {
                "timestamp": now_iso(),
                "summary": "Initialized publication manuscript files.",
                "changed_files": sorted(created),
                "weak_areas": [
                    "Replace placeholders with project-specific goals, motivation, claims, experiments, and evidence."
                ],
                "next_steps": [
                    "Fill project_publication.html sections that are currently placeholders.",
                    "Replace placeholder records in publication JSON and BibTeX files."
                ],
            }
            updates_path.write_text(json.dumps(entry, ensure_ascii=True) + "\n", encoding="utf-8")

    return created


def append_update(
    project: Path,
    summary: str | None,
    changed_files: list[str],
    weak_areas: list[str],
    next_steps: list[str],
    dry_run: bool,
) -> bool:
    if not summary and not weak_areas and not next_steps:
        return False

    entry = {
        "timestamp": now_iso(),
        "summary": summary or "Updated publication manuscript files.",
        "changed_files": changed_files,
        "weak_areas": weak_areas,
        "next_steps": next_steps,
    }
    if not dry_run:
        with (project / "publication_updates.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(entry, ensure_ascii=True) + "\n")
    return True


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".", help="Project root to update.")
    parser.add_argument("--title", help="Project title for newly created files.")
    parser.add_argument("--summary", help="Append a short publication update summary.")
    parser.add_argument("--changed-file", action="append", default=[], help="File changed by this update.")
    parser.add_argument("--weak-area", action="append", default=[], help="Weak manuscript area to record.")
    parser.add_argument("--next-step", action="append", default=[], help="Publication-readiness next step.")
    parser.add_argument("--dry-run", action="store_true", help="Report actions without writing files.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    project = Path(args.project).resolve()
    if not project.exists() or not project.is_dir():
        print(f"Project directory not found: {project}", file=sys.stderr)
        return 2

    project_title = args.title or project.name
    created = create_missing_files(project, project_title, args.dry_run)
    appended = append_update(
        project,
        args.summary,
        args.changed_file or created,
        args.weak_area,
        args.next_step,
        args.dry_run,
    )

    result = {
        "project": str(project),
        "created": created,
        "appended_update": appended,
        "dry_run": args.dry_run,
    }
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=True))
    else:
        if created:
            print("Created: " + ", ".join(created))
        else:
            print("All publication files already exist.")
        if appended:
            print("Appended publication update entry.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
