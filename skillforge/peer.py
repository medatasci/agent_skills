from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
from urllib.parse import urlparse
from urllib.request import url2pathname, urlopen

from .catalog import (
    CATALOG_SKILLS_DIR,
    REPO_ROOT,
    SKILLS_DIR,
    as_list,
    as_text,
    build_search_index,
    discovery_metadata_from_validation,
    generate_static_catalog,
    infer_tags,
    skill_checksum,
    skill_files,
    summary_from_metadata,
    utc_now,
    write_json,
)
from .filesystem import copy_tree, is_transient_path, remove_tree
from .install import resolve_install_dir
from .validate import validate_skill


PEER_CATALOGS_PATH = REPO_ROOT / "peer-catalogs.json"
DEFAULT_PEER_TTL_HOURS = 24
GENERIC_PEER_TERMS = {
    "agent",
    "agents",
    "catalog",
    "catalogs",
    "find",
    "for",
    "help",
    "helping",
    "install",
    "marketplace",
    "skill",
    "skills",
    "task",
    "tasks",
    "workflow",
    "workflows",
}


@dataclass
class PeerRepo:
    peer: dict
    repo_path: Path
    commit: str
    fetched_at: str
    stale: bool = False
    error: str | None = None


def cache_root(cache_dir: str | Path | None = None) -> Path:
    return Path(cache_dir or os.environ.get("SKILLFORGE_CACHE_DIR", REPO_ROOT / ".skillforge" / "cache")).expanduser()


def normalize_peer(peer: dict) -> dict:
    normalized = dict(peer)
    peer_id = as_text(normalized.get("id"))
    display_name = as_text(normalized.get("display_name")) or as_text(normalized.get("name")) or peer_id
    adapter = as_text(normalized.get("adapter")) or as_text(normalized.get("kind")) or "github-skill-repo"
    catalog_url = normalized.get("catalog_url", normalized.get("index_url"))
    ttl_raw = normalized.get("ttl_hours", DEFAULT_PEER_TTL_HOURS)
    try:
        ttl_hours = int(ttl_raw)
    except (TypeError, ValueError):
        ttl_hours = DEFAULT_PEER_TTL_HOURS

    if not as_list(normalized.get("supported_formats")):
        if "static" in adapter or "catalog-adapter" in adapter or catalog_url:
            supported_formats = ["skills.json", ".well-known/agent-skills/index.json"]
        else:
            supported_formats = ["skills/<skill-id>/SKILL.md"]
    else:
        supported_formats = as_list(normalized.get("supported_formats"))

    normalized.update(
        {
            "display_name": display_name,
            "name": as_text(normalized.get("name")) or display_name,
            "publisher": as_text(normalized.get("publisher")) or "unknown",
            "kind": as_text(normalized.get("kind")) or adapter,
            "adapter": adapter,
            "source_url": normalized.get("source_url"),
            "repo": normalized.get("repo"),
            "catalog_url": catalog_url,
            "index_url": catalog_url,
            "default_enabled": normalized.get("default_enabled", True),
            "reliability": as_text(normalized.get("reliability")) or "unknown",
            "trust_notes": as_text(normalized.get("trust_notes"))
            or as_text(normalized.get("notes"))
            or "Discovery source only; not a trust endorsement.",
            "notes": as_text(normalized.get("notes"))
            or as_text(normalized.get("trust_notes"))
            or "Discovery source only; not a trust endorsement.",
            "ttl_hours": ttl_hours,
            "supported_formats": supported_formats,
            "categories": as_list(normalized.get("categories")),
            "domains": as_list(normalized.get("domains")),
        }
    )
    return normalized


def load_peer_catalogs(path: str | Path | None = None) -> list[dict]:
    catalog_path = Path(path).expanduser() if path else PEER_CATALOGS_PATH
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    return [normalize_peer(peer) for peer in data.get("peers", [])]


def find_peer(peer_id: str, peers: list[dict] | None = None) -> dict:
    peer_list = [normalize_peer(peer) for peer in peers] if peers is not None else load_peer_catalogs()
    for peer in peer_list:
        if peer.get("id") == peer_id:
            return peer
    raise KeyError(f"Peer catalog not found: {peer_id}")


