from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import os
import platform
import re
import subprocess
from urllib.parse import urlparse
from urllib.request import Request, url2pathname, urlopen

from .catalog import (
    CATALOG_SKILLS_DIR,
    REPO_ROOT,
    SKILLS_DIR,
    as_list,
    as_text,
    build_search_index,
    discovery_metadata_from_validation,
    first_sentence,
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
DEFAULT_PEER_SEARCH_JOBS = 15
MAX_PEER_SEARCH_JOBS = 15
PEER_SEARCH_CACHE_VERSION = 11
QUERY_EXPANSIONS = {
    "access": {"access", "connect", "connection", "execute", "inspect", "query", "read", "cli", "mcp"},
    "coach": {"coach", "coaching", "guidance", "mentor", "mentoring", "motivation"},
    "coaching": {"coach", "coaching", "guidance", "mentor", "mentoring", "motivation"},
    "connect": {"access", "connect", "connection", "cli", "mcp"},
    "connection": {"access", "connect", "connection", "cli", "mcp"},
    "database": {
        "database",
        "databases",
        "db",
        "postgres",
        "postgresql",
        "sql",
        "mysql",
        "oracle",
        "sqlite",
        "supabase",
        "schema",
        "schemas",
        "table",
        "tables",
        "migration",
        "migrations",
    },
    "databases": {
        "database",
        "databases",
        "db",
        "postgres",
        "postgresql",
        "sql",
        "mysql",
        "oracle",
        "sqlite",
        "supabase",
        "schema",
        "schemas",
        "table",
        "tables",
        "migration",
        "migrations",
    },
    "db": {"database", "databases", "db", "postgres", "postgresql", "sql", "supabase"},
    "management": {"calendar", "manage", "management", "plan", "planning", "priorities", "priority", "productivity", "schedule", "task", "tasks"},
    "motivation": {"coach", "coaching", "focus", "habit", "habits", "motivated", "motivation"},
    "postgres": {"database", "postgres", "postgresql", "sql", "supabase"},
    "postgresql": {"database", "postgres", "postgresql", "sql", "supabase"},
    "query": {"execute", "query", "queries", "read", "select", "sql"},
    "queries": {"execute", "query", "queries", "read", "select", "sql"},
    "sql": {"database", "databases", "postgres", "postgresql", "query", "sql"},
    "supabase": {"database", "postgres", "postgresql", "sql", "supabase", "cli", "mcp"},
    "time": {"calendar", "daily", "day", "deadline", "deadlines", "focus", "schedule", "time"},
}
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
    explicit = cache_dir or os.environ.get("SKILLFORGE_CACHE_DIR")
    if explicit:
        return Path(explicit).expanduser()
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "SkillForge" / "cache"
        return Path.home() / "AppData" / "Local" / "SkillForge" / "cache"
    if platform.system() == "Darwin":
        return Path.home() / "Library" / "Caches" / "skillforge"
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    return Path(xdg_cache).expanduser() / "skillforge" if xdg_cache else Path.home() / ".cache" / "skillforge"


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
    catalog_path = Path(path or os.environ.get("SKILLFORGE_PEER_CATALOGS") or PEER_CATALOGS_PATH).expanduser()
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    return [normalize_peer(peer) for peer in data.get("peers", [])]


def find_peer(peer_id: str, peers: list[dict] | None = None) -> dict:
    peer_list = [normalize_peer(peer) for peer in peers] if peers is not None else load_peer_catalogs()
    for peer in peer_list:
        if peer.get("id") == peer_id:
            return peer
    raise KeyError(f"Peer catalog not found: {peer_id}")


def text_score(query: str, values: list[str], *, ignore_terms: set[str] | None = None) -> int:
    haystack = " ".join(as_text(value) for value in values).lower().replace("-", " ")
    haystack_terms = set(re.findall(r"[a-z0-9]+", haystack))
    score = 0
    for term in query_terms(query, ignore_terms=ignore_terms):
        variants = term_variants(term)
        matches = haystack_terms.intersection(variants)
        if not matches:
            continue
        group_score = 2 if term in haystack_terms else 1
        if len(matches) > 1:
            group_score += min(2, len(matches) - 1)
        score += group_score
    return score


def text_match_count(query: str, values: list[str], *, ignore_terms: set[str] | None = None) -> int:
    haystack = " ".join(as_text(value) for value in values).lower().replace("-", " ")
    haystack_terms = set(re.findall(r"[a-z0-9]+", haystack))
    score = 0
    for variants in query_term_groups(query, ignore_terms=ignore_terms):
        if haystack_terms.intersection(variants):
            score += 1
    return score


def term_variants(term: str) -> set[str]:
    variants = {term}
    if term.endswith("s") and len(term) > 3:
        variants.add(term[:-1])
    if term.endswith("y") and len(term) > 3:
        variants.add(term[:-1] + "ies")
    if term in QUERY_EXPANSIONS:
        variants.update(QUERY_EXPANSIONS[term])
    return variants


def query_term_groups(query: str, *, ignore_terms: set[str] | None = None) -> list[set[str]]:
    terms = re.findall(r"[a-z0-9]+", query.lower().replace("-", " "))
    if ignore_terms:
        terms = [term for term in terms if term not in ignore_terms]
    return [term_variants(term) for term in terms]


def query_terms(query: str, *, ignore_terms: set[str] | None = None) -> list[str]:
    terms = re.findall(r"[a-z0-9]+", query.lower().replace("-", " "))
    if ignore_terms:
        terms = [term for term in terms if term not in ignore_terms]
    return terms


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
        [
            skill.get("id", ""),
            skill.get("name", ""),
            skill.get("description", ""),
            " ".join(as_list(skill.get("tags"))),
            " ".join(as_list(skill.get("categories"))),
            " ".join(as_list(skill.get("search_terms"))),
        ],
        ignore_terms=GENERIC_PEER_TERMS,
    )
    if query.lower() == skill.get("id", "").lower():
        score += 20
    return score


