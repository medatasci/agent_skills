from __future__ import annotations

import argparse
import json
import sys

from .catalog import build_catalog, load_skill_metadata, search_catalog, upload_skill
from .feedback import FeedbackDraft
from .install import download_skill, install_skill, list_installed, remove_installed_skill, resolve_install_dir
from .validate import validate_skill


def print_json(data: object) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def command_validate(args: argparse.Namespace) -> int:
    result = validate_skill(args.path)
    payload = {
        "ok": result.ok,
        "skill_dir": str(result.skill_dir),
        "metadata": result.metadata,
        "errors": result.errors,
        "warnings": result.warnings,
    }
    if args.json:
        print_json(payload)
    else:
        print(f"Validation {'passed' if result.ok else 'failed'}: {result.skill_dir}")
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        for warning in result.warnings:
            print(f"WARNING: {warning}")
    return 0 if result.ok else 1


def command_upload(args: argparse.Namespace) -> int:
    try:
        metadata = upload_skill(
            args.path,
            owner=args.owner,
            source_url=args.source_url,
            force=args.force,
        )
    except Exception as exc:
        print(f"upload failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(metadata)
    else:
        print(f"Uploaded {metadata['id']} to {metadata['catalog_path']}")
        if metadata.get("warnings"):
            for warning in metadata["warnings"]:
                print(f"WARNING: {warning}")
    return 0


def command_build_catalog(args: argparse.Namespace) -> int:
    catalog = build_catalog()
    if args.json:
        print_json(catalog)
    else:
        print(f"Built catalog with {len(catalog.get('skills', []))} skills")
    return 0


def command_search(args: argparse.Namespace) -> int:
    results = search_catalog(args.query, limit=args.limit)
    if args.json:
        print_json({"query": args.query, "results": results})
    else:
        if not results:
            print("No matching skills found")
            return 1
        for item in results:
            print(f"{item['id']}  score={item['score']}")
            print(f"  {item['description']}")
    return 0


def command_info(args: argparse.Namespace) -> int:
    try:
        metadata = load_skill_metadata(args.skill_id)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.json:
        print_json(metadata)
    else:
        print(metadata["id"])
        print(metadata["description"])
        print(f"Owner: {metadata['owner']}")
        print(f"Source: {metadata['source']['path']}")
        print(f"Checksum: {metadata['checksum']['value']}")
        print("Install:")
        print(f"  {metadata['codex']['global_install_command']}")
        print(f"  {metadata['codex']['project_install_command']}")
    return 0


def command_install(args: argparse.Namespace) -> int:
    try:
        target = install_skill(args.skill_id, scope=args.scope, project=args.project, force=args.force)
    except Exception as exc:
        print(f"install failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json({"installed": args.skill_id, "target": str(target), "scope": args.scope})
    else:
        print(f"Installed {args.skill_id} to {target}")
    return 0


def command_download(args: argparse.Namespace) -> int:
    try:
        target = download_skill(args.skill_id, destination=args.destination, force=args.force)
    except Exception as exc:
        print(f"download failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json({"downloaded": args.skill_id, "target": str(target)})
    else:
        print(f"Downloaded {args.skill_id} to {target}")
    return 0


def command_list(args: argparse.Namespace) -> int:
    try:
        skills = list_installed(args.scope, args.project)
    except Exception as exc:
        print(f"list failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json({"scope": args.scope, "skills": skills})
    else:
        if not skills:
            print("No installed skills found")
        for skill in skills:
            status = "ok" if skill["ok"] else "invalid"
            print(f"{skill['id']}  {status}  {skill['path']}")
    return 0


def command_remove(args: argparse.Namespace) -> int:
    if not args.yes:
        print("remove requires --yes to confirm uninstall", file=sys.stderr)
        return 1
    try:
        target = remove_installed_skill(args.skill_id, scope=args.scope, project=args.project)
    except Exception as exc:
        print(f"remove failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json({"removed": args.skill_id, "target": str(target), "scope": args.scope})
    else:
        print(f"Removed {args.skill_id} from {target}")
    return 0


def command_feedback(args: argparse.Namespace) -> int:
    draft = FeedbackDraft(
        skill_id=args.skill_id,
        trying=args.trying,
        happened=args.happened,
        outcome=args.outcome,
        suggestion=args.suggestion,
        title=args.title,
    )
    payload = draft.as_dict()
    if args.json:
        print_json(payload)
    else:
        print("GitHub issue:")
        print(f"  Title: {payload['title']}")
        print(f"  URL: {payload['issue_url']}")
        print()
        print("Feedback screen:")
        for field in payload["screen"]:
            suffix = "" if field["label"].endswith("?") else ":"
            print(f"{field['label']}{suffix}")
            print(field["value"])
            print()
    return 0


def command_doctor(args: argparse.Namespace) -> int:
    global_dir = resolve_install_dir("global")
    project_dir = resolve_install_dir("project", args.project) if args.project else None
    payload = {
        "global_codex_skills_dir": str(global_dir),
        "global_exists": global_dir.exists(),
        "project_codex_skills_dir": str(project_dir) if project_dir else None,
        "project_exists": project_dir.exists() if project_dir else None,
    }
    if args.json:
        print_json(payload)
    else:
        print(f"Global Codex skills: {payload['global_codex_skills_dir']} ({'exists' if payload['global_exists'] else 'missing'})")
        if project_dir:
            print(f"Project Codex skills: {payload['project_codex_skills_dir']} ({'exists' if payload['project_exists'] else 'missing'})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m skillforge", description="SkillForge catalog and Codex installer")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate a local skill folder")
    validate.add_argument("path")
    validate.add_argument("--json", action="store_true")
    validate.set_defaults(func=command_validate)

    upload = sub.add_parser("upload", help="Add or update a skill in the local catalog")
    upload.add_argument("path")
    upload.add_argument("--owner", required=True)
    upload.add_argument("--source-url")
    upload.add_argument("--force", action="store_true")
    upload.add_argument("--json", action="store_true")
    upload.set_defaults(func=command_upload)

    build = sub.add_parser("build-catalog", help="Regenerate catalog/skills.json")
    build.add_argument("--json", action="store_true")
    build.set_defaults(func=command_build_catalog)

    search = sub.add_parser("search", help="Search local catalog")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--json", action="store_true")
    search.set_defaults(func=command_search)

    info = sub.add_parser("info", help="Show skill metadata")
    info.add_argument("skill_id")
    info.add_argument("--json", action="store_true")
    info.set_defaults(func=command_info)

    install = sub.add_parser("install", help="Install a skill into Codex")
    install.add_argument("skill_id")
    install.add_argument("--scope", choices=["global", "project"], default="global")
    install.add_argument("--project")
    install.add_argument("--force", action="store_true")
    install.add_argument("--json", action="store_true")
    install.set_defaults(func=command_install)

    download = sub.add_parser("download", help="Copy a catalog skill to a local folder")
    download.add_argument("skill_id")
    download.add_argument("--destination", default="downloads")
    download.add_argument("--force", action="store_true")
    download.add_argument("--json", action="store_true")
    download.set_defaults(func=command_download)

    list_cmd = sub.add_parser("list", help="List installed Codex skills")
    list_cmd.add_argument("--scope", choices=["global", "project"], default="global")
    list_cmd.add_argument("--project")
    list_cmd.add_argument("--json", action="store_true")
    list_cmd.set_defaults(func=command_list)

    remove = sub.add_parser("remove", help="Remove an installed Codex skill")
    remove.add_argument("skill_id")
    remove.add_argument("--scope", choices=["global", "project"], default="global")
    remove.add_argument("--project")
    remove.add_argument("--yes", action="store_true", help="Confirm removal")
    remove.add_argument("--json", action="store_true")
    remove.set_defaults(func=command_remove)

    feedback = sub.add_parser("feedback", help="Draft feedback for a SkillForge subject")
    feedback.add_argument("skill_id", metavar="subject", help="Skill, Python helper, CLI command, or documentation area")
    feedback.add_argument("--trying", required=True, help="What you were trying to do")
    feedback.add_argument("--happened", required=True, help="What worked, failed, confused you, or could be improved")
    feedback.add_argument(
        "--outcome",
        default="I found a bug or confusing behavior",
        choices=[
            "Helped me complete the task",
            "Partially helped",
            "Did not help",
            "I have an improvement idea",
            "I found a bug or confusing behavior",
        ],
    )
    feedback.add_argument("--suggestion", help="Suggested improvement")
    feedback.add_argument("--title", help="Override generated GitHub issue title")
    feedback.add_argument("--json", action="store_true")
    feedback.set_defaults(func=command_feedback)

    doctor = sub.add_parser("doctor", help="Show Codex path diagnostics")
    doctor.add_argument("--project")
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(func=command_doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
