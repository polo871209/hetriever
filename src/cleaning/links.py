import re


def clean_links(content: str) -> str:
    """Clean Hugo link shortcodes from markdown content.

    Converts Hugo ref and relref shortcodes to plain text by extracting
    the link target. E.g., {{< ref "path" >}} becomes "path".

    Args:
        content: Markdown content containing Hugo link shortcodes.

    Returns:
        Content with link shortcodes replaced by their target paths.
    """
    content = re.sub(r'\{\{<\s*ref\s+"([^"]+)"\s*>\}\}', r"\1", content)
    return re.sub(r'\{\{<\s*relref\s+"([^"]+)"\s*>\}\}', r"\1", content)
