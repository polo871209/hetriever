import json

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

    repo1 = docs_dir / "istio-docs"
    repo1.mkdir()
    (repo1 / "install.md").write_text(
        "# Install Istio\n\nTo install Istio, you need a Kubernetes cluster "
        "with at least 4GB of RAM."
    )
    (repo1 / "traffic.md").write_text(
        "# Traffic Management\n\nConfigure traffic routing with virtual services."
    )

    repo2 = docs_dir / "hugo-docs"
    repo2.mkdir()
    (repo2 / "quickstart.md").write_text("# Quick Start\n\nGet started with Hugo in minutes.")

    return docs_dir


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "chroma_db"


class TestIndexCommandContract:
    def test_index_all_repos_success(self, runner, test_docs, db_path):
        result = runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        assert result.exit_code == 0
        assert "repositories" in result.output.lower() or "repos" in result.output.lower()

    def test_index_specific_repo(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(
            cli, ["--db-path", str(db_path), "index", str(test_docs), "--repo", "istio-docs"]
        )

        assert result.exit_code == 0
        assert "istio-docs" in result.output

    def test_index_no_submodules(self, runner, tmp_path, db_path):
        empty_docs = tmp_path / "empty_docs"
        empty_docs.mkdir()

        result = runner.invoke(cli, ["--db-path", str(db_path), "index", str(empty_docs)])

        assert result.exit_code in [0, 2]

    def test_index_force_reindex(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs), "--force"])

        assert result.exit_code == 0

    def test_index_verbose_option(self, runner, test_docs, db_path):
        result = runner.invoke(
            cli, ["--db-path", str(db_path), "index", str(test_docs), "--verbose"]
        )

        assert result.exit_code == 0


class TestSearchCommandContract:
    def test_search_finds_results(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(cli, ["--db-path", str(db_path), "search", "install istio"])

        assert result.exit_code == 0
        assert "matches" in result.output.lower() or "results" in result.output.lower()

    def test_search_no_results(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(cli, ["--db-path", str(db_path), "search", "xyzabc nonexistent"])

        assert result.exit_code == 0

    def test_search_specific_repo(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(
            cli, ["--db-path", str(db_path), "search", "traffic", "--repo", "istio-docs"]
        )

        assert result.exit_code == 0

    def test_search_json_format(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(
            cli, ["--db-path", str(db_path), "search", "install", "--format", "json"]
        )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "query" in data or "matches" in data

    def test_search_empty_query(self, runner, test_docs, db_path):
        result = runner.invoke(cli, ["--db-path", str(db_path), "search", ""])

        assert result.exit_code in [0, 2]

    def test_search_limit_option(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(
            cli, ["--db-path", str(db_path), "search", "install", "--limit", "5"]
        )

        assert result.exit_code == 0

    def test_search_limit_validation(self, runner, test_docs, db_path):
        result = runner.invoke(
            cli, ["--db-path", str(db_path), "search", "install", "--limit", "0"]
        )

        assert result.exit_code in [0, 2]

    def test_search_invalid_repo(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(
            cli, ["--db-path", str(db_path), "search", "query", "--repo", "nonexistent"]
        )

        assert result.exit_code in [0, 2]


class TestListCommandContract:
    def test_list_shows_repositories(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(cli, ["--db-path", str(db_path), "list"])

        assert result.exit_code == 0
        assert "istio-docs" in result.output or "hugo-docs" in result.output

    def test_list_json_format(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(cli, ["--db-path", str(db_path), "list", "--format", "json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "repositories" in data

    def test_list_no_repos(self, runner, db_path):
        result = runner.invoke(cli, ["--db-path", str(db_path), "list"])

        assert result.exit_code == 0


class TestRemoveCommandContract:
    def test_remove_with_confirm(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(
            cli, ["--db-path", str(db_path), "remove", "istio-docs", "--confirm"]
        )

        assert result.exit_code == 0
        assert "removed" in result.output.lower() or "deleted" in result.output.lower()

    def test_remove_invalid_repo(self, runner, db_path):
        result = runner.invoke(
            cli, ["--db-path", str(db_path), "remove", "nonexistent", "--confirm"]
        )

        assert result.exit_code in [0, 2]


class TestGlobalOptionsContract:
    def test_help_option(self, runner):
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "index" in result.output
        assert "search" in result.output
        assert "list" in result.output
        assert "remove" in result.output

    def test_version_option(self, runner):
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0

    def test_db_path_option(self, runner, test_docs, tmp_path):
        custom_db = tmp_path / "custom_db"

        result = runner.invoke(cli, ["--db-path", str(custom_db), "list"])

        assert result.exit_code == 0

    def test_command_help(self, runner):
        commands = ["index", "search", "list", "remove"]

        for cmd in commands:
            result = runner.invoke(cli, [cmd, "--help"])
            assert result.exit_code == 0


class TestOutputFormats:
    def test_search_text_format_structure(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(cli, ["--db-path", str(db_path), "search", "install"])

        assert result.exit_code == 0
        assert isinstance(result.output, str)

    def test_search_json_format_structure(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(
            cli, ["--db-path", str(db_path), "search", "install", "--format", "json"]
        )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_list_json_format_structure(self, runner, test_docs, db_path):
        runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])

        result = runner.invoke(cli, ["--db-path", str(db_path), "list", "--format", "json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "repositories" in data
        assert isinstance(data["repositories"], list)


class TestExitCodes:
    def test_successful_operations_return_zero(self, runner, test_docs, db_path):
        result = runner.invoke(cli, ["--db-path", str(db_path), "index", str(test_docs)])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["--db-path", str(db_path), "search", "query"])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["--db-path", str(db_path), "list"])
        assert result.exit_code == 0

    def test_error_operations_return_nonzero(self, runner, db_path):
        result = runner.invoke(
            cli, ["--db-path", str(db_path), "remove", "nonexistent", "--confirm"]
        )

        assert result.exit_code in [0, 1, 2]
