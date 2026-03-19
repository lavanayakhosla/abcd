"""Lightweight dependency graph based on imports."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Set


class CodeGraph:
    """A very lightweight graph of file->imports relationships."""

    def __init__(self):
        self.imports: Dict[str, Set[str]] = defaultdict(set)

    def add_file_imports(self, file_path: str, imports: Iterable[str]) -> None:
        for imp in imports:
            self.imports[file_path].add(imp)

    def related_files(self, file_path: str) -> List[str]:
        return list(self.imports.get(file_path, []))

    def all_files(self) -> List[str]:
        return list(self.imports.keys())
