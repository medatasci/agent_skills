from __future__ import annotations

import argparse
import os


CHATTINESS_MODES = ("coach", "normal", "terse", "silent")
DEFAULT_CHATTINESS = "normal"


def normalize_chattiness(value: str | None = None) -> str:
    raw = value or os.environ.get("SKILLFORGE_CHATTINESS") or DEFAULT_CHATTINESS
    mode = raw.strip().lower()
    return mode if mode in CHATTINESS_MODES else DEFAULT_CHATTINESS


def add_chattiness_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--chattiness",
        choices=CHATTINESS_MODES,
        help="Control extra human guidance: coach, normal, terse, or silent",
    )


def chattiness_from_args(args: argparse.Namespace) -> str:
    return normalize_chattiness(getattr(args, "chattiness", None))


def is_coach(mode: str) -> bool:
    return normalize_chattiness(mode) == "coach"


def is_normal_or_coach(mode: str) -> bool:
    return normalize_chattiness(mode) in {"normal", "coach"}


def is_silent(mode: str) -> bool:
    return normalize_chattiness(mode) == "silent"
