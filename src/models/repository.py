from pathlib import Path

from pydantic import BaseModel, Field


class RepositoryMetadata(BaseModel):
    """Metadata for a git repository to be indexed.

    Validates repository information before indexing operations.

    Attributes:
        name: Repository name (lowercase alphanumeric with hyphens).
        path: Local filesystem path to the repository.
        remote_url: Git remote URL.
        branch: Current git branch name.
        commit_hash: Current git commit SHA (40 character hex string).
    """

    name: str = Field(pattern=r"^[a-z0-9-]+$")
    path: Path
    remote_url: str
    branch: str
    commit_hash: str = Field(min_length=40, max_length=40)
