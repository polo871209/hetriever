import json
from typing import Any

CONTENT_PREVIEW_LENGTH = 200


def format_text_index_summary(
    repos_processed: int, files_processed: int, chunks_created: int, total_time: float
) -> str:
    repo_text = "repository" if repos_processed == 1 else "repositories"
    return (
        f"Indexed {repos_processed} {repo_text}, {files_processed} files, "
        f"{chunks_created} chunks in {total_time:.1f}s"
    )


def format_text_index_repo(repo_name: str, files: int, chunks: int, elapsed: float) -> str:
    return f"✓ {repo_name} ({files} files, {chunks:,} chunks) - {elapsed:.1f}s"


def format_text_search_results(query: str, matches: list[Any]) -> str:
    if not matches:
        return f'Results for "{query}" (0 matches)'

    lines = [f'Results for "{query}" ({len(matches)} matches):', ""]

    for i, match in enumerate(matches, 1):
        lines.append(f"{i}. [{match.repository}] {match.file_path} (score: {match.score:.2f})")
        lines.append(f"   {match.heading_context}")
        lines.append("   ")

        content_preview = match.content[:CONTENT_PREVIEW_LENGTH].replace("\n", " ")
        if len(match.content) > CONTENT_PREVIEW_LENGTH:
            content_preview += "..."
        lines.append(f"   {content_preview}")
        lines.append("")

    return "\n".join(lines)


def format_json_search_results(query: str, matches: list[Any], search_time_ms: float) -> str:
    matches_data = []
    for match in matches:
        matches_data.append(
            {
                "chunk_id": match.chunk_id,
                "repository": match.repository,
                "file_path": match.file_path,
                "heading_context": match.heading_context,
                "content": match.content,
                "score": round(match.score, 4),
                "metadata": match.metadata,
            }
        )

    result = {
        "query": query,
        "total_results": len(matches),
        "search_time_ms": round(search_time_ms, 1),
        "matches": matches_data,
    }

    return json.dumps(result, indent=2)


def format_text_list_repositories(collections: list[Any]) -> str:
    if not collections:
        return "No indexed repositories"

    lines = ["Indexed repositories:", ""]

    for col in collections:
        lines.append(col.name)
        metadata = col.metadata

        if "source_path" in metadata:
            lines.append(f"  Path: {metadata['source_path']}")

        if "last_updated" in metadata:
            lines.append(f"  Last updated: {metadata['last_updated']}")

        file_count = metadata.get("file_count", "?")
        chunk_count = col.chunk_count
        lines.append(f"  Files: {file_count} | Chunks: {chunk_count:,}")
        lines.append("")

    return "\n".join(lines)


def format_json_list_repositories(collections: list[Any]) -> str:
    repos = []
    for col in collections:
        metadata = col.metadata
        repos.append(
            {
                "name": col.name,
                "source_path": metadata.get("source_path"),
                "last_updated": metadata.get("last_updated"),
                "file_count": metadata.get("file_count"),
                "chunk_count": col.chunk_count,
            }
        )

    return json.dumps({"repositories": repos}, indent=2)


def format_text_remove_confirmation(repo: str, chunk_count: int) -> str:
    return f"Remove repository '{repo}'? This will delete {chunk_count:,} chunks. [y/N]: "


def format_text_remove_success(repo: str, chunk_count: int) -> str:
    return f"✓ Removed {repo} ({chunk_count:,} chunks deleted)"
