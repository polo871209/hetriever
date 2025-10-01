import pytest
from click.testing import CliRunner

from src.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def test_docs(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    repo1 = docs_dir / "repo1"
    repo1.mkdir()
    (repo1 / "intro.md").write_text("# Introduction\nWelcome to repo1")
    (repo1 / "guide.md").write_text("# Guide\nPython programming guide")

    repo2 = docs_dir / "repo2"
    repo2.mkdir()
    (repo2 / "readme.md").write_text("# README\nJavaScript documentation")
    (repo2 / "api.md").write_text("# API\nREST API reference")

    return docs_dir


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "chroma_db"


def test_index_all_repositories(runner, test_docs, db_path):
    result = runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

    assert result.exit_code == 0
    assert "repo1" in result.output
    assert "repo2" in result.output
    assert "files" in result.output.lower()
    assert "chunks" in result.output.lower()


def test_index_single_repository(runner, test_docs, db_path):
    result = runner.invoke(
        cli, ["--db-path", str(db_path), "index", str(test_docs), "--repo", "repo1"]
    )

    assert result.exit_code == 0
    assert "repo1" in result.output
    assert "repo2" not in result.output


def test_index_with_verbose(runner, test_docs, db_path):
    result = runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs), "--verbose"])

    assert result.exit_code == 0


def test_index_force_reindex(runner, test_docs, db_path):
    runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

    result = runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs), "--force"])

    assert result.exit_code == 0


def test_index_nonexistent_path(runner, db_path):
    result = runner.invoke(cli, ["--db-path", str(db_path), "index", "/nonexistent/path"])

    assert result.exit_code != 0


def test_index_empty_directory(runner, tmp_path, db_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    result = runner.invoke(cli, ["--db-path", str(db_path), "index", str(empty_dir)])

    assert result.exit_code == 2
    assert "No submodules found" in result.output


def test_index_with_markdown_features(runner, tmp_path, db_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    repo = docs_dir / "test_repo"
    repo.mkdir()

    complex_md = repo / "complex.md"
    complex_md.write_text("""---
title: Test Document
author: Test Author
---

# Main Title

Some content with [links](http://example.com).

```python
def hello():
    print("world")
```

More content here.
""")

    result = runner.invoke(cli, ["--db-path", str(db_path), "index", str(docs_dir)])

    assert result.exit_code == 0
    assert "test-repo" in result.output or "test_repo" in result.output


def test_index_nonexistent_repo_filter(runner, test_docs, db_path):
    result = runner.invoke(
        cli, ["--db-path", str(db_path), "index", str(test_docs), "--repo", "nonexistent"]
    )

    assert result.exit_code == 2
    assert "not found" in result.output
