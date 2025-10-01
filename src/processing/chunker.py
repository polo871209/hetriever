import re
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a semantic chunk of markdown content.

    Attributes:
        content: The actual text content of the chunk.
        heading_context: The heading under which this chunk appears.
        start_line: Starting line number in the original document.
        end_line: Ending line number in the original document.
        token_count: Estimated token count for the chunk.
    """

    content: str
    heading_context: str
    start_line: int
    end_line: int
    token_count: int


def estimate_tokens(text: str) -> int:
    """Estimate token count using word-based approximation.

    Args:
        text: Text content to estimate tokens for.

    Returns:
        Estimated number of tokens (word count).
    """
    return len(text.split())


def chunk_by_headings(
    content: str,
    target_tokens: int = 800,
    max_tokens: int = 2000,
) -> list[Chunk]:
    """Split markdown content into semantic chunks based on heading structure.

    Chunks are created at markdown heading boundaries, with automatic splitting
    when chunks exceed target token count. Chunks smaller than 100 tokens are
    filtered out to maintain quality.

    Args:
        content: Markdown content to chunk.
        target_tokens: Target token count per chunk (triggers split).
        max_tokens: Maximum allowed tokens per chunk (currently unused).

    Returns:
        List of Chunk objects with content, heading context, and metadata.
    """
    lines = content.split("\n")
    chunks: list[Chunk] = []
    current_chunk_lines: list[str] = []
    current_heading = ""
    chunk_start_line = 0

    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    for i, line in enumerate(lines):
        match = heading_pattern.match(line)

        if match:
            if current_chunk_lines:
                chunk_text = "\n".join(current_chunk_lines)
                token_count = estimate_tokens(chunk_text)

                if token_count >= 100:
                    chunks.append(
                        Chunk(
                            content=chunk_text,
                            heading_context=current_heading,
                            start_line=chunk_start_line,
                            end_line=i - 1,
                            token_count=token_count,
                        )
                    )
                    current_chunk_lines = []

            current_heading = match.group(2).strip()
            chunk_start_line = i
            current_chunk_lines = [line]
        else:
            current_chunk_lines.append(line)

            if current_chunk_lines:
                current_text = "\n".join(current_chunk_lines)
                current_tokens = estimate_tokens(current_text)

                if current_tokens >= target_tokens:
                    chunks.append(
                        Chunk(
                            content=current_text,
                            heading_context=current_heading,
                            start_line=chunk_start_line,
                            end_line=i,
                            token_count=current_tokens,
                        )
                    )
                    current_chunk_lines = []
                    chunk_start_line = i + 1

    if current_chunk_lines:
        chunk_text = "\n".join(current_chunk_lines)
        token_count = estimate_tokens(chunk_text)

        if token_count >= 100:
            chunks.append(
                Chunk(
                    content=chunk_text,
                    heading_context=current_heading,
                    start_line=chunk_start_line,
                    end_line=len(lines) - 1,
                    token_count=token_count,
                )
            )

    return chunks
