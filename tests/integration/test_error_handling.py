import json
import subprocess
import tempfile


def test_index_nonexistent_path(tmp_path):
    nonexistent = tmp_path / "does_not_exist"
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(nonexistent)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_index_empty_directory(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(empty_dir)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_index_no_markdown_files(tmp_path):
    no_md_dir = tmp_path / "no-markdown"
    no_md_dir.mkdir()
    (no_md_dir / "file.txt").write_text("Not markdown")
    (no_md_dir / "file.json").write_text("{}")

    result = subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(no_md_dir)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_index_malformed_frontmatter(tmp_path):
    repo_dir = tmp_path / "repos" / "malformed-repo"
    repo_dir.mkdir(parents=True)

    (repo_dir / "bad.md").write_text("""---
title: Missing closing delimiter
weight: 10
This is not valid YAML
Content here
""")

    result = subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(tmp_path / "repos")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_index_binary_file_mixed_with_markdown(tmp_path):
    repo_dir = tmp_path / "repos" / "mixed-repo"
    repo_dir.mkdir(parents=True)

    (repo_dir / "valid.md").write_text("# Valid Markdown\n\nContent here.")
    (repo_dir / "binary.md").write_bytes(b"\x00\x01\x02\x03\xff\xfe")

    result = subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(tmp_path / "repos")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_index_unicode_content(tmp_path):
    repo_dir = tmp_path / "repos" / "unicode-repo"
    repo_dir.mkdir(parents=True)

    (repo_dir / "unicode.md").write_text(
        """---
title: Unicode Test
---

# Unicode Content

Emoji: 🚀 ✨ 🎉
Chinese: 你好世界
Arabic: مرحبا بالعالم
Math: ∑ ∫ ∂ ∇
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(tmp_path / "repos")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    search_result = subprocess.run(
        ["python", "-m", "src.cli.main", "search", "Unicode", "--limit", "1", "--format", "json"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert search_result.returncode == 0
    data = json.loads(search_result.stdout)
    assert len(data) > 0


def test_search_empty_database():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "search", "anything", "--db-path", tmpdir],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0


def test_search_nonexistent_repository():
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "search", "test", "--repo", "nonexistent-repo-xyz"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_search_invalid_limit():
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "search", "test", "-n", "0"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_search_invalid_format():
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "search", "test", "--format", "invalid"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_remove_without_confirmation(tmp_path):
    repo_dir = tmp_path / "repos" / "test-repo"
    repo_dir.mkdir(parents=True)
    (repo_dir / "doc.md").write_text("# Test\n\nContent")

    subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(tmp_path / "repos")],
        check=False,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        ["python", "-m", "src.cli.main", "remove", "test-repo"],
        check=False,
        capture_output=True,
        text=True,
        input="n\n",
    )
    assert result.returncode == 1


def test_list_empty_database():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "--db-path", tmpdir, "list", "--format", "json"],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data == {"repositories": []}


def test_index_very_large_file(tmp_path):
    repo_dir = tmp_path / "repos" / "large-repo"
    repo_dir.mkdir(parents=True)

    large_content = "# Large File\n\n" + ("This is a line of content.\n" * 10000)
    (repo_dir / "large.md").write_text(large_content)

    result = subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(tmp_path / "repos")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_index_deeply_nested_headings(tmp_path):
    repo_dir = tmp_path / "repos" / "nested-repo"
    repo_dir.mkdir(parents=True)

    nested_content = """# H1
Content 1

## H2
Content 2

### H3
Content 3

#### H4
Content 4

##### H5
Content 5

###### H6
Content 6
"""
    (repo_dir / "nested.md").write_text(nested_content)

    result = subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(tmp_path / "repos")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_search_special_characters_in_query():
    special_queries = [
        "test & query",
        "test | query",
        "test (query)",
        "test [query]",
        "test {query}",
        'test "query"',
        "test 'query'",
    ]

    for query in special_queries:
        result = subprocess.run(
            ["python", "-m", "src.cli.main", "search", query, "--limit", "1"],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode in [0, 1]


def test_index_file_with_no_content(tmp_path):
    repo_dir = tmp_path / "repos" / "empty-content-repo"
    repo_dir.mkdir(parents=True)

    (repo_dir / "empty.md").write_text("")
    (repo_dir / "whitespace.md").write_text("   \n\n   \t\t\n")

    result = subprocess.run(
        ["python", "-m", "src.cli.main", "index", str(tmp_path / "repos")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode in [0, 1]


def test_index_with_invalid_repo_filter(tmp_path):
    repo_dir = tmp_path / "repos" / "valid-repo"
    repo_dir.mkdir(parents=True)
    (repo_dir / "doc.md").write_text("# Test")

    result = subprocess.run(
        [
            "python",
            "-m",
            "src.cli.main",
            "index",
            str(tmp_path / "repos"),
            "--repo",
            "invalid-repo",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
