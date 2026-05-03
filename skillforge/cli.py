from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from .catalog import (
    REPO_ROOT,
    as_list,
    as_text,
    build_catalog,
    evaluate_skill,
    load_skill_metadata,
    search_audit_skill,
    search_catalog,
    upload_skill,
)
from .create import create_skill
from .feedback import FeedbackDraft
from .help import getting_started_payload, help_payload, render_getting_started, render_help, render_welcome, welcome_payload
from .install import download_skill, install_skill, list_installed, remove_installed_skill, resolve_install_dir
from .output import add_chattiness_argument, chattiness_from_args, is_coach, is_normal_or_coach, is_silent
from .peer import (
    cache_listing,
    cache_peer_catalogs,
    clear_cache,
    corpus_search,
    import_peer_skill,
    install_peer_skill,
    peer_diagnostics,
    peer_search,
    refresh_cache,
)
from .update import DEFAULT_UPDATE_TTL_HOURS, update_check, update_skillforge, whats_new
from .validate import parse_frontmatter, validate_skill


def configure_output_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if not reconfigure:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            try:
                reconfigure(errors="replace")
            except Exception:
                pass


def print_json(data: object) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def table_text(value: object, *, max_chars: int = 96) -> str:
    text = "" if value is None else str(value)
    text = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    text = text.replace("|", "\\|")
    if len(text) > max_chars:
        return text[: max_chars - 1].rstrip() + "..."
    return text


def result_skill_text(item: dict) -> str:
    skill_text = item.get("skill_text")
    if isinstance(skill_text, str) and skill_text.strip():
        return skill_text

    source = item.get("source", {}) if isinstance(item.get("source"), dict) else {}
    candidates: list[Path] = []
    cache_path = source.get("cache_path")
    source_path = source.get("path") or item.get("catalog_path")

    if cache_path and source_path:
        cached = Path(str(cache_path)) / str(source_path)
        candidates.append(cached if cached.name == "SKILL.md" else cached / "SKILL.md")

    for value in (source_path, item.get("catalog_path")):
        if not value:
            continue
        path = Path(str(value))
        if not path.is_absolute():
            path = REPO_ROOT / path
        candidates.append(path if path.name == "SKILL.md" else path / "SKILL.md")

    seen: set[Path] = set()
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.exists() and resolved.is_file():
            try:
                return resolved.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
    return ""


def markdown_body(skill_text: str) -> str:
    lines = skill_text.splitlines()
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return "\n".join(lines[index + 1 :])
    return skill_text


def clean_skill_comment_line(line: str) -> str:
    text = line.strip()
    text = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = text.replace("`", "")
    return " ".join(text.split())


def summarize_skill_comment_block(block: str, *, max_items: int = 2) -> str:
    comments: list[str] = []
    in_code = False
    for raw_line in block.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped or stripped.startswith("#"):
            continue
        if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", raw_line):
            comments.append(clean_skill_comment_line(raw_line))
        elif not comments:
            comments.append(clean_skill_comment_line(raw_line))
        if len(comments) >= max_items:
            break
    return " ".join(comment for comment in comments if comment)


def markdown_section(skill_text: str, section_names: list[str]) -> str:
    body = markdown_body(skill_text)
    wanted = {name.lower() for name in section_names}
    lines = body.splitlines()
    capture = False
    captured: list[str] = []
    heading_level = 0
    for line in lines:
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            normalized = re.sub(r"[^a-z0-9 ]+", " ", match.group(2).lower())
            normalized = " ".join(normalized.split())
            current_level = len(match.group(1))
            if capture and current_level <= heading_level:
                break
            if not capture and any(name in normalized for name in wanted):
                capture = True
                heading_level = current_level
                continue
        if capture:
            captured.append(line)
    return "\n".join(captured)


