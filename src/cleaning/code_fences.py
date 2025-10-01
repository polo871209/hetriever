import re


def clean_code_fences(content: str) -> str:
    """Remove metadata annotations from code fence declarations.

    Cleans code fence lines like ```python {hl_lines=[1,2]} to just ```python
    by removing the curly brace metadata.

    Args:
        content: Markdown content with potentially annotated code fences.

    Returns:
        Content with code fence metadata removed.
    """
    pattern = r"(```\w+)\s*\{[^}]+\}"
    return re.sub(pattern, r"\1", content)
