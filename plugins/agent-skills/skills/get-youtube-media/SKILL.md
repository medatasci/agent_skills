---
name: get-youtube-media
description: Search YouTube for learning topics or research evidence, get transcripts/captions from YouTube videos, optionally download the video as an MP4 plus a separate audio file, and run restartable queue-based retrieval with sleep/retry handling for rate limits. Use when Codex needs to search YouTube from a query/results URL, transcribe one or many YouTube URLs, save caption text/SRT/JSON, inspect available caption languages, resume interrupted retrieval, build a research/evidence source workflow, or download YouTube media files with yt-dlp for videos the user is authorized to save.
---

# Get YouTube Media

## Quick Start

Use `scripts/youtube_media.py` for repeatable YouTube transcript and media extraction:

```bash
python scripts/youtube_media.py "https://www.youtube.com/watch?v=VIDEO_ID" --output-dir ./youtube-output
python scripts/youtube_media.py "https://youtu.be/VIDEO_ID" --lang en --write-srt --write-json
python scripts/youtube_media.py "how to read an MRI for brain lesions" --search --search-count 8 --search-only
python scripts/youtube_media.py "brain MRI tutorial" --search-count 10 --license creativeCommon --search-only --youtube-api-key "$YOUTUBE_API_KEY"
python scripts/youtube_media.py "https://www.youtube.com/results?search_query=how+to+read+an+MRI+for+brain+lesions" --transcribe-search-results 2
python scripts/youtube_media.py "how to read an MRI for brain lesions" --search-count 10 --queue-only --queue-file ./youtube-output/mri-lesions.queue.json
python scripts/youtube_media.py --resume-queue ./youtube-output/mri-lesions.queue.json
python scripts/youtube_media.py "https://youtu.be/VIDEO_ID" --require-creative-commons --download-video
python scripts/youtube_media.py "https://youtu.be/VIDEO_ID" --download-video --download-audio
```

Run the script from the skill directory, or use an absolute path to it. The script first checks for a vendored `yt-dlp` package in `vendor/`, then falls back to the active Python environment. If `yt-dlp` is missing, install it into the skill:

```bash
python -m pip install --target vendor yt-dlp
```

## Workflow

1. Confirm the user has provided a YouTube URL and whether they want transcript only, MP4 video, audio, or all outputs.
2. For learning/research requests, pass a plain topic or YouTube `/results?search_query=...` URL with `--search-only` first to collect candidate videos.
3. Use `--queue-only` to save a restartable queue without retrieval, or `--transcribe-search-results N` to save a queue and process the top N results.
4. Use `--resume-queue <path>` to continue an interrupted queue. Completed tasks are skipped; queued, retrying, interrupted, and not-yet-exhausted failed tasks are attempted.
5. Tune politeness/retry behavior with `--request-sleep`, `--max-retries`, `--retry-sleep`, `--rate-limit-sleep`, and `--retry-backoff`. Defaults are intentionally conservative.
6. Prefer transcript-only extraction first; it is fast, small, and usually enough for summarization, quoting, notes, or analysis.
7. Use `--license any|creativeCommon|youtube` to annotate and filter search results by YouTube license. Specific license filters fetch each candidate's video metadata and post-filter the result list.
8. Provide `--youtube-api-key <key>` or set `YOUTUBE_API_KEY` for reliable license checks through the official YouTube Data API. Without an API key, the script falls back to `yt-dlp` metadata, which may report `unknown`.
9. Use `--require-creative-commons` when transcript/media retrieval must only proceed for Creative Commons Attribution (CC BY) videos. This implies `--license creativeCommon` and fails closed if the license is unknown or not Creative Commons.
10. Use `--lang <code>` when the user asks for a specific language. The script prefers manually uploaded captions, then automatic captions. Default language is `en`.
11. Use `--list-languages` when the requested transcript language is missing or when choosing among available caption tracks.
12. Add `--download-video` only when the user wants an MP4 file and is authorized to save the video.
13. Add `--download-audio` when the user wants a separate audio file. Default audio output is `m4a` when available.

For research hubs, evidence corpora, source registries, timestamped citations,
or multi-label learning projects, read
`references/research_hub_youtube_workflow.md` before searching or downloading.

## Output Files

The script writes files into `--output-dir`:

- `<query>.search-results.md`
- `<query>.search-results.json`
- `<query>.queue.json` with restartable retrieval status, attempts, errors, retry timestamps, and output paths
- `<title> [<id>].transcript.txt`
- `<title> [<id>].captions.<source-extension>`
- Optional `<title> [<id>].transcript.srt`
- Optional `<title> [<id>].segments.json`
- Optional `<title> [<id>].video.<ext>`
- Optional `<title> [<id>].audio.<ext>`
- `<title> [<id>].summary.json` with metadata and output paths

Search results, queue tasks, and summary JSON include a `license` object with
the raw value, normalized YouTube value (`creativeCommon`, `youtube`, or
`unknown`), source (`youtube-data-api` or `yt-dlp`), and whether the official API
was checked.

## Download Notes

- `yt-dlp` is required. `ffmpeg` is optional but recommended for best MP4 merging and MP3 audio conversion.
- YouTube and yt-dlp requests can be rate-limited. HTTP 429/Too Many Requests should be treated as a signal to pause, not to increase concurrency.
- The queue runner sleeps after rate-limit-like errors, then retries the same item until `--max-retries` is exhausted.
- License checks prefer the official YouTube Data API when `--youtube-api-key` or `YOUTUBE_API_KEY` is available, then fall back to metadata exposed by `yt-dlp`. Treat unknown license as not reusable; `--require-creative-commons` refuses unknown or Standard YouTube License videos.
- Without `ffmpeg`, MP4 downloads use YouTube's best progressive MP4 when available.
- For private, age-restricted, member-only, or region-gated videos, ask the user for a valid cookies file and pass `--cookies <path>`.
- Respect copyright, licenses, and platform terms. Do not help bypass access controls or download videos the user is not allowed to save.