def first_markdown_paragraph(skill_text: str) -> str:
    body = markdown_body(skill_text)
    lines = body.splitlines()
    paragraph: list[str] = []
    in_code = False
    seen_h1 = False
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith("# "):
            seen_h1 = True
            paragraph = []
            continue
        if stripped.startswith("#"):
            if paragraph:
                break
            continue
        if not stripped:
            if paragraph:
                break
            continue
        if seen_h1:
            paragraph.append(clean_skill_comment_line(stripped))
    return " ".join(paragraph)


def frontmatter_skill_comments(skill_text: str) -> str:
    metadata, _errors = parse_frontmatter(skill_text)
    for field_name in ["comments", "comment", "notes", "usage_notes", "limitations", "do_not_use_when", "requirements"]:
        value = metadata.get(field_name)
        if not value:
            continue
        if isinstance(value, list):
            return " ".join(as_list(value)[:2])
        return as_text(value)
    return ""


def skill_md_comments(item: dict) -> str:
    skill_text = result_skill_text(item)
    if not skill_text.strip():
        return ""

    explicit = frontmatter_skill_comments(skill_text)
    if explicit:
        return explicit

    section_groups = [
        ["important rules", "entry quality rules", "rules", "guardrails"],
        ["before you start", "getting started", "setup", "configuration"],
        ["requirements", "prerequisites"],
        ["limitations", "known limitations"],
        ["trust and safety", "safety", "privacy"],
        ["do not use", "when not to use"],
    ]
    for section_names in section_groups:
        comment = summarize_skill_comment_block(markdown_section(skill_text, section_names))
        if comment:
            return comment
    return first_markdown_paragraph(skill_text)


def search_result_source_comments(item: dict) -> str:
    return skill_md_comments(item)


def search_result_source_url(item: dict) -> str:
    source_catalog = item.get("source_catalog", {}) if isinstance(item.get("source_catalog"), dict) else {}
    source = item.get("source", {}) if isinstance(item.get("source"), dict) else {}
    for value in (
        source.get("url"),
        item.get("url"),
        source_catalog.get("source_url"),
        source_catalog.get("catalog_url"),
    ):
        text = "" if value is None else str(value).strip()
        if text:
            return text
    return ""


def search_result_install_command(item: dict) -> str:
    command = item.get("install_command")
    if command:
        return str(command)
    source = item.get("source", {}) if isinstance(item.get("source"), dict) else {}
    skill_id = item.get("id")
    if skill_id and source.get("type") == "peer-catalog" and source.get("peer_id"):
        return f"python -m skillforge install {skill_id} --peer {source['peer_id']} --scope global --yes"
    codex = item.get("codex", {}) if isinstance(item.get("codex"), dict) else {}
    return str(codex.get("global_install_command") or "")


