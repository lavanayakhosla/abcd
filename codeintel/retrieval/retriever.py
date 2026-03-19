"""Semantic retrieval across code chunks and file summaries."""

from __future__ import annotations

from typing import Any, Dict, List

from codeintel.storage.chroma_client import ChromaClient


class Retriever:
    def __init__(self, chroma: ChromaClient):
        self.chroma = chroma

    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search both code chunks and file summaries."""
        code_res = self.chroma.query_code(query, top_k=top_k)
        summary_res = self.chroma.query_summaries(query, top_k=top_k)
        return {"code": code_res, "summaries": summary_res}
