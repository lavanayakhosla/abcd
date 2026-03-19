from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    repo_root: Path
    chroma_dir: Path
    embedding_model: str
    embedding_task: str
    embedding_inference_mode: str
    embedding_device: str | None
    exclude_dirs: list[str]
    include_exts: list[str]

    @classmethod
    def from_env(cls, repo_root: Path | str):
        repo_root = Path(repo_root)
        if not repo_root.exists():
            repo_root = repo_root.resolve()

        # If the user is in a subdirectory, try to locate an existing index.
        search_root = repo_root
        while True:
            candidate = search_root / ".codeintel_chroma"
            if candidate.exists():
                repo_root = search_root
                break
            if search_root.parent == search_root:
                break
            search_root = search_root.parent

        chroma_dir = Path(os.getenv("CODEINTEL_CHROMA_DIR", repo_root / ".codeintel_chroma"))
        return cls(
            repo_root=repo_root,
            chroma_dir=chroma_dir,
            embedding_model=os.getenv("CODEINTEL_EMBEDDING_MODEL", "nomic-embed-text-v1.5"),
            embedding_task=os.getenv("CODEINTEL_EMBEDDING_TASK", "search_document"),
            embedding_inference_mode=os.getenv("CODEINTEL_EMBEDDING_MODE", "local"),
            embedding_device=os.getenv("CODEINTEL_EMBEDDING_DEVICE", None),
            exclude_dirs=[
                ".git",
                "node_modules",
                "build",
                "dist",
                "__pycache__",
                ".venv",
                "venv",
            ],
            include_exts=[".py", ".java", ".kt", ".cpp", ".js"],
        )