def print_search_table(results: list[dict]) -> None:
    print("| Rank | Skill Name | Helps With | Comments | Install Command | Source URL |")
    print("| ---: | --- | --- | --- | --- | --- |")
    for index, item in enumerate(results, start=1):
        print(
            "| "
            + " | ".join(
                [
                    str(index),
                    f"`{table_text(item.get('id'), max_chars=42)}`",
                    table_text(item.get("summary") or item.get("short_description") or item.get("description"), max_chars=120),
                    table_text(search_result_source_comments(item), max_chars=120),
                    table_text(search_result_install_command(item), max_chars=1000),
                    table_text(search_result_source_url(item), max_chars=1000),
                ]
            )
            + " |"
        )


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
    chattiness = chattiness_from_args(args)
    results = search_catalog(args.query, limit=args.limit)
    if args.json:
        print_json({"query": args.query, "results": results})
    else:
        if not results:
            if not is_silent(chattiness):
                print("No matching skills found")
                if is_coach(chattiness):
                    print("Try `python -m skillforge corpus-search \"your task\"` to include cached peer catalogs.")
            return 1
        print_search_table(results)
        if is_coach(chattiness):
            print()
            print("Next steps:")
            print(f"  python -m skillforge info {results[0]['id']} --json")
            print(f"  python -m skillforge install {results[0]['id']} --scope global")
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
            jobs=args.jobs,
        )
    except Exception as exc:
        print(f"peer search failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        if not payload["results"]:
            print("No matching peer skills found")
        else:
            print_search_table(payload["results"])
        for error in payload.get("errors", []):
            kind = error.get("kind", "peer_error")
            print(f"WARNING: peer {error['peer_id']} ({kind}): {error['error']}", file=sys.stderr)
    return 0


def command_corpus_search(args: argparse.Namespace) -> int:
    chattiness = chattiness_from_args(args)
    try:
        payload = corpus_search(
            args.query,
            peer_id=args.peer,
            refresh=args.refresh,
            limit=args.limit,
            ttl_hours=args.ttl_hours,
            jobs=args.jobs,
            enabled_only=args.enabled_only,
        )
    except Exception as exc:
        print(f"corpus search failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        if not payload["results"]:
            if not is_silent(chattiness):
                print("No matching cached provider skills found")
                if is_coach(chattiness):
                    print("Try `python -m skillforge peer-search \"your task\" --refresh --json` for live peer search.")
        else:
            print_search_table(payload["results"])
            if is_normal_or_coach(chattiness):
                print()
                print(
                    f"Results: {payload['result_count']}  "
                    f"Providers: {payload['cache']['provider_count']}  "
                    f"Cache TTL: {payload['cache']['ttl_hours']}h"
                )
            if is_coach(chattiness):
                best = payload["results"][0]
                print("Next steps:")
                print(f"  Review source: {search_result_source_url(best) or '(source URL unavailable)'}")
                install_command = search_result_install_command(best)
                if install_command:
                    print(f"  Install after review: {install_command}")
        for error in payload.get("errors", []):
            if error.get("kind") == "parser_skipped":
                continue
            kind = error.get("kind", "peer_error")
            print(f"WARNING: peer {error['peer_id']} ({kind}): {error['error']}", file=sys.stderr)
    return 0


def command_help(args: argparse.Namespace) -> int:
    payload = help_payload(args.topic)
    if args.json:
        print_json(payload)
    else:
        print(render_help(payload, chattiness=chattiness_from_args(args)))
    return 0


def command_welcome(args: argparse.Namespace) -> int:
    payload = welcome_payload()
    if args.json:
        print_json(payload)
    else:
        print(render_welcome(payload, chattiness=chattiness_from_args(args)))
    return 0


def command_getting_started(args: argparse.Namespace) -> int:
    payload = getting_started_payload()
    if args.json:
        print_json(payload)
    else:
        print(render_getting_started(payload, chattiness=chattiness_from_args(args)))
    return 0


def command_update_check(args: argparse.Namespace) -> int:
    try:
        payload = update_check(refresh=args.refresh, no_fetch=args.no_fetch, ttl_hours=args.ttl_hours)
    except Exception as exc:
        print(f"update check failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        if payload.get("updates_available"):
            print(f"SkillForge updates available: behind by {payload['behind_by']} commits")
            print(f"Local:    {payload['local_commit']}")
            print(f"Upstream: {payload['upstream_commit']}")
            print(f"Next:     {payload['next_command']}")
        else:
            print("SkillForge is up to date with the known upstream ref")
            if payload.get("cache", {}).get("used"):
                print("Used cached update status")
        if payload.get("dirty"):
            print("WARNING: local checkout has uncommitted changes", file=sys.stderr)
        fetch = payload.get("fetch", {})
        if fetch.get("attempted") and fetch.get("ok") is False:
            print(f"WARNING: fetch failed: {fetch.get('error')}", file=sys.stderr)
    return 0 if payload.get("ok") else 1


def command_update(args: argparse.Namespace) -> int:
    try:
        payload = update_skillforge(yes=args.yes, no_fetch=args.no_fetch, ttl_hours=args.ttl_hours)
    except Exception as exc:
        print(f"update failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        if payload.get("updated"):
            print("SkillForge updated")
            print(f"Previous: {payload['previous_commit']}")
            print(f"Current:  {payload['current_commit']}")
            print()
            print("What's new:")
            for line in (payload.get("whats_new") or {}).get("summary", []):
                print(f"- {line}")
        elif payload.get("requires_confirmation"):
            check = payload.get("check", {})
            print(f"SkillForge updates are available: behind by {check.get('behind_by', 0)} commits")
            print(f"Local:    {check.get('local_commit', '')}")
            print(f"Upstream: {check.get('upstream_commit', '')}")
            print("No files were changed.")
            print(f"Preview:  python -m skillforge whats-new --since {check.get('local_commit', '')}")
            print(f"Apply:    {payload['next_command']}")
        elif payload.get("refused"):
            print(f"SkillForge update was not applied: {payload.get('reason', 'unknown reason')}", file=sys.stderr)
        else:
            print(payload.get("reason", "SkillForge update did not change files."))
        merge = payload.get("merge", {})
        if merge.get("attempted") and merge.get("ok") is False:
            print(f"WARNING: fast-forward failed: {merge.get('error')}", file=sys.stderr)
    return 0 if payload.get("ok") else 1


def command_whats_new(args: argparse.Namespace) -> int:
    try:
        payload = whats_new(since=args.since, until=args.until, limit=args.limit)
    except Exception as exc:
        print(f"whats-new failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print("What's new in SkillForge")
        if payload.get("revision_range"):
            print(f"Range: {payload['revision_range']}")
        for line in payload["summary"]:
            print(f"- {line}")
        if payload["commits"]:
            print()
            print("Commits:")
            for commit in payload["commits"][: args.limit]:
                print(f"- {commit['commit'][:12]} {commit['summary']}")
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
            print(
                f"{peer['peer_id']}  repo_cached={peer['repo_cached']}  "
                f"catalog_cached={peer.get('catalog_cached', False)}  commits={len(peer['skill_cache_commits'])}"
            )
        print(f"Search cache files: {len(payload['search_cache_files'])}")
        print(f"Provider catalog files: {len(payload.get('provider_catalog_files', []))}")
    return 0


def command_cache_catalogs(args: argparse.Namespace) -> int:
    try:
        payload = cache_peer_catalogs(
            peer_id=args.peer,
            refresh=args.refresh,
            ttl_hours=args.ttl_hours,
            jobs=args.jobs,
            enabled_only=args.enabled_only,
        )
    except Exception as exc:
        print(f"cache catalogs failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print(
            f"Cached provider catalogs: {payload['provider_count']}  "
            f"cache={payload['cache']['root']}  ttl_hours={payload['cache']['ttl_hours']}"
        )
        for provider in payload["providers"]:
            stale = " stale" if provider.get("stale") else ""
            print(
                f"{provider['peer_id']}  {provider['status']}{stale}  "
                f"skills={provider['skill_count']}  path={provider['cache_path']}"
            )
            if provider["error_count"]:
                print(f"  WARNING: errors={provider['error_count']}")
    return 0 if payload["ok"] else 1


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

    help_cmd = sub.add_parser("help", help="Show SkillForge workflow help")
    help_cmd.add_argument("topic", nargs="?", help="Workflow topic or natural-language help request")
    help_cmd.add_argument("--json", action="store_true")
    add_chattiness_argument(help_cmd)
    help_cmd.set_defaults(func=command_help)

    welcome = sub.add_parser("welcome", help="Show a novice-friendly SkillForge welcome")
    welcome.add_argument("--json", action="store_true")
    add_chattiness_argument(welcome)
    welcome.set_defaults(func=command_welcome)

    getting_started = sub.add_parser("getting-started", help="Show first-run SkillForge guidance")
    getting_started.add_argument("--json", action="store_true")
    add_chattiness_argument(getting_started)
    getting_started.set_defaults(func=command_getting_started)

    search = sub.add_parser("search", help="Search local catalog")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--json", action="store_true")
    add_chattiness_argument(search)
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
    peer_search_cmd.add_argument("--jobs", type=int, help="Maximum concurrent peer searches, capped at 15")
    peer_search_cmd.add_argument("--refresh", action="store_true", help="Refresh peer repo and search cache")
    peer_search_cmd.add_argument("--json", action="store_true")
    peer_search_cmd.set_defaults(func=command_peer_search)

    corpus_search_cmd = sub.add_parser("corpus-search", help="Search cached full provider catalogs")
    corpus_search_cmd.add_argument("query")
    corpus_search_cmd.add_argument("--peer", help="Limit search to one peer catalog ID")
    corpus_search_cmd.add_argument("--limit", type=int, default=10)
    corpus_search_cmd.add_argument("--ttl-hours", type=int, default=24)
    corpus_search_cmd.add_argument("--jobs", type=int, help="Maximum concurrent provider catalog reads/fetches, capped at 15")
    corpus_search_cmd.add_argument("--refresh", action="store_true", help="Refresh provider catalog caches before searching")
    corpus_search_cmd.add_argument("--enabled-only", action="store_true", help="Only search default-enabled peer catalogs")
    corpus_search_cmd.add_argument("--json", action="store_true")
    add_chattiness_argument(corpus_search_cmd)
    corpus_search_cmd.set_defaults(func=command_corpus_search)

    update_check_cmd = sub.add_parser("update-check", help="Check whether the local SkillForge checkout is behind upstream")
    update_check_cmd.add_argument("--refresh", action="store_true", help="Force a fresh Git fetch before comparing")
    update_check_cmd.add_argument("--no-fetch", action="store_true", help="Use local remote-tracking refs only")
    update_check_cmd.add_argument(
        "--ttl-hours",
        type=int,
        default=DEFAULT_UPDATE_TTL_HOURS,
        help="Cached update-check freshness window in hours",
    )
    update_check_cmd.add_argument("--json", action="store_true")
    update_check_cmd.set_defaults(func=command_update_check)

    update_cmd = sub.add_parser("update", help="Fast-forward the local SkillForge checkout after review")
    update_cmd.add_argument("--yes", action="store_true", help="Apply the fast-forward update when it is safe")
    update_cmd.add_argument("--no-fetch", action="store_true", help="Use local remote-tracking refs only")
    update_cmd.add_argument(
        "--ttl-hours",
        type=int,
        default=DEFAULT_UPDATE_TTL_HOURS,
        help="Cached update-check freshness window in hours",
    )
    update_cmd.add_argument("--json", action="store_true")
    update_cmd.set_defaults(func=command_update)

    whats_new_cmd = sub.add_parser("whats-new", help="Summarize SkillForge Git changes since a previous revision")
    whats_new_cmd.add_argument("--since", help="Start commit/ref. Defaults to cached previous local revision or recent history.")
    whats_new_cmd.add_argument("--until", default="HEAD", help="End commit/ref. Defaults to HEAD.")
    whats_new_cmd.add_argument("--limit", type=int, default=20, help="Maximum commits to display")
    whats_new_cmd.add_argument("--json", action="store_true")
    whats_new_cmd.set_defaults(func=command_whats_new)

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

    cache_catalogs = cache_sub.add_parser("catalogs", help="Cache full provider catalogs for semantic search")
    cache_catalogs.add_argument("--peer", help="Limit to one peer catalog ID")
    cache_catalogs.add_argument("--refresh", action="store_true", help="Refresh even when the provider catalog cache is fresh")
    cache_catalogs.add_argument("--ttl-hours", type=int, default=24, help="Provider catalog cache expiration in hours")
    cache_catalogs.add_argument("--jobs", type=int, help="Maximum concurrent provider catalog fetches, capped at 15")
    cache_catalogs.add_argument("--enabled-only", action="store_true", help="Only cache default-enabled peers")
    cache_catalogs.add_argument("--json", action="store_true")
    cache_catalogs.set_defaults(func=command_cache_catalogs)

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
    configure_output_streams()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
