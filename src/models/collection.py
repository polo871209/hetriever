from datetime import datetime

from pydantic import BaseModel, Field


class CollectionMetadata(BaseModel):
    """Metadata for a ChromaDB collection representing a repository.

    Stores repository-level information for tracking indexed content.

    Attributes:
        repository_url: URL of the source repository.
        last_updated: Timestamp of last indexing operation.
        commit_hash: Git commit SHA (40 character hex string).
        total_documents: Total number of markdown files indexed.
        total_chunks: Total number of chunks created from documents.
    """

    repository_url: str
    last_updated: datetime
    commit_hash: str = Field(min_length=40, max_length=40)
    total_documents: int = Field(ge=0)
    total_chunks: int = Field(ge=0)
