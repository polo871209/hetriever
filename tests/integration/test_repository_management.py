import json

import pytest
from click.testing import CliRunner

from src.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "chroma_db"


@pytest.fixture
def sample_python_repo(tmp_path):
    repo = tmp_path / "python-repo"
    repo.mkdir()
    (repo / "intro.md").write_text("""# Python Introduction

Python is a high-level, interpreted programming language known for its simplicity and readability.
Created by Guido van Rossum and first released in 1991, Python emphasizes code readability with its
notable use of significant indentation. The language provides constructs that enable clear programming
on both small and large scales. Python features a dynamic type system and automatic memory management
and supports multiple programming paradigms including structured, object-oriented and functional programming.
Python is often described as a batteries included language due to its comprehensive standard library.
The language has a large ecosystem of third-party packages available through the Python Package Index.
Python is widely used in web development, data science, artificial intelligence, scientific computing,
automation, and many other domains.""")
    return repo


@pytest.fixture
def sample_js_repo(tmp_path):
    repo = tmp_path / "js-repo"
    repo.mkdir()
    (repo / "basics.md").write_text("""# JavaScript Basics

JavaScript is a versatile scripting language primarily used for web development. Originally designed to
make web pages interactive, it has evolved into a powerful language that runs on both client and server
sides. JavaScript is a prototype-based, multi-paradigm language that supports event-driven, functional,
and imperative programming styles. The language is dynamically typed, meaning variables can hold values
of any type and type checking happens at runtime. JavaScript has a C-like syntax but differs significantly
in its object model and other features. Variables can be declared using var, let, or const keywords, each
with different scoping rules.""")
    return repo


def test_list_empty_database(runner, db_path):
    result = runner.invoke(cli, ["--db-path", str(db_path), "list", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"repositories": []}


def test_list_single_repository(runner, db_path, sample_python_repo):
    runner.invoke(
        cli,
        [
            "--db-path",
            str(db_path),
            "index",
            str(sample_python_repo.parent),
            "--repo",
            "python-repo",
        ],
    )

    result = runner.invoke(cli, ["--db-path", str(db_path), "list", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "repositories" in data
    assert len(data["repositories"]) == 1
    repo = data["repositories"][0]
    assert repo["name"] == "python-repo"
    assert repo["chunk_count"] > 0
    assert "last_updated" in repo


def test_list_multiple_repositories(runner, db_path, sample_python_repo, sample_js_repo):
    runner.invoke(
        cli,
        [
            "--db-path",
            str(db_path),
            "index",
            str(sample_python_repo.parent),
            "--repo",
            "python-repo",
        ],
    )
    runner.invoke(
        cli,
        ["--db-path", str(db_path), "index", str(sample_js_repo.parent), "--repo", "js-repo"],
    )

    result = runner.invoke(cli, ["--db-path", str(db_path), "list", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data["repositories"]) == 2
    names = {repo["name"] for repo in data["repositories"]}
    assert names == {"python-repo", "js-repo"}


def test_list_text_format(runner, db_path, sample_python_repo):
    runner.invoke(
        cli,
        [
            "--db-path",
            str(db_path),
            "index",
            str(sample_python_repo.parent),
            "--repo",
            "python-repo",
        ],
    )

    result = runner.invoke(cli, ["--db-path", str(db_path), "list"])
    assert result.exit_code == 0
    assert "python-repo" in result.output
    assert "files" in result.output.lower() or "chunks" in result.output.lower()


def test_remove_existing_repository(runner, db_path, sample_python_repo):
    runner.invoke(
        cli,
        [
            "--db-path",
            str(db_path),
            "index",
            str(sample_python_repo.parent),
            "--repo",
            "python-repo",
        ],
    )

    result = runner.invoke(cli, ["--db-path", str(db_path), "remove", "python-repo", "--confirm"])
    assert result.exit_code == 0

    list_result = runner.invoke(cli, ["--db-path", str(db_path), "list", "--format", "json"])
    data = json.loads(list_result.output)
    assert len(data["repositories"]) == 0


def test_remove_nonexistent_repository(runner, db_path):
    result = runner.invoke(cli, ["--db-path", str(db_path), "remove", "nonexistent-repo"])
    assert result.exit_code == 2
    assert "not found" in result.output.lower() or "does not exist" in result.output.lower()


def test_remove_one_of_multiple_repositories(runner, db_path, sample_python_repo, sample_js_repo):
    runner.invoke(
        cli,
        [
            "--db-path",
            str(db_path),
            "index",
            str(sample_python_repo.parent),
            "--repo",
            "python-repo",
        ],
    )
    runner.invoke(
        cli,
        ["--db-path", str(db_path), "index", str(sample_js_repo.parent), "--repo", "js-repo"],
    )

    result = runner.invoke(cli, ["--db-path", str(db_path), "remove", "python-repo", "--confirm"])
    assert result.exit_code == 0

    list_result = runner.invoke(cli, ["--db-path", str(db_path), "list", "--format", "json"])
    data = json.loads(list_result.output)
    assert len(data["repositories"]) == 1
    assert data["repositories"][0]["name"] == "js-repo"


def test_remove_and_reindex_repository(runner, db_path, sample_python_repo):
    runner.invoke(
        cli,
        [
            "--db-path",
            str(db_path),
            "index",
            str(sample_python_repo.parent),
            "--repo",
            "python-repo",
        ],
    )

    runner.invoke(cli, ["--db-path", str(db_path), "remove", "python-repo", "--confirm"])

    result = runner.invoke(
        cli,
        [
            "--db-path",
            str(db_path),
            "index",
            str(sample_python_repo.parent),
            "--repo",
            "python-repo",
        ],
    )
    assert result.exit_code == 0

    list_result = runner.invoke(cli, ["--db-path", str(db_path), "list", "--format", "json"])
    data = json.loads(list_result.output)
    assert len(data["repositories"]) == 1
    assert data["repositories"][0]["name"] == "python-repo"
