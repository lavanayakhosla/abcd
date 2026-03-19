"""Filesystem utilities used across the CodeIntel pipeline."""

import os
from pathlib import Path
from typing import Iterator


def is_binary_file(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(2048)
            if b"\0" in chunk:
                return True
        return False
    except Exception:
        return True


def list_source_files(root: Path, exclude_dirs: list[str], include_exts: list[str]) -> Iterator[Path]:
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel == ".":
            rel = ""
        parts = rel.split(os.sep) if rel else []
        if any(p in exclude_dirs for p in parts):
            dirnames[:] = []
            continue

        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for fname in filenames:
            path = Path(dirpath) / fname
            if path.suffix.lower() in include_exts and not is_binary_file(path):
                yield path


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return path.read_text(encoding="utf-8", errors="ignore")
