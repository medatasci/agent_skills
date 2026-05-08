from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import re
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .catalog import REPO_ROOT


def slug_text(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return text or "disease"


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def default_disease_dir() -> Path:
    return REPO_ROOT / "docs" / "clinical-statistical-expert" / "diseases"


def packaged_disease_dir() -> Path:
    return REPO_ROOT / "skills" / "clinical-statistical-expert" / "references" / "diseases"


def packaged_template_dir() -> Path:
    return REPO_ROOT / "skills" / "clinical-statistical-expert" / "references" / "templates"


def implementation_template_dir() -> Path:
    return REPO_ROOT / "skillforge" / "templates" / "clinical-statistical-expert"


def default_template_dir() -> Path:
    packaged = packaged_template_dir()
    if packaged.exists():
        return packaged
    return implementation_template_dir()


def default_report_dir() -> Path:
    return REPO_ROOT / "docs" / "clinical-statistical-expert" / "reports"


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
EXPLICIT_LOCAL_REUSE_STATUSES = {
    "ok-to-embed",
    "local-embeddable",
    "local-embeddable-cc-by",
    "downloaded",
    "downloaded-explicit-license",
}
EXPLICIT_REUSABLE_LICENSE_TERMS = {
    "creative commons",
    "cc by",
    "cc-by",
    "cc0",
    "public domain",
}
DIRECT_IMAGE_URL_FIELDS = (
    "image_url",
    "download_url",
    "direct_image_url",
    "asset_url",
    "image_path",
    "source_image_path",
    "local_source_path",
    "figure_file_url",
    "figure_url",
)


def relative_link(from_dir: Path, to_path: Path) -> str:
    return Path(os.path.relpath(to_path.resolve(), from_dir.resolve())).as_posix()


def local_asset_records(project_root: Path, item: dict[str, Any], reports_dir: Path) -> list[dict[str, Any]]:
    slug = item["slug"]
    disease_dir = project_root / "diseases" / slug
    figures_path = disease_dir / "figures.json"
    figure_by_path: dict[str, dict[str, Any]] = {}
    if figures_path.exists():
        figures_doc = load_json(figures_path, {"figures": []})
        for figure in figures_doc.get("figures", []):
            local_path = figure.get("local_path") or figure.get("image_path")
            if isinstance(local_path, str) and local_path:
                figure_by_path[local_path.replace("\\", "/")] = figure

    assets_dir = disease_dir / "assets"
    if not assets_dir.exists():
        return []

    records: list[dict[str, Any]] = []
    for path in sorted(assets_dir.rglob("*")):
        if not path.is_file():
            continue
        local_path = path.relative_to(disease_dir).as_posix()
        figure = figure_by_path.get(local_path, {})
        records.append(
            {
                "path": path,
                "local_path": local_path,
                "href": relative_link(reports_dir, path),
                "name": path.name,
                "is_image": path.suffix.lower() in IMAGE_EXTENSIONS,
                "figure_label": figure.get("figure_label") or path.stem,
                "source_title": figure.get("source_title") or "",
                "source_url": figure.get("source_url") or "",
                "license": figure.get("license") or "",
                "reuse_status": figure.get("reuse_status") or "",
                "clinical_point": figure.get("clinical_point") or "",
            }
        )
    return records


def asset_gap_summary(project_root: Path, items: list[dict[str, Any]], asset_records: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    completed_status = "final_thorough_research_target_met_needs_human_review"
    for item in items:
        if item.get("status") != completed_status:
            continue
        slug = item["slug"]
        disease_dir = project_root / "diseases" / slug
        figures_path = disease_dir / "figures.json"
        figures = load_json(figures_path, {"figures": []}).get("figures", []) if figures_path.exists() else []
        local_count = len(asset_records.get(slug, []))
        link_only = len(
            [
                figure
                for figure in figures
                if str(figure.get("reuse_status") or "").lower() == "link-only"
            ]
        )
        explicit_reusable = len(
            [
                figure
                for figure in figures
                if (
                    "creative commons" in str(figure.get("license") or "").lower()
                    or "cc by" in str(figure.get("license") or "").lower()
                    or "local-embeddable" in str(figure.get("reuse_status") or "").lower()
                    or str(figure.get("reuse_status") or "").lower() in {"ok-to-embed", "downloaded"}
                )
            ]
        )
        if local_count == 0:
            gaps.append(
                {
                    "slug": slug,
                    "name": item.get("name", slug),
                    "figures_total": len(figures),
                    "local_assets": local_count,
                    "link_only_figures": link_only,
                    "explicit_reusable_candidates": explicit_reusable,
                    "recommended_action": (
                        "review figure reuse rights and download only sources with explicit reusable licenses"
                    ),
                }
            )
    return gaps


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def is_explicitly_reusable_figure(figure: dict[str, Any]) -> tuple[bool, str]:
    status = str(figure.get("reuse_status") or "").strip().lower()
    license_text = str(figure.get("license") or "").strip().lower()
    status_allows_local = status in EXPLICIT_LOCAL_REUSE_STATUSES or "local-embeddable" in status
    license_allows_reuse = any(term in license_text for term in EXPLICIT_REUSABLE_LICENSE_TERMS)
    if not status_allows_local:
        return False, "reuse_status does not explicitly allow local storage or embedding"
    if not license_allows_reuse:
        return False, "license text does not explicitly identify a reusable license"
    return True, "explicit reusable license and local reuse status"


def figure_local_path(figure: dict[str, Any]) -> str:
    for key in ("local_path", "image_path"):
        value = figure.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def figure_identifier(figure: dict[str, Any], index: int) -> str:
    for key in ("id", "figure_id", "figure_label", "source_title"):
        value = figure.get(key)
        if isinstance(value, str) and value.strip():
            return slug_text(value)
    return f"figure-{index + 1}"


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme.lower() in {"http", "https", "file"}


def is_direct_image_reference(value: str) -> bool:
    parsed = urlparse(value)
    path = parsed.path if parsed.scheme else value
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS


def direct_image_reference(figure: dict[str, Any]) -> tuple[str, str] | None:
    for field in DIRECT_IMAGE_URL_FIELDS:
        value = figure.get(field)
        if not isinstance(value, str) or not value.strip():
            continue
        text = value.strip()
        if field == "figure_url" and not is_direct_image_reference(text):
            continue
        if is_direct_image_reference(text) or field in {"image_url", "download_url", "direct_image_url", "asset_url"}:
            return field, text
    return None


def infer_image_extension(source: str, content_type: str | None = None) -> str:
    parsed = urlparse(source)
    path = parsed.path if parsed.scheme else source
    suffix = Path(path).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return suffix
    content = (content_type or "").lower()
    if "png" in content:
        return ".png"
    if "jpeg" in content or "jpg" in content:
        return ".jpg"
    if "gif" in content:
        return ".gif"
    if "webp" in content:
        return ".webp"
    if "svg" in content:
        return ".svg"
    return ".bin"


def looks_like_image_payload(data: bytes, content_type: str | None, source: str) -> bool:
    content = (content_type or "").lower()
    if content.startswith("image/"):
        return True
    if is_direct_image_reference(source):
        return True
    return data.startswith((b"\x89PNG", b"\xff\xd8\xff", b"GIF87a", b"GIF89a", b"RIFF", b"<svg", b"<?xml"))


def read_direct_image(source: str) -> dict[str, Any]:
    if is_url(source):
        request = Request(source, headers={"User-Agent": "SkillForge reusable asset downloader/0.1"})
        with urlopen(request, timeout=30) as response:
            data = response.read()
            content_type = response.headers.get("Content-Type", "")
            final_url = response.geturl()
    else:
        path = Path(source)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"image source is not a file: {source}")
        data = path.read_bytes()
        content_type = ""
        final_url = path.resolve().as_posix()
    if not looks_like_image_payload(data, content_type, final_url or source):
        raise ValueError("downloaded payload was not recognized as an image")
    return {
        "bytes": len(data),
        "checksum_sha256": hashlib.sha256(data).hexdigest(),
        "content_type": content_type,
        "final_url": final_url or source,
        "data": data,
    }


def existing_local_asset_path(disease_dir: Path, local_path: str) -> Path:
    path = Path(local_path)
    if path.is_absolute():
        return path
    return disease_dir / path


def figure_manifest_paths(disease_dir: Path, slug: str) -> list[Path]:
    candidates = [disease_dir / "figures.json", disease_dir / f"{slug}.figures.json"]
    seen: set[Path] = set()
    paths: list[Path] = []
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if path.exists():
            paths.append(path)
    return paths


def write_figure_manifests(paths: list[Path], payload: dict[str, Any]) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    for path in paths:
        path.write_text(text, encoding="utf-8")


def download_reusable_assets(
    *,
    project_root: str | Path | None = None,
    disease: str | None = None,
    dry_run: bool = False,
    force: bool = False,
    refresh_homepage: bool = True,
    template_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(project_root) if project_root else (
        REPO_ROOT / "docs" / "clinical-statistical-expert" / "mr-rate-disease-research"
    )
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Disease research manifest not found: {manifest_path}")
    manifest = load_json(manifest_path, {"items": []})
    items = manifest.get("items", [])
    if not isinstance(items, list):
        raise ValueError("manifest.json must contain an items list")

    requested = slug_text(disease) if disease else ""
    selected_items = [
        item
        for item in items
        if isinstance(item, dict)
        and item.get("slug")
        and (not requested or slug_text(str(item.get("slug"))) == requested or slug_text(str(item.get("name", ""))) == requested)
    ]
    if requested and not selected_items:
        raise ValueError(f"Disease not found in manifest: {disease}")

    review: list[dict[str, Any]] = []
    totals = {
        "diseases_reviewed": 0,
        "figures_reviewed": 0,
        "eligible": 0,
        "downloaded": 0,
        "already_local": 0,
        "skipped": 0,
        "failed": 0,
    }

    for item in selected_items:
        slug = str(item["slug"])
        disease_dir = root / "diseases" / slug
        paths = figure_manifest_paths(disease_dir, slug)
        disease_report = {
            "slug": slug,
            "name": item.get("name", slug),
            "manifest_paths": [repo_relative(path) for path in paths],
            "figures_reviewed": 0,
            "eligible": 0,
            "downloaded": 0,
            "already_local": 0,
            "skipped": 0,
            "failed": 0,
            "entries": [],
        }
        totals["diseases_reviewed"] += 1
        if not paths:
            disease_report["entries"].append(
                {
                    "status": "skipped",
                    "reason": "figure manifest not found",
                }
            )
            disease_report["skipped"] += 1
            totals["skipped"] += 1
            review.append(disease_report)
            continue

        figure_payload = load_json(paths[0], {"figures": []})
        figures = figure_payload.get("figures", [])
        if not isinstance(figures, list):
            figures = []
            figure_payload["figures"] = figures
        updated = False

        for index, figure in enumerate(figures):
            if not isinstance(figure, dict):
                continue
            disease_report["figures_reviewed"] += 1
            totals["figures_reviewed"] += 1
            identifier = figure_identifier(figure, index)
            entry: dict[str, Any] = {
                "id": identifier,
                "figure_label": figure.get("figure_label") or figure.get("figure_id") or identifier,
                "reuse_status": figure.get("reuse_status") or "",
                "license": figure.get("license") or "",
            }

            reusable, reason = is_explicitly_reusable_figure(figure)
            if reusable:
                disease_report["eligible"] += 1
                totals["eligible"] += 1

            local_path = figure_local_path(figure)
            if local_path and existing_local_asset_path(disease_dir, local_path).exists() and not force:
                entry.update({"status": "already-local", "local_path": local_path})
                disease_report["already_local"] += 1
                totals["already_local"] += 1
                disease_report["entries"].append(entry)
                continue

            if not reusable:
                entry.update({"status": "skipped", "reason": reason})
                disease_report["skipped"] += 1
                totals["skipped"] += 1
                disease_report["entries"].append(entry)
                continue

            direct = direct_image_reference(figure)
            if not direct:
                entry.update({"status": "skipped", "reason": "no direct image URL or local image source is recorded"})
                disease_report["skipped"] += 1
                totals["skipped"] += 1
                disease_report["entries"].append(entry)
                continue

            source_field, source = direct
            extension = infer_image_extension(source)
            target_dir = disease_dir / "assets" / slug
            target = target_dir / f"{identifier}{extension}"
            if dry_run:
                entry.update(
                    {
                        "status": "would-download",
                        "source_field": source_field,
                        "source": source,
                        "target_path": target.relative_to(disease_dir).as_posix(),
                    }
                )
                disease_report["entries"].append(entry)
                continue

            try:
                payload = read_direct_image(source)
                extension = infer_image_extension(payload["final_url"], payload["content_type"])
                target = target_dir / f"{identifier}{extension}"
                target_dir.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload["data"])
                relative_asset = target.relative_to(disease_dir).as_posix()
                figure["local_path"] = relative_asset
                figure["checksum_sha256"] = payload["checksum_sha256"]
                figure["bytes"] = payload["bytes"]
                figure["content_type"] = payload["content_type"]
                figure["downloaded_at"] = utc_now_iso()
                figure["download_source_field"] = source_field
                figure["download_final_url"] = payload["final_url"]
                if figure.get("reuse_status") != "local-embeddable-cc-by":
                    figure["reuse_status"] = "downloaded-explicit-license"
                updated = True
                entry.update(
                    {
                        "status": "downloaded",
                        "source_field": source_field,
                        "source": source,
                        "local_path": relative_asset,
                        "checksum_sha256": payload["checksum_sha256"],
                        "bytes": payload["bytes"],
                    }
                )
                disease_report["downloaded"] += 1
                totals["downloaded"] += 1
            except (OSError, URLError, TimeoutError, ValueError) as exc:
                entry.update(
                    {
                        "status": "failed",
                        "source_field": source_field,
                        "source": source,
                        "reason": str(exc),
                    }
                )
                disease_report["failed"] += 1
                totals["failed"] += 1
            disease_report["entries"].append(entry)

        if updated:
            write_figure_manifests(paths, figure_payload)
        review.append(disease_report)

    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "download-reusable-assets.json"
    payload = {
        "ok": totals["failed"] == 0,
        "command": "download-reusable-assets",
        "project_root": repo_relative(root),
        "manifest_path": repo_relative(manifest_path),
        "created_at": utc_now_iso(),
        "dry_run": dry_run,
        "force": force,
        "totals": totals,
        "diseases": review,
        "review_policy": {
            "download_rule": "Only direct image references with explicit reusable license text and local-embedding reuse status are downloaded.",
            "allowed_reuse_statuses": sorted(EXPLICIT_LOCAL_REUSE_STATUSES),
            "allowed_license_terms": sorted(EXPLICIT_REUSABLE_LICENSE_TERMS),
        },
    }
    if not dry_run:
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        payload["report_path"] = repo_relative(report_path)
    else:
        payload["report_path"] = ""

    if refresh_homepage and not dry_run:
        homepage_payload = disease_homepage(project_root=root, template_dir=template_dir)
        payload["homepage"] = {
            "output_path": homepage_payload["output_path"],
            "assets_output_path": homepage_payload["assets_output_path"],
            "downloaded_asset_count": homepage_payload["downloaded_asset_count"],
            "download_asset_gaps": homepage_payload["download_asset_gaps"],
        }

    return payload


def render_asset_gallery(
    *,
    project_title: str,
    downloaded_asset_count: int,
    asset_records_by_slug: dict[str, list[dict[str, Any]]],
    asset_gaps: list[dict[str, Any]],
    items: list[dict[str, Any]],
    template_path: Path,
    output_path: Path,
) -> None:
    asset_sections: list[str] = []
    for item in items:
        slug = item["slug"]
        records = asset_records_by_slug.get(slug, [])
        if not records:
            continue
        asset_sections.append(f'<section id="{html.escape(slug)}">')
        asset_sections.append(
            f"<h2>{html.escape(item.get('name', slug))} "
            f"<code>{html.escape(slug)}</code></h2>"
        )
        asset_sections.append('<div class="asset-grid">')
        for record in records:
            caption_parts = [
                f"<strong>{html.escape(str(record['figure_label']))}</strong>",
                f"<code>{html.escape(str(record['local_path']))}</code>",
            ]
            if record["source_title"]:
                source_title = html.escape(str(record["source_title"]))
                source_url = html.escape(str(record["source_url"]))
                caption_parts.append(f'Source: <a href="{source_url}">{source_title}</a>')
            if record["reuse_status"] or record["license"]:
                caption_parts.append(
                    f"Reuse: {html.escape(str(record['reuse_status']))}; "
                    f"{html.escape(str(record['license']))}"
                )
            if record["clinical_point"]:
                caption_parts.append(html.escape(str(record["clinical_point"])))
            caption = "<br>".join(caption_parts)
            href = html.escape(str(record["href"]))
            name = html.escape(str(record["name"]))
            if record["is_image"]:
                media = f'<a href="{href}"><img src="{href}" alt="{name}"></a>'
            else:
                media = f'<a href="{href}">{name}</a>'
            asset_sections.append(f"<figure>{media}<figcaption>{caption}</figcaption></figure>")
        asset_sections.append("</div></section>")

    if not asset_sections:
        asset_sections.append("<p>No downloaded local assets have been recorded yet.</p>")
    if asset_gaps:
        asset_sections.append("<h2>Download Priorities</h2>")
        asset_sections.append(
            "<p>These completed diseases have figure evidence, but no downloaded local assets yet. "
            "Download only after reuse rights are reviewed and explicitly allow local storage or embedding.</p>"
        )
        asset_sections.append(
            "<table><thead><tr><th>Disease</th><th>Figure Records</th>"
            "<th>Link-Only Figures</th><th>Explicit Reusable Candidates</th><th>Recommended Action</th>"
            "</tr></thead><tbody>"
        )
        for gap in asset_gaps:
            asset_sections.append(
                "<tr>"
                f"<td><strong>{html.escape(str(gap['name']))}</strong><br><code>{html.escape(str(gap['slug']))}</code></td>"
                f"<td>{gap['figures_total']}</td>"
                f"<td>{gap['link_only_figures']}</td>"
                f"<td>{gap['explicit_reusable_candidates']}</td>"
                f"<td>{html.escape(str(gap['recommended_action']))}</td>"
                "</tr>"
            )
        asset_sections.append("</tbody></table>")

    page = template_path.read_text(encoding="utf-8")
    replacements = {
        "{{ project_title }}": project_title,
        "{{ downloaded_asset_count }}": str(downloaded_asset_count),
        "{{ asset_sections }}": "\n".join(asset_sections),
    }
    for old, new in replacements.items():
        page = page.replace(old, new)
    output_path.write_text(page, encoding="utf-8")


def link_disease_pages_to_project_reports(project_root: Path, items: list[dict[str, Any]]) -> int:
    reports_dir = project_root / "reports"
    disease_reports_dir = reports_dir / "diseases"
    changed = 0
    for item in items:
        slug = item["slug"]
        path = disease_reports_dir / f"{slug}.html"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "assets.html#" in text and "all-diseases.html" in text:
            continue
        homepage_link = f"<a href='../all-diseases.html'>Project homepage</a>"
        assets_link = f"<a href='../assets.html#{html.escape(slug)}'>Downloaded assets</a>"
        replacement = (
            "<div class='nav'><a href='../index.html'>Back to MR-RATE status index</a>"
            f" | {homepage_link} | {assets_link}</div>"
        )
        if "<div class='nav'><a href='../index.html'>Back to MR-RATE status index</a></div>" in text:
            text = text.replace(
                "<div class='nav'><a href='../index.html'>Back to MR-RATE status index</a></div>",
                replacement,
                1,
            )
        elif "<body>\n  <main>" in text:
            text = text.replace("<body>\n  <main>", f"<body>\n  <main>\n{replacement}", 1)
        elif "<body><main>" in text:
            text = text.replace("<body><main>", f"<body><main>\n{replacement}", 1)
        elif "<main>" in text:
            text = text.replace("<main>", f"<main>\n{replacement}", 1)
        else:
            continue
        path.write_text(text, encoding="utf-8")
        changed += 1
    return changed


def disease_homepage(
    *,
    project_root: str | Path | None = None,
    output: str | Path | None = None,
    assets_output: str | Path | None = None,
    template_dir: str | Path | None = None,
    link_disease_pages: bool = True,
) -> dict[str, Any]:
    root = Path(project_root) if project_root else (
        REPO_ROOT / "docs" / "clinical-statistical-expert" / "mr-rate-disease-research"
    )
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Disease research manifest not found: {manifest_path}")
    manifest = load_json(manifest_path, {"items": []})
    items = manifest.get("items", [])
    if not isinstance(items, list):
        raise ValueError("manifest.json must contain an items list")

    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = Path(output) if output else reports_dir / "all-diseases.html"
    assets_path = Path(assets_output) if assets_output else reports_dir / "assets.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    assets_path.parent.mkdir(parents=True, exist_ok=True)

    templates = Path(template_dir) if template_dir else implementation_template_dir()
    homepage_template = templates / "disease-research-homepage.html.tmpl"
    assets_template = templates / "disease-research-assets.html.tmpl"
    if not homepage_template.exists():
        raise FileNotFoundError(f"Homepage template not found: {homepage_template}")
    if not assets_template.exists():
        raise FileNotFoundError(f"Asset template not found: {assets_template}")

    asset_records_by_slug = {
        item["slug"]: local_asset_records(root, item, reports_dir)
        for item in items
        if isinstance(item, dict) and item.get("slug")
    }
    downloaded_asset_count = sum(len(records) for records in asset_records_by_slug.values())
    completed_status = "final_thorough_research_target_met_needs_human_review"
    completed = len([item for item in items if item.get("status") == completed_status])

    clusters: list[str] = []
    for item in items:
        cluster = item.get("cluster", "uncategorized")
        if cluster not in clusters:
            clusters.append(cluster)

    sections: list[str] = []
    for cluster in clusters:
        label = cluster.replace("_", " ").title()
        sections.append(f"<h2>{html.escape(label)}</h2>")
        sections.append(
            "<table><thead><tr>"
            "<th>Rank</th><th>Disease</th><th>MR-RATE Name</th><th>Status</th>"
            "<th>Evidence</th><th>Ontology</th><th>Review Page</th>"
            "<th>Downloaded Assets</th><th>Evidence Metadata</th>"
            "</tr></thead><tbody>"
        )
        for item in [entry for entry in items if entry.get("cluster") == cluster]:
            status = item.get("status", "")
            status_class = "complete" if status == completed_status else "draft"
            counts = item.get("current_counts") or {}
            evidence = (
                f"sources {counts.get('sources', 0)}<br>"
                f"figures {counts.get('figures', 0)}<br>"
                f"videos {counts.get('videos', 0)}"
            )
            ontology = item.get("snomed_id") or item.get("radlex_id") or ""
            slug = item["slug"]
            artifact_prefix = f"../diseases/{html.escape(slug)}"
            metadata_links = (
                '<div class="links">'
                f'<a href="{artifact_prefix}/sources.json">source metadata</a>'
                f'<a href="{artifact_prefix}/figures.json">figure metadata</a>'
                f'<a href="{artifact_prefix}/videos.json">video metadata</a>'
                f'<a href="{artifact_prefix}/research-plan.md">plan</a>'
                f'<a href="{artifact_prefix}/differential-matrix.md">differential</a>'
                "</div>"
            )
            local_count = len(asset_records_by_slug.get(slug, []))
            if local_count:
                downloaded_assets = (
                    '<div class="links">'
                    f'<a href="{html.escape(assets_path.name)}#{html.escape(slug)}">{local_count} downloaded files</a>'
                    f'<a href="{artifact_prefix}/assets/">asset folder</a>'
                    "</div>"
                )
            else:
                downloaded_assets = "No local downloads yet"
            sections.append(
                "<tr>"
                f"<td>{item.get('rank', '')}</td>"
                f"<td><strong>{html.escape(item.get('name', slug))}</strong><br>"
                f"<code>{html.escape(slug)}</code></td>"
                f"<td>{html.escape(item.get('original_name', '') or '')}</td>"
                f'<td><span class="badge {status_class}">{html.escape(status)}</span></td>'
                f"<td>{evidence}</td>"
                f"<td><code>{html.escape(str(ontology))}</code></td>"
                f'<td><a href="diseases/{html.escape(slug)}.html">Open HTML preview</a></td>'
                f"<td>{downloaded_assets}</td>"
                f"<td>{metadata_links}</td>"
                "</tr>"
            )
        sections.append("</tbody></table>")

    homepage = homepage_template.read_text(encoding="utf-8")
    replacements = {
        "{{ project_title }}": "MR-RATE Disease Research Project Homepage",
        "{{ project_description }}": (
            "This page links to disease HTML previews, downloaded local assets, "
            "and evidence metadata for all disease categories in the current "
            "disease research manifest."
        ),
        "{{ updated_at }}": html.escape(str(manifest.get("updated_at", "unknown"))),
        "{{ total_count }}": str(len(items)),
        "{{ completed_count }}": str(completed),
        "{{ remaining_count }}": str(len(items) - completed),
        "{{ downloaded_asset_count }}": str(downloaded_asset_count),
        "{{ cluster_tables }}": "\n".join(sections),
    }
    for old, new in replacements.items():
        homepage = homepage.replace(old, new)
    output_path.write_text(homepage, encoding="utf-8")

    gaps = asset_gap_summary(root, items, asset_records_by_slug)

    render_asset_gallery(
        project_title="MR-RATE Disease Research",
        downloaded_asset_count=downloaded_asset_count,
        asset_records_by_slug=asset_records_by_slug,
        asset_gaps=gaps,
        items=items,
        template_path=assets_template,
        output_path=assets_path,
    )

    linked_pages = link_disease_pages_to_project_reports(root, items) if link_disease_pages else 0

    return {
        "ok": True,
        "project_root": repo_relative(root),
        "manifest_path": repo_relative(manifest_path),
        "output_path": repo_relative(output_path),
        "assets_output_path": repo_relative(assets_path),
        "disease_count": len(items),
        "completed_count": completed,
        "remaining_count": len(items) - completed,
        "downloaded_asset_count": downloaded_asset_count,
        "diseases_with_downloaded_assets": len(
            [slug for slug, records in asset_records_by_slug.items() if records]
        ),
        "linked_disease_pages": linked_pages,
        "download_asset_gaps": gaps,
    }


def default_expert_role(lens: str, modality: str | None) -> str:
    normalized_lens = canonical_heading(lens)
    normalized_modality = canonical_heading(modality or "")
    if "radiology" in normalized_lens or normalized_modality in {"mri", "ct", "pet", "spect"}:
        if normalized_modality == "mri":
            return "neuroradiologist"
        return "radiology expert"
    if "statistic" in normalized_lens:
        return "clinical trial statistician"
    if "biomarker" in normalized_lens:
        return "imaging biomarker scientist"
    return "clinical expert"


def evidence_query_pack(
    target_concept: str,
    *,
    lens: str = "diagnostic-radiology",
    expert_role: str | None = None,
    modality: str | None = None,
    evidence_type: str | None = None,
) -> dict[str, Any]:
    concept = target_concept.strip()
    if not concept:
        raise ValueError("target concept is required")
    modality_text = (modality or "").strip()
    evidence_text = (evidence_type or (f"{modality_text} images" if modality_text else "the relevant evidence")).strip()
    role = (expert_role or default_expert_role(lens, modality_text)).strip()
    modality_phrase = modality_text or "the relevant modality"
    modality_specific = (
        f"sequence-specific {modality_text} signal characteristics"
        if modality_text.upper() == "MRI"
        else f"{modality_phrase}-specific imaging characteristics"
    )
    structural_patterns = "volume-loss patterns" if modality_text.upper() == "MRI" else "structural patterns"

    basic_prompt = (
        f"As a radiology expert, given a diagnosis of {concept}, "
        f"what would you look for in {evidence_text} to confirm?"
    )
    advanced_prompt = (
        f"As a {role}, given a diagnosis of {concept}, what {modality_specific}, "
        "lesion morphology, anatomic distribution, chronicity features, "
        f"{structural_patterns}, and associated findings would you expect to see on {modality_phrase}?"
    )

    search_variants = [
        f"{concept} {modality_phrase} imaging characteristics",
        f"{concept} {modality_phrase} lesion morphology anatomic distribution",
        f"{concept} {modality_phrase} chronicity features structural patterns",
        f"{concept} {modality_phrase} associated findings radiology",
        f"{concept} {modality_phrase} differential diagnosis mimics",
        f"{concept} {modality_phrase} report language findings impression",
        f"{concept} clinical course progression stable treatment response",
        f"{concept} cohort definition endpoint misclassification adjudication",
    ]
    if modality_text.upper() == "MRI":
        search_variants.insert(
            1,
            f"{concept} MRI T1 T2 FLAIR DWI ADC SWI contrast signal characteristics",
        )

    return {
        "ok": True,
        "target_concept": concept,
        "lens": lens,
        "expert_role": role,
        "modality": modality_text,
        "evidence_type": evidence_text,
        "template_reference": "skillforge/templates/clinical-statistical-expert/disease-research-plan.md.tmpl",
        "section": "Expert-Framed Source Discovery Questions",
        "basic_pattern": (
            "As a <radiology expert role>, given a diagnosis of <disease or imaging finding>, "
            "what would you look for in <modality> images to confirm?"
        ),
        "basic_prompt": basic_prompt,
        "advanced_pattern": (
            "As a <radiology expert role>, given a diagnosis of <disease or imaging finding>, "
            "what <modality-specific> imaging characteristics, lesion morphology, anatomic "
            "distribution, chronicity features, structural patterns, and associated findings "
            "would you expect to see on <modality>?"
        ),
        "advanced_prompt": advanced_prompt,
        "search_variants": search_variants,
        "source_type_suggestions": [
            "medical imaging textbooks or textbook-style chapters",
            "professional society guidance and appropriateness criteria",
            "clinician-facing radiology training resources",
            "broad clinical or radiology review articles",
            "narrow primary studies only for narrow technical claims",
        ],
        "capture_notes": [
            "Use confirm for natural-language searching when helpful.",
            "When writing the chapter, translate search findings into clinically precise language such as support, favor, characterize, distinguish from mimics, or identify missing information.",
            "Use the answer to populate What To Look For, Modality-Specific Appearance, Locations And Structural Appearance, Report Language Patterns, and Differential Diagnosis sections.",
            "Do not treat generated searches as source evidence; use them to find and review authoritative sources.",
        ],
    }


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def resolve_markdown_reference(reference: str, *, markdown_dir: Path, output_dir: Path) -> str:
    if re.match(r"^[a-z]+://|^#", reference):
        return reference
    target = (markdown_dir / reference).resolve()
    try:
        return Path(os.path.relpath(target, output_dir.resolve())).as_posix()
    except ValueError:
        try:
            return target.relative_to(REPO_ROOT.resolve()).as_posix()
        except ValueError:
            return target.as_posix()


def linkify_inline(text: str, *, markdown_dir: Path, output_dir: Path) -> str:
    token = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)|(?<!!)\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`")
    rendered: list[str] = []
    cursor = 0
    for match in token.finditer(text):
        rendered.append(html.escape(text[cursor : match.start()]))
        if match.group(1) is not None:
            alt = html.escape(match.group(1), quote=True)
            src = resolve_markdown_reference(match.group(2).strip(), markdown_dir=markdown_dir, output_dir=output_dir)
            rendered.append(f'<img src="{html.escape(src, quote=True)}" alt="{alt}" loading="lazy">')
        elif match.group(3) is not None:
            label = html.escape(match.group(3))
            href = resolve_markdown_reference(match.group(4).strip(), markdown_dir=markdown_dir, output_dir=output_dir)
            rendered.append(f'<a href="{html.escape(href, quote=True)}">{label}</a>')
        else:
            rendered.append(f"<code>{html.escape(match.group(5))}</code>")
        cursor = match.end()
    rendered.append(html.escape(text[cursor:]))
    return "".join(rendered)


def render_table(lines: list[str], *, markdown_dir: Path, output_dir: Path) -> str:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    if len(rows) < 2:
        return ""
    header = rows[0]
    body = rows[2:] if re.match(r"^[\s|:-]+$", lines[1]) else rows[1:]
    head_html = "".join(f"<th>{linkify_inline(cell, markdown_dir=markdown_dir, output_dir=output_dir)}</th>" for cell in header)
    body_rows = []
    for row in body:
        cells = "".join(f"<td>{linkify_inline(cell, markdown_dir=markdown_dir, output_dir=output_dir)}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{head_html}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def markdown_to_html(markdown: str, *, markdown_dir: Path, output_dir: Path) -> str:
    blocks: list[str] = []
    paragraph: list[str] = []
    unordered_items: list[str] = []
    ordered_items: list[str] = []
    table_lines: list[str] = []
    code_lines: list[str] = []
    in_code_block = False

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(line.strip() for line in paragraph).strip()
            blocks.append(f"<p>{linkify_inline(text, markdown_dir=markdown_dir, output_dir=output_dir)}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if unordered_items:
            blocks.append("<ul>" + "".join(unordered_items) + "</ul>")
            unordered_items.clear()
        if ordered_items:
            blocks.append("<ol>" + "".join(ordered_items) + "</ol>")
            ordered_items.clear()

    def flush_table() -> None:
        if table_lines:
            rendered = render_table(table_lines, markdown_dir=markdown_dir, output_dir=output_dir)
            if rendered:
                blocks.append(rendered)
            table_lines.clear()

    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            flush_table()
            if in_code_block:
                blocks.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines.clear()
                in_code_block = False
            else:
                in_code_block = True
            continue
        if in_code_block:
            code_lines.append(line)
            continue
        if not stripped:
            flush_paragraph()
            flush_list()
            flush_table()
            continue
        is_list_continuation = (
            bool(unordered_items or ordered_items)
            and (line.startswith("  ") or line.startswith("\t"))
            and not re.match(r"^\s*(- |\d+\.\s+|#{1,6}\s+|\|)", line)
            and not stripped.startswith("![")
        )
        if is_list_continuation:
            continuation = linkify_inline(stripped, markdown_dir=markdown_dir, output_dir=output_dir)
            if unordered_items:
                unordered_items[-1] = unordered_items[-1].removesuffix("</li>") + f" {continuation}</li>"
            elif ordered_items:
                ordered_items[-1] = ordered_items[-1].removesuffix("</li>") + f" {continuation}</li>"
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            flush_list()
            table_lines.append(stripped)
            continue
        flush_table()
        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_list()
            level = min(len(heading.group(1)), 4)
            text = linkify_inline(heading.group(2), markdown_dir=markdown_dir, output_dir=output_dir)
            blocks.append(f"<h{level}>{text}</h{level}>")
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            item = stripped[2:].strip()
            unordered_items.append(f"<li>{linkify_inline(item, markdown_dir=markdown_dir, output_dir=output_dir)}</li>")
            continue
        numbered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if numbered:
            flush_paragraph()
            item = numbered.group(1).strip()
            ordered_items.append(f"<li>{linkify_inline(item, markdown_dir=markdown_dir, output_dir=output_dir)}</li>")
            continue
        if stripped.startswith("!["):
            flush_paragraph()
            flush_list()
            blocks.append(linkify_inline(stripped, markdown_dir=markdown_dir, output_dir=output_dir))
            continue
        paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    flush_table()
    if in_code_block:
        blocks.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    return "\n".join(blocks)


def evidence_summary(disease: str, disease_dir: Path) -> dict[str, Any]:
    slug = slug_text(disease)
    source_manifest = load_json(disease_dir / f"{slug}.sources.json", {"sources": []})
    figure_manifest = load_json(disease_dir / f"{slug}.figures.json", {"figures": []})
    sources = source_manifest.get("sources", [])
    figures = figure_manifest.get("figures", [])
    source_status = {}
    for source in sources:
        status = source.get("cache_status") or "unknown"
        source_status[status] = source_status.get(status, 0) + 1
    figure_status = {}
    for figure in figures:
        status = figure.get("reuse_status") or "unknown"
        figure_status[status] = figure_status.get(status, 0) + 1
    return {
        "sources_total": len(sources),
        "source_status": source_status,
        "figures_total": len(figures),
        "figure_status": figure_status,
        "local_figures": len([figure for figure in figures if figure.get("local_path")]),
        "source_manifest": source_manifest,
        "figure_manifest": figure_manifest,
    }


def render_status_cards(summary: dict[str, Any]) -> str:
    source_items = "".join(
        f"<li>{html.escape(status)}: {count}</li>"
        for status, count in sorted(summary["source_status"].items())
    )
    figure_items = "".join(
        f"<li>{html.escape(status)}: {count}</li>"
        for status, count in sorted(summary["figure_status"].items())
    )
    return f"""
<section class="cards">
  <article><strong>{summary['sources_total']}</strong><span>Sources recorded</span><ul>{source_items}</ul></article>
  <article><strong>{summary['figures_total']}</strong><span>Image candidates</span><ul>{figure_items}</ul></article>
  <article><strong>{summary['local_figures']}</strong><span>Local embeddable figures</span><p>Other figures remain link-only until reuse is reviewed.</p></article>
</section>
"""


def disease_preview(
    disease: str,
    *,
    disease_dir: str | Path | None = None,
    output: str | Path | None = None,
) -> dict[str, Any]:
    slug = slug_text(disease)
    disease_root = Path(disease_dir) if disease_dir else default_disease_dir()
    markdown_path = disease_root / f"{slug}.md"
    if disease_dir is None and not markdown_path.exists():
        fallback_root = packaged_disease_dir()
        fallback_path = fallback_root / f"{slug}.md"
        if fallback_path.exists():
            disease_root = fallback_root
            markdown_path = fallback_path
    if not markdown_path.exists():
        raise FileNotFoundError(f"Disease chapter not found: {markdown_path}")
    output_path = Path(output) if output else default_report_dir() / f"{slug}.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    markdown = markdown_path.read_text(encoding="utf-8")
    summary = evidence_summary(slug, disease_root)
    body = markdown_to_html(markdown, markdown_dir=markdown_path.parent, output_dir=output_path.parent)
    cards = render_status_cards(summary)
    generated = datetime.now(timezone.utc).isoformat()
    title = f"{slug.replace('-', ' ').title()} Disease Chapter Preview"
    project_report_dir = output_path.parent.parent if output_path.parent.name == "diseases" else output_path.parent
    homepage_href = relative_link(output_path.parent, project_report_dir / "all-diseases.html")
    assets_href = relative_link(output_path.parent, project_report_dir / "assets.html") + f"#{slug}"
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.55; margin: 0; color: #1f2933; background: #f7f8fa; }}
    header {{ background: #102033; color: white; padding: 32px max(24px, calc((100vw - 1120px) / 2)); }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; background: white; overflow-x: auto; }}
    h1, h2, h3 {{ line-height: 1.2; }}
    a {{ color: #0b5cab; }}
    img {{ max-width: 100%; height: auto; border: 1px solid #d7dde5; margin: 12px 0; }}
    table {{ width: 100%; min-width: 760px; border-collapse: collapse; margin: 16px 0; font-size: 0.94rem; }}
    th, td {{ border: 1px solid #d7dde5; padding: 8px; vertical-align: top; }}
    th {{ background: #edf2f7; text-align: left; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 20px 0; }}
    .cards article {{ border: 1px solid #d7dde5; border-radius: 6px; padding: 16px; background: #fbfcfd; }}
    .cards strong {{ display: block; font-size: 2rem; color: #102033; }}
    .cards span {{ font-weight: 700; }}
    .nav {{ margin: 0 0 18px; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <p>Generated {html.escape(generated)} from {html.escape(repo_relative(markdown_path))}.</p>
  </header>
  <main>
<div class="nav"><a href="{html.escape(homepage_href)}">Project homepage</a> | <a href="{html.escape(assets_href)}">Downloaded assets</a></div>
{cards}
{body}
  </main>
</body>
</html>
"""
    output_path.write_text(page, encoding="utf-8")
    return {
        "ok": True,
        "disease": slug,
        "output_path": repo_relative(output_path),
        "markdown_path": repo_relative(markdown_path),
        "sources_total": summary["sources_total"],
        "figures_total": summary["figures_total"],
        "local_figures": summary["local_figures"],
    }


def canonical_heading(value: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", value)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return " ".join(text.split())


def markdown_headings(markdown: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        text = match.group(2).strip()
        headings.append(
            {
                "level": len(match.group(1)),
                "text": text,
                "canonical": canonical_heading(text),
                "line": line_number,
            }
        )
    return headings


def headings_from_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return markdown_headings(path.read_text(encoding="utf-8-sig"))


def has_heading(headings: list[dict[str, Any]], expected: str) -> bool:
    canonical = canonical_heading(expected)
    return any(heading["canonical"] == canonical for heading in headings)


def has_any_heading(headings: list[dict[str, Any]], options: list[str]) -> bool:
    return any(has_heading(headings, option) for option in options)


def section_headings(
    headings: list[dict[str, Any]],
    *,
    start: str,
    end: str,
    minimum_level: int = 3,
) -> list[dict[str, Any]]:
    start_key = canonical_heading(start)
    end_key = canonical_heading(end)
    in_section = False
    collected: list[dict[str, Any]] = []
    for heading in headings:
        if heading["canonical"] == start_key:
            in_section = True
            continue
        if in_section and heading["canonical"] == end_key:
            break
        if in_section and heading["level"] >= minimum_level:
            collected.append(heading)
    return collected


def chapter_markdown_files(disease_root: Path) -> list[Path]:
    if not disease_root.exists():
        return []
    files: list[Path] = []
    for path in sorted(disease_root.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        if "." in path.stem:
            continue
        files.append(path)
    return files


def validate_json_manifest(path: Path, key: str) -> tuple[bool, str, dict[str, Any] | None]:
    if not path.exists():
        return False, "missing", None
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}", None
    if not isinstance(payload, dict):
        return False, "manifest root must be an object", payload
    value = payload.get(key)
    if not isinstance(value, list):
        return False, f"manifest must contain a list named {key}", payload
    return True, f"{len(value)} {key} recorded", payload


def local_figure_path_status(disease_root: Path, figure_payload: dict[str, Any] | None) -> tuple[bool, str]:
    if not figure_payload:
        return False, "figure manifest unavailable"
    missing: list[str] = []
    checked = 0
    for figure in figure_payload.get("figures", []):
        if not isinstance(figure, dict):
            continue
        local_path = figure.get("local_path")
        if not local_path:
            continue
        checked += 1
        local_path_text = str(local_path)
        target = (disease_root / local_path_text).resolve()
        repo_target = (REPO_ROOT / local_path_text).resolve()
        if not target.exists() and not repo_target.exists():
            missing.append(str(local_path))
    if missing:
        return False, f"missing local figure assets: {', '.join(missing[:5])}"
    return True, f"{checked} local figure paths checked"


DISEASE_TEMPLATE_SECTION_GROUPS: list[tuple[str, list[str]]] = [
    ("Goals", ["Goals"]),
    ("Source Review Status", ["Source Review Status"]),
    ("Figure Evidence", ["Figure Evidence"]),
    ("Common Names And Aliases", ["Common Names And Aliases"]),
    ("Scope", ["Scope"]),
    ("Clinical Context", ["Clinical Context"]),
    ("Known-Diagnosis Review Frame", ["Known-Diagnosis Review Frame"]),
    ("What To Look For", ["What To Look For"]),
    ("Primary Imaging Modality", ["Primary Imaging Modality"]),
    ("Other Modalities And When They Matter", ["Other Modalities And When They Matter"]),
    ("Locations And Structural Appearance", ["Locations And Structural Appearance"]),
    ("Typical Appearance", ["Typical Appearance"]),
    ("Atypical Or Red-Flag Appearance", ["Atypical Or Red-Flag Appearance"]),
    ("Differential Diagnosis And Mimics", ["Differential Diagnosis And Mimics"]),
    ("Quick Differential Diagnosis Guide", ["Quick Differential Diagnosis Guide"]),
    ("Key Imaging Discriminators", ["Key Imaging Discriminators"]),
    ("Differential Diagnosis Matrix", ["Differential Diagnosis Matrix"]),
    ("Similar-Presentation Diseases And Mimic-Aware Comparison", ["Similar-Presentation Diseases And Mimic-Aware Comparison"]),
    (
        "Report Language That Supports Or Argues Against Each Diagnosis",
        ["Report Language That Supports Or Argues Against Each Diagnosis"],
    ),
    ("When Additional Imaging Or Clinical Context Helps", ["When Additional Imaging Or Clinical Context Helps"]),
    ("Natural History And Clinical Course", ["Natural History And Clinical Course"]),
    ("Treatment, Response, And Outcome Context", ["Treatment, Response, And Outcome Context"]),
    ("Guideline-Based Management Context", ["Guideline-Based Management Context"]),
    ("Common Treatment Pathways", ["Common Treatment Pathways"]),
    ("Imaging Appearance After Treatment", ["Imaging Appearance After Treatment"]),
    ("Evidence Of Treatment Response", ["Evidence Of Treatment Response"]),
    (
        "Evidence Of Progression, Recurrence, Or Treatment Failure",
        ["Evidence Of Progression, Recurrence, Or Treatment Failure"],
    ),
    ("Expected Outcomes And Prognostic Factors", ["Expected Outcomes And Prognostic Factors"]),
    ("Statistical Implications Of Treatment And Progression", ["Statistical Implications Of Treatment And Progression"]),
    ("Evidence Of Active Disease, Progression, Or Recurrence", ["Evidence Of Active Disease, Progression, Or Recurrence"]),
    ("Stable Or Chronic Residual Findings", ["Stable Or Chronic Residual Findings"]),
    ("Improvement, Treatment Response, Or Resolution", ["Improvement, Treatment Response, Or Resolution"]),
    ("Serial Imaging Assessment And Interval Change", ["Serial Imaging Assessment And Interval Change"]),
    ("Clinical Endpoints", ["Clinical Endpoints"]),
    ("Imaging, Biomarker, And Measurement Endpoints", ["Imaging, Biomarker, And Measurement Endpoints"]),
    ("Common Covariates And Confounders", ["Common Covariates And Confounders"]),
    ("Clinical Covariates", ["Clinical Covariates"]),
    ("Imaging Covariates", ["Imaging Covariates"]),
    ("Treatment And Temporal Confounders", ["Treatment And Temporal Confounders"]),
    ("Acquisition And Protocol Confounders", ["Acquisition And Protocol Confounders"]),
    ("Research Design Implications", ["Research Design Implications"]),
    ("Statistical Implications", ["Statistical Implications"]),
    ("Missing Information To Ask For", ["Missing Information To Ask For"]),
    ("Claim Boundaries", ["Safety And Claim Boundaries", "Expert Use And Claim Boundaries"]),
    ("Related Disease Files", ["Related Disease Files"]),
    ("Related Statistical Method Files", ["Related Statistical Method Files"]),
    ("Authoritative Sources", ["Authoritative Sources"]),
    ("Notes For Skill Authors", ["Notes For Skill Authors"]),
]


def disease_template_check(
    disease: str | None = None,
    *,
    disease_dir: str | Path | None = None,
    template_dir: str | Path | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    disease_root = Path(disease_dir) if disease_dir else packaged_disease_dir()
    if disease_dir is None and not disease_root.exists():
        disease_root = default_disease_dir()
    template_root = Path(template_dir) if template_dir else default_template_dir()
    disease_template = template_root / "disease.md.tmpl"
    template_headings = headings_from_file(disease_template)
    expected_template_headings = [
        heading["text"]
        for heading in template_headings
        if heading["level"] in {2, 3} and not str(heading["text"]).strip().startswith("{{")
    ]
    expected_files = [
        "disease.md.tmpl",
        "disease-research-plan.md.tmpl",
        "disease-review-criteria.md.tmpl",
        "disease-figure-evidence.md.tmpl",
        "disease.sources.schema.json",
        "disease.figures.schema.json",
    ]
    template_missing = [name for name in expected_files if not (template_root / name).exists()]

    if disease:
        markdown_files = [disease_root / f"{slug_text(disease)}.md"]
    else:
        markdown_files = chapter_markdown_files(disease_root)

    results: list[dict[str, Any]] = []
    for markdown_path in markdown_files:
        slug = markdown_path.stem
        checks: list[dict[str, Any]] = []

        def add_check(category: str, ok: bool, message: str, *, required: bool = True) -> None:
            checks.append(
                {
                    "category": category,
                    "ok": ok,
                    "required": required,
                    "message": message,
                }
            )

        if not markdown_path.exists():
            add_check("chapter_exists", False, f"missing disease chapter {repo_relative(markdown_path)}")
            results.append(
                {
                    "disease": slug,
                    "ok": False,
                    "markdown_path": repo_relative(markdown_path),
                    "checks": checks,
                    "missing_required_sections": [],
                    "strict_missing_sections": [],
                }
            )
            continue

        markdown = markdown_path.read_text(encoding="utf-8-sig")
        headings = markdown_headings(markdown)
        missing_required = [
            label
            for label, options in DISEASE_TEMPLATE_SECTION_GROUPS
            if not has_any_heading(headings, options)
        ]
        add_check(
            "template_headings",
            not missing_required,
            "required conceptual headings present"
            if not missing_required
            else f"missing required conceptual headings: {', '.join(missing_required)}",
        )

        longitudinal_headings = section_headings(headings, start="What To Look For", end="Primary Imaging Modality")
        add_check(
            "longitudinal_what_to_look_for",
            len(longitudinal_headings) >= 4,
            f"{len(longitudinal_headings)} longitudinal or report-language subsections found between What To Look For and Primary Imaging Modality",
        )

        strict_missing = [
            expected
            for expected in expected_template_headings
            if not has_heading(headings, expected)
        ]
        add_check(
            "strict_template_heading_match",
            not strict_missing,
            "all template headings match exactly"
            if not strict_missing
            else f"missing exact template headings: {', '.join(strict_missing)}",
            required=strict,
        )

        source_ok, source_message, _source_payload = validate_json_manifest(
            disease_root / f"{slug}.sources.json",
            "sources",
        )
        add_check("source_manifest", source_ok, source_message)

        figure_ok, figure_message, figure_payload = validate_json_manifest(
            disease_root / f"{slug}.figures.json",
            "figures",
        )
        add_check("figure_manifest", figure_ok, figure_message)

        local_figure_ok, local_figure_message = local_figure_path_status(disease_root, figure_payload)
        add_check("local_figure_paths", local_figure_ok, local_figure_message, required=False)

        supporting_artifacts = [
            disease_root / f"{slug}.research-plan.md",
            disease_root / f"{slug}.research-plan.backtest.md",
            disease_root / f"{slug}.source-review.md",
            disease_root / f"{slug}.review.md",
            disease_root / f"{slug}.build-retrospective.md",
        ]
        present_artifacts = [repo_relative(path) for path in supporting_artifacts if path.exists()]
        add_check(
            "supporting_artifacts",
            bool(present_artifacts),
            f"{len(present_artifacts)} supporting artifacts found",
            required=False,
        )

        add_check(
            "template_directory",
            not template_missing,
            "clinical-statistical-expert templates are packaged with the skill"
            if not template_missing
            else f"missing packaged templates: {', '.join(template_missing)}",
        )

        required_ok = all(check["ok"] for check in checks if check["required"])
        results.append(
            {
                "disease": slug,
                "ok": required_ok,
                "markdown_path": repo_relative(markdown_path),
                "checks": checks,
                "missing_required_sections": missing_required,
                "strict_missing_sections": strict_missing,
                "supporting_artifacts": present_artifacts,
            }
        )

    return {
        "ok": bool(results) and all(result["ok"] for result in results),
        "strict": strict,
        "checked": len(results),
        "disease_dir": repo_relative(disease_root),
        "template_dir": repo_relative(template_root),
        "template_path": repo_relative(disease_template),
        "template_missing_files": template_missing,
        "results": results,
    }
