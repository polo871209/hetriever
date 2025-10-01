import re
import time
from datetime import UTC, datetime

from chromadb import Collection, PersistentClient
from chromadb.config import Settings

from src.models.document import DocumentChunk
from src.models.retrieval import RetrievalMatch, RetrievalResult

MAX_COLLECTION_NAME_LENGTH = 63
MAX_BATCH_SIZE = 1000
MAX_SEARCH_LIMIT = 100


class ChromaDBConnectionError(Exception):
    """Raised when ChromaDB connection or operation fails."""

    pass


class CollectionNotFoundError(Exception):
    """Raised when a requested collection does not exist."""

    pass


class InvalidCollectionNameError(Exception):
    """Raised when collection name violates naming constraints."""

    pass


class DuplicateChunkIDError(Exception):
    """Raised when attempting to add a chunk with an existing ID."""

    pass


class EmptyQueryError(Exception):
    """Raised when search query is empty or whitespace-only."""

    pass


class InvalidLimitError(Exception):
    """Raised when search limit is outside valid range."""

    pass


class CollectionInfo:
    """Information about a ChromaDB collection.

    Attributes:
        name: Collection name (repository identifier).
        chunk_count: Number of chunks stored in collection.
        metadata: Collection-level metadata (timestamps, config, etc.).
    """

    def __init__(self, name: str, chunk_count: int, metadata: dict):
        self.name = name
        self.chunk_count = chunk_count
        self.metadata = metadata


