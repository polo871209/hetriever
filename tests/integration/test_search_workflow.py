import json

import pytest
from click.testing import CliRunner

from src.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def indexed_repos(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    repo1 = docs_dir / "python-docs"
    repo1.mkdir()
    (repo1 / "intro.md").write_text("""# Python Introduction

Python is a high-level, interpreted programming language known for its simplicity and readability.
Created by Guido van Rossum and first released in 1991, Python emphasizes code readability with its
notable use of significant indentation. The language provides constructs that enable clear programming
on both small and large scales. Python features a dynamic type system and automatic memory management
and supports multiple programming paradigms including structured, object-oriented and functional programming.
Python is often described as a batteries included language due to its comprehensive standard library.
The language has a large ecosystem of third-party packages available through the Python Package Index.
Python is widely used in web development, data science, artificial intelligence, scientific computing,
automation, and many other domains. Its syntax allows programmers to express concepts in fewer lines
of code than would be possible in languages such as C++ or Java, making it an excellent choice for
beginners and experienced developers alike.""")

    (repo1 / "advanced.md").write_text("""# Advanced Python Concepts

Decorators are a powerful feature in Python that allow you to modify the behavior of functions or classes.
They provide a clean syntax for wrapping functions with additional functionality. Metaclasses are even more
advanced and allow you to customize class creation. A metaclass is the class of a class that defines how
a class behaves. Context managers, implemented using the with statement, provide a convenient way to manage
resources like file handles or database connections. Generator functions use the yield keyword to produce
values lazily, which is memory efficient for large datasets. List comprehensions offer a concise way to
create lists based on existing sequences. Python also supports asynchronous programming through async and
await keywords, enabling concurrent execution of code without threading complexity. Type hints, introduced
in Python 3.5, allow you to specify expected types for function arguments and return values.""")

    repo2 = docs_dir / "javascript-docs"
    repo2.mkdir()
    (repo2 / "basics.md").write_text("""# JavaScript Basics

JavaScript is a versatile scripting language primarily used for web development. Originally designed to
make web pages interactive, it has evolved into a powerful language that runs on both client and server
sides. JavaScript is a prototype-based, multi-paradigm language that supports event-driven, functional,
and imperative programming styles. The language is dynamically typed, meaning variables can hold values
of any type and type checking happens at runtime. JavaScript has a C-like syntax but differs significantly
in its object model and other features. Variables can be declared using var, let, or const keywords, each
with different scoping rules. Functions are first-class citizens in JavaScript, meaning they can be assigned
to variables, passed as arguments, and returned from other functions. The language includes several built-in
objects like Array, String, Math, and Date that provide useful functionality. Modern JavaScript supports
arrow functions, template literals, destructuring, and the spread operator for cleaner code.""")

    (repo2 / "async.md").write_text("""# Asynchronous JavaScript

Asynchronous programming is essential in JavaScript for handling operations that take time to complete
without blocking the main thread. Promises represent the eventual completion or failure of an asynchronous
operation and provide a cleaner alternative to callback hell. A Promise can be in one of three states:
pending, fulfilled, or rejected. The async and await keywords, introduced in ES2017, provide syntactic
sugar over promises, making asynchronous code look and behave more like synchronous code. Async functions
always return a promise, and the await keyword can only be used inside async functions. Error handling in
async code can be done using try-catch blocks with async/await or the catch method with promises. The
Promise.all method allows you to wait for multiple promises to complete, while Promise.race returns when
the first promise settles. Understanding the event loop is crucial for mastering asynchronous JavaScript,
as it controls how callbacks, promises, and other asynchronous operations are executed.""")

    db_path = tmp_path / "chroma_db"

    runner = CliRunner()
    result = runner.invoke(cli, ["--db-path", str(db_path), "index", str(docs_dir)])

    if result.exit_code != 0:
        pytest.fail(f"Indexing failed: {result.output}")

    return {"docs_dir": docs_dir, "db_path": db_path, "runner": runner}


def test_search_single_repository(indexed_repos):
    runner = indexed_repos["runner"]
    db_path = indexed_repos["db_path"]

    result = runner.invoke(
        cli, ["--db-path", str(db_path), "search", "Python programming", "--repo", "python-docs"]
    )

    assert result.exit_code == 0
    assert "python" in result.output.lower()


def test_search_all_repositories(indexed_repos):
    runner = indexed_repos["runner"]
    db_path = indexed_repos["db_path"]

    result = runner.invoke(cli, ["--db-path", str(db_path), "search", "programming language"])

    assert result.exit_code == 0
    assert "python" in result.output.lower() or "javascript" in result.output.lower()


def test_search_with_limit(indexed_repos):
    runner = indexed_repos["runner"]
    db_path = indexed_repos["db_path"]

    result = runner.invoke(
        cli, ["--db-path", str(db_path), "search", "asynchronous", "--limit", "1"]
    )

    assert result.exit_code == 0
    result_lines = [
        line
        for line in result.output.split("\n")
        if line.strip() and not line.startswith("Results for")
    ]
    match_count = len([line for line in result_lines if line.strip() and line[0].isdigit()])
    assert match_count <= 1


def test_search_json_format(indexed_repos):
    runner = indexed_repos["runner"]
    db_path = indexed_repos["db_path"]

    result = runner.invoke(
        cli, ["--db-path", str(db_path), "search", "Python decorators", "--format", "json"]
    )

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert isinstance(data, dict)
    assert "query" in data
    assert "total_results" in data
    assert "matches" in data
    assert isinstance(data["matches"], list)


def test_search_text_format(indexed_repos):
    runner = indexed_repos["runner"]
    db_path = indexed_repos["db_path"]

    result = runner.invoke(cli, ["--db-path", str(db_path), "search", "Python", "--format", "text"])

    assert result.exit_code == 0


def test_search_empty_query(indexed_repos):
    runner = indexed_repos["runner"]
    db_path = indexed_repos["db_path"]

    result = runner.invoke(cli, ["--db-path", str(db_path), "search", ""])

    assert result.exit_code == 2


def test_search_with_irrelevant_query(indexed_repos):
    runner = indexed_repos["runner"]
    db_path = indexed_repos["db_path"]

    result = runner.invoke(cli, ["--db-path", str(db_path), "search", "xyzqwertyuiop123456789"])

    assert result.exit_code == 0


def test_search_nonexistent_repo(indexed_repos):
    runner = indexed_repos["runner"]
    db_path = indexed_repos["db_path"]

    result = runner.invoke(
        cli, ["--db-path", str(db_path), "search", "Python", "--repo", "nonexistent"]
    )

    assert result.exit_code == 2


def test_search_unindexed_database(runner, tmp_path):
    db_path = tmp_path / "empty_db"

    result = runner.invoke(cli, ["--db-path", str(db_path), "search", "test"])

    assert result.exit_code == 0 or result.exit_code == 2


def test_search_cross_repository(indexed_repos):
    runner = indexed_repos["runner"]
    db_path = indexed_repos["db_path"]

    result = runner.invoke(cli, ["--db-path", str(db_path), "search", "async programming"])

    assert result.exit_code == 0
