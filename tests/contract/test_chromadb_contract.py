from pathlib import Path

import pytest

from src.models.document import DocumentChunk
from src.storage import ChromaDBClient
from src.storage.chromadb_client import (
    CollectionNotFoundError,
    DuplicateChunkIDError,
    EmptyQueryError,
    InvalidCollectionNameError,
)


@pytest.fixture
def chroma_client(tmp_path):
    return ChromaDBClient(str(tmp_path / "chroma_test"))


@pytest.fixture
def test_collection(chroma_client):
    return chroma_client.create_collection(
        "test-docs",
        {
            "repository_url": "https://github.com/test/test",
            "last_updated": "2025-09-30T00:00:00Z",
            "commit_hash": "0" * 40,
            "total_documents": 0,
            "total_chunks": 0,
        },
    )


@pytest.mark.contract
def test_create_collection_success(chroma_client):
    collection = chroma_client.create_collection(
        "istio-docs",
        {
            "repository_url": "https://github.com/istio/istio.io",
            "last_updated": "2025-09-30T00:00:00Z",
            "commit_hash": "a" * 40,
            "total_documents": 247,
            "total_chunks": 1500,
        },
    )
    assert collection.name == "istio-docs"
    assert collection.metadata["repository_url"] == "https://github.com/istio/istio.io"


@pytest.mark.contract
def test_create_collection_invalid_name(chroma_client):
    with pytest.raises(InvalidCollectionNameError):
        chroma_client.create_collection("Invalid_Name!", {})


@pytest.mark.contract
def test_create_collection_idempotent(chroma_client):
    chroma_client.create_collection(
        "istio-docs",
        {
            "repository_url": "https://github.com/istio/istio.io",
            "last_updated": "2025-09-30T00:00:00Z",
            "commit_hash": "a" * 40,
            "total_documents": 100,
            "total_chunks": 500,
        },
    )
    collection = chroma_client.create_collection(
        "istio-docs",
        {
            "repository_url": "https://github.com/istio/istio.io",
            "last_updated": "2025-09-30T01:00:00Z",
            "commit_hash": "b" * 40,
            "total_documents": 200,
            "total_chunks": 1000,
        },
    )
    assert collection.metadata["commit_hash"] == "b" * 40


@pytest.mark.contract
def test_add_chunks_success(test_collection):
    chunks = [
        DocumentChunk(
            chunk_id="id1",
            content="Test content 1",
            file_path=Path("docs/test1.md"),
            repository_name="test-docs",
            heading_context="Installation",
            chunk_index=0,
            token_count=100,
            metadata={"title": "Test 1", "has_code": True, "tags": ["test"]},
        ),
        DocumentChunk(
            chunk_id="id2",
            content="Test content 2",
            file_path=Path("docs/test2.md"),
            repository_name="test-docs",
            heading_context="Configuration",
            chunk_index=0,
            token_count=150,
            metadata={"title": "Test 2", "has_code": False, "tags": ["config"]},
        ),
    ]
    client = ChromaDBClient()
    client.add_chunks(test_collection, chunks)
    assert test_collection.count() == 2


@pytest.mark.contract
def test_add_chunks_batching(test_collection):
    chunks = [
        DocumentChunk(
            chunk_id=f"id{i}",
            content=f"Content {i}",
            file_path=Path(f"docs/test{i}.md"),
            repository_name="test-docs",
            heading_context="Section",
            chunk_index=0,
            token_count=100,
            metadata={},
        )
        for i in range(250)
    ]
    client = ChromaDBClient()
    client.add_chunks(test_collection, chunks, batch_size=100)
    assert test_collection.count() == 250


@pytest.mark.contract
def test_add_chunks_duplicate_id(test_collection):
    chunk = DocumentChunk(
        chunk_id="duplicate",
        content="Test content",
        file_path=Path("docs/test.md"),
        repository_name="test-docs",
        heading_context="Section",
        chunk_index=0,
        token_count=100,
        metadata={},
    )
    client = ChromaDBClient()
    client.add_chunks(test_collection, [chunk])
    with pytest.raises(DuplicateChunkIDError):
        client.add_chunks(test_collection, [chunk])


@pytest.mark.contract
def test_add_chunks_empty_content(test_collection):
    with pytest.raises(ValueError):
        DocumentChunk(
            chunk_id="id1",
            content="   ",
            file_path=Path("docs/test.md"),
            repository_name="test-docs",
            heading_context="Section",
            chunk_index=0,
            token_count=100,
            metadata={},
        )


@pytest.mark.contract
def test_search_finds_results(test_collection):
    chunks = [
        DocumentChunk(
            chunk_id="k8s-1",
            content="Install Kubernetes on your cluster",
            file_path=Path("docs/install.md"),
            repository_name="test-docs",
            heading_context="Installation",
            chunk_index=0,
            token_count=100,
            metadata={},
        ),
        DocumentChunk(
            chunk_id="k8s-2",
            content="Configure Kubernetes settings",
            file_path=Path("docs/config.md"),
            repository_name="test-docs",
            heading_context="Configuration",
            chunk_index=0,
            token_count=100,
            metadata={},
        ),
    ]
    client = ChromaDBClient()
    client.add_chunks(test_collection, chunks)
    result = client.search_chunks(test_collection, "install kubernetes")
    assert result.total_results > 0
    assert result.matches[0].score >= result.matches[-1].score


