import logging
import sys

import click

from src.cli.formatters import format_json_list_repositories, format_text_list_repositories
from src.storage.chromadb_client import ChromaDBClient, ChromaDBConnectionError

logger = logging.getLogger(__name__)


def list_command(db_path: str, output_format: str) -> None:
    logger.debug(f"List command: db_path={db_path}, format={output_format}")

    try:
        db_client = ChromaDBClient(path=db_path)
        logger.debug(f"Connected to ChromaDB at {db_path}")
    except ChromaDBConnectionError:
        logger.error(f"Failed to connect to ChromaDB at {db_path}")
        click.echo(f"Error: Cannot connect to ChromaDB at {db_path}", err=True)
        sys.exit(2)

    try:
        collections = db_client.list_collections()
        logger.info(f"Found {len(collections)} indexed repositories")

        if output_format == "json":
            click.echo(format_json_list_repositories(collections))
        else:
            click.echo(format_text_list_repositories(collections))

    except ChromaDBConnectionError as e:
        logger.error(f"Error listing collections: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
