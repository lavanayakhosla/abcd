"""Chunk parsed code into embedding-friendly documents."""

from __future__ import annotations

from typing import Any, Dict, List


def chunks_from_parse(parse: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert parse output into chunk documents for indexing."""
    file_path = parse.get("file", "<unknown>")
    chunks: List[Dict[str, Any]] = []

    for fn in parse.get("functions", []):
        name = fn.get("name") or "<unnamed>"
        chunks.append(
            {
                "id": f"{file_path}::function::{name}",
                "type": "function",
                "file": file_path,
                "name": name,
                "content": fn.get("code", ""),
                "imports": parse.get("imports", []),
            }
        )

    for cls in parse.get("classes", []):
        name = cls.get("name") or "<unnamed>"
        chunks.append(
            {
                "id": f"{file_path}::class::{name}",
                "type": "class",
                "file": file_path,
                "name": name,
                "content": cls.get("code", ""),
                "imports": parse.get("imports", []),
            }
        )

    # Fallback: if no functions/classes, index full file so we can still answer queries.
    if not chunks:
        chunks.append(
            {
                "id": f"{file_path}::file",
                "type": "file",
                "file": file_path,
                "name": None,
                "content": parse.get("content", ""),
                "imports": parse.get("imports", []),
            }
        )

    return chunks
