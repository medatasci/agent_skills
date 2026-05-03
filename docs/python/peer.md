# `skillforge/peer.py`

Peer catalog federation, cache, provider corpus search, peer install, peer
import, and peer diagnostics module.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Loading and normalizing `peer-catalogs.json`.
- Fetching, caching, and searching peer skill repositories and static catalogs.
- Installing peer skills into Codex and importing peer skills into SkillForge.

This module does not own:

- Local SkillForge catalog generation; use `catalog.py`.
- Local install path resolution details; use `install.py`.

## When To Edit This Module

Edit this module when:

- Peer selection, diagnostics, adapters, cache behavior, or corpus search changes.
- Peer install or peer import provenance changes.
- Provider catalog snapshots or `corpus-search` JSON fields change.

Choose another module when:

- Local-only search changes; use `catalog.py`.
- Codex target directory behavior changes; use `install.py`.

## Commands Or Workflows

Commands, workflows, or APIs backed by this module:

```text
python -m skillforge peer-search "<task>"
python -m skillforge corpus-search "<task>"
python -m skillforge cache catalogs --json
```

Related commands:

- `python -m skillforge install <skill-id> --peer <peer-id> --yes`
- `python -m skillforge import-peer <skill-id> --peer <peer-id>`

## Inputs And Reads

This module reads:

- `peer-catalogs.json`
- SkillForge cache directories.
- Peer Git repositories and static JSON catalogs.

Important environment variables:

- `SKILLFORGE_CACHE_DIR`: Overrides the SkillForge user cache root.
- `SKILLFORGE_PEER_JOBS`: Sets default bounded peer-search concurrency.

## Outputs And Writes

This module writes:

- Peer repo caches, search caches, and provider catalog snapshots.
- Installed peer skills or imported local catalog skills when explicitly requested.

Generated or modified files:

```text
<SkillForge cache>/peers/
<SkillForge cache>/search/
<SkillForge cache>/catalogs/<peer-id>/catalog.json
skills/<skill-id>/            # import-peer only
catalog/                      # import-peer only
```

Search commands can write cache files. `peer-diagnostics` is read-only except
for reading cache metadata.

## Side Effects And Safety

Risk level:
high

Network access:
Peer search, cache refresh, and provider catalog caching may use network access.

Filesystem writes:
Peer cache, peer install, and peer import can write local files.

External commands:
Git is used for GitHub-style peer repositories.

User confirmation gates:

- Peer install requires `--yes` in the CLI after source review.
- Peer import must be explicit and should not happen during install.

Safety notes:

- Peer catalogs are discovery sources, not endorsements.
- Preserve source catalog, repo URL, commit, path, checksum, and warnings.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `peer_search(query, ...)`: searches configured peers and returns source-attributed results.
- `corpus_search(query, ...)`: searches cached full provider catalog snapshots.
- `cache_peer_catalogs(...)`: materializes normalized provider catalog JSON.

Stable JSON fields or return payloads:

- `results`: source-attributed skill matches.
- `peer_statuses`: deterministic status for searched, disabled, matched, or errored peers.
- `cache`: cache root, TTL, provider count, and freshness metadata.

Compatibility notes:

- Peer errors should use stable machine-readable kinds.
- Result ordering should stay deterministic even when peer queries run in parallel.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Use OS-appropriate user cache locations by default.
- Handle Windows path length and read-only file behavior.
- Use subprocess argument lists for Git.

Avoid:

- Shell-specific behavior in Python module logic.
- Hard-coded path separators.
- Assuming external tools are installed or on `PATH`.

## Tests

Primary tests:

```text
python -m unittest tests.test_skillforge
tests/test_skillforge.py
```

Acceptance checks:

- Peer search queries all enabled peers unless `--peer` narrows scope.
- `corpus-search` returns install commands, source URLs, and comments.
- Peer install does not mutate local catalog files.

## Agent Notes

Before editing:

1. Read this document.
2. Read `skillforge/modules.toml` for ownership and side-effect metadata.
3. Read the source file.
4. Search for tests that already cover the behavior.

After editing:

1. Add or update focused tests.
2. Run the relevant test subset.
3. Run `python -m unittest tests.test_skillforge` before publishing.
4. Update this document and `skillforge/modules.toml` if ownership,
   side effects, commands, or data contracts changed.

## Related Docs

- `skillforge/README.md`
- `skillforge/modules.toml`
- `docs/python/README.md`
- `docs/python/install.md`
- `requirements.md`
