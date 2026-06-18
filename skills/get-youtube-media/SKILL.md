---
name: get-youtube-media
description: >-
  Search YouTube for learning topics or research evidence, get transcripts/captions from YouTube videos, optionally download the video as an MP4 plus a separate audio file, run local ASR fallback for captionless authorized media, and run restartable queue-based retrieval with sleep/retry handling for rate limits. Use when Codex needs to search YouTube from a query/results URL, transcribe one or many YouTube URLs, save caption text/SRT/JSON, inspect available caption languages, resume interrupted retrieval, build a research/evidence source workflow, run local Nemotron/NeMo ASR when captions are missing, or download YouTube media files with yt-dlp for videos the user is authorized to save.
title: Get YouTube Media
short_description: >-
  Search YouTube, retrieve transcripts and captions, run optional local ASR fallback, inspect caption languages, and download authorized media for research workflows.
expanded_description: >-
  Use this skill when a user wants YouTube transcripts, captions, search results, local ASR fallback for captionless videos, or authorized media downloads for research, evidence gathering, learning, or repeatable source collection. It supports search queries, YouTube result URLs, direct video URLs, restartable queues, language selection, caption formats, optional Nemotron/NeMo ASR, and optional video or audio downloads.
aliases:
  - youtube transcripts
  - youtube captions
  - youtube research
  - video transcript extraction
  - yt-dlp workflow
categories:
  - Research
  - Media
tags:
  - youtube
  - transcripts
  - captions
  - media
  - research
tasks:
  - search YouTube for research sources
  - get a transcript from a YouTube URL
  - inspect available caption languages
  - save transcript text, SRT, or JSON
  - run local ASR for captionless authorized videos
  - download authorized YouTube video or audio
use_when:
  - The user needs YouTube transcripts, captions, or reusable video research artifacts.
  - The user wants to search YouTube and collect candidate sources for analysis.
  - The user is authorized to save requested media and asks for video or audio files.
do_not_use_when:
  - The user wants to bypass access controls, paywalls, region gates, or age restrictions.
  - The user wants to download media they are not allowed to save.
inputs:
  - YouTube URL
  - YouTube search query
  - YouTube results URL
  - optional language code
outputs:
  - transcript text
  - captions file
  - optional local ASR transcript for captionless videos
  - search result JSON or Markdown
  - restartable queue JSON
  - optional video or audio file
examples:
  - Use get-youtube-media to find transcripts for YouTube videos about agent skill marketplaces.
  - Use get-youtube-media to get captions from this YouTube URL and save them as text and SRT.
  - Use get-youtube-media to search YouTube for videos about MR datasets and summarize the best sources.
related_skills:
  - project-retrospective
risk_level: medium
permissions:
  - network access to YouTube or YouTube Data API
  - local file writes for transcript, queue, caption, ASR, and optional media outputs
  - optional YOUTUBE_API_KEY for reliable license checks
  - optional local NeMo/PyTorch runtime and ffmpeg for ASR fallback
page_title: Get YouTube Media Skill - YouTube Transcript, Caption, and Research Workflow for Codex
meta_description: Install the Get YouTube Media Skill for Codex to search YouTube, retrieve transcripts and captions, inspect caption languages, and support repeatable research workflows.
---

# Get YouTube Media

## What This Skill Does

Use this skill when a user asks to search YouTube, retrieve transcripts or
captions, inspect caption languages, resume a queue of retrieval work, or save
authorized video/audio media for research and learning workflows.

## Safe Default Behavior

Prefer transcript, caption, search-result, and metadata retrieval before media
downloads. Confirm authorization before downloading video or audio files,
explain network and file-write side effects before running commands, and do not
help bypass access controls or download media the user is not allowed to save.

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
python scripts/youtube_media.py --resume-queue ./youtube-output/mri-lesions.queue.json --asr-fallback --asr-model nvidia/nemotron-3.5-asr-streaming-0.6b --asr-lang en-US
python scripts/youtube_media.py "https://youtu.be/VIDEO_ID" --require-creative-commons --download-video
python scripts/youtube_media.py "https://youtu.be/VIDEO_ID" --require-creative-commons --asr-fallback --asr-source video --keep-asr-wav
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
12. If no usable captions exist, queue items are marked `needs_asr` instead of being retried as transient failures. Resume those items with `--asr-fallback` when local ASR is desired and the user is authorized to process the media locally.
13. Use `--asr-fallback` with `--asr-model nvidia/nemotron-3.5-asr-streaming-0.6b` to run local NeMo ASR after captions fail. Provide `--asr-python <path>` when NeMo is installed in a separate Python environment. The helper requires `ffmpeg` or Python package `imageio-ffmpeg` and writes ASR transcripts as `source: local-asr`.
14. Use `--asr-source audio` for smaller ASR downloads or `--asr-source video` when the workflow specifically needs an MP4 before transcription.
15. Add `--download-video` only when the user wants an MP4 file and is authorized to save the video.
16. Add `--download-audio` when the user wants a separate audio file. Default audio output is `m4a` when available.

