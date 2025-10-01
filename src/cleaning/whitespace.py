from .patterns import MULTIPLE_NEWLINES, TRAILING_WHITESPACE


def normalize_whitespace(content: str) -> str:
    """Normalize whitespace in markdown while preserving code blocks.

    Applies whitespace normalization only to non-code content:
    - Removes trailing whitespace from lines
    - Collapses multiple newlines to at most two (blank line)
    - Ensures content ends with single newline

    Code blocks (delimited by ```) are preserved without modification.

    Args:
        content: Markdown content to normalize.

    Returns:
        Content with normalized whitespace outside code blocks.
    """
    parts = []
    in_code_block = False
    current_part = []

    for line in content.split("\n"):
        if line.strip().startswith("```"):
            if current_part:
                text = "\n".join(current_part)
                if not in_code_block:
                    text = TRAILING_WHITESPACE.sub("", text)
                    text = MULTIPLE_NEWLINES.sub("\n\n", text)
                parts.append(text)
                current_part = []
            in_code_block = not in_code_block
            parts.append(line)
        else:
            current_part.append(line)

    if current_part:
        text = "\n".join(current_part)
        if not in_code_block:
            text = TRAILING_WHITESPACE.sub("", text)
            text = MULTIPLE_NEWLINES.sub("\n\n", text)
        parts.append(text)

    result = "\n".join(parts)

    if result and not result.endswith("\n"):
        result += "\n"

    return result
