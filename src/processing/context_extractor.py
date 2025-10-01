import re


def extract_heading_hierarchy(content: str, chunk_start_line: int) -> str:
    """Extract hierarchical heading context for a chunk location.

    Builds a breadcrumb trail of headings from the document start up to the
    specified line, maintaining proper hierarchy by tracking heading levels.

    Args:
        content: Full document content.
        chunk_start_line: Line number where the chunk starts.

    Returns:
        Breadcrumb string of headings separated by ' > ', e.g., 'Guide > Setup > Installation'.
        Returns empty string if no headings found.
    """
    lines = content.split("\n")
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    hierarchy: list[tuple[int, str]] = []

    for i in range(chunk_start_line + 1):
        if i >= len(lines):
            break

        match = heading_pattern.match(lines[i])
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()

            hierarchy = [h for h in hierarchy if h[0] < level]
            hierarchy.append((level, text))

    if not hierarchy:
        return ""

    return " > ".join([h[1] for h in hierarchy])


def build_breadcrumb(headings: list[str]) -> str:
    """Build breadcrumb trail from list of heading strings.

    Args:
        headings: Ordered list of heading texts.

    Returns:
        Breadcrumb string with headings joined by ' > ', or empty string if no headings.
    """
    return " > ".join(headings) if headings else ""