## ASR Fallback

Use ASR fallback only after transcript/caption retrieval fails, or when a queue
item is already marked `needs_asr`. The normal order remains:

1. Manual YouTube captions.
2. Automatic YouTube captions.
3. Local ASR on authorized downloaded media.

Do not use ASR just to replace an available caption track. Captions are faster,
smaller, timestamped, and closer to YouTube's own transcript surface. Use ASR
when YouTube reports no usable caption tracks for the requested language, when a
saved queue item has `status: "needs_asr"`, or when the user explicitly wants
local ASR for authorized media.

For Windows GPU testing, a working local setup is:

```powershell
$PY = "C:\Users\medgar\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $PY -m venv .venv-youtube-asr-win
& .\.venv-youtube-asr-win\Scripts\python.exe -m pip install --upgrade pip setuptools wheel imageio-ffmpeg yt-dlp Cython packaging hf_xet
& .\.venv-youtube-asr-win\Scripts\python.exe -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
& .\.venv-youtube-asr-win\Scripts\python.exe -m pip install "nemo_toolkit[asr] @ git+https://github.com/NVIDIA/NeMo.git@main"
```

Use NVIDIA NeMo from GitHub rather than the older PyPI-only package when running
`nvidia/nemotron-3.5-asr-streaming-0.6b`; the model requires prompt-aware RNNT
classes that may not exist in older NeMo releases.

Before running ASR on Windows, set writable caches to avoid user-profile
permission issues:

```powershell
$env:MPLCONFIGDIR = "$PWD\.cache\youtube-asr-win\matplotlib"
$env:HF_HOME = "$PWD\.cache\youtube-asr-win\hf"
$env:TORCH_HOME = "$PWD\.cache\youtube-asr-win\torch"
```

Run the full fallback path with:

```powershell
& .\.venv-youtube-asr-win\Scripts\python.exe scripts\youtube_media.py "https://www.youtube.com/watch?v=VIDEO_ID" --asr-fallback --asr-source audio --asr-model nvidia/nemotron-3.5-asr-streaming-0.6b --asr-lang en-US --asr-python .\.venv-youtube-asr-win\Scripts\python.exe --write-json
```

Use `--asr-source audio` by default because it downloads less data. Use
`--asr-source video` only when the workflow also needs an MP4. Local ASR output
is saved as `source: local-asr`; review it before clinical, research, or quoted
use because ASR can introduce domain-specific errors.

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
- Optional `<title> [<id>].asr.json`
- Optional `<title> [<id>].transcript.asr.wav` when `--keep-asr-wav` is used
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
- Captionless videos are marked `needs_asr` in queue files. They are skipped on ordinary resumes and retried only when `--asr-fallback` is supplied.
- ASR fallback uses `scripts/nemotron_asr.py` to convert downloaded authorized media to mono WAV with system `ffmpeg` or Python package `imageio-ffmpeg`, then run a local NeMo ASR model such as `nvidia/nemotron-3.5-asr-streaming-0.6b`.
- License checks prefer the official YouTube Data API when `--youtube-api-key` or `YOUTUBE_API_KEY` is available, then fall back to metadata exposed by `yt-dlp`. Treat unknown license as not reusable; `--require-creative-commons` refuses unknown or Standard YouTube License videos.
- Without `ffmpeg`, MP4 downloads use YouTube's best progressive MP4 when available.
- For private, age-restricted, member-only, or region-gated videos, ask the user for a valid cookies file and pass `--cookies <path>`.
- Respect copyright, licenses, and platform terms. Do not help bypass access controls or download videos the user is not allowed to save.
