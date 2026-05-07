from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
from typing import Any

from .catalog import REPO_ROOT


SCHEMA_VERSION = "1.0"
LOCAL_ALLOWED_REUSE_STATUSES = {"ok-to-embed"}
KNOWN_REUSE_STATUSES = {"ok-to-embed", "link-only", "needs-review", "private-review"}


def slug_text(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return text or "figure"


def utc_today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def default_manifest_path(disease: str) -> Path:
    return REPO_ROOT / "docs" / "clinical-statistical-expert" / "diseases" / f"{slug_text(disease)}.figures.json"


def default_assets_dir(disease: str) -> Path:
    return REPO_ROOT / "docs" / "clinical-statistical-expert" / "assets" / "diseases" / slug_text(disease) / "figures"


def load_manifest(path: Path, disease: str) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "disease": disease, "figures": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"schema_version": SCHEMA_VERSION, "disease": disease, "figures": data}
    if not isinstance(data, dict):
        raise ValueError(f"Figure manifest must be a JSON object or list: {path}")
    figures = data.get("figures")
    if not isinstance(figures, list):
        data["figures"] = []
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("disease", disease)
    return data


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def markdown_snippet(entry: dict[str, Any], *, disease_markdown_path: Path | None = None) -> str:
    figure_label = entry.get("figure_label") or entry["id"]
    clinical_point = entry.get("clinical_point") or "Figure evidence."
    license_text = entry.get("license") or "license not recorded"
    source_title = entry.get("source_title") or "source"
    source_url = entry.get("source_url") or entry.get("figure_url") or ""
    local_path = entry.get("local_path")

    if local_path:
        image_path = Path(local_path)
        if not image_path.is_absolute():
            image_path = REPO_ROOT / image_path
        if disease_markdown_path:
            try:
                image_ref = image_path.resolve().relative_to(disease_markdown_path.parent.resolve()).as_posix()
            except ValueError:
                try:
                    image_ref = image_path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
                except ValueError:
                    image_ref = image_path.resolve().as_posix()
        else:
            image_ref = local_path
        source = f"[{source_title}]({source_url})" if source_url else source_title
        return (
            f"![{clinical_point}]({image_ref})\n\n"
            f"Figure: {clinical_point} Source: {source}. "
            f"Figure reference: {figure_label}. License: {license_text}."
        )

    link = entry.get("figure_url") or source_url
    if link:
        return (
            f"Figure evidence: [{figure_label}]({link}) supports: {clinical_point}. "
            f"Image is linked externally because reuse status is `{entry.get('reuse_status')}`. "
            f"License: {license_text}."
        )
    return (
        f"Figure evidence: {figure_label} supports: {clinical_point}. "
        f"No local image or external URL is recorded. License: {license_text}."
    )


def record_figure_evidence(
    *,
    disease: str,
    figure_id: str,
    source_title: str,
    source_url: str,
    figure_label: str,
    clinical_point: str,
    license_text: str,
    reuse_status: str,
    supports_sections: list[str] | None = None,
    figure_url: str | None = None,
    image_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    assets_dir: str | Path | None = None,
    attribution: str | None = None,
    notes: str | None = None,
    date_accessed: str | None = None,
) -> dict[str, Any]:
    disease = disease.strip()
    figure_id = slug_text(figure_id)
    reuse_status = reuse_status.strip().lower()
    if reuse_status not in KNOWN_REUSE_STATUSES:
        raise ValueError(f"Unsupported reuse status: {reuse_status}")

    manifest = Path(manifest_path) if manifest_path else default_manifest_path(disease)
    asset_root = Path(assets_dir) if assets_dir else default_assets_dir(disease)
    warnings: list[str] = []
    copied = False
    local_path: str | None = None

    if image_path and reuse_status in LOCAL_ALLOWED_REUSE_STATUSES:
        source_image = Path(image_path)
        if not source_image.exists() or not source_image.is_file():
            raise FileNotFoundError(f"Image path does not exist or is not a file: {source_image}")
        suffix = source_image.suffix.lower() or ".png"
        asset_root.mkdir(parents=True, exist_ok=True)
        target = asset_root / f"{figure_id}{suffix}"
        shutil.copy2(source_image, target)
        copied = True
        local_path = repo_relative(target)
    elif image_path:
        warnings.append(
            f"Image was not copied because reuse_status is {reuse_status}; record a source or figure URL instead."
        )
    elif reuse_status in LOCAL_ALLOWED_REUSE_STATUSES:
        warnings.append("reuse_status allows local storage, but no image_path was provided.")

    if reuse_status != "ok-to-embed" and not (figure_url or source_url):
        warnings.append("link-only or review-needed figure evidence should include a source_url or figure_url.")

    entry = {
        "id": figure_id,
        "disease": disease,
        "source_title": source_title.strip(),
        "source_url": source_url.strip(),
        "figure_label": figure_label.strip(),
        "figure_url": (figure_url or "").strip(),
        "license": license_text.strip(),
        "reuse_status": reuse_status,
        "local_path": local_path,
        "supports_sections": supports_sections or [],
        "clinical_point": clinical_point.strip(),
        "attribution": (attribution or "").strip(),
        "notes": (notes or "").strip(),
        "date_accessed": date_accessed or utc_today(),
    }

    payload = load_manifest(manifest, disease)
    figures = [figure for figure in payload["figures"] if figure.get("id") != figure_id]
    figures.append(entry)
    payload["figures"] = sorted(figures, key=lambda figure: figure.get("id", ""))
    write_manifest(manifest, payload)

    disease_markdown = manifest.with_suffix(".md")
    return {
        "ok": True,
        "command": "figure-evidence",
        "copied": copied,
        "manifest_path": repo_relative(manifest),
        "asset_path": local_path,
        "entry": entry,
        "warnings": warnings,
        "markdown_snippet": markdown_snippet(entry, disease_markdown_path=disease_markdown),
    }
