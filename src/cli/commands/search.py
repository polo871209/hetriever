import logging
import sys

import click

from src.cli.formatters import format_json_search_results, format_text_search_results
from src.models.retrieval import RetrievalResult
from src.storage.chromadb_client import (
    ChromaDBClient,
    ChromaDBConnectionError,
    CollectionNotFoundError,
    EmptyQueryError,
    InvalidLimitError,
)

logger = logging.getLogger(__name__)


def search_command(
    db_path: str,
    query: str,
    repo: str | None,
    limit: int,
    output_format: str,
    rerank: bool = True,
) -> None:
    logger.debug(f"Search command: query='{query}', repo={repo}, limit={limit}")

    if not query or not query.strip():
        logger.error("Empty query provided")
        click.echo("Error: Query cannot be empty", err=True)
        sys.exit(2)

    try:
        db_client = ChromaDBClient(path=db_path)
        logger.debug(f"Connected to ChromaDB at {db_path}")
    except ChromaDBConnectionError:
        logger.error(f"Failed to connect to ChromaDB at {db_path}")
        click.echo(f"Error: Cannot connect to ChromaDB at {db_path}", err=True)
        sys.exit(2)

    try:
        if repo:
            logger.debug(f"Searching in repository: {repo}")
            try:
                collection = db_client.get_collection(repo)
                result = db_client.search_chunks(collection, query, limit, rerank=rerank)
                logger.info(
                    f"Found {result.total_results} results in {repo} "
                    f"({result.search_time_ms:.2f}ms)"
                )
            except CollectionNotFoundError:
                logger.error(f"Repository '{repo}' not indexed")
                click.echo(f"Error: Repository '{repo}' not indexed", err=True)
                sys.exit(2)
        else:
            logger.debug("Searching across all repositories")
            collections = db_client.list_collections()
            if not collections:
                logger.warning("No indexed repositories found")
                click.echo("No indexed repositories found", err=True)
                sys.exit(2)

            all_matches = []
            total_search_time = 0.0

            for col_info in collections:
                try:
                    collection = db_client.get_collection(col_info.name)
                    result = db_client.search_chunks(collection, query, limit, rerank=rerank)
                    all_matches.extend(result.matches)
                    total_search_time += result.search_time_ms
                    logger.debug(f"Searched {col_info.name}: {len(result.matches)} matches")
                except Exception:
                    continue

            all_matches.sort(key=lambda m: m.score, reverse=True)
            all_matches = all_matches[:limit]

            result = RetrievalResult(
                query=query,
                matches=all_matches,
                total_results=len(all_matches),
                search_time_ms=total_search_time,
            )
            logger.info(
                f"Found {len(all_matches)} total results across all repos "
                f"({total_search_time:.2f}ms)"
            )

        if output_format == "json":
            click.echo(format_json_search_results(query, result.matches, result.search_time_ms))
        else:
            click.echo(format_text_search_results(query, result.matches))

    except EmptyQueryError:
        logger.error("Empty query error")
        click.echo("Error: Query cannot be empty", err=True)
        sys.exit(2)
    except InvalidLimitError as e:
        logger.error(f"Invalid limit: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
