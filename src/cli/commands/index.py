import logging
import sys
import time
from pathlib import Path

import click

from src.cli.formatters import format_text_index_repo, format_text_index_summary
from src.processing.indexer import index_repository
from src.storage.chromadb_client import ChromaDBClient, ChromaDBConnectionError

logger = logging.getLogger(__name__)


def index_command(
    db_path: Path,
    path: Path,
    repo: str | None,
    force: bool,
    verbose: bool,
) -> None:
    logger.debug(f"Starting index command: path={path}, repo={repo}, force={force}")

    try:
        ChromaDBClient(path=str(db_path))
        logger.debug(f"Connected to ChromaDB at {db_path}")
    except ChromaDBConnectionError as e:
        logger.error(f"Failed to connect to ChromaDB at {db_path}: {e}")
        click.echo(f"Error: Cannot connect to ChromaDB at {db_path}", err=True)
        sys.exit(2)

    if not path.exists():
        logger.error(f"Path does not exist: {path}")
        click.echo(f"Error: Path does not exist: {path}", err=True)
        sys.exit(2)

    subdirs = [d for d in path.iterdir() if d.is_dir() and not d.name.startswith(".")]

    if not subdirs:
        logger.error(f"No submodules found in {path}")
        click.echo("Error: No submodules found in docs/", err=True)
        sys.exit(2)

    if repo:
        repo_path = path / repo
        if not repo_path.exists():
            logger.error(f"Repository '{repo}' not found in {path}")
            click.echo(f"Error: Repository '{repo}' not found in {path}", err=True)
            sys.exit(2)
        repositories_to_index = [(repo, repo_path)]
    else:
        repositories_to_index = [(d.name, d) for d in subdirs]

    logger.info(f"Indexing {len(repositories_to_index)} repository(ies)")
    click.echo("Indexing repositories...")

    total_files = 0
    total_chunks = 0
    repos_processed = 0
    overall_start = time.perf_counter()

    for repo_name, repo_path in repositories_to_index:
        repo_start = time.perf_counter()

        try:
            if verbose:
                click.echo(f"[{repo_name}] Starting indexing...")

            logger.debug(f"Indexing repository: {repo_name} at {repo_path}")
            result = index_repository(
                repository_path=repo_path,
                repository_name=repo_name,
                db_path=str(db_path),
            )

            files_processed = result["files_processed"]
            chunks_created = result["chunks_created"]

            total_files += files_processed
            total_chunks += chunks_created
            repos_processed += 1

            repo_elapsed = time.perf_counter() - repo_start
            logger.info(
                f"Indexed {repo_name}: {files_processed} files, "
                f"{chunks_created} chunks in {repo_elapsed:.2f}s"
            )

            click.echo(
                format_text_index_repo(repo_name, files_processed, chunks_created, repo_elapsed)
            )

        except Exception as e:
            logger.warning(f"Failed to index {repo_name}: {e}")
            if verbose:
                click.echo(f"Warning: Failed to index {repo_name}: {e}", err=True)
            continue

    overall_elapsed = time.perf_counter() - overall_start

    if repos_processed == 0:
        logger.error("Failed to index any repositories")
        click.echo("Error: Failed to index any repositories", err=True)
        sys.exit(2)

    logger.info(
        f"Indexing complete: {repos_processed} repos, {total_files} files, "
        f"{total_chunks} chunks in {overall_elapsed:.2f}s"
    )
    click.echo(
        format_text_index_summary(repos_processed, total_files, total_chunks, overall_elapsed)
    )
