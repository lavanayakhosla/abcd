"""Schema definitions for stored metadata."""

from dataclasses import dataclass


@dataclass
class ChunkMetadata:
    file: str
    type: str
    name: str | None


@dataclass
class FileSummaryMetadata:
    file: str
