#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
VENDOR_DIR = SKILL_DIR / "vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

try:
    import yt_dlp
except ModuleNotFoundError:
    print(
        "Missing dependency: yt-dlp. Install it with:\n"
        f"  {sys.executable} -m pip install --target \"{VENDOR_DIR}\" yt-dlp",
        file=sys.stderr,
    )
    raise SystemExit(2)


SUPPORTED_CAPTION_EXTS = {"json3", "srv3", "vtt", "srt", "ttml"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search YouTube, extract a transcript, and optionally download video/audio files."
    )
    parser.add_argument("target", nargs="?", help="YouTube video URL, YouTube results URL, or search query")
    parser.add_argument("-o", "--output-dir", default="youtube-output", help="Directory for outputs")
    parser.add_argument("--lang", default="en", help="Preferred caption language, such as en or es")
    parser.add_argument("--search", action="store_true", help="Treat target as a YouTube search query/results URL")
    parser.add_argument("--search-count", type=int, default=5, help="Number of YouTube search results to return")
    parser.add_argument("--search-only", action="store_true", help="Save search results without transcribing videos")
    parser.add_argument(
        "--transcribe-search-results",
        type=int,
        default=0,
        help="Transcribe the top N search results after saving the search result list",
    )
    parser.add_argument("--queue-file", help="Path for a restartable JSON retrieval queue")
    parser.add_argument("--queue-only", action="store_true", help="Create/update the queue and exit without retrieval")
    parser.add_argument("--resume-queue", help="Resume retrieval from an existing queue JSON file")
    parser.add_argument("--max-retries", type=int, default=5, help="Maximum attempts per queued item")
    parser.add_argument("--retry-sleep", type=int, default=60, help="Seconds to sleep between non-rate-limit retries")
    parser.add_argument("--rate-limit-sleep", type=int, default=900, help="Seconds to sleep after HTTP 429/rate-limit errors")
    parser.add_argument("--retry-backoff", type=float, default=2.0, help="Retry sleep multiplier after each failed attempt")
    parser.add_argument("--request-sleep", type=int, default=5, help="Seconds to sleep between queued videos")
    parser.add_argument("--list-languages", action="store_true", help="List available captions and exit")
    parser.add_argument("--skip-transcript", action="store_true", help="Only download media/metadata")
    parser.add_argument("--write-srt", action="store_true", help="Also write transcript as SRT")
    parser.add_argument("--write-json", action="store_true", help="Also write transcript segments as JSON")
    parser.add_argument("--download-video", action="store_true", help="Download an MP4 video file")
    parser.add_argument("--download-audio", action="store_true", help="Download a separate audio file")
    parser.add_argument(
        "--audio-format",
        choices=["m4a", "mp3", "webm", "best"],
        default="m4a",
        help="Preferred audio file format; mp3 requires ffmpeg",
    )
    parser.add_argument("--cookies", help="Path to a Netscape-format cookies.txt file")
    parser.add_argument("--force", action="store_true", help="Overwrite existing transcript files")
    parser.add_argument("--no-timestamps", action="store_true", help="Omit timestamps from TXT transcript")
    parser.add_argument("--quiet", action="store_true", help="Reduce yt-dlp output during downloads")
    return parser.parse_args()


def ydl_base_options(args: argparse.Namespace, quiet: bool = True) -> dict[str, Any]:
    options: dict[str, Any] = {
        "quiet": quiet,
        "no_warnings": quiet,
        "noplaylist": True,
    }
    if quiet:
        options["noprogress"] = True
    if args.cookies:
        options["cookiefile"] = args.cookies
    return options


def extract_info(args: argparse.Namespace, target: str) -> dict[str, Any]:
    options = ydl_base_options(args, quiet=True)
    options["skip_download"] = True
    with yt_dlp.YoutubeDL(options) as ydl:
        return ydl.extract_info(target, download=False)


def is_youtube_results_url(value: str) -> bool:
    parsed = urllib.parse.urlparse(value)
    return "youtube.com" in parsed.netloc.lower() and parsed.path == "/results"