def skill_match_count(query: str, skill: dict) -> int:
    return text_match_count(
        query,
        [
            skill.get("id", ""),
            skill.get("name", ""),
            skill.get("description", ""),
            " ".join(as_list(skill.get("tags"))),
            " ".join(as_list(skill.get("categories"))),
            " ".join(as_list(skill.get("search_terms"))),
        ],
        ignore_terms=GENERIC_PEER_TERMS,
    )


def corpus_search_values(skill: dict) -> list[str]:
    values = [
        skill.get("id", ""),
        skill.get("name", ""),
        skill.get("title", ""),
        skill.get("summary", ""),
        skill.get("description", ""),
        skill.get("short_description", ""),
        skill.get("expanded_description", ""),
        skill.get("skill_text", ""),
        skill.get("readme_text", ""),
    ]
    for field_name in [
        "aliases",
        "categories",
        "tags",
        "tasks",
        "use_when",
        "do_not_use_when",
        "inputs",
        "outputs",
        "examples",
        "related_skills",
        "permissions",
        "search_terms",
    ]:
        values.append(" ".join(as_list(skill.get(field_name))))
    return values


def corpus_match_count(query: str, skill: dict) -> int:
    haystack = " ".join(as_text(value) for value in corpus_search_values(skill)).lower().replace("-", " ")
    haystack_terms = set(re.findall(r"[a-z0-9]+", haystack))
    score = 0
    for variants in query_term_groups(query, ignore_terms=GENERIC_PEER_TERMS):
        if haystack_terms.intersection(variants):
            score += 1
    return score


def corpus_skill_score(query: str, skill: dict) -> int:
    query_lower = query.lower().replace("-", " ").strip()
    score = 0
    weighted_fields = [
        (["id", "name", "title"], 12),
        (["summary", "short_description", "description", "expanded_description"], 8),
        (["aliases", "categories", "tags", "tasks", "use_when", "examples", "search_terms"], 5),
        (["skill_text", "readme_text"], 1),
    ]
    for fields, weight in weighted_fields:
        values: list[str] = []
        for field_name in fields:
            raw_value = skill.get(field_name)
            values.append(" ".join(as_list(raw_value)) if isinstance(raw_value, list) else as_text(raw_value))
        haystack = " ".join(values).lower().replace("-", " ")
        haystack_terms = set(re.findall(r"[a-z0-9]+", haystack))
        if query_lower and query_lower in haystack:
            score += weight * 2
        for variants in query_term_groups(query, ignore_terms=GENERIC_PEER_TERMS):
            if haystack_terms.intersection(variants):
                score += weight
    return score


def minimum_skill_score(query: str) -> int:
    groups = query_term_groups(query, ignore_terms=GENERIC_PEER_TERMS)
    if len(groups) <= 1:
        return 1
    if len(groups) == 2:
        return 2
    return 3


def classify_peer_error(message: str) -> dict:
    lowered = message.lower()
    system = platform.system() or "unknown"
    if any(
        marker in lowered
        for marker in [
            "could not connect to server",
            "failed to connect",
            "could not resolve host",
            "connection timed out",
            "operation timed out",
            "network is unreachable",
            "proxy",
            "ssl certificate problem",
            "tls",
        ]
    ):
        return {
            "kind": "network_blocked",
            "platform": system,
            "remediation": "Allow GitHub/network access, configure proxy or TLS certificates, or use an existing cache/static peer catalog.",
        }
    if any(marker in lowered for marker in ["filename too long", "file name too long", "path too long"]):
        return {
            "kind": "path_too_long",
            "platform": system,
            "remediation": "Use the OS user cache, a shorter SKILLFORGE_CACHE_DIR, sparse checkout, or enable long path support where the operating system requires it.",
        }
    if "unable to checkout working tree" in lowered:
        return {
            "kind": "checkout_failed",
            "platform": system,
            "remediation": "Retry with a shorter cache path or sparse checkout; inspect the peer cache before trusting stale results.",
        }
    return {
        "kind": "peer_error",
        "platform": system,
        "remediation": "Inspect the peer error and retry with --refresh or a known-good cache.",
    }


def peer_error(peer_id: str | None, message: str, *, stale: bool, **extra: object) -> dict:
    classified = classify_peer_error(message)
    return {
        "peer_id": peer_id,
        "error": message,
        "stale": stale,
        **classified,
        **extra,
    }


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
        "default_enabled": peer.get("default_enabled"),
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
    return [peer for peer in all_peers if peer.get("default_enabled", True)]


def run_git(args: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *git_platform_options(), *args],
        cwd=str(cwd) if cwd else None,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        details = (result.stderr or result.stdout).strip()
        command = "git " + " ".join(args)
        raise RuntimeError(f"{command} failed with exit code {result.returncode}: {details}")
    return result.stdout.strip()