@pytest.mark.contract
def test_search_with_limit(test_collection):
    chunks = [
        DocumentChunk(
            chunk_id=f"setup-{i}",
            content=f"Setup step {i}",
            file_path=Path(f"docs/setup{i}.md"),
            repository_name="test-docs",
            heading_context="Setup",
            chunk_index=0,
            token_count=100,
            metadata={},
        )
        for i in range(10)
    ]
    client = ChromaDBClient()
    client.add_chunks(test_collection, chunks)
    result = client.search_chunks(test_collection, "setup", limit=5)
    assert len(result.matches) <= 5


@pytest.mark.contract
def test_search_with_where_filter(test_collection):
    chunks = [
        DocumentChunk(
            chunk_id="istio-1",
            content="Routing in Istio",
            file_path=Path("docs/routing.md"),
            repository_name="istio-docs",
            heading_context="Routing",
            chunk_index=0,
            token_count=100,
            metadata={},
        ),
        DocumentChunk(
            chunk_id="hugo-1",
            content="Routing in Hugo",
            file_path=Path("docs/routing.md"),
            repository_name="hugo-docs",
            heading_context="Routing",
            chunk_index=0,
            token_count=100,
            metadata={},
        ),
    ]
    client = ChromaDBClient()
    client.add_chunks(test_collection, chunks)
    result = client.search_chunks(test_collection, "routing", where={"repository": "istio-docs"})
    assert all(m.repository == "istio-docs" for m in result.matches)


@pytest.mark.contract
def test_search_empty_query(test_collection):
    client = ChromaDBClient()
    with pytest.raises(EmptyQueryError):
        client.search_chunks(test_collection, "")


@pytest.mark.contract
def test_search_no_results(test_collection):
    client = ChromaDBClient()
    result = client.search_chunks(test_collection, "xyzabc nonexistent")
    assert result.total_results == 0
    assert len(result.matches) == 0


@pytest.mark.contract
def test_get_collection_exists(chroma_client):
    chroma_client.create_collection(
        "istio-docs",
        {
            "repository_url": "https://github.com/istio/istio.io",
            "last_updated": "2025-09-30T00:00:00Z",
            "commit_hash": "a" * 40,
            "total_documents": 0,
            "total_chunks": 0,
        },
    )
    collection = chroma_client.get_collection("istio-docs")
    assert collection.name == "istio-docs"


@pytest.mark.contract
def test_get_collection_not_found(chroma_client):
    with pytest.raises(CollectionNotFoundError):
        chroma_client.get_collection("nonexistent")


@pytest.mark.contract
def test_list_collections_multiple(chroma_client):
    chroma_client.create_collection(
        "istio-docs",
        {
            "repository_url": "https://github.com/istio/istio.io",
            "last_updated": "2025-09-30T00:00:00Z",
            "commit_hash": "a" * 40,
            "total_documents": 0,
            "total_chunks": 0,
        },
    )
    chroma_client.create_collection(
        "hugo-docs",
        {
            "repository_url": "https://github.com/gohugoio/hugo",
            "last_updated": "2025-09-30T00:00:00Z",
            "commit_hash": "b" * 40,
            "total_documents": 0,
            "total_chunks": 0,
        },
    )
    collections = chroma_client.list_collections()
    assert len(collections) == 2
    assert collections[0].name == "hugo-docs"


@pytest.mark.contract
def test_list_collections_empty(chroma_client):
    collections = chroma_client.list_collections()
    assert len(collections) == 0


@pytest.mark.contract
def test_delete_collection_success(chroma_client, test_collection):
    chunks = [
        DocumentChunk(
            chunk_id="id1",
            content="Content 1",
            file_path=Path("docs/test1.md"),
            repository_name="test-docs",
            heading_context="Section",
            chunk_index=0,
            token_count=100,
            metadata={},
        ),
        DocumentChunk(
            chunk_id="id2",
            content="Content 2",
            file_path=Path("docs/test2.md"),
            repository_name="test-docs",
            heading_context="Section",
            chunk_index=0,
            token_count=100,
            metadata={},
        ),
    ]
    chroma_client.add_chunks(test_collection, chunks)
    deleted = chroma_client.delete_collection("test-docs")
    assert deleted == 2
    with pytest.raises(CollectionNotFoundError):
        chroma_client.get_collection("test-docs")


@pytest.mark.contract
def test_delete_collection_not_found(chroma_client):
    with pytest.raises(CollectionNotFoundError):
        chroma_client.delete_collection("nonexistent")


@pytest.mark.contract
def test_update_metadata(chroma_client, test_collection):
    chroma_client.update_collection_metadata(test_collection, {"commit_hash": "c" * 40})
    updated = chroma_client.get_collection("test-docs")
    assert updated.metadata["commit_hash"] == "c" * 40
    assert "last_updated" in updated.metadata
