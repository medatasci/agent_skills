from __future__ import annotations

import argparse
import json
import sys

from .catalog import (
    build_catalog,
    evaluate_skill,
    load_skill_metadata,
    search_audit_skill,
    search_catalog,
    upload_skill,
)
from .create import create_skill
from .feedback import FeedbackDraft
from .install import download_skill, install_skill, list_installed, remove_installed_skill, resolve_install_dir
from .peer import cache_listing, clear_cache, import_peer_skill, install_peer_skill, peer_diagnostics, peer_search, refresh_cache
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


def command_search_audit(args: argparse.Namespace) -> int:
    try:
        payload = search_audit_skill(args.skill_id)
    except Exception as exc:
        print(f"search audit failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print(f"Search/SEO audit for {payload['skill_id']}: {payload['score']}/100")
        if not payload["recommendations"]:
            print("No search/SEO gaps found")
        for recommendation in payload["recommendations"]:
            print(f"- {recommendation['category']}: {recommendation['recommendation']}")
            print(f"  Files: {', '.join(recommendation['files'])}")
    return 0


def command_create(args: argparse.Namespace) -> int:
    try:
        payload = create_skill(
            args.skill_id,
            title=args.title,
            description=args.description,
            owner=args.owner,
            categories=args.category or [],
            tags=args.tag or [],
            risk_level=args.risk_level,
            force=args.force,
        )
    except Exception as exc:
        print(f"create failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print(f"Created {payload['skill_id']} at {payload['skill_dir']}")
        print("Files:")
        for file_path in payload["files"]:
            print(f"  {file_path}")
        placeholders = payload.get("placeholders_remaining", {})
        if placeholders:
            print("Template placeholders remain; replace them before publication:")
            for file_name, values in placeholders.items():
                print(f"  {file_name}: {len(values)} placeholders")
        print("Next commands:")
        for command in payload["next_commands"]:
            print(f"  {command}")
    return 0 if payload["validation"]["ok"] else 1


def command_evaluate(args: argparse.Namespace) -> int:
    try:
        payload = evaluate_skill(args.target)
    except Exception as exc:
        print(f"evaluation failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print(f"Evaluation for {payload['skill_id']}: {payload['score']}/100")
        failed = [check for check in payload["checks"] if not check["ok"]]
        if not failed:
            print("Ready for publication")
        for check in failed:
            print(f"- {check['category']}: {check['message']}")
            if check["files"]:
                print(f"  Files: {', '.join(check['files'])}")
    return 0 if payload["ok"] else 1


def command_peer_search(args: argparse.Namespace) -> int:
    try:
        payload = peer_search(
            args.query,
            peer_id=args.peer,
            refresh=args.refresh,
            limit=args.limit,
            ttl_hours=args.ttl_hours,
        )
    except Exception as exc:
        print(f"peer search failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        if not payload["results"]:
            print("No matching peer skills found")
        for item in payload["results"]:
            catalog = item["source_catalog"]
            stale = " stale-cache" if item["source"].get("stale") else ""
            print(f"{item['id']}  score={item['score']}  source={catalog['id']}{stale}")
            print(f"  {item['description']}")
        for error in payload.get("errors", []):
            print(f"WARNING: peer {error['peer_id']}: {error['error']}", file=sys.stderr)
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
        if args.peer:
            if not args.yes:
                print("peer install requires --yes after reviewing the source catalog", file=sys.stderr)
                return 1
            payload = install_peer_skill(
                args.skill_id,
                peer_id=args.peer,
                scope=args.scope,
                project=args.project,
                force=args.force,
                refresh=args.refresh_peer,
            )
            if args.json:
                print_json(payload)
            else:
                print(f"Installed {args.skill_id} from {args.peer} to {payload['target']}")
            return 0
        target = install_skill(args.skill_id, scope=args.scope, project=args.project, force=args.force)
    except Exception as exc:
        print(f"install failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json({"installed": args.skill_id, "target": str(target), "scope": args.scope})
    else:
        print(f"Installed {args.skill_id} to {target}")
    return 0


def command_import_peer(args: argparse.Namespace) -> int:
    try:
        metadata = import_peer_skill(
            args.skill_id,
            peer_id=args.peer,
            owner=args.owner,
            force=args.force,
            refresh=args.refresh_peer,
        )
    except Exception as exc:
        print(f"import peer failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(metadata)
    else:
        print(f"Imported {metadata['id']} from {args.peer} to {metadata['catalog_path']}")
        if metadata.get("warnings"):
            for warning in metadata["warnings"]:
                print(f"WARNING: {warning}")
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


def command_peer_diagnostics(args: argparse.Namespace) -> int:
    payload = peer_diagnostics()
    if args.json:
        print_json(payload)
    else:
        print(f"Peer catalogs: {payload['peer_count']}  cache={payload['cache_root']}")
        if payload["duplicate_peer_ids"]:
            print(f"Duplicate peer IDs: {', '.join(payload['duplicate_peer_ids'])}")
        for peer in payload["peers"]:
            status = "ok" if peer["ok"] else "needs attention"
            stale = ""
            if peer["cache"]["stale"] is True:
                stale = " stale-cache"
            print(f"{peer['id']}  {status}{stale}  adapter={peer['adapter']}")
            if peer["problems"]:
                for problem in peer["problems"]:
                    print(f"  WARNING: {problem}")
    return 0 if payload["ok"] else 1


def command_cache_list(args: argparse.Namespace) -> int:
    payload = cache_listing()
    if args.json:
        print_json(payload)
    else:
        print(f"Cache root: {payload['cache_root']}")
        for peer in payload["peers"]:
            print(f"{peer['peer_id']}  repo_cached={peer['repo_cached']}  commits={len(peer['skill_cache_commits'])}")
        print(f"Search cache files: {len(payload['search_cache_files'])}")
    return 0


def command_cache_clear(args: argparse.Namespace) -> int:
    try:
        payload = clear_cache(peer_id=args.peer, yes=args.yes)
    except Exception as exc:
        print(f"cache clear failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print(f"Cleared {payload['cleared']}")
    return 0


def command_cache_refresh(args: argparse.Namespace) -> int:
    try:
        payload = refresh_cache(peer_id=args.peer)
    except Exception as exc:
        print(f"cache refresh failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print(f"Refreshed {payload['peer_id']} at {payload['commit']}")
        if payload.get("error"):
            print(f"WARNING: {payload['error']}", file=sys.stderr)
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

    search_audit = sub.add_parser("search-audit", help="Audit skill search and SEO discoverability")
    search_audit.add_argument("skill_id")
    search_audit.add_argument("--json", action="store_true")
    search_audit.set_defaults(func=command_search_audit)

    create = sub.add_parser("create", help="Create a new local skill from templates")
    create.add_argument("skill_id")
    create.add_argument("--title")
    create.add_argument("--description")
    create.add_argument("--owner")
    create.add_argument("--category", action="append", help="Add a category; may be repeated")
    create.add_argument("--tag", action="append", help="Add a tag; may be repeated")
    create.add_argument("--risk-level")
    create.add_argument("--force", action="store_true")
    create.add_argument("--json", action="store_true")
    create.set_defaults(func=command_create)

    evaluate = sub.add_parser("evaluate", help="Evaluate skill publication readiness")
    evaluate.add_argument("target", help="Skill ID, skill folder, or SKILL.md path")
    evaluate.add_argument("--json", action="store_true")
    evaluate.set_defaults(func=command_evaluate)

    peer_search_cmd = sub.add_parser("peer-search", help="Search cached or configured peer catalogs")
    peer_search_cmd.add_argument("query")
    peer_search_cmd.add_argument("--peer", help="Limit search to one peer catalog ID")
    peer_search_cmd.add_argument("--limit", type=int, default=10)
    peer_search_cmd.add_argument("--ttl-hours", type=int, default=24)
    peer_search_cmd.add_argument("--refresh", action="store_true", help="Refresh peer repo and search cache")
    peer_search_cmd.add_argument("--json", action="store_true")
    peer_search_cmd.set_defaults(func=command_peer_search)

    info = sub.add_parser("info", help="Show skill metadata")
    info.add_argument("skill_id")
    info.add_argument("--json", action="store_true")
    info.set_defaults(func=command_info)

    install = sub.add_parser("install", help="Install a skill into Codex")
    install.add_argument("skill_id")
    install.add_argument("--scope", choices=["global", "project"], default="global")
    install.add_argument("--project")
    install.add_argument("--force", action="store_true")
    install.add_argument("--peer", help="Install from a peer catalog ID instead of the local catalog")
    install.add_argument("--refresh-peer", action="store_true", help="Refresh peer cache before installing")
    install.add_argument("--yes", action="store_true", help="Confirm peer install after reviewing source catalog")
    install.add_argument("--json", action="store_true")
    install.set_defaults(func=command_install)

    import_peer = sub.add_parser("import-peer", help="Import a peer skill into the local SkillForge catalog")
    import_peer.add_argument("skill_id")
    import_peer.add_argument("--peer", required=True, help="Peer catalog ID")
    import_peer.add_argument("--owner", required=True)
    import_peer.add_argument("--force", action="store_true")
    import_peer.add_argument("--refresh-peer", action="store_true", help="Refresh peer cache before importing")
    import_peer.add_argument("--json", action="store_true")
    import_peer.set_defaults(func=command_import_peer)

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

    peer_diagnostics_cmd = sub.add_parser("peer-diagnostics", help="Report peer catalog configuration and cache health")
    peer_diagnostics_cmd.add_argument("--json", action="store_true")
    peer_diagnostics_cmd.set_defaults(func=command_peer_diagnostics)

    cache = sub.add_parser("cache", help="Manage SkillForge peer caches")
    cache_sub = cache.add_subparsers(dest="cache_command", required=True)

    cache_list = cache_sub.add_parser("list", help="List cached peer repos and search results")
    cache_list.add_argument("--json", action="store_true")
    cache_list.set_defaults(func=command_cache_list)

    cache_clear = cache_sub.add_parser("clear", help="Clear peer cache")
    cache_clear.add_argument("--peer", help="Limit clear to one peer catalog ID")
    cache_clear.add_argument("--yes", action="store_true", help="Confirm cache deletion")
    cache_clear.add_argument("--json", action="store_true")
    cache_clear.set_defaults(func=command_cache_clear)

    cache_refresh = cache_sub.add_parser("refresh", help="Refresh one peer repo cache")
    cache_refresh.add_argument("--peer", required=True, help="Peer catalog ID")
    cache_refresh.add_argument("--json", action="store_true")
    cache_refresh.set_defaults(func=command_cache_refresh)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
