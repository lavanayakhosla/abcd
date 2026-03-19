"""File summarization utilities."""

from __future__ import annotations

from typing import Dict


def summarize_file(file_path: str, content: str, parsed: dict | None = None) -> Dict[str, str]:
    """Summarize a file for developer consumption.

    This is a lightweight heuristic summarizer. In production, this should
    be backed by an LLM or a more advanced summarization model.
    """

    lines = [l.strip() for l in content.splitlines() if l.strip()]
    summary_lines = []

    if parsed is not None:
        n_funcs = len(parsed.get("functions", []))
        n_classes = len(parsed.get("classes", []))
        imports = parsed.get("imports", [])
        summary_lines.append(f"Contains {n_funcs} function(s) and {n_classes} class(es).")
        if imports:
            summary_lines.append(f"Imports: {', '.join(imports[:5])}{'...' if len(imports) > 5 else ''}")

    # Use first few non-empty lines as a heuristic summary.
    if lines:
        summary_lines.append("Example starting lines:")
        summary_lines.extend(lines[:3])

    return {"type": "file_summary", "file": file_path, "summary": "\n".join(summary_lines)}
