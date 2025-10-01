import logging
from pathlib import Path

from src.cleaning.pipeline import clean_markdown
from src.models.document import DocumentChunk
from src.processing.chunker import chunk_by_headings
from src.processing.context_extractor import extract_heading_hierarchy
from src.processing.file_discovery import discover_markdown_files
from src.processing.metadata import enrich_metadata
from src.storage.chromadb_client import ChromaDBClient

logger = logging.getLogger(__name__)


def index_repository(
    repository_path: Path,
    repository_name: str,
    db_path: str = "./chroma_data",
    target_tokens: int = 800,
    batch_size: int = 100,
) -> dict[str, int]:
    """Index all markdown files from a repository into ChromaDB.

    Main orchestration function that:
    1. Discovers markdown files
    2. Cleans and extracts frontmatter
    3. Chunks content by headings
    4. Extracts heading hierarchy context
    5. Enriches metadata
    6. Stores chunks in ChromaDB with embeddings

    Args:
        repository_path: Path to repository root directory.
        repository_name: Human-readable repository identifier.
        db_path: ChromaDB storage directory path.
        target_tokens: Target token count per chunk (default 800).
        batch_size: Number of chunks to add per batch (default 100).

    Returns:
        Dictionary with 'files_processed' and 'chunks_created' counts.

    Raises:
        FileNotFoundError: If repository_path does not exist.
    """
    logger.info(f"Starting indexing for repository: {repository_name} at {repository_path}")

    if not repository_path.exists():
        logger.error(f"Repository path does not exist: {repository_path}")
        raise FileNotFoundError(f"Repository path does not exist: {repository_path}")

    sanitized_name = repository_name.lower().replace("_", "-")
    logger.debug(f"Sanitized repository name: {sanitized_name}")

    markdown_files = discover_markdown_files(repository_path)
    logger.info(f"Discovered {len(markdown_files)} markdown files")

    db_client = ChromaDBClient(path=db_path)

    collection_metadata = {
        "source_path": str(repository_path),
        "file_count": len(markdown_files),
    }
    collection = db_client.create_collection(sanitized_name, collection_metadata)
    logger.info(f"Created collection: {sanitized_name}")

    all_chunks: list[DocumentChunk] = []
    total_chunks = 0
    failed_files = 0

    for file_path in markdown_files:
        try:
            logger.debug(f"Processing file: {file_path}")
            content = file_path.read_text(encoding="utf-8")

            frontmatter, cleaned_body = clean_markdown(content)

            chunks = chunk_by_headings(cleaned_body, target_tokens=target_tokens)

            for idx, chunk in enumerate(chunks):
                chunk_id = f"{sanitized_name}:{file_path.relative_to(repository_path)}:chunk{idx}"

                heading_context = extract_heading_hierarchy(content, chunk.start_line)

                metadata = enrich_metadata(
                    frontmatter,
                    file_path,
                    repository_name,
                )

                doc_chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    file_path=file_path,
                    repository_name=repository_name,
                    content=chunk.content,
                    heading_context=heading_context or chunk.heading_context,
                    chunk_index=idx,
                    token_count=chunk.token_count,
                    metadata=metadata,
                )

                all_chunks.append(doc_chunk)
                total_chunks += 1

        except Exception as e:
            failed_files += 1
            logger.warning(f"Failed to process file {file_path}: {e}")
            continue

    if all_chunks:
        logger.info(f"Adding {len(all_chunks)} chunks to collection")
        db_client.add_chunks(collection, all_chunks, batch_size=batch_size)

    db_client.update_collection_metadata(collection, {"total_chunks": total_chunks})

    if failed_files > 0:
        logger.warning(f"Failed to process {failed_files} files")

    logger.info(f"Indexing complete: {len(markdown_files)} files, {total_chunks} chunks")

    return {
        "files_processed": len(markdown_files),
        "chunks_created": total_chunks,
    }
