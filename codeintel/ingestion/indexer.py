"""Main ingestion pipeline for indexing a repository."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from codeintel.config import Config
from codeintel.ingestion.chunker import chunks_from_parse
from codeintel.ingestion.parser import parse_file
from codeintel.ingestion.summarizer import summarize_file
from codeintel.storage.chroma_client import ChromaClient
from codeintel.utils.file_utils import list_source_files
from codeintel.utils.logger import get_logger

logger = get_logger(__name__)


class Indexer:
    def __init__(self, config: Config):
        self.config = config
        self.chroma = ChromaClient(config)

    def index(self) -> Dict[str, int]:
        """Traverse the repo, parse files, chunk, summarize, and store in ChromaDB."""
        files_indexed = 0
        chunks_indexed = 0

        for path in list_source_files(self.config.repo_root, self.config.exclude_dirs, self.config.include_exts):
            try:
                parsed = parse_file(path)
                chunks = chunks_from_parse(parsed)
                for chunk in chunks:
                    # ensure file content available for fallback chunks
                    if not chunk.get("content"):
                        chunk["content"] = parsed.get("content", "")
                self.chroma.add_code_chunks(chunks)

                summary = summarize_file(str(path), parsed.get("content", ""), parsed)
                self.chroma.add_file_summary(summary)

                files_indexed += 1
                chunks_indexed += len(chunks)
            except Exception as e:
                logger.warning("Failed to index %s: %s", path, e)

        logger.info("Indexed %d files and %d chunks", files_indexed, chunks_indexed)
        return {"files": files_indexed, "chunks": chunks_indexed}
