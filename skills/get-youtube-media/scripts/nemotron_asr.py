#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from contextlib import contextmanager
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert local YouTube media to mono WAV and transcribe it with NVIDIA NeMo ASR."
    )
    parser.add_argument("media_path", help="Local media file, such as MP4, M4A, WebM, MP3, or WAV")
    parser.add_argument("--model", default="nvidia/nemotron-3.5-asr-streaming-0.6b")
    parser.add_argument("--lang", default="auto", help="Language/locale passed to NeMo when supported")
    parser.add_argument("--txt-out", required=True, help="Transcript text output path")
    parser.add_argument("--json-out", required=True, help="ASR metadata JSON output path")
    parser.add_argument("--segments-out", help="Optional single-segment JSON output path")
    parser.add_argument("--wav-out", help="Optional path for the mono WAV intermediate")
    parser.add_argument("--sample-rate", type=int, default=16000, help="WAV sample rate for ASR")
    parser.add_argument("--keep-wav", action="store_true", help="Keep the converted mono WAV file")
    return parser.parse_args()


def require_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    try:
        import imageio_ffmpeg
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "ASR fallback requires ffmpeg to convert media to mono WAV. Install ffmpeg or "
            "install imageio-ffmpeg in the ASR Python environment."
        ) from exc
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    if not ffmpeg:
        raise RuntimeError("ASR fallback could not locate ffmpeg or imageio-ffmpeg's bundled ffmpeg.")
    return ffmpeg


def wav_duration(path: Path) -> float | None:
    try:
        with wave.open(str(path), "rb") as handle:
            frames = handle.getnframes()
            rate = handle.getframerate()
            return frames / float(rate) if rate else None
    except Exception:
        return None


def convert_to_wav(media_path: Path, wav_path: Path, sample_rate: int) -> None:
    ffmpeg = require_ffmpeg()
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg,
        "-y",
        "-i",
        str(media_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        str(wav_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if completed.returncode != 0:
        stderr = (completed.stderr or completed.stdout or "unknown ffmpeg error").strip()
        raise RuntimeError(f"ffmpeg failed while preparing ASR audio: {stderr[-4000:]}")


def transcription_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list) and value:
        return transcription_text(value[0])
    if isinstance(value, tuple) and value:
        return transcription_text(value[0])
    if isinstance(value, dict):
        for key in ("text", "transcript", "pred_text"):
            if key in value:
                return transcription_text(value[key])
    text = getattr(value, "text", None)
    if text is not None:
        return str(text).strip()
    return str(value).strip()


@contextmanager
def tolerate_windows_temp_cleanup_lock() -> Any:
    if os.name != "nt":
        yield
        return

    original_rmtree = tempfile.TemporaryDirectory._rmtree

    def rmtree_ignore_permission_error(cls: type[tempfile.TemporaryDirectory], name: str, ignore_errors: bool = False, repeated: bool = False) -> None:
        try:
            original_rmtree(name, ignore_errors=ignore_errors, repeated=repeated)
        except PermissionError:
            # NeMo may briefly keep its generated manifest open during
            # TemporaryDirectory cleanup on Windows. The ASR result is already
            # produced; leaving a temp directory behind is preferable to
            # failing the transcription.
            return

    tempfile.TemporaryDirectory._rmtree = classmethod(rmtree_ignore_permission_error)
    try:
        yield
    finally:
        tempfile.TemporaryDirectory._rmtree = original_rmtree


def run_nemo_asr(model_name: str, wav_path: Path, lang: str) -> tuple[str, list[str]]:
    try:
        import nemo.collections.asr as nemo_asr
        from nemo.collections.asr.models.rnnt_bpe_models_prompt import RNNTPromptTranscribeConfig
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing dependency: NVIDIA NeMo. Install NeMo ASR in the ASR Python environment before "
            "using --asr-fallback."
        ) from exc

    warnings: list[str] = []
    asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name=model_name)
    target_lang = lang or "auto"
    config = RNNTPromptTranscribeConfig(
        use_lhotse=False,
        batch_size=1,
        num_workers=0,
        target_lang=target_lang,
        verbose=True,
    )
    try:
        with tolerate_windows_temp_cleanup_lock():
            output = asr_model.transcribe([str(wav_path)], override_config=config)
    except TypeError:
        warnings.append("Installed NeMo transcribe() did not accept RNNTPromptTranscribeConfig; retried without it.")
        with tolerate_windows_temp_cleanup_lock():
            output = asr_model.transcribe([str(wav_path)], batch_size=1, num_workers=0, target_lang=target_lang)
    return transcription_text(output), warnings


def main() -> int:
    args = parse_args()
    media_path = Path(args.media_path).expanduser().resolve()
    txt_path = Path(args.txt_out).expanduser().resolve()
    json_path = Path(args.json_out).expanduser().resolve()
    wav_path = (
        Path(args.wav_out).expanduser().resolve()
        if args.wav_out
        else txt_path.with_name(f"{txt_path.stem}.asr.wav")
    )

    if not media_path.exists():
        raise RuntimeError(f"ASR media file does not exist: {media_path}")

    convert_to_wav(media_path, wav_path, args.sample_rate)
    text, warnings = run_nemo_asr(args.model, wav_path, args.lang)
    duration = wav_duration(wav_path)

    txt_path.parent.mkdir(parents=True, exist_ok=True)
    txt_path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")

    segments_json_path = None
    segments = 0
    if args.segments_out:
        segment = {"start": 0.0, "end": duration, "text": text, "source": "local-asr"}
        segments_path = Path(args.segments_out).expanduser().resolve()
        segments_path.parent.mkdir(parents=True, exist_ok=True)
        segments_path.write_text(json.dumps([segment], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        segments_json_path = str(segments_path)
        segments = 1 if text else 0

    result = {
        "source": "local-asr",
        "engine": "nemo",
        "model": args.model,
        "language": args.lang,
        "input_path": str(media_path),
        "wav_path": str(wav_path),
        "wav_retained": bool(args.keep_wav),
        "txt_path": str(txt_path),
        "json_path": str(json_path),
        "segments_json_path": segments_json_path,
        "segments": segments or (1 if text else 0),
        "duration": duration,
        "text": text,
        "warnings": warnings,
    }

    if not args.keep_wav:
        try:
            wav_path.unlink()
            result["wav_path"] = None
        except FileNotFoundError:
            result["wav_path"] = None

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