def git_platform_options() -> list[str]:
    if os.name == "nt":
        return ["-c", "core.longpaths=true"]
    return []


def clone_peer_repo(source: str, repo_path: Path) -> None:
    run_git(["clone", "--depth", "1", "--filter=blob:none", "--sparse", source, str(repo_path)])
    try:
        run_git(["sparse-checkout", "set", "skills"], cwd=repo_path)
    except RuntimeError:
        # Older Git versions may not support sparse-checkout. Keep the clone if
        # it has a usable skills directory; otherwise surface the original state.
        if not (repo_path / "skills").exists():
            raise


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
            except RuntimeError:
                run_git(["reset", "--hard", "origin/HEAD"], cwd=repo_path)
        elif not repo_path.exists():
            repo_path.parent.mkdir(parents=True, exist_ok=True)
            clone_peer_repo(source, repo_path)
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


def iter_peer_skills_with_diagnostics(repo_path: Path) -> tuple[list[dict], list[dict]]:
    skills_root = repo_path / "skills"
    if not skills_root.exists():
        return [], []
    skills: list[dict] = []
    skipped: list[dict] = []
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
        else:
            skipped.append(
                {
                    "path": skill_dir.relative_to(repo_path).as_posix(),
                    "errors": validation.errors,
                }
            )
    return skills, skipped


def iter_peer_skills(repo_path: Path) -> list[dict]:
    skills, _skipped = iter_peer_skills_with_diagnostics(repo_path)
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


def peer_catalog_cache_path(peer: dict, *, cache_dir: str | Path | None = None) -> Path:
    return cache_root(cache_dir) / "catalogs" / peer["id"] / "catalog.json"


def peer_catalog_raw_cache_path(peer: dict, *, cache_dir: str | Path | None = None) -> Path:
    return cache_root(cache_dir) / "catalogs" / peer["id"] / "raw.json"


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
        request = Request(location, headers={"User-Agent": "SkillForge/0.1 (+https://github.com/medatasci/agent_skills)"})
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    raise FileNotFoundError(f"Static catalog not found: {location}")


def read_text_if_exists(path: Path, *, max_chars: int | None = None) -> str:
    if not path.exists() or not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    return text[:max_chars] if max_chars else text


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
    repo = as_text(raw.get("repo") or raw.get("topSource"))
    skill_id = as_text(raw.get("id") or raw.get("name") or raw.get("slug"))
    name = as_text(raw.get("name")) or skill_id
    description = (
        as_text(raw.get("description"))
        or as_text(raw.get("short_description"))
        or as_text(raw.get("title"))
        or as_text(raw.get("desc"))
        or as_text(raw.get("summary"))
    )
    source = raw.get("source", {}) if isinstance(raw.get("source"), dict) else {}
    checksum = raw.get("checksum") if isinstance(raw.get("checksum"), dict) else {}
    categories = as_list(raw.get("categories") or raw.get("category"))
    tags = as_list(raw.get("tags"))
    url = raw.get("url") or source.get("url")
    if not url and repo:
        url = f"https://github.com/{repo}"
    return {
        "id": skill_id,
        "name": name,
        "title": raw.get("title"),
        "description": description,
        "short_description": as_text(raw.get("short_description")) or first_sentence(description),
        "expanded_description": as_text(raw.get("expanded_description")) or description,
        "summary": as_text(raw.get("summary")) or as_text(raw.get("short_description")) or first_sentence(description),
        "path": as_text(source.get("path") or raw.get("path") or raw.get("url") or skill_id),
        "repo": repo,
        "categories": categories,
        "tags": tags,
        "search_terms": [*categories, *tags, repo],
        "warnings": as_list(raw.get("warnings")),
        "checksum": checksum,
        "url": url,
        "updated_at": raw.get("updated_at"),
    }


def iter_static_catalog_skills(payload: dict) -> list[dict]:
    if isinstance(payload, list):
        raw_skills = payload
    elif isinstance(payload, dict):
        raw_skills = payload.get("skills") or payload.get("results") or []
    else:
        raw_skills = []
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


def enrich_peer_search_result(item: dict) -> dict:
    enriched = dict(item)
    description = as_text(enriched.get("description"))
    enriched["description"] = description
    enriched["short_description"] = as_text(enriched.get("short_description")) or first_sentence(description)
    enriched["expanded_description"] = as_text(enriched.get("expanded_description")) or description
    enriched["summary"] = as_text(enriched.get("summary")) or enriched["short_description"] or first_sentence(description)
    return enriched


def cache_modified_at(path: Path) -> str | None:
    if not path.exists():
        return None
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return modified.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def cache_expires_at(path: Path, ttl_hours: int) -> str | None:
    if not path.exists():
        return None
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return (modified + timedelta(hours=ttl_hours)).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def catalog_skill_from_repo(peer: dict, repo: PeerRepo, skill: dict) -> dict:
    skill_dir = repo.repo_path / skill["path"]
    validation = validate_skill(skill_dir)
    discovery = discovery_metadata_from_validation(
        validation,
        fallback_tags=infer_tags(as_text(skill.get("name")), as_text(skill.get("description"))),
    )
    skill_text = read_text_if_exists(skill_dir / "SKILL.md")
    readme_text = read_text_if_exists(skill_dir / "README.md")
    entry = {
        **skill,
        **discovery,
        "id": as_text(validation.metadata.get("name")) or skill["id"],
        "name": as_text(validation.metadata.get("name")) or skill["name"],
        "description": as_text(validation.metadata.get("description")) or skill["description"],
        "path": skill["path"],
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
        "checksum": {
            "algorithm": "sha256-tree",
            "value": skill_checksum(skill_dir),
        },
        "skill_text": skill_text,
        "readme_text": readme_text,
        "warnings": validation.warnings,
    }
    return enrich_peer_search_result(entry)


