import json
import subprocess
import tempfile
import time


def test_indexing_throughput_small_dataset(tmp_path):
    repo_dir = tmp_path / "repos" / "perf-repo"
    repo_dir.mkdir(parents=True)

    for i in range(10):
        (repo_dir / f"doc{i}.md").write_text(f"""# Document {i}

## Section 1
Content for section 1 in document {i}.

## Section 2
Content for section 2 in document {i}.

## Section 3
Content for section 3 in document {i}.
""")

    start = time.time()
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(tmp_path / "repos")],
        check=False,
        capture_output=True,
        text=True,
    )
    elapsed = time.time() - start

    assert result.returncode == 0
    assert elapsed < 10.0


def test_search_latency_basic(tmp_path):
    repo_dir = tmp_path / "repos" / "search-repo"
    repo_dir.mkdir(parents=True)

    (repo_dir / "doc.md").write_text("""# Search Performance Test

## Database Performance
Testing search latency for basic queries.

## Query Optimization
Ensuring queries return quickly.
""")

    with tempfile.TemporaryDirectory() as db_dir:
        subprocess.run(
            ["python", "-m", "src.cli.main", "--db-path", db_dir, "index", str(tmp_path / "repos")],
            check=False,
            capture_output=True,
            text=True,
        )

        start = time.time()
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "--db-path", db_dir, "search", "performance"],
            check=False,
            capture_output=True,
            text=True,
        )
        elapsed = time.time() - start

        assert result.returncode == 0
        assert elapsed < 2.0


def test_indexing_multiple_repositories(tmp_path):
    for i in range(5):
        repo_dir = tmp_path / "repos" / f"repo{i}"
        repo_dir.mkdir(parents=True)
        (repo_dir / "index.md").write_text(f"# Repository {i}\nContent for repo {i}.")

    start = time.time()
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(tmp_path / "repos")],
        check=False,
        capture_output=True,
        text=True,
    )
    elapsed = time.time() - start

    assert result.returncode == 0
    assert elapsed < 15.0


def test_search_result_limit_performance(tmp_path):
    repo_dir = tmp_path / "repos" / "large-repo"
    repo_dir.mkdir(parents=True)

    for i in range(20):
        (repo_dir / f"doc{i}.md").write_text(f"# Document {i}\nCommon search term appears here.")

    with tempfile.TemporaryDirectory() as db_dir:
        subprocess.run(
            ["python", "-m", "src.cli.main", "--db-path", db_dir, "index", str(tmp_path / "repos")],
            check=False,
            capture_output=True,
            text=True,
        )

        start = time.time()
        result = subprocess.run(
            [
                "python",
                "-m",
                "src.cli.main",
                "--db-path",
                db_dir,
                "search",
                "common",
                "--limit",
                "5",
                "--format",
                "json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        elapsed = time.time() - start

        assert result.returncode == 0
        assert elapsed < 2.0

        data = json.loads(result.stdout)
        assert len(data["matches"]) <= 5


def test_list_repositories_performance(tmp_path):
    for i in range(10):
        repo_dir = tmp_path / "repos" / f"repo{i}"
        repo_dir.mkdir(parents=True)
        (repo_dir / "doc.md").write_text(f"# Repo {i}")

    with tempfile.TemporaryDirectory() as db_dir:
        subprocess.run(
            ["python", "-m", "src.cli.main", "--db-path", db_dir, "index", str(tmp_path / "repos")],
            check=False,
            capture_output=True,
            text=True,
        )

        start = time.time()
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "--db-path", db_dir, "list", "--format", "json"],
            check=False,
            capture_output=True,
            text=True,
        )
        elapsed = time.time() - start

        assert result.returncode == 0
        assert elapsed < 2.0

        data = json.loads(result.stdout)
        assert len(data["repositories"]) == 10


def test_indexing_large_file_performance(tmp_path):
    repo_dir = tmp_path / "repos" / "large-file-repo"
    repo_dir.mkdir(parents=True)

    large_content = "# Large File\n\n" + "\n\n".join(
        [f"## Section {i}\nContent for section {i}." for i in range(500)]
    )
    (repo_dir / "large.md").write_text(large_content)

    start = time.time()
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(tmp_path / "repos")],
        check=False,
        capture_output=True,
        text=True,
    )
    elapsed = time.time() - start

    assert result.returncode == 0
    assert elapsed < 10.0


def test_remove_repository_performance(tmp_path):
    for i in range(5):
        repo_dir = tmp_path / "repos" / f"repo{i}"
        repo_dir.mkdir(parents=True)
        (repo_dir / "doc.md").write_text(f"# Repo {i}")

    with tempfile.TemporaryDirectory() as db_dir:
        subprocess.run(
            ["python", "-m", "src.cli.main", "--db-path", db_dir, "index", str(tmp_path / "repos")],
            check=False,
            capture_output=True,
            text=True,
        )

        start = time.time()
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "--db-path", db_dir, "remove", "repo0", "--confirm"],
            check=False,
            capture_output=True,
            text=True,
        )
        elapsed = time.time() - start

        assert result.returncode == 0
        assert elapsed < 2.0


def test_reindexing_performance(tmp_path):
    repo_dir = tmp_path / "repos" / "reindex-repo"
    repo_dir.mkdir(parents=True)

    for i in range(10):
        (repo_dir / f"doc{i}.md").write_text(f"# Document {i}\nOriginal content.")

    with tempfile.TemporaryDirectory() as db_dir:
        result1 = subprocess.run(
            ["python", "-m", "src.cli.main", "--db-path", db_dir, "index", str(tmp_path / "repos")],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result1.returncode == 0

        for i in range(10):
            (repo_dir / f"doc{i}.md").write_text(f"# Document {i}\nUpdated content.")

        start = time.time()
        result2 = subprocess.run(
            ["python", "-m", "src.cli.main", "--db-path", db_dir, "index", str(tmp_path / "repos")],
            check=False,
            capture_output=True,
            text=True,
        )
        elapsed = time.time() - start

        assert result2.returncode == 0
        assert elapsed < 10.0
