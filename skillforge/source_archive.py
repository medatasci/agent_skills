from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .catalog import REPO_ROOT


SCHEMA_VERSION = "1.0"
KNOWN_CACHE_STATUSES = {
    "cached-local-only",
    "cached-local-only-and-figure-saved-in-repo",
    "downloaded-but-needs-review",
    "downloaded-but-client-challenge",
    "download-failed",
    "url-only",
}


def slug_text(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return text or "source"


def utc_today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def default_manifest_path(disease: str) -> Path:
    return REPO_ROOT / "docs" / "clinical-statistical-expert" / "diseases" / f"{slug_text(disease)}.sources.json"


def default_cache_root(disease: str, date_accessed: str) -> Path:
    return REPO_ROOT / ".skillforge" / "source-cache" / "clinical-statistical-expert" / slug_text(disease) / date_accessed


def load_manifest(path: Path, disease: str) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "disease": disease, "sources": []}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        return {"schema_version": SCHEMA_VERSION, "disease": disease, "sources": data}
    if not isinstance(data, dict):
        raise ValueError(f"Source manifest must be a JSON object or list: {path}")
    sources = data.get("sources")
    if not isinstance(sources, list):
        data["sources"] = []
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("disease", disease)
    return data


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def infer_extension(url: str, content_type: str | None) -> str:
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    if suffix and len(suffix) <= 12:
        return suffix
    content_type = (content_type or "").lower()
    if "pdf" in content_type:
        return ".pdf"
    if "html" in content_type:
        return ".html"
    if "json" in content_type:
        return ".json"
    if "text" in content_type:
        return ".txt"
    return ".bin"


def looks_like_client_challenge(data: bytes, content_type: str | None) -> bool:
    content_type = (content_type or "").lower()
    if "html" not in content_type and b"<html" not in data[:4096].lower():
        return False
    sample = data[:50000].decode("utf-8", errors="ignore").lower()
    challenge_terms = [
        "access denied",
        "captcha",
        "checking your browser",
        "just a moment",
        "client challenge",
        "login required",
        "403 forbidden",
        "http error 403",
        "cloudflare ray id",
        "cf-chl",
        "turnstile",
    ]
    return any(term in sample for term in challenge_terms)


def download_source(url: str, target: Path) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "SkillForge source archive/0.1"})
    with urlopen(request, timeout=30) as response:
        data = response.read()
        content_type = response.headers.get("Content-Type", "")
        final_url = response.geturl()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    checksum = hashlib.sha256(data).hexdigest()
    return {
        "bytes": len(data),
        "checksum_sha256": checksum,
        "content_type": content_type,
        "final_url": final_url,
        "client_challenge": looks_like_client_challenge(data, content_type),
    }


def record_source_archive(
    *,
    disease: str,
    source_id: str,
    title: str,
    url: str,
    source_type: str,
    claim_breadth: str,
    license_text: str = "",
    reuse_status: str = "",
    supported_sections: list[str] | None = None,
    manifest_path: str | Path | None = None,
    cache_root: str | Path | None = None,
    cache_status: str | None = None,
    download: bool = False,
    notes: str | None = None,
    date_accessed: str | None = None,
) -> dict[str, Any]:
    disease = disease.strip()
    source_id = slug_text(source_id)
    date_accessed = date_accessed or utc_today()
    manifest = Path(manifest_path) if manifest_path else default_manifest_path(disease)
    cache_dir = Path(cache_root) if cache_root else default_cache_root(disease, date_accessed)
    warnings: list[str] = []
    local_cache_path: str | None = None
    checksum_sha256 = ""
    byte_count: int | None = None
    content_type = ""
    final_url = ""

    if cache_status and cache_status not in KNOWN_CACHE_STATUSES:
        raise ValueError(f"Unsupported cache status: {cache_status}")

    resolved_cache_status = cache_status or "url-only"
    if download:
        preliminary_target = cache_dir / f"{source_id}.download"
        try:
            download_payload = download_source(url, preliminary_target)
            content_type = download_payload["content_type"]
            extension = infer_extension(download_payload["final_url"] or url, content_type)
            target = cache_dir / f"{source_id}{extension}"
            if target != preliminary_target:
                preliminary_target.replace(target)
            local_cache_path = repo_relative(target)
            checksum_sha256 = download_payload["checksum_sha256"]
            byte_count = download_payload["bytes"]
            final_url = download_payload["final_url"]
            if download_payload["client_challenge"]:
                resolved_cache_status = "downloaded-but-client-challenge"
                warnings.append("Downloaded content appears to be an access-denial, login, captcha, or client-challenge page.")
            else:
                resolved_cache_status = cache_status or "cached-local-only"
        except (OSError, URLError, TimeoutError) as exc:
            resolved_cache_status = "download-failed"
            warnings.append(f"Download failed: {exc}")
            try:
                preliminary_target.unlink(missing_ok=True)
            except OSError:
                pass

    entry = {
        "id": source_id,
        "disease": disease,
        "title": title.strip(),
        "url": url.strip(),
        "final_url": final_url,
        "source_type": source_type.strip(),
        "claim_breadth_supported": claim_breadth.strip(),
        "license": license_text.strip(),
        "reuse_status": reuse_status.strip(),
        "cache_status": resolved_cache_status,
        "local_cache_path": local_cache_path,
        "checksum_sha256": checksum_sha256,
        "bytes": byte_count,
        "content_type": content_type,
        "date_accessed": date_accessed,
        "supported_sections": supported_sections or [],
        "notes": (notes or "").strip(),
        "warnings": warnings,
    }

    payload = load_manifest(manifest, disease)
    sources = [source for source in payload["sources"] if source.get("id") != source_id]
    sources.append(entry)
    payload["sources"] = sorted(sources, key=lambda source: source.get("id", ""))
    write_manifest(manifest, payload)

    ok = resolved_cache_status != "download-failed"
    return {
        "ok": ok,
        "command": "source-archive",
        "manifest_path": repo_relative(manifest),
        "cache_root": repo_relative(cache_dir),
        "entry": entry,
        "warnings": warnings,
    }