def looks_like_youtube_video(value: str) -> bool:
    parsed = urllib.parse.urlparse(value)
    host = parsed.netloc.lower()
    if host.endswith("youtu.be") and parsed.path.strip("/"):
        return True
    if "youtube.com" in host and (parsed.path == "/watch" or parsed.path.startswith("/shorts/")):
        return True
    return False


def search_query_from_target(target: str) -> str:
    parsed = urllib.parse.urlparse(target)
    if is_youtube_results_url(target):
        query = urllib.parse.parse_qs(parsed.query).get("search_query", [""])[0]
        if query:
            return query
    return target.strip()


def should_search(args: argparse.Namespace) -> bool:
    if not args.target:
        return False
    return args.search or is_youtube_results_url(args.target) or not looks_like_youtube_video(args.target)


def video_url_from_info(info: dict[str, Any]) -> str:
    url = info.get("webpage_url") or info.get("url")
    video_id = info.get("id")
    if url and str(url).startswith("http"):
        return str(url)
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    raise RuntimeError("Could not determine a YouTube video URL from search result metadata.")


def sanitize_filename(value: str, max_length: int = 120) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', " ", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return (value[:max_length].strip(" .") or "youtube-video")


def output_stem(info: dict[str, Any]) -> str:
    video_id = info.get("id") or "unknown-id"
    title = sanitize_filename(info.get("title") or "youtube-video")
    return f"{title} [{video_id}]"


def unique_path(path: Path, force: bool) -> Path:
    if force or not path.exists():
        return path
    for index in range(1, 1000):
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find an unused output name for {path}")


def write_text(path: Path, text: str, force: bool = False) -> Path:
    path = unique_path(path, force)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def write_json(path: Path, data: Any, force: bool = False) -> Path:
    return write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", force=force)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def iso_after(seconds: float) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).replace(microsecond=0).isoformat()


def seconds_until(iso_text: str | None) -> float:
    if not iso_text:
        return 0.0
    target = datetime.fromisoformat(iso_text)
    if target.tzinfo is None:
        target = target.replace(tzinfo=timezone.utc)
    return max(0.0, (target - datetime.now(timezone.utc)).total_seconds())


def save_queue(path: Path, queue: dict[str, Any]) -> None:
    queue["updated_at"] = now_iso()
    queue["counts"] = queue_counts(queue)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    temp_path.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    temp_path.replace(path)


