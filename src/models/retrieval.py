from pydantic import BaseModel, Field


class RetrievalMatch(BaseModel):
    """Single search result match from vector similarity search.

    Attributes:
        chunk_id: Unique identifier of the matched chunk.
        content: The text content of the matched chunk.
        score: Similarity score between query and chunk (0.0 to 1.0).
        repository: Name of the repository containing the match.
        file_path: Path to the source file.
        heading_context: Breadcrumb trail of headings.
        metadata: Additional metadata associated with the chunk.
    """

    chunk_id: str
    content: str
    score: float = Field(ge=0.0, le=1.0)
    repository: str
    file_path: str
    heading_context: str
    metadata: dict[str, str | bool | list[str]]


class RetrievalResult(BaseModel):
    """Complete search result containing query, matches, and timing.

    Attributes:
        query: The search query string.
        matches: List of matching chunks ordered by relevance.
        total_results: Total number of results found (may exceed matches returned).
        search_time_ms: Search execution time in milliseconds.
    """

    query: str
    matches: list[RetrievalMatch]
    total_results: int = Field(ge=0)
    search_time_ms: float = Field(ge=0.0)

    def model_post_init(self, __context) -> None:
        """Validate that total_results is consistent with matches count."""
        if self.total_results < len(self.matches):
            raise ValueError("total_results must be >= len(matches)")
