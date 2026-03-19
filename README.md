# CodeIntel (abcd)

A minimal code intelligence system that indexes a codebase using embeddings + metadata and enables semantic queries (explain, trace, ask).

## Quickstart

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

> In this workspace, the required dependencies are already installed (tree-sitter, chromadb, nomic).

### 2) Index a repository

```bash
python -m codeintel.main index <repo_path>
```

Example:

```bash
python -m codeintel.main index sample_repo
```

This creates a local index at `<repo_path>/.codeintel_chroma`.

### 3) Ask questions

```bash
python -m codeintel.main ask "What does this repo do?" --repo sample_repo
```

### 4) Explain a file

```bash
python -m codeintel.main explain sample_repo/auth.py --repo sample_repo
```

### 5) Trace a function

```bash
python -m codeintel.main trace login_user --repo sample_repo
```

## Project structure

- `codeintel/`
  - `main.py` — CLI entrypoint
  - `config.py` — configuration loader
  - `ingestion/` — parsing, chunking, summarizing and indexing logic
  - `storage/` — ChromaDB storage + embedding glue
  - `retrieval/` — semantic retrieval and query routing
  - `llm/` — placeholder for LLM integration
  - `utils/` — helper utilities

## Notes

- Embeddings are generated via `nomic` (local inference via `gpt4all`).
- Tree-sitter is used for parsing supported languages; a regex fallback is used otherwise.
- The system is designed to be extended with better LLM support (Qwen 2.5, etc.) and richer graph analysis.