def catalog_skill_from_static(peer: dict, skill: dict, cache_state: dict, catalog_timestamp: str | None) -> dict:
    entry = {
        **skill,
        "source_catalog": source_catalog_metadata(peer),
        "source": {
            "type": "peer-static-catalog",
            "peer_id": peer["id"],
            "repo": skill.get("repo") or peer.get("repo"),
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
    return enrich_peer_search_result(entry)


def write_peer_catalog_snapshot(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cached_peer_catalog_payload(peer: dict, *, ttl_hours: int, cache_dir: str | Path | None = None) -> dict | None:
    catalog_path = peer_catalog_cache_path(peer, cache_dir=cache_dir)
    if not cache_is_fresh(catalog_path, ttl_hours):
        return None
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    payload["cache"] = {
        **payload.get("cache", {}),
        "status": "hit",
        "path": str(catalog_path),
        "ttl_hours": ttl_hours,
        "modified_at": cache_modified_at(catalog_path),
        "expires_at": cache_expires_at(catalog_path, ttl_hours),
        "stale": False,
    }
    return payload


def build_static_peer_catalog_snapshot(
    peer: dict,
    *,
    refresh: bool,
    ttl_hours: int,
    cache_dir: str | Path | None,
) -> dict:
    raw_payload, cache_state = load_static_catalog(peer, refresh=refresh, cache_dir=cache_dir)
    raw_path = peer_catalog_raw_cache_path(peer, cache_dir=cache_dir)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps(raw_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    catalog_timestamp = None
    if isinstance(raw_payload, dict):
        catalog_timestamp = raw_payload.get("generated_at") or raw_payload.get("updated_at") or raw_payload.get("updated")
    skills = [
        catalog_skill_from_static(peer, skill, cache_state, catalog_timestamp)
        for skill in iter_static_catalog_skills(raw_payload)
    ]
    return {
        "schema_version": "0.1",
        "kind": "peer-provider-catalog",
        "provider": source_catalog_metadata(peer),
        "generated_at": utc_now(),
        "catalog_timestamp": catalog_timestamp,
        "skill_count": len(skills),
        "skills": skills,
        "skipped": [],
        "errors": [peer_error(peer["id"], cache_state["error"], stale=True)] if cache_state.get("error") else [],
        "raw_cache_path": str(raw_path),
        "cache": {
            "status": "refresh" if refresh else cache_state["cache_status"],
            "path": str(peer_catalog_cache_path(peer, cache_dir=cache_dir)),
            "ttl_hours": ttl_hours,
            "source_cache_path": cache_state["cache_path"],
            "raw_cache_path": str(raw_path),
            "modified_at": cache_modified_at(peer_catalog_cache_path(peer, cache_dir=cache_dir)),
            "expires_at": cache_expires_at(peer_catalog_cache_path(peer, cache_dir=cache_dir), ttl_hours),
            "stale": cache_state["stale"],
        },
    }


def build_repo_peer_catalog_snapshot(
    peer: dict,
    *,
    refresh: bool,
    ttl_hours: int,
    cache_dir: str | Path | None,
) -> dict:
    repo = ensure_peer_repo(peer, refresh=refresh, cache_dir=cache_dir)
    peer_skills, skipped_skills = iter_peer_skills_with_diagnostics(repo.repo_path)
    skills = [catalog_skill_from_repo(peer, repo, skill) for skill in peer_skills]
    errors = []
    for skipped in skipped_skills:
        errors.append(
            peer_error(
                peer["id"],
                "; ".join(skipped["errors"]),
                stale=repo.stale,
                kind="parser_skipped",
                skill_path=skipped["path"],
                remediation="Update SKILL.md frontmatter or parser support for this peer skill.",
            )
        )
    if repo.error:
        errors.append(peer_error(peer["id"], repo.error, stale=True))
    return {
        "schema_version": "0.1",
        "kind": "peer-provider-catalog",
        "provider": source_catalog_metadata(peer),
        "generated_at": utc_now(),
        "repo": {
            "path": str(repo.repo_path),
            "commit": repo.commit,
            "fetched_at": repo.fetched_at,
            "stale": repo.stale,
        },
        "skill_count": len(skills),
        "skills": skills,
        "skipped": skipped_skills,
        "errors": errors,
        "cache": {
            "status": "refresh" if refresh else "miss",
            "path": str(peer_catalog_cache_path(peer, cache_dir=cache_dir)),
            "ttl_hours": ttl_hours,
            "repo_cache_path": str(repo.repo_path),
            "modified_at": cache_modified_at(peer_catalog_cache_path(peer, cache_dir=cache_dir)),
            "expires_at": cache_expires_at(peer_catalog_cache_path(peer, cache_dir=cache_dir), ttl_hours),
            "stale": repo.stale,
        },
    }


def cache_one_peer_catalog(
    peer: dict,
    *,
    refresh: bool = False,
    ttl_hours: int = DEFAULT_PEER_TTL_HOURS,
    cache_dir: str | Path | None = None,
) -> dict:
    peer = normalize_peer(peer)
    catalog_path = peer_catalog_cache_path(peer, cache_dir=cache_dir)
    if not refresh:
        cached = cached_peer_catalog_payload(peer, ttl_hours=ttl_hours, cache_dir=cache_dir)
        if cached is not None:
            return cached

    try:
        if is_static_catalog_peer(peer):
            payload = build_static_peer_catalog_snapshot(peer, refresh=refresh, ttl_hours=ttl_hours, cache_dir=cache_dir)
        else:
            payload = build_repo_peer_catalog_snapshot(peer, refresh=refresh, ttl_hours=ttl_hours, cache_dir=cache_dir)
        payload["cache"]["modified_at"] = utc_now()
        payload["cache"]["expires_at"] = (
            datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
        ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        write_peer_catalog_snapshot(catalog_path, payload)
        return payload
    except Exception as exc:
        if catalog_path.exists():
            payload = json.loads(catalog_path.read_text(encoding="utf-8"))
            error = peer_error(peer["id"], str(exc), stale=True)
            payload["errors"] = [*payload.get("errors", []), error]
            payload["cache"] = {
                **payload.get("cache", {}),
                "status": "stale",
                "path": str(catalog_path),
                "ttl_hours": ttl_hours,
                "modified_at": cache_modified_at(catalog_path),
                "expires_at": cache_expires_at(catalog_path, ttl_hours),
                "stale": True,
            }
            return payload
        error = peer_error(peer.get("id"), str(exc), stale=False)
        return {
            "schema_version": "0.1",
            "kind": "peer-provider-catalog",
            "provider": source_catalog_metadata(peer),
            "generated_at": utc_now(),
            "skill_count": 0,
            "skills": [],
            "skipped": [],
            "errors": [error],
            "cache": {
                "status": "error",
                "path": str(catalog_path),
                "ttl_hours": ttl_hours,
                "modified_at": None,
                "expires_at": None,
                "stale": False,
            },
        }


def cache_peer_catalogs_parallel(
    peer_list: list[dict],
    *,
    refresh: bool,
    ttl_hours: int,
    cache_dir: str | Path | None,
    jobs: int | None,
) -> list[dict]:
    worker_count = peer_search_jobs(jobs, len(peer_list))
    if worker_count <= 1:
        return [
            cache_one_peer_catalog(peer, refresh=refresh, ttl_hours=ttl_hours, cache_dir=cache_dir)
            for peer in peer_list
        ]

    outputs: list[dict | None] = [None] * len(peer_list)
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_indexes = {
            executor.submit(
                cache_one_peer_catalog,
                peer,
                refresh=refresh,
                ttl_hours=ttl_hours,
                cache_dir=cache_dir,
            ): index
            for index, peer in enumerate(peer_list)
        }
        for future in as_completed(future_indexes):
            index = future_indexes[future]
            peer = peer_list[index]
            try:
                outputs[index] = future.result()
            except Exception as exc:
                error = peer_error(peer.get("id"), str(exc), stale=False)
                outputs[index] = {
                    "schema_version": "0.1",
                    "kind": "peer-provider-catalog",
                    "provider": source_catalog_metadata(peer),
                    "generated_at": utc_now(),
                    "skill_count": 0,
                    "skills": [],
                    "skipped": [],
                    "errors": [error],
                    "cache": {
                        "status": "error",
                        "path": str(peer_catalog_cache_path(peer, cache_dir=cache_dir)),
                        "ttl_hours": ttl_hours,
                        "modified_at": None,
                        "expires_at": None,
                        "stale": False,
                    },
                }
    return [output for output in outputs if output is not None]


def cache_peer_catalogs(
    *,
    peer_id: str | None = None,
    refresh: bool = False,
    ttl_hours: int = DEFAULT_PEER_TTL_HOURS,
    peers: list[dict] | None = None,
    cache_dir: str | Path | None = None,
    jobs: int | None = None,
    enabled_only: bool = False,
) -> dict:
    all_peers = [normalize_peer(peer) for peer in peers] if peers is not None else load_peer_catalogs()
    if peer_id:
        peer_list = [find_peer(peer_id, all_peers)]
    elif enabled_only:
        peer_list = [peer for peer in all_peers if peer.get("default_enabled", True)]
    else:
        peer_list = all_peers
    catalogs = cache_peer_catalogs_parallel(
        peer_list,
        refresh=refresh,
        ttl_hours=ttl_hours,
        cache_dir=cache_dir,
        jobs=jobs,
    )
    providers = []
    errors = []
    for catalog in catalogs:
        provider = catalog["provider"]
        catalog_errors = catalog.get("errors", [])
        errors.extend(catalog_errors)
        providers.append(
            {
                "peer_id": provider["id"],
                "name": provider.get("name"),
                "adapter": provider.get("adapter"),
                "default_enabled": provider.get("default_enabled"),
                "skill_count": catalog.get("skill_count", 0),
                "skipped_count": len(catalog.get("skipped", [])),
                "error_count": len(catalog_errors),
                "status": catalog.get("cache", {}).get("status"),
                "cache_path": catalog.get("cache", {}).get("path"),
                "raw_cache_path": catalog.get("raw_cache_path") or catalog.get("cache", {}).get("raw_cache_path"),
                "expires_at": catalog.get("cache", {}).get("expires_at"),
                "stale": catalog.get("cache", {}).get("stale"),
            }
        )
    return {
        "schema_version": "0.1",
        "kind": "peer-provider-catalog-cache",
        "generated_at": utc_now(),
        "ok": not any(provider["status"] == "error" for provider in providers),
        "cache": {
            "root": str(cache_root(cache_dir)),
            "ttl_hours": ttl_hours,
            "jobs": peer_search_jobs(jobs, len(peer_list)),
        },
        "provider_count": len(providers),
        "providers": providers,
        "errors": errors,
    }


def corpus_result_next_step(result: dict) -> dict:
    source = result.get("source", {}) if isinstance(result.get("source"), dict) else {}
    source_catalog = result.get("source_catalog", {}) if isinstance(result.get("source_catalog"), dict) else {}
    peer_id = as_text(source.get("peer_id")) or as_text(source_catalog.get("id"))
    skill_id = as_text(result.get("id"))
    path = as_text(source.get("path") or result.get("path"))
    source_type = as_text(source.get("type"))
    installable = bool(skill_id and peer_id and source_type == "peer-catalog" and path.startswith("skills/"))
    if installable:
        command = f"python -m skillforge install {skill_id} --peer {peer_id} --scope global --yes"
        return {
            "installable": True,
            "command": command,
            "label": f"Review source, then `{command}`",
        }
    source_url = as_text(source.get("url") or result.get("url"))
    if source_url:
        return {
            "installable": False,
            "command": None,
            "label": f"Review source: {source_url}",
        }
    return {
        "installable": False,
        "command": None,
        "label": f"Review cached catalog: {peer_catalog_cache_path(source_catalog) if peer_id else 'unknown'}",
    }


def enrich_corpus_result(item: dict, *, query: str, score: int) -> dict:
    enriched = enrich_peer_search_result(item)
    matched_terms = []
    haystack = " ".join(as_text(value) for value in corpus_search_values(enriched)).lower().replace("-", " ")
    haystack_terms = set(re.findall(r"[a-z0-9]+", haystack))
    for term in query_terms(query, ignore_terms=GENERIC_PEER_TERMS):
        if haystack_terms.intersection(term_variants(term)):
            matched_terms.append(term)
    next_step = corpus_result_next_step(enriched)
    enriched.update(
        {
            "score": score,
            "matched_terms": sorted(set(matched_terms)),
            "installable": next_step["installable"],
            "install_command": next_step["command"],
            "next_step": next_step["label"],
        }
    )
    return enriched


def dedupe_corpus_results(results: list[dict]) -> list[dict]:
    best: dict[tuple[str, str], dict] = {}
    for result in results:
        source = result.get("source", {}) if isinstance(result.get("source"), dict) else {}
        repo = as_text(source.get("repo") or result.get("repo") or result.get("source_catalog", {}).get("repo"))
        key = (as_text(result.get("id")), repo or as_text(result.get("source_catalog", {}).get("id")))
        current = best.get(key)
        if current is None:
            best[key] = result
            continue
        if result.get("installable") and not current.get("installable"):
            current["installable"] = True
            current["install_command"] = result.get("install_command")
            current["next_step"] = result.get("next_step")
        if current.get("installable") and not result.get("installable"):
            result["installable"] = True
            result["install_command"] = current.get("install_command")
            result["next_step"] = current.get("next_step")
        current_rank = (int(current.get("score", 0)), bool(current.get("installable")), len(as_text(current.get("summary"))))
        new_rank = (int(result.get("score", 0)), bool(result.get("installable")), len(as_text(result.get("summary"))))
        if new_rank > current_rank:
            best[key] = result
    return list(best.values())


def corpus_search(
    query: str,
    *,
    peer_id: str | None = None,
    refresh: bool = False,
    limit: int = 10,
    ttl_hours: int = DEFAULT_PEER_TTL_HOURS,
    peers: list[dict] | None = None,
    cache_dir: str | Path | None = None,
    jobs: int | None = None,
    enabled_only: bool = False,
) -> dict:
    all_peers = [normalize_peer(peer) for peer in peers] if peers is not None else load_peer_catalogs()
    if peer_id:
        peer_list = [find_peer(peer_id, all_peers)]
    elif enabled_only:
        peer_list = [peer for peer in all_peers if peer.get("default_enabled", True)]
    else:
        peer_list = all_peers

    catalogs = cache_peer_catalogs_parallel(
        peer_list,
        refresh=refresh,
        ttl_hours=ttl_hours,
        cache_dir=cache_dir,
        jobs=jobs,
    )
    results: list[dict] = []
    errors: list[dict] = []
    provider_statuses: list[dict] = []
    min_matches = minimum_skill_score(query)
    for catalog in catalogs:
        provider = catalog.get("provider", {})
        catalog_errors = catalog.get("errors", [])
        errors.extend(catalog_errors)
        provider_statuses.append(
            {
                "peer_id": provider.get("id"),
                "status": catalog.get("cache", {}).get("status"),
                "skill_count": catalog.get("skill_count", 0),
                "result_count": 0,
                "error_count": len(catalog_errors),
                "cache_path": catalog.get("cache", {}).get("path"),
                "expires_at": catalog.get("cache", {}).get("expires_at"),
            }
        )
        for skill in catalog.get("skills", []):
            relevance = corpus_match_count(query, skill)
            if relevance < min_matches:
                continue
            score = corpus_skill_score(query, skill)
            if score <= 0:
                continue
            results.append(enrich_corpus_result(skill, query=query, score=score))
        provider_statuses[-1]["result_count"] = sum(
            1 for result in results if result.get("source_catalog", {}).get("id") == provider.get("id")
        )

    results = dedupe_corpus_results(results)
    results.sort(
        key=lambda item: (
            -int(item.get("score", 0)),
            not bool(item.get("installable")),
            item.get("source_catalog", {}).get("id") or "",
            item.get("id") or "",
        )
    )
    limited = results[:limit]
    return {
        "schema_version": "0.1",
        "kind": "peer-provider-corpus-search",
        "query": query,
        "generated_at": utc_now(),
        "result_count": len(results),
        "results": limited,
        "provider_statuses": provider_statuses,
        "errors": errors,
        "cache": {
            "root": str(cache_root(cache_dir)),
            "ttl_hours": ttl_hours,
            "jobs": peer_search_jobs(jobs, len(peer_list)),
            "provider_count": len(peer_list),
        },
    }


def peer_search_jobs(jobs: int | None, peer_count: int) -> int:
    if peer_count <= 0:
        return 0
    raw = jobs if jobs is not None else os.environ.get("SKILLFORGE_PEER_JOBS")
    try:
        requested = int(raw) if raw is not None else DEFAULT_PEER_SEARCH_JOBS
    except (TypeError, ValueError):
        requested = DEFAULT_PEER_SEARCH_JOBS
    return max(1, min(requested, MAX_PEER_SEARCH_JOBS, peer_count))


def search_one_peer(
    query: str,
    peer: dict,
    *,
    refresh: bool,
    cache_dir: str | Path | None,
) -> dict:
    results: list[dict] = []
    errors: list[dict] = []
    try:
        if is_static_catalog_peer(peer):
            static_payload, cache_state = load_static_catalog(peer, refresh=refresh, cache_dir=cache_dir)
            catalog_timestamp = None
            if isinstance(static_payload, dict):
                catalog_timestamp = static_payload.get("generated_at") or static_payload.get("updated_at") or static_payload.get("updated")
            for skill in iter_static_catalog_skills(static_payload):
                relevance = skill_match_count(query, skill)
                if relevance < minimum_skill_score(query):
                    continue
                score = skill_score(query, skill) + peer_score(query, peer)
                results.append(
                    enrich_peer_search_result(
                        {
                            **skill,
                            "score": score,
                            "source_catalog": source_catalog_metadata(peer),
                            "source": {
                                "type": "peer-static-catalog",
                                "peer_id": peer["id"],
                                "repo": skill.get("repo") or peer.get("repo"),
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
                )
            if cache_state.get("error"):
                errors.append(peer_error(peer["id"], cache_state["error"], stale=True))
                status = {"peer_id": peer["id"], "status": "error", "kind": errors[-1]["kind"], "result_count": len(results)}
            else:
                status_name = "matched" if results else "no_match"
                status = {"peer_id": peer["id"], "status": status_name, "result_count": len(results)}
            return {"peer_id": peer["id"], "results": results, "errors": errors, "status": status}

        repo = ensure_peer_repo(peer, refresh=refresh, cache_dir=cache_dir)
        peer_skills, skipped_skills = iter_peer_skills_with_diagnostics(repo.repo_path)
        for skipped in skipped_skills:
            errors.append(
                peer_error(
                    peer["id"],
                    "; ".join(skipped["errors"]),
                    stale=repo.stale,
                    kind="parser_skipped",
                    skill_path=skipped["path"],
                    remediation="Update SKILL.md frontmatter or parser support for this peer skill.",
                )
            )
        for skill in peer_skills:
            relevance = skill_match_count(query, skill)
            if relevance < minimum_skill_score(query):
                continue
            score = skill_score(query, skill) + peer_score(query, peer)
            skill_dir = repo.repo_path / skill["path"]
            results.append(
                enrich_peer_search_result(
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
            )
        if repo.error:
            errors.append(peer_error(peer["id"], repo.error, stale=True))
        status_name = "matched" if results else "no_match"
        status = {"peer_id": peer["id"], "status": status_name, "result_count": len(results), "stale": repo.stale}
        return {"peer_id": peer["id"], "results": results, "errors": errors, "status": status}
    except Exception as exc:
        error = peer_error(peer.get("id"), str(exc), stale=False)
        return {
            "peer_id": peer.get("id"),
            "results": results,
            "errors": [*errors, error],
            "status": {"peer_id": peer.get("id"), "status": "error", "kind": error["kind"], "result_count": len(results)},
        }


def search_peers_parallel(
    query: str,
    peer_list: list[dict],
    *,
    refresh: bool,
    cache_dir: str | Path | None,
    jobs: int | None,
) -> list[dict]:
    worker_count = peer_search_jobs(jobs, len(peer_list))
    if worker_count <= 1:
        return [search_one_peer(query, peer, refresh=refresh, cache_dir=cache_dir) for peer in peer_list]

    outputs: list[dict | None] = [None] * len(peer_list)
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_indexes = {
            executor.submit(search_one_peer, query, peer, refresh=refresh, cache_dir=cache_dir): index
            for index, peer in enumerate(peer_list)
        }
        for future in as_completed(future_indexes):
            index = future_indexes[future]
            peer = peer_list[index]
            try:
                outputs[index] = future.result()
            except Exception as exc:
                error = peer_error(peer.get("id"), str(exc), stale=False)
                outputs[index] = {
                    "peer_id": peer.get("id"),
                    "results": [],
                    "errors": [error],
                    "status": {"peer_id": peer.get("id"), "status": "error", "kind": error["kind"], "result_count": 0},
                }
    return [output for output in outputs if output is not None]


def peer_search(
    query: str,
    *,
    peer_id: str | None = None,
    refresh: bool = False,
    limit: int = 10,
    ttl_hours: int = 24,
    peers: list[dict] | None = None,
    cache_dir: str | Path | None = None,
    jobs: int | None = None,
) -> dict:
    cache_path = search_cache_path(query, peer_id=peer_id, cache_dir=cache_dir)
    if not refresh and cache_is_fresh(cache_path, ttl_hours):
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        if payload.get("cache_version") == PEER_SEARCH_CACHE_VERSION:
            payload["cache"] = {"status": "hit", "path": str(cache_path)}
            return limited_search_payload(payload, limit)

    all_peers = [normalize_peer(peer) for peer in peers] if peers is not None else load_peer_catalogs()
    peer_list = selected_peers(query, peer_id=peer_id, peers=all_peers, cache_dir=cache_dir)
    results: list[dict] = []
    errors: list[dict] = []
    peer_statuses: list[dict] = []
    peer_outputs = search_peers_parallel(query, peer_list, refresh=refresh, cache_dir=cache_dir, jobs=jobs)
    for output in peer_outputs:
        results.extend(output["results"])
        errors.extend(output["errors"])
        peer_statuses.append(output["status"])

    if not peer_id:
        for peer in all_peers:
            if not peer.get("default_enabled", True):
                peer_statuses.append({"peer_id": peer["id"], "status": "disabled", "result_count": 0})

    results.sort(key=lambda item: (-item["score"], item["source_catalog"]["id"], item["id"]))
    payload = {
        "cache_version": PEER_SEARCH_CACHE_VERSION,
        "query": query,
        "result_count": len(results),
        "results": results,
        "errors": errors,
        "peer_statuses": peer_statuses,
        "peer_search": {
            "jobs": peer_search_jobs(jobs, len(peer_list)),
            "peer_count": len(peer_list),
            "max_jobs": MAX_PEER_SEARCH_JOBS,
        },
        "cache": {"status": "refresh" if refresh else "miss", "path": str(cache_path)},
        "generated_at": utc_now(),
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return limited_search_payload(payload, limit)


def limited_search_payload(payload: dict, limit: int) -> dict:
    limited = dict(payload)
    limited["results"] = [enrich_peer_search_result(item) for item in list(payload.get("results", []))[:limit]]
    return limited


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
    catalogs_root = root / "catalogs"
    if peers_root.exists():
        for peer_dir in sorted(path for path in peers_root.iterdir() if path.is_dir()):
            repo_path = peer_dir / "repo"
            catalog_path = catalogs_root / peer_dir.name / "catalog.json"
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
                    "catalog_cached": catalog_path.exists(),
                    "catalog_path": str(catalog_path) if catalog_path.exists() else None,
                    "skill_cache_commits": commits,
                }
            )
    if catalogs_root.exists():
        known_peer_ids = {peer["peer_id"] for peer in peers}
        for catalog_dir in sorted(path for path in catalogs_root.iterdir() if path.is_dir()):
            if catalog_dir.name in known_peer_ids:
                continue
            catalog_path = catalog_dir / "catalog.json"
            peers.append(
                {
                    "peer_id": catalog_dir.name,
                    "repo_cached": False,
                    "repo_path": None,
                    "catalog_cached": catalog_path.exists(),
                    "catalog_path": str(catalog_path) if catalog_path.exists() else None,
                    "skill_cache_commits": [],
                }
            )
    search_files = sorted((root / "search").glob("*.json")) if (root / "search").exists() else []
    catalog_files = sorted((root / "catalogs").glob("*/catalog.json")) if (root / "catalogs").exists() else []
    return {
        "cache_root": str(root),
        "peers": peers,
        "search_cache_files": [str(path) for path in search_files],
        "provider_catalog_files": [str(path) for path in catalog_files],
    }


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
        provider_catalog_path = peer_catalog_cache_path(peer, cache_dir=cache_dir)
        cache_exists = cache_path.exists()
        provider_catalog_exists = provider_catalog_path.exists()
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
                "provider_catalog_cache": {
                    "path": str(provider_catalog_path),
                    "exists": provider_catalog_exists,
                    "modified_at": cache_modified_at(provider_catalog_path),
                    "expires_at": cache_expires_at(provider_catalog_path, int(peer.get("ttl_hours") or DEFAULT_PEER_TTL_HOURS)),
                    "stale": None
                    if not provider_catalog_exists
                    else not cache_is_fresh(provider_catalog_path, int(peer.get("ttl_hours") or DEFAULT_PEER_TTL_HOURS)),
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
