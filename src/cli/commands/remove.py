import logging
import sys

import click

from src.cli.formatters import format_text_remove_confirmation, format_text_remove_success
from src.storage.chromadb_client import (
    ChromaDBClient,
    ChromaDBConnectionError,
    CollectionNotFoundError,
)

logger = logging.getLogger(__name__)


def remove_command(db_path: str, repo: str, confirm: bool) -> None:
    logger.debug(f"Remove command: repo={repo}, confirm={confirm}")

    try:
        db_client = ChromaDBClient(path=db_path)
        logger.debug(f"Connected to ChromaDB at {db_path}")
    except ChromaDBConnectionError:
        logger.error(f"Failed to connect to ChromaDB at {db_path}")
        click.echo(f"Error: Cannot connect to ChromaDB at {db_path}", err=True)
        sys.exit(2)

    try:
        collection = db_client.get_collection(repo)
        chunk_count = collection.count()
        logger.debug(f"Repository '{repo}' has {chunk_count} chunks")
    except CollectionNotFoundError:
        logger.error(f"Repository '{repo}' not found")
        click.echo(f"Error: Repository '{repo}' not found", err=True)
        sys.exit(2)

    if not confirm:
        prompt = format_text_remove_confirmation(repo, chunk_count)
        response = click.prompt(prompt, type=str, default="N", show_default=False)

        if response.lower() not in ["y", "yes"]:
            logger.info(f"User cancelled removal of '{repo}'")
            click.echo("Operation cancelled")
            sys.exit(1)

    try:
        deleted_count = db_client.delete_collection(repo)
        logger.info(f"Deleted repository '{repo}' with {deleted_count} chunks")
        click.echo(format_text_remove_success(repo, deleted_count))
    except ChromaDBConnectionError as e:
        logger.error(f"Error deleting collection '{repo}': {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
