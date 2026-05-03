from __future__ import annotations

from pathlib import Path
import os
import shutil
import stat


TRANSIENT_FILE_NAMES = {".DS_Store", "Thumbs.db"}
TRANSIENT_DIR_NAMES = {"__pycache__", ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
TRANSIENT_SUFFIXES = {".pyc", ".pyo"}


def _retry_remove_readonly(function, target, exc_info) -> None:
    try:
        current_mode = os.stat(target).st_mode
        os.chmod(target, current_mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    except OSError:
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    function(target)


def remove_tree(path: str | Path) -> None:
    target = Path(path)
    if not target.exists():
        return
    try:
        shutil.rmtree(target, onexc=_retry_remove_readonly)
    except TypeError:
        shutil.rmtree(target, onerror=_retry_remove_readonly)


def is_transient_path(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return (
        path.name in TRANSIENT_FILE_NAMES
        or path.suffix.lower() in TRANSIENT_SUFFIXES
        or any(part in TRANSIENT_DIR_NAMES for part in parts)
    )


def ignore_transient_artifacts(directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        path = Path(directory) / name
        if (
            name in TRANSIENT_FILE_NAMES
            or name in TRANSIENT_DIR_NAMES
            or path.suffix.lower() in TRANSIENT_SUFFIXES
        ):
            ignored.add(name)
    return ignored


def copy_tree(source: str | Path, destination: str | Path) -> None:
    shutil.copytree(source, destination, ignore=ignore_transient_artifacts)
