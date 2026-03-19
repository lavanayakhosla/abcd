"""ChromaDB client wrapper for code intelligence storage."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, List, Optional

import chromadb
from chromadb.config import Settings
from chromadb.api import Collection

from nomic.embed import text as nomic_text

from codeintel.config import Config
from codeintel.utils.logger import get_logger

logger = get_logger(__name__)


class NomicEmbeddingFunction:
    """Embedding function wrapper that satisfies ChromaDB embedding interface."""

    def __init__(self, config: Config):
        self.config = config

    def __call__(self, input: list[str]) -> List[List[float]]:  # type: ignore[override]
        if not input:
            return []
        resp = nomic_text(
            input,
            model=self.config.embedding_model,
            task_type=self.config.embedding_task,
            inference_mode=self.config.embedding_inference_mode,
            device=self.config.embedding_device,
        )
        return resp.get("embeddings", [])

    def embed_query(self, input: list[str]) -> List[List[float]]:  # type: ignore[override]
        # ChromaDB may call embed_query for query strings. Delegate to __call__.
        return self(input)

    @staticmethod
    def name() -> str:
        return "nomic"


class ChromaClient:
    def __init__(self, config: Config):
        self.config = config
        settings = Settings(is_persistent=True, persist_directory=str(config.chroma_dir))
        self.client = chromadb.Client(settings=settings)
        self._embedding_fn = NomicEmbeddingFunction(config)

        self.code_collection = self.client.get_or_create_collection(
            name="code_chunks", embedding_function=self._embedding_fn
        )
        self.summary_collection = self.client.get_or_create_collection(
            name="file_summaries", embedding_function=self._embedding_fn
        )

    def add_code_chunks(self, chunks: list[dict]) -> None:
        if not chunks:
            return
        ids = [c["id"] for c in chunks]
        docs = [c["content"] for c in chunks]
        metadatas = [
            {
                "file": c.get("file"),
                "type": c.get("type"),
                "name": c.get("name"),
                "imports": c.get("imports", []),
            }
            for c in chunks
        ]
        self.code_collection.add(ids=ids, documents=docs, metadatas=metadatas)

    def add_file_summary(self, summary: dict) -> None:
        self.summary_collection.add(
            ids=[summary["file"]],
            documents=[summary.get("summary", "")],
            metadatas=[{"file": summary.get("file"), "type": "file_summary"}],
        )

    def query_code(self, query: str, top_k: int = 5) -> dict:
        return self.code_collection.query(query_texts=[query], n_results=top_k)

    def query_summaries(self, query: str, top_k: int = 5) -> dict:
        return self.summary_collection.query(query_texts=[query], n_results=top_k)