def load_queue(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def queue_counts(queue: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for task in queue.get("tasks", []):
        status = task.get("status", "queued")
        counts[status] = counts.get(status, 0) + 1
    counts["total"] = len(queue.get("tasks", []))
    return counts


def default_queue_path(output_dir: Path, name: str) -> Path:
    return output_dir / f"{sanitize_filename(name, max_length=90)}.queue.json"


def task_from_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": entry.get("id"),
        "title": entry.get("title"),
        "webpage_url": entry.get("webpage_url") or entry.get("url"),
        "channel": entry.get("channel"),
        "duration": entry.get("duration"),
        "status": "queued",
        "attempts": 0,
        "created_at": now_iso(),
        "started_at": None,
        "completed_at": None,
        "next_retry_at": None,
        "last_error": None,
        "result": None,
    }


def merge_queue_tasks(existing: list[dict[str, Any]], incoming: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged = {task.get("webpage_url"): task for task in existing if task.get("webpage_url")}
    for task in incoming:
        url = task.get("webpage_url")
        if not url:
            continue
        if url in merged:
            preserved = merged[url]
            for key in ("id", "title", "channel", "duration"):
                if not preserved.get(key) and task.get(key):
                    preserved[key] = task[key]
        else:
            merged[url] = task
    return list(merged.values())


def build_queue(
    args: argparse.Namespace,
    output_dir: Path,
    queue_path: Path,
    name: str,
    tasks: list[dict[str, Any]],
    query: str | None = None,
) -> dict[str, Any]:
    if queue_path.exists() and not args.force:
        queue = load_queue(queue_path)
        queue["tasks"] = merge_queue_tasks(queue.get("tasks", []), tasks)
    else:
        queue = {
            "version": 1,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "name": name,
            "query": query,
            "output_dir": str(output_dir.resolve()),
            "tasks": tasks,
        }
    save_queue(queue_path, queue)
    return queue


def is_rate_limit_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return (
        "http error 429" in text
        or "429" in text and "too many requests" in text
        or "rate limit" in text
        or "ratelimit" in text
        or "quotaexceeded" in text
        or "soft block" in text
    )


def retry_delay(args: argparse.Namespace, exc: Exception, attempt_index: int) -> float:
    base = args.rate_limit_sleep if is_rate_limit_error(exc) else args.retry_sleep
    return max(0.0, float(base) * (max(args.retry_backoff, 1.0) ** max(attempt_index - 1, 0)))


def sleep_for_retry(args: argparse.Namespace, exc: Exception, attempt_index: int, label: str) -> None:
    seconds = retry_delay(args, exc, attempt_index)
    if is_rate_limit_error(exc):
        reason = "rate limit"
    else:
        reason = "transient error"
    print(f"{label}: {reason}; sleeping {int(seconds)} seconds before retry.", file=sys.stderr)
    if seconds > 0:
        time.sleep(seconds)


def run_with_retries(args: argparse.Namespace, label: str, operation: Any) -> Any:
    max_retries = max(1, args.max_retries)
    for attempt in range(1, max_retries + 1):
        try:
            return operation()
        except Exception as exc:
            if attempt >= max_retries:
                raise
            sleep_for_retry(args, exc, attempt, label)
    raise RuntimeError(f"{label}: retry loop exited unexpectedly")


def write_search_markdown(path: Path, query: str, entries: list[dict[str, Any]], force: bool = False) -> Path:
    lines = [f"# YouTube Search: {query}", ""]
    for index, entry in enumerate(entries, start=1):
        title = entry.get("title") or "Untitled"
        url = entry.get("webpage_url") or entry.get("url") or ""
        channel = entry.get("channel") or entry.get("uploader") or "Unknown channel"
        duration = entry.get("duration")
        duration_text = clock(float(duration)) if duration else "unknown duration"
        lines.append(f"{index}. [{title}]({url})")
        lines.append(f"   - Channel: {channel}")
        lines.append(f"   - Duration: {duration_text}")
        if entry.get("view_count") is not None:
            lines.append(f"   - Views: {entry['view_count']}")
        lines.append("")
    return write_text(path, "\n".join(lines).rstrip() + "\n", force=force)


def normalize_search_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": entry.get("id"),
        "title": entry.get("title"),
        "webpage_url": video_url_from_info(entry),
        "channel": entry.get("channel") or entry.get("uploader"),
        "duration": entry.get("duration"),
        "view_count": entry.get("view_count"),
        "upload_date": entry.get("upload_date"),
        "description": entry.get("description"),
    }


def search_youtube(args: argparse.Namespace, output_dir: Path) -> dict[str, Any]:
    query = search_query_from_target(args.target)
    if not query:
        raise RuntimeError("Search query is empty.")
    count = max(1, args.search_count)
    options = ydl_base_options(args, quiet=True)
    options["skip_download"] = True
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(f"ytsearch{count}:{query}", download=False)
    raw_entries = [entry for entry in (info.get("entries") or []) if entry]
    entries = [normalize_search_entry(entry) for entry in raw_entries]
    stem = sanitize_filename(query, max_length=90) or "youtube-search"
    result: dict[str, Any] = {
        "query": query,
        "count": len(entries),
        "results": entries,
    }
    json_path = write_json(output_dir / f"{stem}.search-results.json", result, force=args.force)
    markdown_path = write_search_markdown(output_dir / f"{stem}.search-results.md", query, entries, force=args.force)
    result["search_results_json_path"] = str(json_path.resolve())
    result["search_results_markdown_path"] = str(markdown_path.resolve())
    return result


def available_languages(info: dict[str, Any]) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for source, key in (("manual", "subtitles"), ("automatic", "automatic_captions")):
        for lang, tracks in sorted((info.get(key) or {}).items()):
            exts = sorted({track.get("ext", "?") for track in tracks})
            rows.append((source, lang, ",".join(exts)))
    return rows


def print_languages(info: dict[str, Any]) -> None:
    rows = available_languages(info)
    if not rows:
        print("No caption tracks reported by yt-dlp.")
        return
    print("Available captions:")
    for source, lang, exts in rows:
        print(f"  {lang:12} {source:9} {exts}")


def language_score(candidate: str, requested: str) -> int:
    if candidate == requested:
        return 0
    if candidate.lower() == requested.lower():
        return 1
    if candidate.split("-")[0].lower() == requested.split("-")[0].lower():
        return 2
    if candidate.lower().startswith(requested.lower()):
        return 3
    return 99


def choose_language(pool: dict[str, list[dict[str, Any]]], requested: str) -> str | None:
    matches = sorted(
        (lang for lang in pool if language_score(lang, requested) < 99),
        key=lambda lang: (language_score(lang, requested), lang),
    )
    return matches[0] if matches else None


def choose_caption_track(info: dict[str, Any], requested_lang: str) -> tuple[str, str, dict[str, Any]]:
    for source, key in (("manual", "subtitles"), ("automatic", "automatic_captions")):
        pool = info.get(key) or {}
        lang = choose_language(pool, requested_lang)
        if not lang:
            continue
        tracks = pool.get(lang) or []
        supported = [track for track in tracks if track.get("ext") in SUPPORTED_CAPTION_EXTS and track.get("url")]
        if not supported:
            continue
        rank = {"json3": 0, "srv3": 1, "vtt": 2, "srt": 3, "ttml": 4}
        supported.sort(key=lambda track: rank.get(track.get("ext", ""), 99))
        return source, lang, supported[0]

    langs = ", ".join(f"{source}:{lang}" for source, lang, _ in available_languages(info)) or "none"
    raise RuntimeError(f"No supported captions found for language '{requested_lang}'. Available: {langs}")


def fetch_caption(track: dict[str, Any]) -> str:
    request = urllib.request.Request(track["url"], headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    return data.decode(charset, errors="replace")


def clean_caption_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def segments_from_json3(raw: str) -> list[dict[str, Any]]:
    data = json.loads(raw)
    segments: list[dict[str, Any]] = []
    for event in data.get("events", []):
        text = "".join(part.get("utf8", "") for part in event.get("segs", []))
        text = clean_caption_text(text)
        if not text:
            continue
        start = (event.get("tStartMs") or 0) / 1000
        duration = (event.get("dDurationMs") or 0) / 1000
        end = start + duration if duration else None
        segments.append({"start": start, "end": end, "text": text})
    return segments


def seconds_from_timecode(value: str) -> float:
    parts = value.replace(",", ".").split(":")
    parts = [float(part) for part in parts]
    if len(parts) == 3:
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours = 0.0
        minutes, seconds = parts
    else:
        return float(parts[0])
    return hours * 3600 + minutes * 60 + seconds


def parse_xml_duration(value: str | None) -> float | None:
    if not value:
        return None
    value = value.strip()
    if value.endswith("ms"):
        return float(value[:-2]) / 1000
    if value.endswith("s"):
        return float(value[:-1])
    if ":" in value:
        return seconds_from_timecode(value)
    return float(value)


def segments_from_srv3_xml(raw: str) -> list[dict[str, Any]]:
    root = ET.fromstring(raw)
    segments: list[dict[str, Any]] = []
    for node in root.iter():
        tag = node.tag.split("}")[-1]
        if tag != "p":
            continue
        text = clean_caption_text("".join(node.itertext()))
        if not text:
            continue
        start = float(node.attrib.get("t") or 0) / 1000
        duration = float(node.attrib.get("d") or 0) / 1000
        end = start + duration if duration else None
        segments.append({"start": start, "end": end, "text": text})
    return segments


def segments_from_ttml_xml(raw: str) -> list[dict[str, Any]]:
    root = ET.fromstring(raw)
    segments: list[dict[str, Any]] = []
    for node in root.iter():
        tag = node.tag.split("}")[-1]
        if tag != "p":
            continue
        text = clean_caption_text("".join(node.itertext()))
        if not text:
            continue
        start = parse_xml_duration(node.attrib.get("begin")) or 0.0
        duration = parse_xml_duration(node.attrib.get("dur"))
        end = parse_xml_duration(node.attrib.get("end"))
        if end is None and duration is not None:
            end = start + duration
        segments.append({"start": start, "end": end, "text": text})
    return segments


def segments_from_vtt_or_srt(raw: str) -> list[dict[str, Any]]:
    lines = raw.replace("\ufeff", "").splitlines()
    segments: list[dict[str, Any]] = []
    index = 0
    timing_re = re.compile(
        r"(?P<start>\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3})\s+-->\s+"
        r"(?P<end>\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3})"
    )
    while index < len(lines):
        match = timing_re.search(lines[index])
        if not match:
            index += 1
            continue
        start = seconds_from_timecode(match.group("start"))
        end = seconds_from_timecode(match.group("end"))
        index += 1
        text_lines: list[str] = []
        while index < len(lines) and lines[index].strip():
            if not lines[index].strip().isdigit():
                text_lines.append(lines[index])
            index += 1
        text = clean_caption_text(" ".join(text_lines))
        if text:
            segments.append({"start": start, "end": end, "text": text})
    return segments


def caption_segments(raw: str, extension: str) -> list[dict[str, Any]]:
    if extension == "json3":
        return segments_from_json3(raw)
    if extension == "srv3":
        return segments_from_srv3_xml(raw)
    if extension == "ttml":
        return segments_from_ttml_xml(raw)
    if extension in {"vtt", "srt"}:
        return segments_from_vtt_or_srt(raw)
    raise RuntimeError(f"Unsupported caption format: {extension}")


def clock(seconds: float) -> str:
    total = int(max(seconds, 0))
    hours, remainder = divmod(total, 3600)
    minutes, sec = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{sec:02}"


def srt_time(seconds: float) -> str:
    seconds = max(seconds, 0)
    whole = int(seconds)
    millis = int(round((seconds - whole) * 1000))
    hours, remainder = divmod(whole, 3600)
    minutes, sec = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{sec:02},{millis:03}"


def txt_transcript(segments: list[dict[str, Any]], include_timestamps: bool) -> str:
    lines: list[str] = []
    for segment in segments:
        text = segment["text"]
        if include_timestamps:
            lines.append(f"[{clock(segment['start'])}] {text}")
        else:
            lines.append(text)
    return "\n".join(lines).strip() + "\n"


def srt_transcript(segments: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for index, segment in enumerate(segments, start=1):
        start = float(segment["start"])
        end = segment.get("end")
        if end is None or end <= start:
            next_start = segments[index]["start"] if index < len(segments) else start + 2.0
            end = max(start + 0.5, float(next_start) - 0.01)
        blocks.append(f"{index}\n{srt_time(start)} --> {srt_time(float(end))}\n{segment['text']}")
    return "\n\n".join(blocks).strip() + "\n"


def has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def collect_matching_files(output_dir: Path, stem: str, kind: str) -> list[str]:
    prefix = f"{stem}.{kind}."
    paths = []
    for path in output_dir.iterdir():
        if not path.name.startswith(prefix):
            continue
        if path.suffix in {".part", ".ytdl"} or not path.is_file():
            continue
        paths.append(str(path.resolve()))
    return sorted(paths)


def download_video(args: argparse.Namespace, target: str, output_dir: Path, stem: str) -> list[str]:
    options = ydl_base_options(args, quiet=args.quiet)
    if has_ffmpeg():
        video_format = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best"
        options["merge_output_format"] = "mp4"
    else:
        video_format = "best[ext=mp4]/best"
        print("ffmpeg not found; using YouTube's best progressive MP4 when available.", file=sys.stderr)
    options.update(
        {
            "format": video_format,
            "outtmpl": str(output_dir / f"{stem}.video.%(ext)s"),
            "overwrites": args.force,
            "continuedl": True,
        }
    )
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([target])
    return collect_matching_files(output_dir, stem, "video")


def download_audio(args: argparse.Namespace, target: str, output_dir: Path, stem: str) -> list[str]:
    options = ydl_base_options(args, quiet=args.quiet)
    if args.audio_format == "mp3":
        if not has_ffmpeg():
            raise RuntimeError("MP3 audio conversion requires ffmpeg. Use --audio-format m4a or install ffmpeg.")
        options["format"] = "bestaudio/best"
        options["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "0"}
        ]
    elif args.audio_format == "m4a":
        options["format"] = "bestaudio[ext=m4a]/bestaudio/best"
    elif args.audio_format == "webm":
        options["format"] = "bestaudio[ext=webm]/bestaudio/best"
    else:
        options["format"] = "bestaudio/best"
    options.update(
        {
            "outtmpl": str(output_dir / f"{stem}.audio.%(ext)s"),
            "overwrites": args.force,
            "continuedl": True,
        }
    )
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([target])
    return collect_matching_files(output_dir, stem, "audio")


def process_video(args: argparse.Namespace, target: str, output_dir: Path, write_summary: bool = True) -> dict[str, Any]:
    info = extract_info(args, target)
    stem = output_stem(info)
    result: dict[str, Any] = {
        "id": info.get("id"),
        "title": info.get("title"),
        "webpage_url": info.get("webpage_url") or target,
        "duration": info.get("duration"),
        "outputs": {},
    }

    if args.list_languages:
        print_languages(info)
        if not (args.download_video or args.download_audio):
            return result

    if not args.skip_transcript:
        source, lang, track = choose_caption_track(info, args.lang)
        extension = track.get("ext", "txt")
        raw = fetch_caption(track)
        segments = caption_segments(raw, extension)
        if not segments:
            raise RuntimeError(f"Caption track {lang} ({extension}) did not contain readable transcript text.")

        raw_path = write_text(output_dir / f"{stem}.captions.{extension}", raw, force=args.force)
        txt_path = write_text(
            output_dir / f"{stem}.transcript.txt",
            txt_transcript(segments, include_timestamps=not args.no_timestamps),
            force=args.force,
        )
        result["transcript"] = {
            "source": source,
            "language": lang,
            "caption_extension": extension,
            "segments": len(segments),
            "raw_caption_path": str(raw_path.resolve()),
            "txt_path": str(txt_path.resolve()),
        }
        if args.write_srt:
            srt_path = write_text(output_dir / f"{stem}.transcript.srt", srt_transcript(segments), force=args.force)
            result["transcript"]["srt_path"] = str(srt_path.resolve())
        if args.write_json:
            json_path = write_json(output_dir / f"{stem}.segments.json", segments, force=args.force)
            result["transcript"]["segments_json_path"] = str(json_path.resolve())

    if args.download_video:
        result["outputs"]["video_files"] = download_video(args, target, output_dir, stem)
    if args.download_audio:
        result["outputs"]["audio_files"] = download_audio(args, target, output_dir, stem)

    if write_summary:
        summary_path = write_json(output_dir / f"{stem}.summary.json", result, force=args.force)
        result["summary_path"] = str(summary_path.resolve())

    return result


def pending_queue_tasks(queue: dict[str, Any]) -> list[dict[str, Any]]:
    retryable = {"queued", "in_progress", "retry_wait", "failed"}
    tasks = []
    for task in queue.get("tasks", []):
        if task.get("status", "queued") not in retryable:
            continue
        if task.get("status") == "failed" and int(task.get("attempts") or 0) >= 1:
            tasks.append(task)
            continue
        tasks.append(task)
    return tasks


def process_queue(args: argparse.Namespace, queue: dict[str, Any], queue_path: Path, output_dir: Path) -> dict[str, Any]:
    processed: list[dict[str, Any]] = []
    tasks = pending_queue_tasks(queue)
    max_retries = max(1, args.max_retries)

    for index, task in enumerate(tasks, start=1):
        if int(task.get("attempts") or 0) >= max_retries and task.get("status") == "failed":
            continue
        target = task.get("webpage_url")
        if not target:
            task["status"] = "failed"
            task["last_error"] = "Missing webpage_url"
            save_queue(queue_path, queue)
            processed.append(task)
            continue

        wait_seconds = seconds_until(task.get("next_retry_at")) if task.get("status") == "retry_wait" else 0.0
        if wait_seconds > 0:
            print(
                f"{task.get('title') or target}: waiting {int(wait_seconds)} seconds until queued retry time.",
                file=sys.stderr,
            )
            time.sleep(wait_seconds)

        while int(task.get("attempts") or 0) < max_retries:
            task["status"] = "in_progress"
            task["attempts"] = int(task.get("attempts") or 0) + 1
            task["started_at"] = now_iso()
            task["next_retry_at"] = None
            save_queue(queue_path, queue)

            try:
                task["result"] = process_video(args, target, output_dir, write_summary=True)
                task["status"] = "done"
                task["completed_at"] = now_iso()
                task["last_error"] = None
                task["next_retry_at"] = None
                save_queue(queue_path, queue)
                processed.append(task)
                break
            except Exception as exc:
                task["last_error"] = str(exc)
                if int(task.get("attempts") or 0) >= max_retries:
                    task["status"] = "failed"
                    task["completed_at"] = now_iso()
                    task["next_retry_at"] = None
                    save_queue(queue_path, queue)
                    processed.append(task)
                    break

                delay = retry_delay(args, exc, int(task.get("attempts") or 1))
                task["status"] = "retry_wait"
                task["next_retry_at"] = iso_after(delay)
                save_queue(queue_path, queue)
                sleep_for_retry(args, exc, int(task.get("attempts") or 1), task.get("title") or target)

        if index < len(tasks) and args.request_sleep > 0:
            time.sleep(args.request_sleep)

    return {
        "queue_path": str(queue_path.resolve()),
        "counts": queue_counts(queue),
        "processed": [
            {
                "id": task.get("id"),
                "title": task.get("title"),
                "webpage_url": task.get("webpage_url"),
                "status": task.get("status"),
                "attempts": task.get("attempts"),
                "last_error": task.get("last_error"),
                "result": task.get("result"),
            }
            for task in processed
        ],
    }


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.resume_queue:
        queue_path = Path(args.resume_queue).expanduser().resolve()
        queue = load_queue(queue_path)
        queued_output_dir = Path(queue.get("output_dir") or output_dir).expanduser().resolve()
        queued_output_dir.mkdir(parents=True, exist_ok=True)
        result = process_queue(args, queue, queue_path, queued_output_dir)
    elif should_search(args):
        result = run_with_retries(args, "youtube search", lambda: search_youtube(args, output_dir))
        limit = max(0, args.transcribe_search_results)
        queued_entries = result["results"][:limit] if limit else result["results"]
        queue_path = Path(args.queue_file).expanduser().resolve() if args.queue_file else default_queue_path(output_dir, result["query"])
        queue = build_queue(
            args,
            output_dir,
            queue_path,
            name=result["query"],
            query=result["query"],
            tasks=[task_from_entry(entry) for entry in queued_entries],
        )
        result["queue_path"] = str(queue_path.resolve())
        result["queue_counts"] = queue_counts(queue)
        if not (args.search_only or args.queue_only) and limit:
            queue_result = process_queue(args, queue, queue_path, output_dir)
            result["queue_counts"] = queue_result["counts"]
            result["transcriptions"] = queue_result["processed"]
        write_json(Path(result["search_results_json_path"]), result, force=True)
    else:
        if not args.target:
            raise RuntimeError("Provide a YouTube URL/search query, or pass --resume-queue <queue.json>.")
        if args.queue_file or args.queue_only:
            queue_path = Path(args.queue_file).expanduser().resolve() if args.queue_file else default_queue_path(output_dir, "single-video")
            entry = {"id": None, "title": None, "webpage_url": args.target}
            queue = build_queue(
                args,
                output_dir,
                queue_path,
                name=args.target,
                query=None,
                tasks=[task_from_entry(entry)],
            )
            result = {"queue_path": str(queue_path.resolve()), "queue_counts": queue_counts(queue)}
            if not args.queue_only:
                result.update(process_queue(args, queue, queue_path, output_dir))
        else:
            result = run_with_retries(args, args.target, lambda: process_video(args, args.target, output_dir, write_summary=True))

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
