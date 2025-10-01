import logging
from pathlib import Path

import click

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="0.1.0")
@click.option(
    "--db-path",
    type=click.Path(path_type=Path),
    envvar="HETRIEVER_DB_PATH",
    default="./chroma_data",
    help="ChromaDB storage path",
)
@click.pass_context
def cli(ctx: click.Context, db_path: Path) -> None:
    """Hetriever - Documentation retrieval system with semantic search.

    Main CLI entry point that manages database configuration and command routing.

    Args:
        ctx: Click context object for passing state between commands.
        db_path: Path to ChromaDB storage directory (from --db-path or HETRIEVER_DB_PATH).
    """
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = db_path


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--repo", help="Index only specified repository")
@click.option("--force", is_flag=True, help="Force reindex even if unchanged")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed processing logs")
@click.pass_context
def index(ctx: click.Context, path: Path, repo: str | None, force: bool, verbose: bool) -> None:
    """Index markdown documentation from a repository or directory.

    Processes markdown files, extracts metadata, chunks content, and stores
    embeddings in ChromaDB for semantic search.

    Args:
        ctx: Click context containing database path.
        path: Path to repository or directory to index.
        repo: Optional repository name to scope indexing.
        force: If True, reindex files even if unchanged.
        verbose: If True, show detailed processing logs.
    """
    from src.cli.commands.index import index_command  # noqa: PLC0415

    logger.debug(f"CLI index command invoked: path={path}, repo={repo}")
    db_path = ctx.obj["db_path"]
    index_command(db_path, path, repo, force, verbose)


@cli.command()
@click.argument("query")
@click.option("--repo", help="Search only specified repository")
@click.option("--limit", default=5, help="Maximum results to return")
@click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text")
@click.pass_context
def search(
    ctx: click.Context, query: str, repo: str | None, limit: int, output_format: str
) -> None:
    """Search indexed documentation using semantic similarity.

    Performs vector similarity search against indexed markdown chunks and
    returns relevant results.

    Args:
        ctx: Click context containing database path.
        query: Search query string.
        repo: Optional repository name to scope search.
        limit: Maximum number of results to return (default 10).
        output_format: Output format - 'text' or 'json'.
    """
    from src.cli.commands.search import search_command  # noqa: PLC0415

    db_path = ctx.obj["db_path"]
    search_command(db_path, query, repo, limit, output_format)


@cli.command()
@click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text")
@click.pass_context
def list(ctx: click.Context, output_format: str) -> None:  # noqa: A001
    """List all indexed repositories and their statistics.

    Displays repository names, document counts, and last updated timestamps.

    Args:
        ctx: Click context containing database path.
        output_format: Output format - 'text' or 'json'.
    """
    from src.cli.commands.list import list_command  # noqa: PLC0415

    db_path = ctx.obj["db_path"]
    list_command(db_path, output_format)


@cli.command()
@click.argument("repo")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def remove(ctx: click.Context, repo: str, confirm: bool) -> None:
    """Remove a repository and all its indexed documents.

    Deletes all documents, embeddings, and metadata associated with the
    specified repository from the database.

    Args:
        ctx: Click context containing database path.
        repo: Repository name to remove.
        confirm: If True, skip confirmation prompt.
    """
    from src.cli.commands.remove import remove_command  # noqa: PLC0415

    db_path = ctx.obj["db_path"]
    remove_command(db_path, repo, confirm)


if __name__ == "__main__":
    cli()
