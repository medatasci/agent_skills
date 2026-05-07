# `skillforge/source_archive.py`

## Purpose

`source_archive.py` records source metadata for clinical disease chapters and,
when requested, downloads a local reproducibility cache copy under `.skillforge/`.

The committed artifact is the source manifest. Full source pages, PDFs, article
HTML, or training pages stay in the ignored local cache unless redistribution is
explicitly permitted and reviewed.

## Public Interface

Top-level CLI:

```text
python -m skillforge source-archive <disease> --source-id <id> --title "<title>" --url <url> --source-type "<type>" --claim-breadth "<broad/narrow/scope>" --section "Primary Imaging Modality" --download --json
```

Python API:

```python
from skillforge.source_archive import record_source_archive
```

## Inputs

- disease name
- source ID
- title and URL
- source type
- claim breadth supported
- optional license or reuse status
- optional supported disease sections
- optional source manifest path
- optional local cache root
- optional cache status
- optional download flag
- optional notes and date accessed

## Outputs

- JSON source manifest entry
- optional local cache file under `.skillforge/source-cache/`
- checksum, byte count, content type, and final URL when a download succeeds
- warnings when download fails or the downloaded content appears to be an
  access-denial, login, captcha, JavaScript challenge, or client-challenge page

## Side Effects

- Writes or updates `docs/clinical-statistical-expert/diseases/<disease>.sources.json` by default.
- Downloads source content only when `--download` is supplied.
- Writes downloaded content only under the configured cache root, which should
  remain ignored by git.

## Network Use

The helper may access the network when `--download` is supplied. URL-only source
records do not use the network.

## Cross-Platform Notes

All filesystem work uses `pathlib` and should work on Windows, macOS, and Linux.
The helper does not invoke shell commands.

## Tests

Relevant tests live in:

```text
tests/test_skillforge.py
```
