"""High-level query engine that routes queries and builds context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from codeintel.retrieval.retriever import Retriever
from codeintel.storage.chroma_client import ChromaClient


@dataclass
class QueryResult:
    file_summaries: List[Dict[str, Any]]
    code_results: List[Dict[str, Any]]
    explanation: str


class QueryEngine:
    def __init__(self, chroma: ChromaClient):
        self.chroma = chroma
        self.retriever = Retriever(chroma)

    def _classify(self, query: str) -> str:
        q = query.lower().strip()
        if "explain" in q or "what does" in q or "how" in q:
            return "explain"
        if "trace" in q or "call" in q or "flow" in q:
            return "trace"
        return "general"

    def explain_file(self, file_path: str) -> QueryResult:
        """Explain a specific file by fetching its stored summary."""
        get_res = self.chroma.summary_collection.get(ids=[file_path])

        def _first_item(value: Any):
            if value is None:
                return []
            if isinstance(value, list) and value and isinstance(value[0], list):
                return value[0]
            if isinstance(value, list):
                return value
            return [value]

        docs = _first_item(get_res.get("documents"))
        metas = _first_item(get_res.get("metadatas"))

        summary_text = docs[0] if docs else "(no summary found)"
        file_summary = metas[0].get("file") if metas and isinstance(metas[0], dict) else file_path

        explanation = f"Explaining file: {file_summary}\n\n{summary_text}"
        return QueryResult(file_summaries=[{"file": file_summary, "summary": summary_text}], code_results=[], explanation=explanation)

    def trace_function(self, function_name: str, top_k: int = 5) -> QueryResult:
        """Trace a function by semantic search over code chunks."""
        raw = self.retriever.search(function_name, top_k=top_k)
        code_docs = (raw.get("code", {}).get("documents") or [[]])[0] or []
        code_metas = (raw.get("code", {}).get("metadatas") or [[]])[0] or []
        code_dists = (raw.get("code", {}).get("distances") or [[]])[0] or []

        code_results = []
        for i, doc in enumerate(code_docs):
            meta = code_metas[i] if i < len(code_metas) else {}
            code_results.append(
                {
                    "score": (code_dists[i] if i < len(code_dists) else None),
                    "file": meta.get("file"),
                    "type": meta.get("type"),
                    "name": meta.get("name"),
                    "content": doc,
                }
            )

        explanation = self._build_explanation(function_name, "trace", [], code_results)
        return QueryResult(file_summaries=[], code_results=code_results, explanation=explanation)

    def ask(self, query: str, top_k: int = 5) -> QueryResult:
        qtype = self._classify(query)
        raw = self.retriever.search(query, top_k=top_k)

        summaries = []
        code_results = []

        # ChromaDB query results are batched; the first element is the result list.
        summary_docs = (raw.get("summaries", {}).get("documents") or [[]])[0] or []
        summary_metas = (raw.get("summaries", {}).get("metadatas") or [[]])[0] or []
        summary_dists = (raw.get("summaries", {}).get("distances") or [[]])[0] or []
        for i, doc in enumerate(summary_docs):
            summaries.append(
                {
                    "score": (summary_dists[i] if i < len(summary_dists) else None),
                    "file": (summary_metas[i].get("file") if i < len(summary_metas) else None),
                    "summary": doc,
                }
            )

        code_docs = (raw.get("code", {}).get("documents") or [[]])[0] or []
        code_metas = (raw.get("code", {}).get("metadatas") or [[]])[0] or []
        code_dists = (raw.get("code", {}).get("distances") or [[]])[0] or []
        for i, doc in enumerate(code_docs):
            meta = code_metas[i] if i < len(code_metas) else {}
            code_results.append(
                {
                    "score": (code_dists[i] if i < len(code_dists) else None),
                    "file": meta.get("file"),
                    "type": meta.get("type"),
                    "name": meta.get("name"),
                    "content": doc,
                }
            )

        explanation = self._build_explanation(query, qtype, summaries, code_results)
        return QueryResult(file_summaries=summaries, code_results=code_results, explanation=explanation)

    def _build_explanation(
        self,
        query: str,
        qtype: str,
        summaries: List[Dict[str, Any]],
        code_results: List[Dict[str, Any]],
    ) -> str:
        lines: List[str] = []
        lines.append(f"Query type: {qtype}")
        lines.append(f"Query: {query}")
        lines.append("")
        if summaries:
            lines.append("=== FILE SUMMARIES ===")
            for s in summaries[:3]:
                lines.append(f"- {s.get('file')}: {s.get('summary')}")
            lines.append("")
        if code_results:
            lines.append("=== KEY FUNCTIONS ===")
            for c in code_results[:3]:
                content = str(c.get("content") or "").replace("\n", " ")
                lines.append(
                    f"- {c.get('file')}::{c.get('name')} ({c.get('type')}): {content[:120]}"
                )
            lines.append("")
        lines.append("=== EXPLANATION ===")
        lines.append(
            "This response is based on semantic search over indexed content. Use `codeintel explain <file>` or `codeintel trace <function>` for more targeted results."
        )
        return "\n".join(lines)
