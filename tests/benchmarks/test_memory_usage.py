import gc
import shutil
import tempfile
import tracemalloc

import pytest

from src.processing.indexer import index_repository
from src.storage.chromadb_client import ChromaDBClient


@pytest.fixture
def temp_db_path():
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def memory_test_repo(tmp_path):
    repo_path = tmp_path / "memory_test"
    repo_path.mkdir()

    docs_dir = repo_path / "docs"
    docs_dir.mkdir()

    for i in range(100):
        doc = docs_dir / f"document_{i}.md"
        sections = []
        for section_num in range(10):
            sections.extend(
                [
                    f"## Section {section_num} of Document {i}",
                    "",
                    f"This is section {section_num} content. "
                    + " ".join([f"Word{j}" for j in range(200)]),
                    "",
                ]
            )
        doc.write_text("\n".join(sections))

    return repo_path


@pytest.fixture
def large_memory_test_repo(tmp_path):
    repo_path = tmp_path / "large_memory_test"
    repo_path.mkdir()

    for category in range(5):
        cat_dir = repo_path / f"category_{category}"
        cat_dir.mkdir()

        for i in range(50):
            doc = cat_dir / f"doc_{i}.md"
            sections = []
            for section in range(15):
                sections.extend(
                    [
                        f"## Section {section}",
                        "",
                        f"Content for category {category}, document {i}, section {section}. "
                        + " ".join([f"Content{j}" for j in range(300)]),
                        "",
                    ]
                )
            doc.write_text("\n".join(sections))

    return repo_path


def get_memory_mb():
    current, peak = tracemalloc.get_traced_memory()
    return current / 1024 / 1024, peak / 1024 / 1024


@pytest.mark.benchmark
def test_memory_during_indexing(memory_test_repo, temp_db_path):
    tracemalloc.start()

    initial_current, initial_peak = get_memory_mb()

    result = index_repository(memory_test_repo, "memory-test", temp_db_path)

    final_current, final_peak = get_memory_mb()

    tracemalloc.stop()

    memory_used = final_peak - initial_current

    assert result["files_processed"] == 100
    assert memory_used < 512, f"Peak memory {memory_used:.1f}MB exceeds 512MB target"


@pytest.mark.benchmark
def test_peak_memory_large_repository(large_memory_test_repo, temp_db_path):
    tracemalloc.start()

    initial_current, initial_peak = get_memory_mb()

    result = index_repository(large_memory_test_repo, "large-memory-test", temp_db_path)

    final_current, final_peak = get_memory_mb()

    tracemalloc.stop()

    memory_used = final_peak - initial_current

    assert result["files_processed"] == 250
    assert memory_used < 512, f"Peak memory {memory_used:.1f}MB exceeds 512MB target"


@pytest.mark.benchmark
def test_memory_cleanup_after_indexing(memory_test_repo, temp_db_path):
    gc.collect()
    tracemalloc.start()

    baseline_current, baseline_peak = get_memory_mb()

    index_repository(memory_test_repo, "cleanup-test", temp_db_path)

    after_index_current, after_index_peak = get_memory_mb()

    gc.collect()

    after_gc_current, after_gc_peak = get_memory_mb()

    tracemalloc.stop()

    memory_retained = after_gc_current - baseline_current

    assert memory_retained < 50, (
        f"Memory retained {memory_retained:.1f}MB after GC, should be minimal"
    )


@pytest.mark.benchmark
def test_memory_during_search_operations(memory_test_repo, temp_db_path):
    index_repository(memory_test_repo, "search-memory-test", temp_db_path)

    client = ChromaDBClient(temp_db_path)
    collection = client.get_collection("search-memory-test")

    tracemalloc.start()

    initial_current, initial_peak = get_memory_mb()

    for _ in range(1000):
        client.search_chunks(collection, "document content section", limit=10)

    final_current, final_peak = get_memory_mb()

    tracemalloc.stop()

    memory_used = final_peak - initial_current

    assert memory_used < 100, f"Search operations used {memory_used:.1f}MB, should be <100MB"


@pytest.mark.benchmark
def test_memory_efficiency_per_document(memory_test_repo, temp_db_path):
    tracemalloc.start()

    initial_current, initial_peak = get_memory_mb()

    result = index_repository(memory_test_repo, "efficiency-test", temp_db_path)

    final_current, final_peak = get_memory_mb()

    tracemalloc.stop()

    memory_used = final_peak - initial_current
    memory_per_file = memory_used / result["files_processed"]

    assert memory_per_file < 5, f"Memory per file {memory_per_file:.2f}MB too high, should be <5MB"
