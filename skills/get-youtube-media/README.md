# Get YouTube Media

Skill ID: `get-youtube-media`

Turn YouTube videos and YouTube search results into reusable research
artifacts: transcripts, captions, queue files, source notes, and optional
authorized media files.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/get-youtube-media

Parent package:
SkillForge Agent Skills Marketplace

Parent package repo URL:
https://github.com/medatasci/agent_skills

Distribution or marketplace:
SkillForge local catalog and Codex skill install workflow

Version or release channel:
Repository `main` branch when published

## Parent Collection

Parent collection:
SkillForge Agent Skills Marketplace

Collection URL:
https://github.com/medatasci/agent_skills

Categories:
Research, Media

Collection context:
This skill belongs in SkillForge's Research and Media collection because it
helps agents convert public video sources into durable local artifacts that can
be reviewed, summarized, cited, or revisited later.

## What This Skill Does

Get YouTube Media helps Codex search YouTube, inspect captions, retrieve
transcripts, save restartable retrieval queues, optionally run local ASR when a
video has no usable captions, and optionally download video or audio files when
the user is authorized to save the media. It is designed for research and
evidence workflows where the user wants repeatable local artifacts instead of a
one-off browser session.

## Why You Would Call It

Call this skill when:

- You have a YouTube URL or search topic and need transcript or caption text.
- You want to collect video sources for research, learning, or evidence review.
- You need a restartable queue because the retrieval job may span many videos.
- You have authorized media with no YouTube captions and want local ASR.

Use it to:

- Search YouTube for candidate research sources.
- Retrieve transcripts or captions from one or more YouTube URLs.
- Inspect available caption languages before retrieval.
- Save transcript text, SRT, JSON, or restartable queue files.
- Mark captionless videos as `needs_asr` and resume them with local ASR.
- Download authorized video or audio for local analysis.

Do not use it when:

- The user wants to bypass access controls, paywalls, age gates, region gates,
  or other restrictions.
- The user wants to save media they are not allowed to download.
- The task does not involve YouTube, captions, transcripts, or authorized media
  collection.

## Keywords

YouTube, transcripts, captions, video, media, research, evidence, SRT, JSON,
audio, MP4, yt-dlp, caption languages, restartable queue, source collection,
ASR, NeMo, Nemotron.

## Search Terms

YouTube transcripts, YouTube captions, video transcript extraction, video
research workflow, YouTube research sources, caption language inspection,
authorized YouTube media download, yt-dlp workflow, save YouTube captions,
queue YouTube transcript retrieval, captionless YouTube ASR, local Nemotron ASR.

## How It Works

The skill guides Codex through a read-first workflow:

1. Clarify whether the user provided a YouTube URL, a search query, or a results
   URL.
2. Search or inspect the requested videos.
3. Check available captions and language options when relevant.
4. Retrieve transcript or caption artifacts where available.
5. Mark videos with no usable captions as `needs_asr`, or run local ASR when
   `--asr-fallback` is explicitly supplied.
6. Save durable local outputs such as transcript text, SRT, JSON, Markdown, or a
   restartable queue.
7. Resume interrupted queue work when needed.
8. Download media only when the user is authorized and explicitly asks for local
   media files.

The skill may use bundled helper scripts and YouTube-related tools, but the
README keeps the user-facing contract at the workflow level.

## API And Options

SkillForge CLI options:

```text
python -m skillforge install get-youtube-media --scope global
python -m skillforge install get-youtube-media --scope project --project .
python -m skillforge search "youtube transcripts captions research" --json
python -m skillforge evaluate get-youtube-media --json
```

Skill-specific APIs, scripts, or options:

- YouTube URL, YouTube search query, or YouTube results URL.
- Optional language code for caption or transcript retrieval.
- Optional output folder or file format preference.
- Optional restartable queue workflow for multi-video jobs.
- Optional authorized media download workflow.
- Optional local ASR fallback with `ffmpeg`, NeMo, and
  `nvidia/nemotron-3.5-asr-streaming-0.6b`.

Configuration:

- `YOUTUBE_API_KEY` may be useful for workflows that need reliable YouTube Data
  API metadata or license checks.
- System `ffmpeg` or Python package `imageio-ffmpeg`, plus a Python environment
  with NVIDIA NeMo ASR, are required for `--asr-fallback`.
- Network access to YouTube is required for search, metadata, captions,
  transcripts, or media retrieval.

## Local ASR Fallback

