"""CLI entrypoint for CodeIntel."""

from __future__ import annotations

import argparse
import sys

from codeintel.config import Config
from codeintel.ingestion.indexer import Indexer
from codeintel.retrieval.query_engine import QueryEngine
from codeintel.utils.logger import get_logger

logger = get_logger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="codeintel")
    sub = parser.add_subparsers(dest="command")

    idx = sub.add_parser("index", help="Index a repository into the embedding store")
    idx.add_argument("repo", help="Path to the repository to index")

    ask = sub.add_parser("ask", help="Ask a semantic question about the codebase")
    ask.add_argument("query", help="Natural language query")
    ask.add_argument("--repo", default=".", help="Repository root (where the index is stored)")

    explain = sub.add_parser("explain", help="Explain a file")
    explain.add_argument("file", help="File path to explain")
    explain.add_argument("--repo", default=".", help="Repository root (where the index is stored)")

    trace = sub.add_parser("trace", help="Trace a function")
    trace.add_argument("function", help="Function name to trace")
    trace.add_argument("--repo", default=".", help="Repository root (where the index is stored)")

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 1

    if args.command == "index":
        config = Config.from_env(args.repo)
        indexer = Indexer(config)
        stats = indexer.index()
        print(f"Indexed {stats['files']} files, {stats['chunks']} chunks into {config.chroma_dir}")
        return 0

    # For query commands, use the configured repo root (supports --repo).
    repo_root = getattr(args, "repo", ".")
    config = Config.from_env(repo_root)
    from codeintel.storage.chroma_client import ChromaClient

    chroma = ChromaClient(config)
    engine = QueryEngine(chroma)

    if args.command == "ask":
        result = engine.ask(args.query)
        print(result.explanation)
        return 0

    if args.command == "explain":
        result = engine.explain_file(args.file)
        print(result.explanation)
        return 0

    if args.command == "trace":
        result = engine.trace_function(args.function)
        print(result.explanation)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
