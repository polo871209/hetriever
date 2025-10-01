from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class DocumentChunk(BaseModel):
    """Represents a validated chunk of document content ready for indexing.

    Pydantic model that enforces validation rules on chunk data before
    it's stored in the vector database.

    Attributes:
        chunk_id: Unique identifier for the chunk.
        file_path: Path to the source file.
        repository_name: Name of the repository containing the file.
        content: The actual text content (validated non-empty).
        heading_context: Breadcrumb trail of headings.
        chunk_index: Zero-based index of this chunk within the file.
        token_count: Estimated tokens (constrained to 100-2000).
        metadata: Additional metadata from frontmatter and git.
    """

    chunk_id: str
    file_path: Path
    repository_name: str
    content: str
    heading_context: str
    chunk_index: int = Field(ge=0)
    token_count: int = Field(ge=100, le=2000)
    metadata: dict[str, Any]

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        """Validate that content is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("content must not be empty")
        return v

    @field_validator("chunk_id")
    @classmethod
    def chunk_id_not_empty(cls, v: str) -> str:
        """Validate that chunk_id is not empty."""
        if not v:
            raise ValueError("chunk_id must not be empty")
        return v