Use local ASR only when the transcript-first path cannot produce a usable
caption artifact, or when a restartable queue item is marked `needs_asr`.

The retrieval order is:

1. Manual YouTube captions.
2. Automatic YouTube captions.
3. Local ASR on downloaded media that the user is authorized to process.

Do not use ASR just to replace a usable YouTube caption track. Caption files are
smaller, faster, and usually better for timestamped evidence work. Use ASR when
YouTube reports no supported caption tracks for the requested language, when a
queue item is `needs_asr`, or when the user explicitly wants local ASR for
authorized media.

Windows GPU setup used for validation:

```powershell
$PY = "C:\Users\medgar\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $PY -m venv .venv-youtube-asr-win
& .\.venv-youtube-asr-win\Scripts\python.exe -m pip install --upgrade pip setuptools wheel imageio-ffmpeg yt-dlp Cython packaging hf_xet
& .\.venv-youtube-asr-win\Scripts\python.exe -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
& .\.venv-youtube-asr-win\Scripts\python.exe -m pip install "nemo_toolkit[asr] @ git+https://github.com/NVIDIA/NeMo.git@main"
```

Use the GitHub `main` NeMo package for
`nvidia/nemotron-3.5-asr-streaming-0.6b`. Older PyPI-only NeMo releases may not
include the prompt-conditioned RNNT classes required by this checkpoint.

Set writable cache folders before running Windows ASR to avoid user-profile
permission failures:

```powershell
$env:MPLCONFIGDIR = "$PWD\.cache\youtube-asr-win\matplotlib"
$env:HF_HOME = "$PWD\.cache\youtube-asr-win\hf"
$env:TORCH_HOME = "$PWD\.cache\youtube-asr-win\torch"
```

Run the full fallback workflow:

```powershell
& .\.venv-youtube-asr-win\Scripts\python.exe scripts\youtube_media.py "https://www.youtube.com/watch?v=VIDEO_ID" --asr-fallback --asr-source audio --asr-model nvidia/nemotron-3.5-asr-streaming-0.6b --asr-lang en-US --asr-python .\.venv-youtube-asr-win\Scripts\python.exe --write-json
```

Use `--asr-source audio` by default because it is smaller and faster. Use
`--asr-source video` only when the workflow also needs a local MP4. On Windows,
use PowerShell `-LiteralPath` when reading generated files whose names include
YouTube IDs in square brackets, for example:

```powershell
Get-Content -LiteralPath ".\youtube-output\Example [VIDEO_ID].transcript.txt"
```

ASR output is labeled `source: local-asr`. Review it before clinical, research,
or quoted use because ASR can introduce medical and domain-specific errors.

## Inputs And Outputs

Inputs can include:

- YouTube URL.
- YouTube search query.
- YouTube results URL.
- Optional language code.
- Output folder or format preference.
- User confirmation that requested media downloads are authorized.
- Optional ASR model, ASR language/locale, and ASR Python executable.

Outputs can include:

- Transcript text.
- Caption files such as SRT.
- Local ASR transcript and ASR metadata JSON for captionless authorized media.
- Search result JSON or Markdown.
- Restartable queue JSON.
- Optional video or audio file.

Output locations:

- User-requested local output folder when provided.
- Current project or working directory when no explicit output folder is
  provided.

## Limitations

Known limitations:

- Transcript and caption availability depends on the video, caption language,
  YouTube access, and tool behavior.
- Local ASR fallback has no true caption timestamps by default; it writes a
  transcript and, when requested, a coarse single-segment JSON artifact.
- YouTube and related tools may rate-limit requests; queue-based workflows
  should pause and resume rather than retry aggressively.
- Media downloads are only for videos the user is authorized to save locally.
- The skill should not bypass private, age-restricted, member-only,
  region-gated, paywalled, or otherwise restricted content.
- `yt-dlp`, optional `ffmpeg`, optional NeMo/PyTorch, and optional
  `YOUTUBE_API_KEY` availability can affect which workflows are possible.

Choose another skill when:

- The source is a Hugging Face dataset rather than YouTube media.
- The goal is to record decisions and lessons after a research session rather
  than retrieve media artifacts.

## Examples

Beginner example:

```text
Use get-youtube-media to get the transcript for this YouTube URL and save it as
Markdown.
```

Task-specific example:

```text
Use get-youtube-media to search YouTube for videos about agent skill
marketplaces and save a restartable queue for the top results.
```

Safety-aware or bounded example:

```text
Use get-youtube-media to inspect available caption languages for these videos
before downloading any transcript files.
```

Troubleshooting or refinement example:

```text
Use get-youtube-media to resume the saved queue and tell me which videos still
do not have usable captions.
```

ASR fallback example:

```text
Use get-youtube-media to resume the queue and run local Nemotron ASR for videos
marked needs_asr, but only for videos I am authorized to process locally.
```

## Help And Getting Started

Start with:

```text
Find YouTube videos about <topic>, get transcripts for the best ones, and save
the results so I can review them later.
```

Provide:

- The YouTube URL, search query, or results URL.
- The desired output format or folder if you care where files go.

Ask for help when:

- A transcript is missing.
- A caption language is unexpected.
- A queue needs to resume.
- A queue item is marked `needs_asr`.
- You need to understand what files were created.

## How To Call From An LLM

Direct prompt:

```text
Use get-youtube-media to get captions and transcripts for this YouTube URL.
```

Task-based prompt:

```text
Use get-youtube-media to search YouTube for <topic>, retrieve available
transcripts for the top results, save the artifacts locally, and summarize what
you saved.
```

Guarded prompt:

```text
Use get-youtube-media, but download video or audio only if the workflow confirms
I am authorized to save it locally.
```

Find or install prompt:

```text
Find and install the SkillForge skill that helps with YouTube transcript
retrieval. Ask before installing anything from a peer catalog.
```

## How To Call From The CLI

Search for the skill:

```text
python -m skillforge search "youtube transcript extraction" --json
```

Show skill metadata:

```text
python -m skillforge info get-youtube-media --json
```

Install the skill into Codex:

```text
python -m skillforge install get-youtube-media --scope global
```

Evaluate the skill before publishing changes:

```text
python -m skillforge evaluate get-youtube-media --json
```

Remove the installed skill:

```text
python -m skillforge remove get-youtube-media --scope global --yes
```

## Trust And Safety

Risk level:
medium

Permissions:

- Network access to YouTube or YouTube APIs.
- Local file writes for transcript, queue, caption, and optional media outputs.
- Optional media download tools only when the user is authorized to save media.

Data handling:
Transcript, caption, queue, and optional media files are written locally to the
requested output location. The skill should not collect credentials or private
data unless the user explicitly provides a permitted API key for a supported
workflow.

Writes vs read-only:
The skill is read-only against YouTube services but writes local output files.
Optional downloads are local writes and should remain user-authorized.
Local ASR fallback downloads authorized media, converts it to mono WAV with
system `ffmpeg` or Python package `imageio-ffmpeg`, and runs the configured
local ASR Python environment.

External services:
YouTube, optionally the YouTube Data API, and optionally Hugging Face model
download endpoints when the local NeMo model is not already cached.

Credentials:
No credential is required for basic public transcript or caption workflows.
`YOUTUBE_API_KEY` is optional for API-backed metadata workflows.

User approval gates:

- Ask before downloading media files.
- Ask before using or storing any credential-like value.
- Stop if the request appears to bypass access controls or authorization.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues/new/choose

Send feedback when:

- A transcript fails.
- A caption language is confusing.
- A queue workflow is too slow or hard to resume.
- The examples do not match how you naturally ask for YouTube research help.

Promptable feedback:

```text
Send feedback on get-youtube-media that caption language selection was
confusing for a multi-video queue.
```

## Contributing

Contribution path:
Pull requests are welcome for safer transcript workflows, clearer queue
behavior, better examples, improved error messages, and updated YouTube tooling
notes.

Before opening a pull request:

- Update `skills/get-youtube-media/SKILL.md`, this README, bundled scripts, or
  references only where the behavior is verified.
- Run representative script checks when changing YouTube retrieval code.
- Run `python -m skillforge build-catalog` and
  `python -m skillforge evaluate get-youtube-media --json`.

## Author

Marc Edgar / medatasci

Maintainer status:
SkillForge-maintained example skill.

## Citations

Relevant method and tooling references:

- yt-dlp project: https://github.com/yt-dlp/yt-dlp
- YouTube Data API documentation: https://developers.google.com/youtube/v3

## Related Skills

- `project-retrospective`: record what was searched, retrieved, summarized, and
  missed after a research session.
- `skill-discovery-evaluation`: improve this skill's README, examples,
  metadata, and catalog discoverability.
- `huggingface-datasets`: use when the research source is a Hugging Face
  dataset instead of YouTube media.
