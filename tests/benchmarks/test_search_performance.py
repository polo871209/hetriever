import shutil
import tempfile

import pytest

from src.processing.indexer import index_repository
from src.storage.chromadb_client import ChromaDBClient


@pytest.fixture
def temp_db_path():
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def indexed_repository(tmp_path, temp_db_path):
    repo_path = tmp_path / "search_test_repo"
    repo_path.mkdir()

    content_dir = repo_path / "docs"
    content_dir.mkdir()

    topics = ["database", "api", "authentication", "caching", "deployment"]
    for i in range(25):
        doc = content_dir / f"doc_{i}.md"
        topic = topics[i % len(topics)]
        content_lines = [
            f"# {topic.title()} Guide {i}",
            "",
            f"This document covers {topic} concepts and best practices. "
            + " ".join([f"{topic.capitalize()}Word{j}" for j in range(200)]),
            "",
            f"## {topic.title()} Overview",
            "",
            f"The {topic} system provides essential functionality. "
            + " ".join([f"Overview{j}" for j in range(200)]),
            "",
            "## Implementation",
            "",
            f"To implement {topic}, follow these steps. "
            + " ".join([f"Implementation{j}" for j in range(250)]),
            "",
        ]
        doc.write_text("\n".join(content_lines))

    index_repository(repo_path, "search-test-repo", temp_db_path)
    return temp_db_path


@pytest.mark.benchmark
def test_search_basic_latency(benchmark, indexed_repository):
    db_client = ChromaDBClient(path=indexed_repository)
    collection = db_client.get_collection("search-test-repo")

    result = benchmark(db_client.search_chunks, collection, "database concepts", 10)

    assert result.total_results > 0
    assert result.search_time_ms > 0


@pytest.mark.benchmark
def test_search_p95_latency(indexed_repository):
    db_client = ChromaDBClient(path=indexed_repository)
    collection = db_client.get_collection("search-test-repo")

    queries = [
        "database",
        "api authentication",
        "caching strategies",
        "deployment guide",
        "implementation steps",
    ]

    latencies = []
    for _ in range(100):
        for query in queries:
            result = db_client.search_chunks(collection, query, 10)
            latencies.append(result.search_time_ms)

    latencies.sort()
    p95_latency = latencies[int(len(latencies) * 0.95)]
    p99_latency = latencies[int(len(latencies) * 0.99)]
    median_latency = latencies[len(latencies) // 2]

    assert p95_latency < 100, f"p95 latency {p95_latency:.1f}ms exceeds 100ms target"
    assert median_latency < 50, f"Median latency {median_latency:.1f}ms too high"


@pytest.mark.benchmark
def test_search_multi_term_performance(benchmark, indexed_repository):
    db_client = ChromaDBClient(path=indexed_repository)
    collection = db_client.get_collection("search-test-repo")

    multi_term_query = "database authentication api implementation best practices"
    result = benchmark(db_client.search_chunks, collection, multi_term_query, 10)

    assert result.total_results > 0
    stats = benchmark.stats.stats
    assert stats.mean < 0.1, f"Multi-term search took {stats.mean * 1000:.1f}ms, target <100ms"


@pytest.mark.benchmark
def test_search_large_result_set(benchmark, indexed_repository):
    db_client = ChromaDBClient(path=indexed_repository)
    collection = db_client.get_collection("search-test-repo")

    result = benchmark(db_client.search_chunks, collection, "guide", 100)

    assert result.total_results > 0
    assert len(result.matches) <= 100
    stats = benchmark.stats.stats
    assert stats.mean < 0.15, (
        f"Large result set search took {stats.mean * 1000:.1f}ms, target <150ms"
    )


@pytest.mark.benchmark
def test_search_result_quality(indexed_repository):
    db_client = ChromaDBClient(path=indexed_repository)
    collection = db_client.get_collection("search-test-repo")

    result = db_client.search_chunks(collection, "database concepts", 10)

    assert result.total_results > 0
    if result.matches:
        top_match = result.matches[0]
        assert top_match.score > 0.3
        assert "database" in top_match.content.lower()