def text_score(query: str, values: list[str], *, ignore_terms: set[str] | None = None) -> int:
    terms = re.findall(r"[a-z0-9]+", query.lower().replace("-", " "))
    if ignore_terms:
        terms = [term for term in terms if term not in ignore_terms]
    haystack = " ".join(as_text(value) for value in values).lower().replace("-", " ")
    score = 0
    for term in terms:
        if term in haystack:
            score += 1
    return score


def peer_score(query: str, peer: dict) -> int:
    return text_score(
        query,
        [
            peer.get("id", ""),
            peer.get("name", ""),
            peer.get("display_name", ""),
            peer.get("publisher", ""),
            peer.get("repo", ""),
            peer.get("source_url", ""),
            peer.get("catalog_url", ""),
            peer.get("adapter", ""),
            peer.get("kind", ""),
            " ".join(as_list(peer.get("categories"))),
            " ".join(as_list(peer.get("domains"))),
            peer.get("notes", ""),
            peer.get("trust_notes", ""),
        ],
        ignore_terms=GENERIC_PEER_TERMS,
    )


def skill_score(query: str, skill: dict) -> int:
    score = text_score(
        query,
        [skill.get("id", ""), skill.get("name", ""), skill.get("description", "")],
        ignore_terms=GENERIC_PEER_TERMS,
    )
    if query.lower() == skill.get("id", "").lower():
        score += 20
    return score


def source_catalog_metadata(peer: dict) -> dict:
    return {
        "id": peer["id"],
        "name": peer.get("display_name") or peer.get("name"),
        "publisher": peer.get("publisher"),
        "kind": peer.get("kind"),
        "adapter": peer.get("adapter"),
        "source_url": peer.get("source_url"),
        "repo": peer.get("repo"),
        "catalog_url": peer.get("catalog_url"),
        "reliability": peer.get("reliability"),
        "trust_notes": peer.get("trust_notes"),
        "ttl_hours": peer.get("ttl_hours"),
        "supported_formats": peer.get("supported_formats", []),
        "categories": peer.get("categories", []),
        "domains": peer.get("domains", []),
    }


def is_static_catalog_peer(peer: dict) -> bool:
    adapter = as_text(peer.get("adapter")).lower()
    kind = as_text(peer.get("kind")).lower()
    return bool(peer.get("catalog_url")) or adapter in {"static-catalog", "public-catalog-adapter"} or kind == "static_catalog"


def selected_peers(
    query: str,
    *,
    peer_id: str | None = None,
    peers: list[dict] | None = None,
    cache_dir: str | Path | None = None,
) -> list[dict]:
    all_peers = [normalize_peer(peer) for peer in peers] if peers is not None else load_peer_catalogs()
    if peer_id:
        return [find_peer(peer_id, all_peers)]
    matches = [peer for peer in all_peers if peer.get("default_enabled", True) and peer_score(query, peer)]
    cached_root = cache_root(cache_dir) / "peers"
    cached_ids = {path.name for path in cached_root.iterdir() if path.is_dir()} if cached_root.exists() else set()
    matches_by_id = {peer["id"]: peer for peer in matches}
    for peer in all_peers:
        if peer.get("id") in cached_ids:
            matches_by_id[peer["id"]] = peer
    return sorted(matches_by_id.values(), key=lambda item: (-peer_score(query, item), item.get("id", "")))


