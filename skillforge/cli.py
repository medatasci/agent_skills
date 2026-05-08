from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

from .catalog import (
    REPO_ROOT,
    as_list,
    as_text,
    build_catalog,
    display_path,
    evaluate_skill,
    load_skill_metadata,
    search_audit_skill,
    search_catalog,
    upload_skill,
)
from .clinical_statistical_expert import (
    disease_homepage,
    disease_preview,
    disease_template_check,
    download_reusable_assets,
    evidence_query_pack,
)
from .create import create_skill
from .contribute import ContributionDraft
from .feedback import FeedbackDraft
from .figure_evidence import record_figure_evidence
from .help import getting_started_payload, help_payload, render_getting_started, render_help, render_welcome, welcome_payload
from .improvement_loop import improvement_cycle, render_improvement_cycle
from .install import (
    download_skill,
    install_skill,
    install_skillforge_marketplace,
    list_installed,
    remove_installed_skill,
    resolve_install_dir,
)
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
from .source_archive import record_source_archive
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
        advisory_failed = [check for check in payload.get("advisory_checks", []) if not check["ok"]]
        if advisory_failed:
            print("Advisory warnings:")
            for check in advisory_failed:
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


def load_codebase_to_agentic_skills_module():
    script_path = REPO_ROOT / "skills" / "codebase-to-agentic-skills" / "scripts" / "codebase_to_agentic_skills.py"
    if not script_path.exists():
        raise FileNotFoundError(f"codebase-to-agentic-skills helper was not found: {display_path(script_path)}")

    spec = importlib.util.spec_from_file_location("skillforge_codebase_to_agentic_skills", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load helper module: {display_path(script_path)}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def command_codebase_scan(args: argparse.Namespace) -> int:
    try:
        module = load_codebase_to_agentic_skills_module()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    scan_args = [
        "scan",
        args.repo_path,
        "--workflow-goal",
        args.workflow_goal or "",
        "--max-files-per-category",
        str(args.max_files_per_category),
        "--max-total-files",
        str(args.max_total_files),
    ]
    if args.output_dir:
        scan_args.extend(["--output-dir", args.output_dir])
    if args.json:
        scan_args.append("--json")
    return module.main(scan_args)


def command_codebase_scaffold_adapter(args: argparse.Namespace) -> int:
    try:
        module = load_codebase_to_agentic_skills_module()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    scaffold_args = ["scaffold-adapter"]
    if args.adapter_type:
        scaffold_args.append(args.adapter_type)
    if args.adapter_name:
        scaffold_args.extend(["--adapter-name", args.adapter_name])
    if args.from_scan_json:
        scaffold_args.extend(["--from-scan-json", args.from_scan_json])
    if args.candidate_id:
        scaffold_args.extend(["--candidate-id", args.candidate_id])
    if args.candidate_index is not None:
        scaffold_args.extend(["--candidate-index", str(args.candidate_index)])
    if args.stub_type:
        scaffold_args.extend(["--stub-type", args.stub_type])
    if args.stub_index is not None:
        scaffold_args.extend(["--stub-index", str(args.stub_index)])
    scaffold_args.extend(["--output-dir", args.output_dir])
    if args.force:
        scaffold_args.append("--force")
    if args.json:
        scaffold_args.append("--json")
    return module.main(scaffold_args)


def command_improve_cycle(args: argparse.Namespace) -> int:
    try:
        payload = improvement_cycle(
            focus=args.focus,
            lane=args.lane,
            log_dir=args.log_dir,
            write_log=args.write_log,
            claim_run=args.claim_run,
            release_run_id=args.release_run,
            stale_minutes=args.stale_minutes,
            lock_path=args.lock_path,
        )
    except Exception as exc:
        print(f"improve-cycle failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print(render_improvement_cycle(payload))
    return 0 if payload.get("ok") else 1


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
        print()
        print("User-facing changes:")
        for line in payload["summary"]:
            print(f"- {line}")
        if not (args.details or args.technical or args.commits):
            print()
            print(payload["detail_prompt"])
        if args.details or args.technical:
            print()
            print("Technical summary:")
            for line in payload["technical_summary"]:
                print(f"- {line}")
        if (args.details or args.technical or args.commits) and payload["commits"]:
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


def command_figure_evidence(args: argparse.Namespace) -> int:
    try:
        payload = record_figure_evidence(
            disease=args.disease,
            figure_id=args.figure_id,
            source_title=args.source_title,
            source_url=args.source_url,
            figure_label=args.figure_label,
            figure_url=args.figure_url,
            license_text=args.license,
            reuse_status=args.reuse_status,
            clinical_point=args.clinical_point,
            supports_sections=args.section or [],
            image_path=args.image_path,
            manifest_path=args.manifest,
            assets_dir=args.assets_dir,
            attribution=args.attribution,
            notes=args.notes,
            date_accessed=args.date_accessed,
        )
    except Exception as exc:
        print(f"figure evidence failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print(f"Recorded figure evidence: {payload['entry']['id']}")
        print(f"Manifest: {payload['manifest_path']}")
        if payload.get("asset_path"):
            print(f"Local image: {payload['asset_path']}")
        else:
            print("Local image: not stored")
        for warning in payload.get("warnings", []):
            print(f"WARNING: {warning}", file=sys.stderr)
        print()
        print("Markdown snippet:")
        print(payload["markdown_snippet"])
    return 0 if payload.get("ok") else 1


def command_source_archive(args: argparse.Namespace) -> int:
    try:
        payload = record_source_archive(
            disease=args.disease,
            source_id=args.source_id,
            title=args.title,
            url=args.url,
            source_type=args.source_type,
            claim_breadth=args.claim_breadth,
            license_text=args.license,
            reuse_status=args.reuse_status,
            supported_sections=args.section or [],
            manifest_path=args.manifest,
            cache_root=args.cache_root,
            cache_status=args.cache_status,
            download=args.download,
            notes=args.notes,
            date_accessed=args.date_accessed,
        )
    except Exception as exc:
        print(f"source archive failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        entry = payload["entry"]
        print(f"Recorded source: {entry['id']}")
        print(f"Manifest: {payload['manifest_path']}")
        print(f"Cache status: {entry['cache_status']}")
        if entry.get("local_cache_path"):
            print(f"Local cache: {entry['local_cache_path']}")
        for warning in payload.get("warnings", []):
            print(f"WARNING: {warning}", file=sys.stderr)
    return 0 if payload.get("ok") else 1


def command_disease_preview(args: argparse.Namespace) -> int:
    try:
        payload = disease_preview(
            args.disease,
            disease_dir=args.disease_dir,
            output=args.output,
        )
    except Exception as exc:
        print(f"disease preview failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print(f"Generated disease preview: {payload['output_path']}")
        print(f"Disease chapter: {payload['markdown_path']}")
        print(f"Sources recorded: {payload['sources_total']}")
        print(f"Image candidates recorded: {payload['figures_total']}")
        print(f"Local embeddable figures: {payload['local_figures']}")
    return 0 if payload.get("ok") else 1


def command_disease_homepage(args: argparse.Namespace) -> int:
    try:
        payload = disease_homepage(
            project_root=args.project_root,
            output=args.output,
            assets_output=args.assets_output,
            template_dir=args.template_dir,
            link_disease_pages=not args.no_link_disease_pages,
        )
    except Exception as exc:
        print(f"disease homepage failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print(f"Generated disease project homepage: {payload['output_path']}")
        print(f"Generated downloaded assets page: {payload['assets_output_path']}")
        print(f"Disease categories: {payload['disease_count']}")
        print(f"Evidence-count target met: {payload['completed_count']}")
        print(f"Downloaded asset files: {payload['downloaded_asset_count']}")
        print(f"Linked disease pages: {payload['linked_disease_pages']}")
        gaps = payload.get("download_asset_gaps") or []
        if gaps:
            print("Completed diseases without downloaded local assets:")
            for gap in gaps:
                print(
                    f"- {gap['slug']}: {gap['figures_total']} figure records, "
                    f"{gap['link_only_figures']} link-only, "
                    f"{gap['explicit_reusable_candidates']} explicit reusable candidates"
                )
    return 0 if payload.get("ok") else 1


def command_download_reusable_assets(args: argparse.Namespace) -> int:
    try:
        payload = download_reusable_assets(
            project_root=args.project_root,
            disease=args.disease,
            dry_run=args.dry_run,
            force=args.force,
            refresh_homepage=not args.no_refresh_homepage,
            template_dir=args.template_dir,
        )
    except Exception as exc:
        print(f"download reusable assets failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        totals = payload["totals"]
        print(f"Reviewed diseases: {totals['diseases_reviewed']}")
        print(f"Reviewed figure records: {totals['figures_reviewed']}")
        print(f"Eligible reusable records: {totals['eligible']}")
        print(f"Downloaded files: {totals['downloaded']}")
        print(f"Already local files: {totals['already_local']}")
        print(f"Skipped records: {totals['skipped']}")
        print(f"Failed records: {totals['failed']}")
        if payload.get("report_path"):
            print(f"Review report: {payload['report_path']}")
        homepage = payload.get("homepage") or {}
        if homepage:
            print(f"Asset gallery: {homepage.get('assets_output_path', '')}")
    return 0 if payload.get("ok") else 1


def command_disease_template_check(args: argparse.Namespace) -> int:
    try:
        payload = disease_template_check(
            args.disease,
            disease_dir=args.disease_dir,
            template_dir=args.template_dir,
            strict=args.strict,
        )
    except Exception as exc:
        print(f"disease template check failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print(f"Checked {payload['checked']} disease chapter(s)")
        print(f"Disease directory: {payload['disease_dir']}")
        print(f"Template directory: {payload['template_dir']}")
        for result in payload["results"]:
            status = "ok" if result["ok"] else "needs attention"
            print(f"- {result['disease']}: {status}")
            failed = [check for check in result["checks"] if not check["ok"]]
            for check in failed:
                label = "required" if check["required"] else "advisory"
                print(f"  - {check['category']} ({label}): {check['message']}")
        if payload.get("template_missing_files"):
            print(f"Missing packaged templates: {', '.join(payload['template_missing_files'])}")
    return 0 if payload.get("ok") else 1


def command_evidence_query_pack(args: argparse.Namespace) -> int:
    try:
        payload = evidence_query_pack(
            args.target_concept,
            lens=args.lens,
            expert_role=args.expert_role,
            modality=args.modality,
            evidence_type=args.evidence_type,
        )
    except Exception as exc:
        print(f"evidence query pack failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        print(f"Evidence query pack: {payload['target_concept']}")
        print(f"Lens: {payload['lens']}")
        print(f"Expert role: {payload['expert_role']}")
        if payload.get("modality"):
            print(f"Modality: {payload['modality']}")
        print()
        print("Basic prompt:")
        print(payload["basic_prompt"])
        print()
        print("Advanced prompt:")
        print(payload["advanced_prompt"])
        print()
        print("Search variants:")
        for variant in payload["search_variants"]:
            print(f"- {variant}")
        print()
        print("Capture notes:")
        for note in payload["capture_notes"]:
            print(f"- {note}")
        print()
        print(f"Template: {payload['template_reference']}")
    return 0 if payload.get("ok") else 1


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


def command_install_skillforge(args: argparse.Namespace) -> int:
    try:
        payload = install_skillforge_marketplace(
            codex_home=args.codex_home,
            marketplace_path=args.marketplace_path,
            yes=args.yes,
        )
    except Exception as exc:
        print(f"install-skillforge failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print_json(payload)
    else:
        status = payload["status"]
        if status == "healthy":
            print("SkillForge is already installed and usable.")
        elif status == "repaired":
            print("SkillForge install was repaired.")
        elif status == "repair_available":
            print("SkillForge files were found, but Codex config is missing safe entries.")
            print("No files were changed.")
        elif status == "missing":
            print("SkillForge marketplace checkout was not found.")
        elif status == "conflict":
            print("SkillForge install target needs attention before install can continue.")
        else:
            print("SkillForge install needs manual attention.")
        print(f"Codex home:      {payload['codex_home']}")
        print(f"Marketplace:     {payload['marketplace']['path']}")
        print(f"Config:          {payload['config']['path']}")
        version = payload.get("version", {})
        print(f"Source repo:     {version.get('source_repo') or payload['marketplace'].get('expected_source', '')}")
        print(f"Configured ref:  {version.get('configured_ref') or payload['marketplace'].get('expected_ref', '')}")
        if version.get("plugin_version"):
            print(f"Plugin version:  {version['plugin_version']}")
        if version.get("code_version"):
            print(f"Code version:    {version['code_version']}")
        if version.get("last_updated"):
            print(f"Last updated:    {version['last_updated']} ({version.get('last_updated_source', 'unknown source')})")
        git = payload["marketplace"]["git"]
        if git.get("commit"):
            print(f"Branch/commit:   {git.get('branch') or 'HEAD'} {git['commit'][:12]}")
        print(f"Plugin enabled:  {payload['config']['plugin_enabled']}")
        print(f"Repo verified:   {payload['marketplace']['is_skillforge']}")
        for warning in payload.get("warnings", []):
            print(f"WARNING: {warning}", file=sys.stderr)
        if payload["next_commands"]:
            print("Next commands:")
            for command in payload["next_commands"]:
                print(f"  {command}")
    return 0 if payload.get("ok") else 1


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


def command_contribute(args: argparse.Namespace) -> int:
    draft = ContributionDraft(
        summary=args.summary,
        change_type=args.change_type,
        why=args.why,
        changed_files=args.changed or [],
        checks=args.check or [],
        safety_notes=args.safety_note,
        user_type=args.user_type,
        title=args.title,
        branch=args.branch,
        base=args.base,
    )
    payload = draft.as_dict()
    if args.json:
        print_json(payload)
    else:
        print("Pull request draft:")
        print(f"  Title: {payload['title']}")
        print(f"  Branch: {payload['branch']}")
        print(f"  Base: {payload['base']}")
        print(f"  Contributor profile: {payload['contributor_profile']}")
        print(f"  Manual PR URL: {payload['manual_pr_url']}")
        print()
        print("Promptable request:")
        print(payload["promptable_request"])
        print()
        print("Recommended commands:")
        for command in payload["commands"]:
            print(command)
        print()
        print("PR body:")
        print(payload["body"])
        print()
        print("Side effects:")
        print(payload["side_effects"])
        print()
        print("Next steps:")
        for step in payload["next_steps"]:
            print(f"- {step}")
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

    codebase_scan = sub.add_parser("codebase-scan", help="Scan a local repo for codebase-to-agentic-skills source evidence")
    codebase_scan.add_argument("repo_path")
    codebase_scan.add_argument("--workflow-goal", default="")
    codebase_scan.add_argument("--output-dir")
    codebase_scan.add_argument("--max-files-per-category", type=int, default=25)
    codebase_scan.add_argument("--max-total-files", type=int, default=5000)
    codebase_scan.add_argument("--json", action="store_true")
    codebase_scan.set_defaults(func=command_codebase_scan)

    codebase_scaffold = sub.add_parser(
        "codebase-scaffold-adapter",
        help="Write a review-only adapter scaffold for codebase-to-agentic-skills work",
    )
    codebase_scaffold.add_argument(
        "adapter_type",
        nargs="?",
        choices=["guarded-run", "no-adapter-until-review", "read-only-check", "runtime-plan", "setup-plan"],
    )
    codebase_scaffold.add_argument("--adapter-name")
    codebase_scaffold.add_argument("--from-scan-json")
    codebase_scaffold.add_argument("--candidate-id")
    codebase_scaffold.add_argument("--candidate-index", type=int, default=0)
    codebase_scaffold.add_argument(
        "--stub-type",
        choices=["guarded-run", "no-adapter-until-review", "read-only-check", "runtime-plan", "setup-plan"],
    )
    codebase_scaffold.add_argument("--stub-index", type=int, default=0)
    codebase_scaffold.add_argument("--output-dir", required=True)
    codebase_scaffold.add_argument("--force", action="store_true")
    codebase_scaffold.add_argument("--json", action="store_true")
    codebase_scaffold.set_defaults(func=command_codebase_scaffold_adapter)

    improve_cycle = sub.add_parser(
        "improve-cycle",
        help="Plan and log one strategic SkillForge improvement-loop run",
    )
    improve_cycle.add_argument("--focus", help="Override the selected improvement focus")
    improve_cycle.add_argument(
        "--lane",
        choices=["researcher", "planner", "builder", "hardener", "safety", "brainstormer"],
        help="Select a strategic lane for this run",
    )
    improve_cycle.add_argument("--log-dir", help="Improvement-loop docs directory. Defaults to docs/improvement-loop.")
    improve_cycle.add_argument("--write-log", action="store_true", help="Write a unique Markdown run log stub")
    improve_cycle.add_argument("--claim-run", action="store_true", help="Claim an advisory active-run lock for concurrent jobs")
    improve_cycle.add_argument("--release-run", help="Release a previously claimed active-run lock by run ID")
    improve_cycle.add_argument("--lock-path", help="Override advisory lock path for isolated tests or advanced automation")
    improve_cycle.add_argument(
        "--stale-minutes",
        type=int,
        default=90,
        help="Minutes before an active-run lock is treated as stale",
    )
    improve_cycle.add_argument("--json", action="store_true")
    improve_cycle.set_defaults(func=command_improve_cycle)

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
    whats_new_cmd.add_argument("--details", action="store_true", help="Include technical summary and commits")
    whats_new_cmd.add_argument("--technical", action="store_true", help="Alias for --details")
    whats_new_cmd.add_argument("--commits", action="store_true", help="Include commit list")
    whats_new_cmd.add_argument("--json", action="store_true")
    whats_new_cmd.set_defaults(func=command_whats_new)

    info = sub.add_parser("info", help="Show skill metadata")
    info.add_argument("skill_id")
    info.add_argument("--json", action="store_true")
    info.set_defaults(func=command_info)

    figure_evidence = sub.add_parser(
        "figure-evidence",
        help="Record disease-chapter figure evidence and copy only reusable images",
    )
    figure_evidence.add_argument("disease")
    figure_evidence.add_argument("--figure-id", required=True)
    figure_evidence.add_argument("--source-title", required=True)
    figure_evidence.add_argument("--source-url", required=True)
    figure_evidence.add_argument("--figure-label", required=True, help="Figure number, label, or source-local reference")
    figure_evidence.add_argument("--figure-url", help="Direct figure URL when different from the source URL")
    figure_evidence.add_argument("--license", required=True, help="License or reuse note")
    figure_evidence.add_argument(
        "--reuse-status",
        required=True,
        choices=["ok-to-embed", "link-only", "needs-review", "private-review"],
        help="Whether SkillForge may store the image locally",
    )
    figure_evidence.add_argument("--clinical-point", required=True)
    figure_evidence.add_argument("--section", action="append", help="Disease.md section supported by the figure")
    figure_evidence.add_argument("--image-path", help="Local image file to copy only when reuse-status is ok-to-embed")
    figure_evidence.add_argument("--manifest", help="Figure manifest path. Defaults to docs/clinical-statistical-expert/diseases/<disease>.figures.json")
    figure_evidence.add_argument("--assets-dir", help="Directory for reusable local figure assets")
    figure_evidence.add_argument("--attribution", help="Attribution text required by the source license")
    figure_evidence.add_argument("--notes", help="Reuse, source, or clinical notes")
    figure_evidence.add_argument("--date-accessed", help="Date accessed, YYYY-MM-DD. Defaults to today's UTC date")
    figure_evidence.add_argument("--json", action="store_true")
    figure_evidence.set_defaults(func=command_figure_evidence)

    source_archive = sub.add_parser(
        "source-archive",
        help="Record disease-chapter source metadata and optionally cache the source locally",
    )
    source_archive.add_argument("disease")
    source_archive.add_argument("--source-id", required=True)
    source_archive.add_argument("--title", required=True)
    source_archive.add_argument("--url", required=True)
    source_archive.add_argument("--source-type", required=True, help="Textbook, guideline, teaching resource, review, article, etc.")
    source_archive.add_argument("--claim-breadth", required=True, help="Broad, narrow, or a short claim-scope description")
    source_archive.add_argument("--license", default="", help="Source license or reuse statement when known")
    source_archive.add_argument("--reuse-status", default="", help="Reuse notes such as url-only, local-cache-only, restricted, or public-domain")
    source_archive.add_argument("--section", action="append", help="Disease chapter section supported by this source")
    source_archive.add_argument("--manifest", help="Source manifest path. Defaults to docs/clinical-statistical-expert/diseases/<disease>.sources.json")
    source_archive.add_argument("--cache-root", help="Override local cache directory")
    source_archive.add_argument(
        "--cache-status",
        choices=[
            "cached-local-only",
            "cached-local-only-and-figure-saved-in-repo",
            "downloaded-but-needs-review",
            "downloaded-but-client-challenge",
            "download-failed",
            "url-only",
        ],
        help="Override cache status when not downloading",
    )
    source_archive.add_argument("--download", action="store_true", help="Download a local reproducibility cache copy")
    source_archive.add_argument("--notes", default="")
    source_archive.add_argument("--date-accessed", help="Date accessed, YYYY-MM-DD. Defaults to today's UTC date")
    source_archive.add_argument("--json", action="store_true")
    source_archive.set_defaults(func=command_source_archive)

    disease_preview_cmd = sub.add_parser(
        "disease-preview",
        help="Render a clinical-statistical disease chapter as an HTML review preview",
    )
    disease_preview_cmd.add_argument("disease")
    disease_preview_cmd.add_argument("--disease-dir", help="Directory containing <disease>.md and optional evidence manifests")
    disease_preview_cmd.add_argument("--output", help="Output HTML path. Defaults to docs/clinical-statistical-expert/reports/<disease>.html")
    disease_preview_cmd.add_argument("--json", action="store_true")
    disease_preview_cmd.set_defaults(func=command_disease_preview)

    disease_homepage_cmd = sub.add_parser(
        "disease-homepage",
        help="Generate a clinical-statistical disease research project homepage and downloaded asset gallery",
    )
    disease_homepage_cmd.add_argument(
        "--project-root",
        help="Disease research project root containing manifest.json, diseases/, and reports/",
    )
    disease_homepage_cmd.add_argument(
        "--output",
        help="Homepage output path. Defaults to <project-root>/reports/all-diseases.html",
    )
    disease_homepage_cmd.add_argument(
        "--assets-output",
        help="Downloaded asset gallery output path. Defaults to <project-root>/reports/assets.html",
    )
    disease_homepage_cmd.add_argument(
        "--template-dir",
        help="Template directory containing disease-research-homepage.html.tmpl and disease-research-assets.html.tmpl",
    )
    disease_homepage_cmd.add_argument(
        "--no-link-disease-pages",
        action="store_true",
        help="Do not add project homepage/downloaded-assets links to existing disease HTML pages",
    )
    disease_homepage_cmd.add_argument("--json", action="store_true")
    disease_homepage_cmd.set_defaults(func=command_disease_homepage)

    download_reusable_assets_cmd = sub.add_parser(
        "download-reusable-assets",
        help="Review disease figure manifests and download only explicitly reusable direct image assets",
    )
    download_reusable_assets_cmd.add_argument(
        "--project-root",
        help="Disease research project root containing manifest.json, diseases/, and reports/",
    )
    download_reusable_assets_cmd.add_argument("--disease", help="Limit the review/download to one disease slug or name")
    download_reusable_assets_cmd.add_argument(
        "--dry-run",
        action="store_true",
        help="Review manifests and report what would be downloaded without writing assets or manifests",
    )
    download_reusable_assets_cmd.add_argument(
        "--force",
        action="store_true",
        help="Redownload eligible assets even when a recorded local_path already exists",
    )
    download_reusable_assets_cmd.add_argument(
        "--no-refresh-homepage",
        action="store_true",
        help="Do not regenerate all-diseases.html and assets.html after downloads",
    )
    download_reusable_assets_cmd.add_argument(
        "--template-dir",
        help="Template directory for homepage refresh. Defaults to SkillForge implementation templates.",
    )
    download_reusable_assets_cmd.add_argument("--json", action="store_true")
    download_reusable_assets_cmd.set_defaults(func=command_download_reusable_assets)

    disease_template_check_cmd = sub.add_parser(
        "disease-template-check",
        help="Check clinical-statistical disease chapters against the packaged templates",
    )
    disease_template_check_cmd.add_argument("disease", nargs="?", help="Disease slug or name. Omit to check all packaged chapters.")
    disease_template_check_cmd.add_argument("--disease-dir", help="Directory containing disease chapter Markdown and evidence manifests")
    disease_template_check_cmd.add_argument("--template-dir", help="Directory containing clinical-statistical-expert templates")
    disease_template_check_cmd.add_argument("--strict", action="store_true", help="Require exact template heading names instead of conceptual conformance")
    disease_template_check_cmd.add_argument("--json", action="store_true")
    disease_template_check_cmd.set_defaults(func=command_disease_template_check)

    evidence_query_pack_cmd = sub.add_parser(
        "evidence-query-pack",
        help="Generate expert-framed source discovery prompts for a clinical-statistical concept",
    )
    evidence_query_pack_cmd.add_argument("target_concept", help="Disease, finding, cohort label, endpoint, or concept to research")
    evidence_query_pack_cmd.add_argument("--lens", default="diagnostic-radiology", help="Expert lens, such as diagnostic-radiology or clinical-statistics")
    evidence_query_pack_cmd.add_argument("--expert-role", help="Expert role to use in the advanced prompt")
    evidence_query_pack_cmd.add_argument("--modality", help="Imaging modality or evidence modality, such as MRI")
    evidence_query_pack_cmd.add_argument("--evidence-type", help="Natural-language evidence type for the basic prompt")
    evidence_query_pack_cmd.add_argument("--json", action="store_true")
    evidence_query_pack_cmd.set_defaults(func=command_evidence_query_pack)

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

    install_skillforge_cmd = sub.add_parser(
        "install-skillforge",
        help="Verify or safely repair the SkillForge marketplace installation",
    )
    install_skillforge_cmd.add_argument("--codex-home", help="Codex home to inspect. Defaults to CODEX_HOME or ~/.codex.")
    install_skillforge_cmd.add_argument("--marketplace-path", help="Marketplace checkout path to inspect.")
    install_skillforge_cmd.add_argument("--yes", action="store_true", help="Apply safe missing Codex config entries")
    install_skillforge_cmd.add_argument("--json", action="store_true")
    install_skillforge_cmd.set_defaults(func=command_install_skillforge)

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

    contribute = sub.add_parser("contribute", help="Draft a pull request for a SkillForge contribution")
    contribute.add_argument("summary", help="Short summary of the bug fix, feature, docs change, or skill contribution")
    contribute.add_argument(
        "--type",
        "--kind",
        dest="change_type",
        default="improvement",
        choices=["bugfix", "feature", "docs", "skill", "catalog", "improvement"],
        help="Contribution type",
    )
    contribute.add_argument("--why", help="Why this change helps users or agents")
    contribute.add_argument("--changed", action="append", help="Changed file or folder; may be repeated")
    contribute.add_argument("--check", action="append", help="Validation command or result; may be repeated")
    contribute.add_argument("--safety-note", help="Privacy, data handling, or side-effect note for reviewers")
    contribute.add_argument(
        "--user-type",
        default="unknown",
        choices=["unknown", "non-developer", "developer"],
        help="Contributor comfort level for guidance; not a permission model",
    )
    contribute.add_argument("--title", help="Override generated pull request title")
    contribute.add_argument("--branch", help="Override generated contribution branch name")
    contribute.add_argument("--base", default="main", help="Base branch for the pull request")
    contribute.add_argument("--json", action="store_true")
    contribute.set_defaults(func=command_contribute)

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