class ChromaDBClient:
    """Client for interacting with ChromaDB vector storage.

    Provides methods for managing collections, storing document chunks,
    and performing semantic search.

    Attributes:
        client: ChromaDB PersistentClient instance.
    """

    def __init__(
        self,
        path: str = "./chroma_data",
        embedding_model: str = "sentence-transformers/all-mpnet-base-v2",
    ):
        """Initialize ChromaDB client.

        Args:
            path: Directory path for ChromaDB persistent storage.
            embedding_model: HuggingFace embedding model to use.

        Raises:
            ChromaDBConnectionError: If connection to ChromaDB fails.
        """
        try:
            from chromadb.utils import embedding_functions

            self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model
            )
            self.client = PersistentClient(
                path=path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
        except Exception as e:
            raise ChromaDBConnectionError(f"Cannot connect to ChromaDB at {path}: {e}") from e

    def create_collection(
        self,
        repository_name: str,
        metadata: dict[str, str | int],
    ) -> Collection:
        """Create a new collection for a repository, replacing if exists.

        Args:
            repository_name: Repository identifier (lowercase alphanumeric with hyphens).
            metadata: Collection metadata (timestamps, config, etc.).

        Returns:
            Created ChromaDB collection.

        Raises:
            InvalidCollectionNameError: If name violates constraints.
            ChromaDBConnectionError: If collection creation fails.
        """
        if not re.match(r"^[a-z0-9-]+$", repository_name):
            raise InvalidCollectionNameError(
                f"Collection name must match ^[a-z0-9-]+$, got: {repository_name}"
            )
        if len(repository_name) > MAX_COLLECTION_NAME_LENGTH:
            raise InvalidCollectionNameError(
                f"Collection name must be <= {MAX_COLLECTION_NAME_LENGTH} characters, "
                f"got: {len(repository_name)}"
            )

        try:
            self.client.get_collection(repository_name)
            self.client.delete_collection(repository_name)
        except Exception:
            pass

        try:
            return self.client.create_collection(
                name=repository_name,
                metadata=metadata,
                embedding_function=self._embedding_function,  # type: ignore
            )
        except Exception as e:
            raise ChromaDBConnectionError(f"Failed to create collection: {e}") from e

    def get_collection(self, repository_name: str) -> Collection:
        """Retrieve an existing collection by name.

        Args:
            repository_name: Repository identifier.

        Returns:
            ChromaDB collection object.

        Raises:
            CollectionNotFoundError: If collection does not exist.
        """
        try:
            return self.client.get_collection(
                repository_name, embedding_function=self._embedding_function
            )  # type: ignore
        except Exception as e:
            raise CollectionNotFoundError(f"Collection '{repository_name}' not found") from e

    def add_chunks(
        self,
        collection: Collection,
        chunks: list[DocumentChunk],
        batch_size: int = 100,
    ) -> None:
        """Add document chunks to a collection with automatic embedding.

        ChromaDB automatically generates embeddings for chunk content using
        its default embedding model. Chunks are added in batches for efficiency.

        Args:
            collection: Target ChromaDB collection.
            chunks: List of document chunks to add.
            batch_size: Number of chunks per batch (1-1000, default 100).

        Raises:
            ValueError: If batch_size is invalid or chunks have empty content.
            DuplicateChunkIDError: If chunk ID already exists in collection.
        """
        if not (1 <= batch_size <= MAX_BATCH_SIZE):
            raise ValueError(f"batch_size must be between 1 and {MAX_BATCH_SIZE}")

        for chunk in chunks:
            if not chunk.content or not chunk.content.strip():
                raise ValueError(f"Chunk {chunk.chunk_id} has empty content")

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            ids = [chunk.chunk_id for chunk in batch]
            documents = [chunk.content for chunk in batch]
            metadatas: list[dict[str, str | int | float | bool]] = []
            for chunk in batch:
                meta: dict[str, str | int | float | bool] = {
                    "file_path": str(chunk.file_path),
                    "repository": chunk.repository_name,
                    "heading_context": chunk.heading_context,
                    "chunk_index": chunk.chunk_index,
                }
                for k, v in chunk.metadata.items():
                    if isinstance(v, list):
                        meta[k] = ",".join(str(x) for x in v)
                    else:
                        meta[k] = v
                metadatas.append(meta)

            existing_ids = set(collection.get(ids=ids)["ids"])
            duplicate_ids = [chunk_id for chunk_id in ids if chunk_id in existing_ids]
            if duplicate_ids:
                raise DuplicateChunkIDError(f"Chunk ID already exists: {duplicate_ids[0]}")

            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,  # type: ignore
            )

    def search_chunks(
        self,
        collection: Collection,
        query: str,
        limit: int = 10,
        where: dict | None = None,
        rerank: bool = True,
    ) -> RetrievalResult:
        """Search for similar chunks using semantic vector similarity with optional reranking.

        First performs bi-encoder search to retrieve initial candidates, then optionally
        reranks using a cross-encoder for improved accuracy.

        Args:
            collection: ChromaDB collection to search.
            query: Natural language search query.
            limit: Maximum number of results (1-100, default 10).
            where: Optional metadata filter (ChromaDB where clause).
            rerank: Whether to rerank results with cross-encoder (default True).

        Returns:
            RetrievalResult containing matches and search metadata.

        Raises:
            EmptyQueryError: If query is empty or whitespace-only.
            InvalidLimitError: If limit is outside valid range.
            ChromaDBConnectionError: If search operation fails.
        """
        if not query or not query.strip():
            raise EmptyQueryError("Search query cannot be empty")
        if not (1 <= limit <= MAX_SEARCH_LIMIT):
            raise InvalidLimitError(f"Limit must be between 1 and {MAX_SEARCH_LIMIT}, got: {limit}")

        start_time = time.perf_counter()

        initial_limit = limit * 3 if rerank else limit

        try:
            results = collection.query(
                query_texts=[query],
                n_results=min(initial_limit, MAX_SEARCH_LIMIT),
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            raise ChromaDBConnectionError(f"Search failed: {e}") from e

        matches = []
        ids_list = results.get("ids")
        if ids_list and ids_list[0]:
            for i in range(len(ids_list[0])):
                distances_list = results.get("distances")
                if not distances_list or not distances_list[0]:
                    continue
                distance = distances_list[0][i]
                score = 1 / (1 + distance)

                metadatas_list = results.get("metadatas")
                documents_list = results.get("documents")
                if (
                    not metadatas_list
                    or not metadatas_list[0]
                    or not documents_list
                    or not documents_list[0]
                ):
                    continue

                metadata = metadatas_list[0][i]
                matches.append(
                    RetrievalMatch(
                        chunk_id=ids_list[0][i],
                        content=documents_list[0][i],
                        score=score,
                        repository=str(metadata["repository"]),
                        file_path=str(metadata["file_path"]),
                        heading_context=str(metadata["heading_context"]),
                        metadata={
                            k: str(v) if not isinstance(v, (list, bool)) else v
                            for k, v in metadata.items()
                            if k
                            not in ["repository", "file_path", "heading_context", "chunk_index"]
                        },
                    )
                )

        if rerank and matches:
            matches = self._rerank_matches(query, matches, limit)

        search_time_ms = (time.perf_counter() - start_time) * 1000

        return RetrievalResult(
            query=query,
            matches=matches[:limit],
            total_results=len(matches[:limit]),
            search_time_ms=search_time_ms,
        )

    def _rerank_matches(
        self, query: str, matches: list[RetrievalMatch], top_k: int
    ) -> list[RetrievalMatch]:
        """Rerank matches using cross-encoder for improved accuracy.

        Args:
            query: Original search query.
            matches: Initial retrieval matches to rerank.
            top_k: Number of top results to return after reranking.

        Returns:
            Reranked list of matches with updated scores.
        """
        if not hasattr(self, "_reranker"):
            from sentence_transformers import CrossEncoder

            self._reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        pairs = [[query, match.content] for match in matches]
        scores = self._reranker.predict(pairs)

        for match, score in zip(matches, scores):
            match.score = float(score)

        return sorted(matches, key=lambda x: x.score, reverse=True)[:top_k]

    def list_collections(self) -> list[CollectionInfo]:
        """List all collections with their metadata and statistics.

        Returns:
            Sorted list of CollectionInfo objects (by name).

        Raises:
            ChromaDBConnectionError: If listing operation fails.
        """
        try:
            collections = self.client.list_collections()
        except Exception as e:
            raise ChromaDBConnectionError(f"Failed to list collections: {e}") from e

        infos = []
        for col in collections:
            try:
                collection = self.client.get_collection(col.name)
                infos.append(
                    CollectionInfo(
                        name=col.name,
                        chunk_count=collection.count(),
                        metadata=col.metadata or {},
                    )
                )
            except Exception:
                pass

        return sorted(infos, key=lambda x: x.name)

    def delete_collection(self, repository_name: str) -> int:
        """Delete a collection and all its chunks.

        Args:
            repository_name: Repository identifier.

        Returns:
            Number of chunks that were deleted.

        Raises:
            CollectionNotFoundError: If collection does not exist.
            ChromaDBConnectionError: If deletion fails.
        """
        collection = self.get_collection(repository_name)
        chunk_count = collection.count()

        try:
            self.client.delete_collection(repository_name)
        except Exception as e:
            raise ChromaDBConnectionError(f"Failed to delete collection: {e}") from e

        return chunk_count

    def update_collection_metadata(
        self,
        collection: Collection,
        metadata: dict[str, str | int],
    ) -> None:
        """Update collection metadata with new values and timestamp.

        Merges new metadata with existing, automatically adding 'last_updated'
        timestamp in ISO format.

        Args:
            collection: ChromaDB collection to update.
            metadata: New metadata key-value pairs to merge.

        Raises:
            ChromaDBConnectionError: If metadata update fails.
        """
        try:
            current_metadata = collection.metadata or {}
            updated_metadata = {**current_metadata, **metadata}
            updated_metadata["last_updated"] = datetime.now(UTC).isoformat()

            collection.modify(metadata=updated_metadata)
        except Exception as e:
            raise ChromaDBConnectionError(f"Failed to update metadata: {e}") from e
