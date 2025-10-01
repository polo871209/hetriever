import shutil
import tempfile

import pytest

from src.processing.indexer import index_repository


@pytest.fixture
def temp_db_path():
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def sample_markdown_repo(tmp_path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    content_dir = repo_path / "content"
    content_dir.mkdir()

    for i in range(20):
        doc = content_dir / f"doc_{i}.md"
        content_lines = [
            f"# Main Heading {i}",
            "",
            f"This is the introduction for document {i}. "
            + " ".join([f"Word{j}" for j in range(200)]),
            "",
            "## Section 1",
            "",
            f"Content for section 1 in document {i}. "
            + " ".join([f"Content{j}" for j in range(200)]),
            "This section contains information that should be indexed and searchable. "
            + " ".join([f"Extra{j}" for j in range(150)]),
            "",
        ]
        doc.write_text("\n".join(content_lines))

    return repo_path


@pytest.fixture
def large_markdown_repo(tmp_path):
    repo_path = tmp_path / "large_repo"
    repo_path.mkdir()

    content_dir = repo_path / "content"
    content_dir.mkdir()

    for i in range(50):
        subdir = content_dir / f"category_{i // 10}"
        subdir.mkdir(exist_ok=True)

        doc = subdir / f"doc_{i}.md"
        content_lines = [
            f"# Document {i}",
            "",
            f"Introduction paragraph for document {i}. "
            + " ".join([f"Intro{j}" for j in range(150)]),
            "",
            "## Overview",
            "",
            "This section provides an overview. " + " ".join([f"Overview{j}" for j in range(200)]),
            "",
            "## Details",
            "",
            f"Detailed information about topic {i}. "
            + " ".join([f"Detail{j}" for j in range(250)]),
            "",
        ]
        doc.write_text("\n".join(content_lines))

    return repo_path


@pytest.mark.benchmark
def test_index_small_repository(benchmark, sample_markdown_repo, temp_db_path):
    result = benchmark(index_repository, sample_markdown_repo, "test-repo", temp_db_path)
    assert result["files_processed"] == 20
    assert result["chunks_created"] > 0


@pytest.mark.benchmark
def test_index_large_repository_throughput(benchmark, large_markdown_repo, temp_db_path):
    result = benchmark(index_repository, large_markdown_repo, "large-repo", temp_db_path)

    assert result["files_processed"] == 50
    assert result["chunks_created"] > 0

    stats = benchmark.stats.stats
    elapsed_seconds = stats.mean
    files_per_second = result["files_processed"] / elapsed_seconds

    assert elapsed_seconds < 30, f"Indexing took {elapsed_seconds:.1f}s, target is <30s"
    assert files_per_second > 1.5, f"Throughput {files_per_second:.1f} files/sec too slow"


@pytest.mark.benchmark
def test_index_repository_batch_processing(benchmark, sample_markdown_repo, temp_db_path):
    result = benchmark(
        index_repository, sample_markdown_repo, "batch-test", temp_db_path, batch_size=50
    )
    assert result["chunks_created"] > 0
