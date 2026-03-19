"""Parse code files into structured units (functions, classes, imports)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from tree_sitter import Language, Parser
except ImportError:  # pragma: no cover
    Language = None  # type: ignore
    Parser = None  # type: ignore

# Lazy language loaders for supported languages.
_LANGUAGE_FACTORIES: dict[str, Any] = {}


def _get_tree_sitter_language(ext: str) -> Optional[Language]:
    """Return a Tree-sitter Language object for the given file extension."""
    # Map extension to language module name.
    mapping = {
        ".py": "tree_sitter_python",
        ".js": "tree_sitter_javascript",
        ".java": "tree_sitter_java",
        ".kt": "tree_sitter_kotlin",
        ".cpp": "tree_sitter_cpp",
        ".cc": "tree_sitter_cpp",
        ".c": "tree_sitter_cpp",
        ".hpp": "tree_sitter_cpp",
    }

    module_name = mapping.get(ext.lower())
    if not module_name:
        return None

    if module_name in _LANGUAGE_FACTORIES:
        return _LANGUAGE_FACTORIES[module_name]()

    try:
        module = __import__(module_name)
        if hasattr(module, "language"):
            factory = getattr(module, "language")
            # `language` is a callable that returns a tree_sitter.Language capsule.
            def _make() -> Language:
                caps = factory()
                # Wrap capsule into Language class for parser compatibility.
                return Language(caps)

            _LANGUAGE_FACTORIES[module_name] = _make
            return _make()
    except Exception:
        return None

    return None


def _parse_with_treesitter(ext: str, source: str) -> Dict[str, Any]:
    """Parse source code with tree-sitter if available."""
    lang = _get_tree_sitter_language(ext)
    if lang is None or Parser is None:
        return {}

    parser = Parser()
    parser.language = lang
    tree = parser.parse(bytes(source, "utf8"))
    root = tree.root_node

    functions: List[Dict[str, str]] = []
    classes: List[Dict[str, str]] = []
    imports: List[str] = []

    def _walk(node):
        yield node
        for child in node.children:
            yield from _walk(child)

    # Simplified extraction logic: look for nodes by type.
    for node in _walk(root):
        if node.type in ("function_definition", "function_declaration", "method_definition"):
            # find function name child
            name_node = next((c for c in node.children if c.type == "identifier"), None)
            name = name_node.text.decode("utf-8") if name_node is not None else ""
            code = source[node.start_byte : node.end_byte]
            if name:
                functions.append({"name": name, "code": code})
        elif node.type in ("class_definition", "class_declaration"):
            name_node = next((c for c in node.children if c.type == "identifier"), None)
            name = name_node.text.decode("utf-8") if name_node is not None else ""
            code = source[node.start_byte : node.end_byte]
            if name:
                classes.append({"name": name, "code": code})
        elif node.type in ("import_statement", "import_declaration", "import", "import_clause"):
            imports.append(source[node.start_byte : node.end_byte].strip())

    return {"functions": functions, "classes": classes, "imports": imports}


def _parse_with_regex(ext: str, source: str) -> Dict[str, Any]:
    """Fallback parser that uses regex heuristics."""
    functions: List[Dict[str, str]] = []
    classes: List[Dict[str, str]] = []
    imports: List[str] = []

    if ext == ".py":
        func_re = re.compile(r"^def\s+(\w+)\s*\(.*\):", re.MULTILINE)
        class_re = re.compile(r"^class\s+(\w+)\s*(\(|:)", re.MULTILINE)
        import_re = re.compile(r"^(?:from\s+[\.\w]+\s+import\s+.+|import\s+.+)$", re.MULTILINE)

        for m in func_re.finditer(source):
            name = m.group(1)
            functions.append({"name": name, "code": _extract_block(source, m.start())})
        for m in class_re.finditer(source):
            name = m.group(1)
            classes.append({"name": name, "code": _extract_block(source, m.start())})
        imports = [line.strip() for line in import_re.findall(source)]
    elif ext in (".js", ".java", ".kt", ".cpp"):
        func_re = re.compile(r"\b(function|fun|def)\s+(\w+)\b")
        class_re = re.compile(r"\bclass\s+(\w+)\b")
        import_re = re.compile(r"^\s*import\s+([\w\.\*]+)", re.MULTILINE)

        for m in func_re.finditer(source):
            name = m.group(2)
            functions.append({"name": name, "code": ""})
        for m in class_re.finditer(source):
            name = m.group(1)
            classes.append({"name": name, "code": ""})
        imports = [m.group(1) for m in import_re.finditer(source)]

    return {"functions": functions, "classes": classes, "imports": imports}


def _extract_block(source: str, start_idx: int) -> str:
    """Extract a contiguous block of code starting at a given index (heuristic)."""
    lines = source[start_idx:].splitlines(keepends=True)
    if not lines:
        return ""
    if lines[0].strip() == "":
        return ""
    # Include the first line and any following indented lines
    block = [lines[0]]
    indent = len(lines[0]) - len(lines[0].lstrip())
    for line in lines[1:]:
        stripped = line.lstrip(" \t")
        if stripped == "" or (len(line) - len(stripped)) > indent:
            block.append(line)
        else:
            break
    return "".join(block)


def parse_file(path: Path) -> Dict[str, Any]:
    """Parse a file and return its code structure."""
    content = path.read_text(encoding="utf-8", errors="ignore")
    ext = path.suffix.lower()
    parsed = _parse_with_treesitter(ext, content)
    if not parsed:
        parsed = _parse_with_regex(ext, content)
    return {"file": str(path), "content": content, **parsed}