def run_git(args: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def read_git_head(repo_path: Path) -> str:
    git_dir = repo_path / ".git"
    head_path = git_dir / "HEAD"
    if not head_path.exists():
        raise FileNotFoundError(f"No .git/HEAD found in {repo_path}")
    head = head_path.read_text(encoding="utf-8").strip()
    if head.startswith("ref: "):
        ref = head.removeprefix("ref: ").strip()
        ref_path = git_dir / ref
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
        packed_refs = git_dir / "packed-refs"
        if packed_refs.exists():
            for line in packed_refs.read_text(encoding="utf-8").splitlines():
                if line and not line.startswith("#") and line.endswith(f" {ref}"):
                    return line.split(" ", 1)[0]
        raise FileNotFoundError(f"Git ref {ref} not found in {repo_path}")
    return head


def git_commit(repo_path: Path) -> str:
    try:
        return run_git(["rev-parse", "HEAD"], cwd=repo_path)
    except Exception:
        return read_git_head(repo_path)


def tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    files = (
        file_path
        for file_path in path.rglob("*")
        if file_path.is_file() and not is_transient_path(file_path, path)
    )
    for file_path in sorted(files):
        rel = file_path.relative_to(path).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def repo_cache_dir(peer: dict, *, cache_dir: str | Path | None = None) -> Path:
    return cache_root(cache_dir) / "peers" / peer["id"] / "repo"


def source_is_local(source: str) -> bool:
    return Path(source).expanduser().exists()


def ensure_peer_repo(
    peer: dict,
    *,
    refresh: bool = False,
    cache_dir: str | Path | None = None,
) -> PeerRepo:
    repo_path = repo_cache_dir(peer, cache_dir=cache_dir)
    source = peer.get("source_url") or peer.get("repo")
    if not source:
        raise ValueError(f"Peer {peer.get('id')} has no source_url or repo")

    fetched_at = utc_now()
    try:
        if source_is_local(source):
            source_path = Path(source).expanduser().resolve()
            if refresh and repo_path.exists():
                remove_tree(repo_path)
            if not repo_path.exists():
                repo_path.parent.mkdir(parents=True, exist_ok=True)
                copy_tree(source_path, repo_path)
            commit = "local-" + tree_digest(repo_path)[:12]
            return PeerRepo(peer=peer, repo_path=repo_path, commit=commit, fetched_at=fetched_at)

        if repo_path.exists() and refresh:
            run_git(["fetch", "--depth", "1", "origin"], cwd=repo_path)
            try:
                run_git(["pull", "--ff-only"], cwd=repo_path)
            except subprocess.CalledProcessError:
                run_git(["reset", "--hard", "origin/HEAD"], cwd=repo_path)
        elif not repo_path.exists():
            repo_path.parent.mkdir(parents=True, exist_ok=True)
            run_git(["clone", "--depth", "1", source, str(repo_path)])
        commit = git_commit(repo_path)
        return PeerRepo(peer=peer, repo_path=repo_path, commit=commit, fetched_at=fetched_at)
    except Exception as exc:
        if repo_path.exists():
            commit = "unknown"
            try:
                commit = git_commit(repo_path)
            except Exception:
                pass
            return PeerRepo(peer=peer, repo_path=repo_path, commit=commit, fetched_at=fetched_at, stale=True, error=str(exc))
        raise


def iter_peer_skills(repo_path: Path) -> list[dict]:
    skills_root = repo_path / "skills"
    if not skills_root.exists():
        return []
    skills: list[dict] = []
    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        validation = validate_skill(skill_dir)
        if validation.ok:
            skills.append(
                {
                    "id": as_text(validation.metadata["name"]),
                    "name": as_text(validation.metadata["name"]),
                    "description": as_text(validation.metadata["description"]),
                    "path": skill_dir.relative_to(repo_path).as_posix(),
                    "warnings": validation.warnings,
                }
            )
    return skills


def search_cache_path(
    query: str,
    *,
    peer_id: str | None,
    cache_dir: str | Path | None = None,
) -> Path:
    key = json.dumps({"query": query, "peer": peer_id or "auto"}, sort_keys=True)
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
    return cache_root(cache_dir) / "search" / f"{digest}.json"


def cache_is_fresh(path: Path, ttl_hours: int) -> bool:
    if not path.exists():
        return False
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return datetime.now(timezone.utc) - modified <= timedelta(hours=ttl_hours)


def static_catalog_cache_path(peer: dict, *, cache_dir: str | Path | None = None) -> Path:
    return cache_root(cache_dir) / "static" / peer["id"] / "catalog.json"


def path_from_file_uri(location: str) -> Path:
    parsed = urlparse(location)
    path_text = parsed.path
    if parsed.netloc and parsed.netloc.lower() != "localhost":
        path_text = f"//{parsed.netloc}{path_text}"
    return Path(url2pathname(path_text))


def read_json_location(location: str) -> dict:
    path = Path(location).expanduser()
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    if location.startswith("file://"):
        return json.loads(path_from_file_uri(location).read_text(encoding="utf-8"))
    if location.startswith(("http://", "https://")):
        with urlopen(location, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    raise FileNotFoundError(f"Static catalog not found: {location}")


def load_static_catalog(
    peer: dict,
    *,
    refresh: bool = False,
    cache_dir: str | Path | None = None,
) -> tuple[dict, dict]:
    location = as_text(peer.get("catalog_url") or peer.get("index_url") or peer.get("source_url"))
    if not location:
        raise ValueError(f"Peer {peer.get('id')} has no catalog_url, index_url, or source_url")

    cache_path = static_catalog_cache_path(peer, cache_dir=cache_dir)
    ttl_hours = int(peer.get("ttl_hours") or DEFAULT_PEER_TTL_HOURS)
    local_path = path_from_file_uri(location) if location.startswith("file://") else Path(location).expanduser()
    if local_path.exists():
        payload = read_json_location(location)
        return payload, {
            "cache_status": "local",
            "cache_path": str(local_path),
            "stale": False,
            "fetched_at": utc_now(),
            "error": None,
        }

    if not refresh and cache_is_fresh(cache_path, ttl_hours):
        return json.loads(cache_path.read_text(encoding="utf-8")), {
            "cache_status": "hit",
            "cache_path": str(cache_path),
            "stale": False,
            "fetched_at": utc_now(),
            "error": None,
        }

    try:
        payload = read_json_location(location)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return payload, {
            "cache_status": "refresh" if refresh else "miss",
            "cache_path": str(cache_path),
            "stale": False,
            "fetched_at": utc_now(),
            "error": None,
        }
    except Exception as exc:
        if cache_path.exists():
            return json.loads(cache_path.read_text(encoding="utf-8")), {
                "cache_status": "stale",
                "cache_path": str(cache_path),
                "stale": True,
                "fetched_at": utc_now(),
                "error": str(exc),
            }
        raise


def normalize_static_skill(raw: dict) -> dict:
    skill_id = as_text(raw.get("id") or raw.get("name"))
    name = as_text(raw.get("name")) or skill_id
    description = (
        as_text(raw.get("description"))
        or as_text(raw.get("short_description"))
        or as_text(raw.get("title"))
    )
    source = raw.get("source", {}) if isinstance(raw.get("source"), dict) else {}
    checksum = raw.get("checksum") if isinstance(raw.get("checksum"), dict) else {}
    return {
        "id": skill_id,
        "name": name,
        "title": raw.get("title"),
        "description": description,
        "path": as_text(source.get("path") or raw.get("path") or raw.get("url") or skill_id),
        "warnings": as_list(raw.get("warnings")),
        "checksum": checksum,
        "url": raw.get("url") or source.get("url"),
        "updated_at": raw.get("updated_at"),
    }


def iter_static_catalog_skills(payload: dict) -> list[dict]:
    raw_skills = payload.get("skills", [])
    if not isinstance(raw_skills, list):
        return []
    skills: list[dict] = []
    for raw in raw_skills:
        if not isinstance(raw, dict):
            continue
        skill = normalize_static_skill(raw)
        if skill["id"] and skill["description"]:
            skills.append(skill)
    return skills


def peer_search(
    query: str,
    *,
    peer_id: str | None = None,
    refresh: bool = False,
    limit: int = 10,
    ttl_hours: int = 24,
    peers: list[dict] | None = None,
    cache_dir: str | Path | None = None,
) -> dict:
    cache_path = search_cache_path(query, peer_id=peer_id, cache_dir=cache_dir)
    if not refresh and cache_is_fresh(cache_path, ttl_hours):
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        payload["cache"] = {"status": "hit", "path": str(cache_path)}
        return payload

    results: list[dict] = []
    errors: list[dict] = []
    for peer in selected_peers(query, peer_id=peer_id, peers=peers, cache_dir=cache_dir):
        try:
            if is_static_catalog_peer(peer):
                static_payload, cache_state = load_static_catalog(peer, refresh=refresh, cache_dir=cache_dir)
                catalog_timestamp = static_payload.get("generated_at") or static_payload.get("updated_at")
                for skill in iter_static_catalog_skills(static_payload):
                    score = skill_score(query, skill) + peer_score(query, peer)
                    if not score:
                        continue
                    results.append(
                        {
                            **skill,
                            "score": score,
                            "source_catalog": source_catalog_metadata(peer),
                            "source": {
                                "type": "peer-static-catalog",
                                "peer_id": peer["id"],
                                "repo": peer.get("repo"),
                                "url": skill.get("url") or peer.get("catalog_url") or peer.get("source_url"),
                                "path": skill["path"],
                                "commit": None,
                                "catalog_timestamp": catalog_timestamp,
                                "fetched_at": cache_state["fetched_at"],
                                "stale": cache_state["stale"],
                                "cache_status": cache_state["cache_status"],
                                "cache_path": cache_state["cache_path"],
                                "checksum": skill.get("checksum"),
                            },
                        }
                    )
                if cache_state.get("error"):
                    errors.append({"peer_id": peer["id"], "error": cache_state["error"], "stale": True})
                continue

            repo = ensure_peer_repo(peer, refresh=refresh, cache_dir=cache_dir)
            for skill in iter_peer_skills(repo.repo_path):
                score = skill_score(query, skill) + peer_score(query, peer)
                if not score:
                    continue
                skill_dir = repo.repo_path / skill["path"]
                results.append(
                    {
                        **skill,
                        "score": score,
                        "checksum": {
                            "algorithm": "sha256-tree",
                            "value": skill_checksum(skill_dir),
                        },
                        "source_catalog": source_catalog_metadata(peer),
                        "source": {
                            "type": "peer-catalog",
                            "peer_id": peer["id"],
                            "repo": peer.get("repo"),
                            "url": f"{peer.get('source_url', '').rstrip('/')}/tree/{repo.commit}/{skill['path']}",
                            "path": skill["path"],
                            "commit": repo.commit,
                            "fetched_at": repo.fetched_at,
                            "stale": repo.stale,
                            "cache_status": "stale" if repo.stale else "fresh",
                            "cache_path": str(repo.repo_path),
                        },
                    }
                )
            if repo.error:
                errors.append({"peer_id": peer["id"], "error": repo.error, "stale": True})
        except Exception as exc:
            errors.append({"peer_id": peer.get("id"), "error": str(exc), "stale": False})

    results.sort(key=lambda item: (-item["score"], item["source_catalog"]["id"], item["id"]))
    payload = {
        "query": query,
        "results": results[:limit],
        "errors": errors,
        "cache": {"status": "refresh" if refresh else "miss", "path": str(cache_path)},
        "generated_at": utc_now(),
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def find_peer_skill(
    skill_id: str,
    *,
    peer_id: str,
    refresh: bool = False,
    peers: list[dict] | None = None,
    cache_dir: str | Path | None = None,
) -> tuple[PeerRepo, dict, Path]:
    peer = find_peer(peer_id, peers)
    repo = ensure_peer_repo(peer, refresh=refresh, cache_dir=cache_dir)
    skill_path = repo.repo_path / "skills" / skill_id
    if not (skill_path / "SKILL.md").exists():
        matches = [skill for skill in iter_peer_skills(repo.repo_path) if skill["id"] == skill_id]
        if not matches:
            raise FileNotFoundError(f"Skill {skill_id} not found in peer {peer_id}")
        skill_path = repo.repo_path / matches[0]["path"]
    validation = validate_skill(skill_path)
    if not validation.ok:
        raise ValueError("; ".join(validation.errors))
    return repo, {
        "id": as_text(validation.metadata["name"]),
        "name": as_text(validation.metadata["name"]),
        "description": as_text(validation.metadata["description"]),
        "path": skill_path.relative_to(repo.repo_path).as_posix(),
        "warnings": validation.warnings,
    }, skill_path


def materialize_peer_skill(
    skill_id: str,
    *,
    peer_id: str,
    refresh: bool = False,
    peers: list[dict] | None = None,
    cache_dir: str | Path | None = None,
) -> dict:
    repo, skill, source_path = find_peer_skill(skill_id, peer_id=peer_id, refresh=refresh, peers=peers, cache_dir=cache_dir)
    dest = cache_root(cache_dir) / "peers" / peer_id / repo.commit / "skills" / skill["id"]
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy_tree(source_path, dest)
    provenance = {
        "peer_id": peer_id,
        "source_catalog": source_catalog_metadata(repo.peer),
        "source": {
            "type": "peer-catalog",
            "path": skill["path"],
            "url": f"{repo.peer.get('source_url', '').rstrip('/')}/tree/{repo.commit}/{skill['path']}",
            "commit": repo.commit,
            "fetched_at": repo.fetched_at,
            "stale": repo.stale,
        },
        "cache_path": str(dest),
        "checksum": {
            "algorithm": "sha256-tree",
            "value": skill_checksum(dest),
        },
        "warnings": skill["warnings"],
    }
    provenance_path = cache_root(cache_dir) / "peers" / peer_id / repo.commit / "provenance" / f"{skill['id']}.json"
    write_json(provenance_path, provenance)
    return {**skill, "cache_path": str(dest), "provenance": provenance}


def install_peer_skill(
    skill_id: str,
    *,
    peer_id: str,
    scope: str = "global",
    project: str | Path | None = None,
    force: bool = False,
    refresh: bool = False,
    peers: list[dict] | None = None,
    cache_dir: str | Path | None = None,
) -> dict:
    materialized = materialize_peer_skill(skill_id, peer_id=peer_id, refresh=refresh, peers=peers, cache_dir=cache_dir)
    source = Path(materialized["cache_path"])
    validation = validate_skill(source)
    if not validation.ok:
        raise ValueError("; ".join(validation.errors))
    expected = materialized["provenance"]["checksum"]["value"]
    actual = skill_checksum(source)
    if actual != expected:
        raise ValueError(f"Checksum mismatch for {skill_id}: expected {expected}, got {actual}")

    install_root = resolve_install_dir(scope, project)
    target = install_root / skill_id
    if target.exists():
        if not force:
            raise FileExistsError(f"Skill already installed: {target}. Use --force to replace it.")
        remove_tree(target)
    install_root.mkdir(parents=True, exist_ok=True)
    copy_tree(source, target)
    return {
        "installed": skill_id,
        "scope": scope,
        "target": str(target),
        "source_catalog": materialized["provenance"]["source_catalog"],
        "source": materialized["provenance"]["source"],
        "cache_path": materialized["cache_path"],
        "warnings": validation.warnings,
    }


def peer_metadata(materialized: dict, *, owner: str) -> dict:
    source = Path(materialized["cache_path"])
    validation = validate_skill(source)
    if not validation.ok:
        raise ValueError("; ".join(validation.errors))
    name = as_text(validation.metadata["name"])
    description = as_text(validation.metadata["description"])
    provenance = materialized["provenance"]
    discovery = discovery_metadata_from_validation(validation, fallback_tags=infer_tags(name, description))
    metadata = {
        "schema_version": "0.1",
        "id": name,
        "name": name,
        "description": description,
        "owner": owner,
        "tags": discovery.pop("tags", infer_tags(name, description)),
        "source": {
            **provenance["source"],
            "peer_id": provenance["peer_id"],
            "repo": provenance["source_catalog"].get("repo"),
        },
        "catalog_path": (Path("skills") / name).as_posix(),
        "updated_at": utc_now(),
        "checksum": {
            "algorithm": "sha256-tree",
            "value": skill_checksum(source),
        },
        "codex": {
            "install_scopes": ["global", "project"],
            "global_install_command": f"python -m skillforge install {name} --scope global",
            "project_install_command": f"python -m skillforge install {name} --scope project --project .",
        },
        "files": skill_files(source),
        "warnings": validation.warnings,
    }
    metadata.update(discovery)
    return metadata


def upsert_catalog_summary(metadata: dict) -> dict:
    catalog_path = REPO_ROOT / "catalog" / "skills.json"
    if catalog_path.exists():
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    else:
        catalog = {"schema_version": "0.1", "marketplace": "SkillForge", "skills": []}
    summary = summary_from_metadata(metadata)
    skills = [skill for skill in catalog.get("skills", []) if skill.get("id") != metadata["id"]]
    skills.append(summary)
    catalog["skills"] = sorted(skills, key=lambda item: item["id"])
    catalog["generated_at"] = metadata["updated_at"]
    write_json(catalog_path, catalog)
    search_index = build_search_index(catalog)
    generate_static_catalog(catalog, search_index)
    return catalog


def import_peer_skill(
    skill_id: str,
    *,
    peer_id: str,
    owner: str,
    force: bool = False,
    refresh: bool = False,
    peers: list[dict] | None = None,
    cache_dir: str | Path | None = None,
) -> dict:
    materialized = materialize_peer_skill(skill_id, peer_id=peer_id, refresh=refresh, peers=peers, cache_dir=cache_dir)
    source = Path(materialized["cache_path"])
    dest = SKILLS_DIR / skill_id
    if dest.exists():
        if not force:
            raise FileExistsError(f"Skill already exists: {dest}. Use --force to replace it.")
        remove_tree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    copy_tree(source, dest)
    metadata = peer_metadata(materialized, owner=owner)
    write_json(CATALOG_SKILLS_DIR / f"{skill_id}.json", metadata)
    upsert_catalog_summary(metadata)
    return metadata


def cache_listing(*, cache_dir: str | Path | None = None) -> dict:
    root = cache_root(cache_dir)
    peers: list[dict] = []
    peers_root = root / "peers"
    if peers_root.exists():
        for peer_dir in sorted(path for path in peers_root.iterdir() if path.is_dir()):
            repo_path = peer_dir / "repo"
            commits = [
                commit.name
                for commit in sorted(path for path in peer_dir.iterdir() if path.is_dir())
                if commit.name != "repo"
            ]
            peers.append(
                {
                    "peer_id": peer_dir.name,
                    "repo_cached": repo_path.exists(),
                    "repo_path": str(repo_path) if repo_path.exists() else None,
                    "skill_cache_commits": commits,
                }
            )
    search_files = sorted((root / "search").glob("*.json")) if (root / "search").exists() else []
    return {"cache_root": str(root), "peers": peers, "search_cache_files": [str(path) for path in search_files]}


def clear_cache(*, peer_id: str | None = None, yes: bool = False, cache_dir: str | Path | None = None) -> dict:
    if not yes:
        raise ValueError("cache clear requires --yes")
    root = cache_root(cache_dir)
    target = root / "peers" / peer_id if peer_id else root
    if target.exists():
        remove_tree(target)
    return {"cleared": str(target)}


def refresh_cache(*, peer_id: str, cache_dir: str | Path | None = None) -> dict:
    repo = ensure_peer_repo(find_peer(peer_id), refresh=True, cache_dir=cache_dir)
    return {"peer_id": peer_id, "repo_path": str(repo.repo_path), "commit": repo.commit, "stale": repo.stale, "error": repo.error}


def peer_diagnostics(
    *,
    peers: list[dict] | None = None,
    cache_dir: str | Path | None = None,
) -> dict:
    peer_list = [normalize_peer(peer) for peer in peers] if peers is not None else load_peer_catalogs()
    ids = [as_text(peer.get("id")) for peer in peer_list]
    id_counts = Counter(ids)
    root = cache_root(cache_dir)
    diagnostics: list[dict] = []

    for peer in peer_list:
        peer_id = as_text(peer.get("id"))
        problems: list[str] = []
        if not peer_id:
            problems.append("missing peer ID")
        if id_counts[peer_id] > 1:
            problems.append("duplicate peer ID")
        if not (peer.get("source_url") or peer.get("repo") or peer.get("catalog_url")):
            problems.append("missing source_url, repo, or catalog_url")
        if not peer.get("adapter"):
            problems.append("missing adapter")
        if is_static_catalog_peer(peer) and not (peer.get("catalog_url") or peer.get("index_url") or peer.get("source_url")):
            problems.append("static peer has no catalog URL")

        repo_path = repo_cache_dir(peer, cache_dir=cache_dir)
        static_cache = static_catalog_cache_path(peer, cache_dir=cache_dir)
        cache_path = static_cache if is_static_catalog_peer(peer) else repo_path
        cache_exists = cache_path.exists()
        modified_at = None
        stale = None
        if cache_exists:
            modified = datetime.fromtimestamp(cache_path.stat().st_mtime, tz=timezone.utc)
            modified_at = modified.replace(microsecond=0).isoformat().replace("+00:00", "Z")
            stale = datetime.now(timezone.utc) - modified > timedelta(hours=int(peer.get("ttl_hours") or DEFAULT_PEER_TTL_HOURS))
            if stale:
                problems.append("cache is stale")

        diagnostics.append(
            {
                "id": peer_id,
                "display_name": peer.get("display_name"),
                "publisher": peer.get("publisher"),
                "adapter": peer.get("adapter"),
                "kind": peer.get("kind"),
                "default_enabled": peer.get("default_enabled"),
                "reliability": peer.get("reliability"),
                "trust_notes": peer.get("trust_notes"),
                "ttl_hours": peer.get("ttl_hours"),
                "supported_formats": peer.get("supported_formats", []),
                "source_url": peer.get("source_url"),
                "repo": peer.get("repo"),
                "catalog_url": peer.get("catalog_url"),
                "cache": {
                    "path": str(cache_path),
                    "exists": cache_exists,
                    "modified_at": modified_at,
                    "stale": stale,
                },
                "problems": problems,
                "ok": not problems,
            }
        )

    return {
        "ok": all(peer["ok"] for peer in diagnostics),
        "cache_root": str(root),
        "peer_count": len(peer_list),
        "duplicate_peer_ids": sorted(peer_id for peer_id, count in id_counts.items() if peer_id and count > 1),
        "peers": diagnostics,
    }
